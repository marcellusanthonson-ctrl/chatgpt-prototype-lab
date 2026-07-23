#!/usr/bin/env node
'use strict';

const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const {pathToFileURL} = require('node:url');
const {launchBrowser} = require('./mivf_browser_driver.cjs');

const root = path.resolve(__dirname, '..');
const base = path.join(root, 'foundation-library/visual-foundations/MINIMUM-IMPECCABLE-VISUAL-FOUNDATION-001');
const artifact = path.join(base, 'MINIMUM_IMPECCABLE_BASE_001.html');
const foundationManifest = JSON.parse(fs.readFileSync(path.join(base, 'MANIFEST.json'), 'utf8'));
const validator = path.join(root, 'scripts/validate_minimum_impeccable_browser.cjs');
const driver = path.join(root, 'scripts/mivf_browser_driver.cjs');
const script = __filename;
const output = path.resolve(process.env.MIVF_CAPTURE_OUTPUT || path.join(os.tmpdir(), `mivf-capture-${Date.now()}`));
const captures = path.join(output, 'captures');
const originCommit = process.env.MIVF_ORIGIN_COMMIT || 'VERIFY_LIVE_AT_USE';
const phase = process.env.MIVF_CAPTURE_PHASE || 'CANDIDATE';
const comparisonBaseline = process.env.MIVF_COMPARE_BASELINE_MANIFEST || '';
const failures = [];
let activeBrowser = null;

const sha256 = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const canonicalTextSha256 = file => crypto.createHash('sha256').update(fs.readFileSync(file, 'utf8').replace(/\r\n/g, '\n')).digest('hex');
const writeJson = (file, value) => fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
const check = (condition, message) => { if (!condition) failures.push(message); };

function widths() {
  const values = [];
  for (let width = 320; width <= 1920; width += 16) values.push(width);
  for (const width of [360, 390, 640, 768, 1024, 1280, 1440, 1920]) if (!values.includes(width)) values.push(width);
  return values.sort((a, b) => a - b);
}

const captureWidths = new Set([320, 360, 390, 640, 768, 1024, 1440, 1920]);

function contactSheet(records) {
  const cards = records.map(record => `<figure><a href="captures/${record.filename}"><img src="captures/${record.filename}" loading="lazy" alt="Captura de ${record.width} por ${record.height} pÃ­xeles a DPR ${record.dpr}"></a><figcaption>${record.width}Ã—${record.height} Â· DPR ${record.dpr} Â· ${record.image_sha256.slice(0, 12)}</figcaption></figure>`).join('\n');
  return `<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>MIVF iconography comparison captures</title><style>body{margin:0;background:#151515;color:#eee;font:14px system-ui;padding:24px}h1{font-size:20px}p{color:#bbb}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:18px}figure{margin:0;background:#222;padding:10px;border-radius:8px}img{display:block;width:100%;height:260px;object-fit:contain;object-position:top;background:white}figcaption{padding-top:8px;font-variant-numeric:tabular-nums}</style><h1>FUNCTIONAL_ICONOGRAPHY_COMPARISON_CAPTURE Â· ${phase}</h1><p>Capturas binarias locales; no constituyen aprobaciÃ³n humana ni conformidad WCAG.</p><main class="grid">${cards}</main></html>`;
}

const geometryExpression = `(() => {
  const round = value => Math.round(value * 1000) / 1000;
  const rect = element => { const r = element.getBoundingClientRect(); return {x:round(r.x),y:round(r.y),width:round(r.width),height:round(r.height),left:round(r.left),top:round(r.top),right:round(r.right),bottom:round(r.bottom)}; };
  const controls = [...document.querySelectorAll('.footer__social-link')].map(control => {
    const svg = control.querySelector('svg');
    const style = getComputedStyle(svg);
    return {
      accessible_name: control.getAttribute('aria-label'),
      href: control.href,
      metadata: {
        category: control.dataset.iconCategory || svg?.dataset.iconCategory || null,
        render: control.dataset.iconRender || svg?.dataset.iconRender || null,
        size: control.dataset.iconSize || svg?.dataset.iconSize || null,
        box: control.dataset.iconBox || svg?.dataset.iconBox || null
      },
      control_box: rect(control),
      svg_box: rect(svg),
      view_box: svg.getAttribute('viewBox'),
      aria_hidden: svg.getAttribute('aria-hidden'),
      computed: {width:style.width,height:style.height,fill:style.fill,stroke:style.stroke,filter:style.filter,transform:style.transform},
      geometry: [...svg.children].map(node => ({tag:node.tagName.toLowerCase(),d:node.getAttribute('d'),fill:node.getAttribute('fill'),stroke:node.getAttribute('stroke'),stroke_width:node.getAttribute('stroke-width')}))
    };
  });
  return {
    scroll_width: document.documentElement.scrollWidth,
    client_width: document.documentElement.clientWidth,
    scroll_height: document.documentElement.scrollHeight,
    diagnostic: window.__MIVF_DIAGNOSTIC__,
    fonts: document.fonts?.status || 'unsupported',
    controls
  };
})()`;

