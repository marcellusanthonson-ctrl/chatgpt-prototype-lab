#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawn} = require('node:child_process');

const WINDOWS_BROWSER_CANDIDATES = [
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
  'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
];

const delay = milliseconds => new Promise(resolve => setTimeout(resolve, milliseconds));

function resolveBrowserExecutable() {
  const configured = process.env.MIVF_CHROMIUM_EXECUTABLE;
  if (configured) {
    if (!fs.existsSync(configured)) throw new Error(`Configured browser executable not found: ${configured}`);
    return configured;
  }
  if (process.platform === 'win32') {
    const candidate = WINDOWS_BROWSER_CANDIDATES.find(fs.existsSync);
    if (candidate) return candidate;
  }
  throw new Error('No callable Chromium browser found. Set MIVF_CHROMIUM_EXECUTABLE to an existing executable.');
}

class CdpClient {
  constructor(webSocketUrl) {
    this.webSocketUrl = webSocketUrl;
    this.socket = null;
    this.nextId = 1;
    this.pending = new Map();
    this.listeners = new Map();
  }

  async connect() {
    this.socket = new WebSocket(this.webSocketUrl);
    await new Promise((resolve, reject) => {
      const timeout = setTimeout(() => reject(new Error('Timed out connecting to browser CDP')), 10000);
      this.socket.addEventListener('open', () => {
        clearTimeout(timeout);
        resolve();
      }, {once: true});
      this.socket.addEventListener('error', event => {
        clearTimeout(timeout);
        reject(new Error(`Browser CDP connection failed: ${event.message || 'unknown error'}`));
      }, {once: true});
    });
    this.socket.addEventListener('message', event => {
      const message = JSON.parse(String(event.data));
      if (message.id) {
        const pending = this.pending.get(message.id);
        if (!pending) return;
        this.pending.delete(message.id);
        if (message.error) pending.reject(new Error(`${pending.method}: ${message.error.message}`));
        else pending.resolve(message.result || {});
        return;
      }
      const callbacks = this.listeners.get(message.method) || [];
      callbacks.forEach(callback => callback(message.params || {}));
    });
  }

  send(method, params = {}) {
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, {resolve, reject, method});
      this.socket.send(JSON.stringify({id, method, params}));
    });
  }

  on(method, callback) {
    const callbacks = this.listeners.get(method) || [];
    callbacks.push(callback);
    this.listeners.set(method, callbacks);
    return () => this.listeners.set(method, (this.listeners.get(method) || []).filter(item => item !== callback));
  }

  once(method, timeoutMs = 15000) {
    return new Promise((resolve, reject) => {
      let remove = () => {};
      const timeout = setTimeout(() => {
        remove();
        reject(new Error(`Timed out waiting for ${method}`));
      }, timeoutMs);
      remove = this.on(method, params => {
        clearTimeout(timeout);
        remove();
        resolve(params);
      });
    });
  }

  close() {
    if (this.socket?.readyState === WebSocket.OPEN) this.socket.close();
  }
}

async function waitForDevTools(profile, child, stderrLines) {
  const portFile = path.join(profile, 'DevToolsActivePort');
  for (let attempt = 0; attempt < 600; attempt += 1) {
    if (child.exitCode !== null) {
      throw new Error(`Browser exited before CDP became ready (${child.exitCode}): ${stderrLines.join(' ').trim() || 'no stderr'}`);
    }
    if (fs.existsSync(portFile)) {
      const [port] = fs.readFileSync(portFile, 'utf8').trim().split(/\r?\n/);
      if (port) return Number(port);
    }
    await delay(50);
  }
  throw new Error(`Timed out waiting for browser DevToolsActivePort: ${stderrLines.join(' ').trim() || 'no stderr'}`);
}