function createComparison(before, after) {
  const beforeByKey = new Map(before.geometry_records.map(record => [`${record.width}:${record.dpr}`, record]));
  const records = after.geometry_records.map(record => {
    const prior = beforeByKey.get(`${record.width}:${record.dpr}`);
    return {
      width: record.width,
      dpr: record.dpr,
      controls: record.geometry.controls.map((control, index) => {
        const old = prior?.geometry.controls[index];
        return {
          accessible_name: control.accessible_name,
          control_box_before: old?.control_box || null,
          control_box_after: control.control_box,
          svg_box_before: old?.svg_box || null,
          svg_box_after: control.svg_box,
          control_delta: old ? {width: control.control_box.width - old.control_box.width, height: control.control_box.height - old.control_box.height} : null,
          svg_delta: old ? {width: control.svg_box.width - old.svg_box.width, height: control.svg_box.height - old.svg_box.height} : null
        };
      })
    };
  });
  return {
    schema_version: '1.0.0',
    classification: 'OPTICAL_GEOMETRY_AND_PIXEL_ALIGNMENT_COMPARISON',
    absolute_sharpness_claim: false,
    before_artifact_sha256: before.artifact.sha256,
    after_artifact_sha256: after.artifact.sha256,
    configurations_compared: records.length,
    records
  };
}

(async () => {
  fs.mkdirSync(captures, {recursive: true});
  const artifactHash = canonicalTextSha256(artifact);
  check(artifactHash === foundationManifest.artifact_sha256, `artifact canonical SHA-256 mismatch: ${artifactHash}`);
  const browser = activeBrowser = await launchBrowser();
  const consoleErrors = [];
  const pageErrors = [];
  const externalRequests = [];
  browser.client.on('Runtime.consoleAPICalled', event => {
    if (event.type === 'error') consoleErrors.push(event.args.map(item => item.value || item.description || '').join(' '));
  });
  browser.client.on('Runtime.exceptionThrown', event => pageErrors.push(event.exceptionDetails?.exception?.description || event.exceptionDetails?.text || 'unknown exception'));
  browser.client.on('Network.requestWillBeSent', event => {
    const url = event.request?.url || '';
    if (url && !url.startsWith('file:') && !url.startsWith('data:') && url !== 'about:blank') externalRequests.push(url);
  });

  const geometryRecords = [];
  const screenshotRecords = [];
  await browser.setReducedMotion('reduce');
  await browser.setOffline(true);
  for (const dpr of [1, 2]) {
    for (const width of widths()) {
      const height = width < 640 ? 800 : 900;
      await browser.setViewport({width, height, deviceScaleFactor: dpr});
      await browser.navigate(pathToFileURL(artifact).href);
      const geometry = await browser.evaluate(geometryExpression);
      check(geometry.scroll_width <= geometry.client_width + 1, `${width}px DPR ${dpr}: horizontal overflow`);
      check(geometry.diagnostic?.pass === true, `${width}px DPR ${dpr}: diagnostic failed`);
      geometryRecords.push({width, height, dpr, reduced_motion: 'reduce', offline: true, geometry});
      if (captureWidths.has(width)) {
        const filename = `width-${String(width).padStart(4, '0')}-dpr-${dpr}.png`;
        const imagePath = path.join(captures, filename);
        await browser.screenshot(imagePath, {fullPage: true});
        screenshotRecords.push({filename, width, height, dpr, image_sha256: sha256(imagePath)});
      }
    }
  }
  await browser.close();
  activeBrowser = null;

  check(consoleErrors.length === 0, `console errors: ${consoleErrors.join(' | ')}`);
  check(pageErrors.length === 0, `page errors: ${pageErrors.join(' | ')}`);
  check(externalRequests.length === 0, `external requests: ${externalRequests.join(' | ')}`);
  const manifest = {
    schema_version: '1.0.0',
    package_role: 'FUNCTIONAL_ICONOGRAPHY_COMPARISON_CAPTURE',
    phase,
    human_approval: 'NOT_ESTABLISHED',
    origin_repository: 'marcellusanthonson-ctrl/chatgpt-prototype-lab',
    origin_commit: originCommit,
    artifact: {path: path.relative(root, artifact).replace(/\\/g, '/'), sha256: artifactHash, hash_normalization: 'UTF8_LF'},
    instrumentation: {capture_script_sha256: canonicalTextSha256(script), browser_validator_sha256: canonicalTextSha256(validator), browser_driver_sha256: canonicalTextSha256(driver)},
    environment: {browser: browser.browserVersion, user_agent: browser.userAgent, node: process.version, operating_system: `${os.platform()} ${os.release()} ${os.arch()}`},
    configuration: {geometry_count: geometryRecords.length, screenshot_count: screenshotRecords.length, minimum_width: 320, maximum_width: 1920, maximum_step: 16, device_scale_factors: [1, 2], reduced_motion: 'reduce', offline: true},
    geometry_records: geometryRecords,
    screenshots: screenshotRecords,
    console_errors: consoleErrors,
    page_errors: pageErrors,
    external_requests: externalRequests,
    claim_limits: {absolute_sharpness_automated: false, human_visual_approval: false, wcag_conformance: false, multibrowser_coverage: false}
  };
  writeJson(path.join(output, 'capture-manifest.json'), manifest);
  writeJson(path.join(output, 'defect-log.json'), {schema_version: '1.0.0', status: failures.length ? 'BLOCKED_WITH_DOCUMENTED_DEFECTS' : 'NO_CONFIRMED_DEFECTS', defects: failures.map((finding, index) => ({id: `CAPTURE-DEFECT-${String(index + 1).padStart(3, '0')}`, finding}))});
  writeJson(path.join(output, 'run-report.json'), {
    schema_version: '1.0.0',
    status: failures.length ? 'BLOCKED_WITH_DOCUMENTED_DEFECTS' : 'OPTICAL_GEOMETRY_AND_PIXEL_ALIGNMENT_PASS',
    geometry_configurations: geometryRecords.length,
    screenshots: screenshotRecords.length,
    human_visual_approval: 'NOT_ESTABLISHED',
    wcag_conformance: 'NOT_ESTABLISHED',
    absolute_sharpness: 'NOT_ESTABLISHED'
  });
  fs.writeFileSync(path.join(output, 'contact-sheet.html'), contactSheet(screenshotRecords));
  if (comparisonBaseline) {
    const before = JSON.parse(fs.readFileSync(comparisonBaseline, 'utf8'));
    writeJson(path.join(output, 'comparison.json'), createComparison(before, manifest));
  }
  console.log(`Capture package: ${output}`);
  console.log(`Geometry configurations: ${geometryRecords.length}`);
  console.log(`Screenshots: ${screenshotRecords.length}`);
  console.log(`Result: ${failures.length ? 'BLOCKED_WITH_DOCUMENTED_DEFECTS' : 'OPTICAL_GEOMETRY_AND_PIXEL_ALIGNMENT_PASS'}`);
  if (failures.length) process.exit(1);
})().catch(async error => {
  try { await activeBrowser?.close(); } catch {}
  try {
    fs.mkdirSync(output, {recursive: true});
    writeJson(path.join(output, 'defect-log.json'), {schema_version: '1.0.0', status: 'BLOCKED_WITH_DOCUMENTED_DEFECTS', defects: [{id: 'CAPTURE-EXECUTION-001', finding: String(error.stack || error)}]});
  } catch {}
  console.error(error);
  process.exit(1);
});