async function launchBrowser() {
  const executablePath = resolveBrowserExecutable();
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'mivf-browser-'));
  const stderrLines = [];
  const child = spawn(executablePath, [
    '--headless=new',
    '--remote-debugging-port=0',
    `--user-data-dir=${profile}`,
    '--remote-allow-origins=*',
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-background-networking',
    '--disable-component-update',
    '--disable-domain-reliability',
    '--disable-features=MediaRouter,OptimizationHints,Translate',
    '--disable-sync',
    '--hide-scrollbars',
    '--metrics-recording-only',
    '--safebrowsing-disable-auto-update',
    'about:blank'
  ], {stdio: ['ignore', 'ignore', 'pipe'], windowsHide: true});
  child.stderr.setEncoding('utf8');
  child.stderr.on('data', chunk => {
    stderrLines.push(chunk);
    if (stderrLines.length > 20) stderrLines.shift();
  });

  let port;
  try {
    port = await waitForDevTools(profile, child, stderrLines);
  } catch (error) {
    if (child.exitCode === null) child.kill();
    fs.rmSync(profile, {recursive: true, force: true});
    throw error;
  }
  let version;
  let client;
  try {
    version = await fetch(`http://127.0.0.1:${port}/json/version`).then(response => response.json());
    const targets = await fetch(`http://127.0.0.1:${port}/json/list`).then(response => response.json());
    let pageTarget = targets.find(target => target.type === 'page');
    if (!pageTarget) {
      pageTarget = await fetch(`http://127.0.0.1:${port}/json/new?about%3Ablank`, {method: 'PUT'})
        .then(response => response.json());
    }
    if (!pageTarget?.webSocketDebuggerUrl) throw new Error('Browser started without a callable page target');
    client = new CdpClient(pageTarget.webSocketDebuggerUrl);
    await client.connect();
    await Promise.all([
      client.send('Page.enable'),
      client.send('Runtime.enable'),
      client.send('Network.enable'),
      client.send('Log.enable')
    ]);
  } catch (error) {
    client?.close();
    if (child.exitCode === null) child.kill();
    fs.rmSync(profile, {recursive: true, force: true, maxRetries: 10, retryDelay: 100});
    throw error;
  }

  async function setViewport({width, height, deviceScaleFactor = 1}) {
    await client.send('Emulation.setDeviceMetricsOverride', {
      width, height, deviceScaleFactor, mobile: false, screenWidth: width, screenHeight: height
    });
  }

  async function setReducedMotion(value) {
    await client.send('Emulation.setEmulatedMedia', {
      media: '',
      features: [{name: 'prefers-reduced-motion', value}]
    });
  }

  async function setOffline(offline) {
    await client.send('Network.emulateNetworkConditions', {
      offline,
      latency: 0,
      downloadThroughput: -1,
      uploadThroughput: -1,
      connectionType: offline ? 'none' : 'wifi'
    });
  }

  async function navigate(url) {
    const loaded = client.once('Page.loadEventFired');
    const result = await client.send('Page.navigate', {url});
    if (result.errorText) throw new Error(`Navigation failed: ${result.errorText}`);
    await loaded;
  }

  async function evaluate(expression) {
    const result = await client.send('Runtime.evaluate', {
      expression,
      awaitPromise: true,
      returnByValue: true,
      userGesture: true
    });
    if (result.exceptionDetails) {
      const description = result.exceptionDetails.exception?.description || result.exceptionDetails.text;
      throw new Error(`Browser evaluation failed: ${description}`);
    }
    return result.result?.value;
  }

  async function dispatchMouse(type, x, y, button = 'none', buttons = 0) {
    await client.send('Input.dispatchMouseEvent', {type, x, y, button, buttons, clickCount: button === 'left' ? 1 : 0});
  }

  async function screenshot(file, {fullPage = true} = {}) {
    let clip;
    if (fullPage) {
      const metrics = await client.send('Page.getLayoutMetrics');
      const size = metrics.cssContentSize || metrics.contentSize;
      clip = {x: 0, y: 0, width: size.width, height: size.height, scale: 1};
    }
    const result = await client.send('Page.captureScreenshot', {
      format: 'png',
      fromSurface: true,
      captureBeyondViewport: fullPage,
      ...(clip ? {clip} : {})
    });
    fs.writeFileSync(file, Buffer.from(result.data, 'base64'));
  }

  async function close() {
    try { await client.send('Browser.close'); } catch {}
    client.close();
    for (let attempt = 0; attempt < 30 && child.exitCode === null; attempt += 1) await delay(100);
    if (child.exitCode === null) {
      child.kill();
      for (let attempt = 0; attempt < 20 && child.exitCode === null; attempt += 1) await delay(100);
    }
    const resolvedProfile = path.resolve(profile);
    const resolvedTemp = path.resolve(os.tmpdir());
    if (resolvedProfile.startsWith(`${resolvedTemp}${path.sep}`)) {
      fs.rmSync(resolvedProfile, {recursive: true, force: true, maxRetries: 10, retryDelay: 100});
    }
  }

  return {
    client,
    executablePath,
    browserVersion: version.Browser || 'UNKNOWN',
    userAgent: version['User-Agent'] || 'UNKNOWN',
    setViewport,
    setReducedMotion,
    setOffline,
    navigate,
    evaluate,
    dispatchMouse,
    screenshot,
    close
  };
}

module.exports = {launchBrowser, resolveBrowserExecutable};
