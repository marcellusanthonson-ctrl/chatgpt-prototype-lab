#!/usr/bin/env node
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { pathToFileURL } = require('node:url');
const { chromium } = require('playwright');

const root = path.resolve(__dirname, '..');
const artifact = path.join(root, 'foundation-library/visual-foundations/MINIMUM-IMPECCABLE-VISUAL-FOUNDATION-001/MINIMUM_IMPECCABLE_BASE_001.html');
const validator = path.join(root, 'scripts/validate_minimum_impeccable_browser.cjs');
const script = __filename;
const output = path.resolve(process.env.MIVF_CAPTURE_OUTPUT || path.join('/tmp', `mivf-capture-${Date.now()}`));
const captures = path.join(output, 'captures');
const executablePath = process.env.MIVF_CHROMIUM_EXECUTABLE || undefined;
const originCommit = process.env.MIVF_ORIGIN_COMMIT || 'VERIFY_LIVE_AT_USE';
const expectedArtifactHash = '20f38c901d7787d1528e7520c2d46840622e43d8b5daabb1f3d5887af6ff8143';
const failures = [];

const sha256 = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const writeJson = (file, value) => fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
const check = (condition, message) => { if (!condition) failures.push(message); };

function widths() {
  const values = [];
  for (let width = 320; width <= 1920; width += 16) values.push(width);
  for (const width of [360, 390, 640, 768, 1024, 1280, 1440, 1920]) if (!values.includes(width)) values.push(width);
  return values.sort((a, b) => a - b);
}

function contactSheet(records) {
  const cards = records.map(record => `<figure><a href="captures/${record.filename}"><img src="captures/${record.filename}" loading="lazy" alt="Captura de ${record.width} por ${record.height} píxeles"></a><figcaption>${record.width}×${record.height} · ${record.image_sha256.slice(0, 12)}</figcaption></figure>`).join('\n');
  return `<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>MIVF candidate baseline contact sheet</title><style>body{margin:0;background:#151515;color:#eee;font:14px system-ui;padding:24px}h1{font-size:20px}p{color:#bbb}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:18px}figure{margin:0;background:#222;padding:10px;border-radius:8px}img{display:block;width:100%;height:260px;object-fit:contain;object-position:top;background:white}figcaption{padding-top:8px;font-variant-numeric:tabular-nums}</style><h1>CANDIDATE_BASELINE_CAPTURE</h1><p>103 configuraciones; no constituye aprobación humana ni baseline de regresión.</p><main class="grid">${cards}</main></html>`;
}

(async () => {
  fs.mkdirSync(captures, {recursive: true});
  const artifactHash = sha256(artifact);
  check(artifactHash === expectedArtifactHash, `artifact SHA-256 mismatch: ${artifactHash}`);
  const browser = await chromium.launch({headless: true, executablePath});
  const version = await browser.version();
  const context = await browser.newContext({reducedMotion: 'reduce', colorScheme: 'light', deviceScaleFactor: 1});
  const page = await context.newPage();
  const consoleErrors = [];
  const pageErrors = [];
  const externalRequests = [];
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => pageErrors.push(String(error)));
  page.on('request', request => { if (!request.url().startsWith('file:')) externalRequests.push(request.url()); });
  const records = [];
  const userAgent = await page.evaluate(() => navigator.userAgent);

  for (const width of widths()) {
    const height = width < 640 ? 800 : 900;
    await page.setViewportSize({width, height});
    await page.goto(pathToFileURL(artifact).href, {waitUntil: 'load'});
    await page.waitForFunction(() => typeof window.__MIVF_DIAGNOSTIC__ === 'object');
    await page.evaluate(async () => { if (document.fonts?.ready) await document.fonts.ready; window.scrollTo(0, 0); });
    const geometry = await page.evaluate(() => ({
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
      scrollHeight: document.documentElement.scrollHeight,
      diagnostic: window.__MIVF_DIAGNOSTIC__,
      fonts: document.fonts?.status || 'unsupported'
    }));
    check(geometry.scrollWidth <= geometry.clientWidth + 1, `${width}px: horizontal overflow`);
    check(geometry.diagnostic.pass, `${width}px: diagnostic failed`);
    const filename = `width-${String(width).padStart(4, '0')}.png`;
    const imagePath = path.join(captures, filename);
    await page.screenshot({path: imagePath, fullPage: true, animations: 'disabled'});
    records.push({
      filename, width, height, dpr: 1, reduced_motion: 'reduce', color_scheme: 'light',
      scroll_position: {x: 0, y: 0}, fonts: geometry.fonts,
      geometry: {scroll_width: geometry.scrollWidth, client_width: geometry.clientWidth, scroll_height: geometry.scrollHeight, diagnostic_pass: geometry.diagnostic.pass},
      image_sha256: sha256(imagePath)
    });
  }

  await context.close();
  const motionContext = await browser.newContext({reducedMotion: 'no-preference', colorScheme: 'light', deviceScaleFactor: 1, viewport: {width: 390, height: 844}});
  const motionPage = await motionContext.newPage();
  const motionErrors = [];
  motionPage.on('pageerror', error => motionErrors.push(String(error)));
  await motionPage.addInitScript(() => {
    window.__layoutShifts = [];
    new PerformanceObserver(list => window.__layoutShifts.push(...list.getEntries().filter(entry => !entry.hadRecentInput).map(entry => entry.value))).observe({type: 'layout-shift', buffered: true});
  });
  await motionPage.goto(pathToFileURL(artifact).href, {waitUntil: 'load'});
  await motionPage.waitForFunction(() => typeof window.__MIVF_DIAGNOSTIC__ === 'object');
  const initialHeight = await motionPage.evaluate(() => document.documentElement.scrollHeight);
  await motionPage.evaluate(() => document.querySelector('#proceso').scrollIntoView({behavior: 'smooth'}));
  await motionPage.waitForTimeout(500);
  const motion = await motionPage.evaluate(initial => ({
    media_no_preference: matchMedia('(prefers-reduced-motion: no-preference)').matches,
    final_scroll_y: scrollY,
    layout_shift_total: window.__layoutShifts.reduce((sum, value) => sum + value, 0),
    stable_height: document.documentElement.scrollHeight === initial,
    diagnostic_pass: window.__MIVF_DIAGNOSTIC__?.pass === true
  }), initialHeight);
  check(motion.media_no_preference, 'motion smoke: no-preference media state unavailable');
  check(motion.final_scroll_y > 0, 'motion smoke: smooth navigation did not move');
  check(motion.layout_shift_total === 0, `motion smoke: unexpected layout shift ${motion.layout_shift_total}`);
  check(motion.stable_height, 'motion smoke: document height changed');
  check(motion.diagnostic_pass, 'motion smoke: diagnostic failed');
  check(motionErrors.length === 0, `motion smoke page errors: ${motionErrors.join(' | ')}`);
  await motionContext.close();
  await browser.close();

  check(consoleErrors.length === 0, `console errors: ${consoleErrors.join(' | ')}`);
  check(pageErrors.length === 0, `page errors: ${pageErrors.join(' | ')}`);
  check(externalRequests.length === 0, `external requests: ${externalRequests.join(' | ')}`);
  const manifest = {
    schema_version: '1.0.0', package_role: 'CANDIDATE_BASELINE_CAPTURE', human_approval: 'NOT_ESTABLISHED',
    origin_repository: 'marcellusanthonson-ctrl/chatgpt-prototype-lab', origin_commit: originCommit,
    artifact: {path: path.relative(root, artifact), sha256: artifactHash},
    instrumentation: {capture_script_sha256: sha256(script), browser_validator_sha256: sha256(validator)},
    environment: {browser: version, playwright: require('playwright/package.json').version, user_agent: userAgent, operating_system: `${os.platform()} ${os.release()} ${os.arch()}`},
    configuration: {count: records.length, minimum_width: 320, maximum_width: 1920, maximum_step: 16, dpr: 1, reduced_motion: 'reduce', color_scheme: 'light'},
    captures: records
  };
  writeJson(path.join(output, 'capture-manifest.json'), manifest);
  writeJson(path.join(output, 'defect-log.json'), {schema_version: '1.0.0', status: failures.length ? 'BLOCKED_WITH_DOCUMENTED_DEFECTS' : 'NO_CONFIRMED_DEFECTS', defects: failures.map((finding, index) => ({id: `CAPTURE-DEFECT-${String(index + 1).padStart(3, '0')}`, finding}))});
  writeJson(path.join(output, 'run-report.json'), {
    schema_version: '1.0.0', status: failures.length ? 'BLOCKED_WITH_DOCUMENTED_DEFECTS' : 'CANDIDATE_BASELINE_CAPTURE_READY_FOR_HUMAN_REVIEW',
    capture_count: records.length, browser_matrix: failures.length ? 'FAIL' : 'PASS', optical_review: 'PENDING_HUMAN_REVIEW', motion_smoke: motion,
    console_errors: consoleErrors, page_errors: pageErrors, external_requests: externalRequests,
    human_visual_approval: 'NOT_ESTABLISHED', wcag_conformance: 'NOT_ESTABLISHED', multibrowser_coverage: 'NOT_ESTABLISHED'
  });
  fs.writeFileSync(path.join(output, 'contact-sheet.html'), contactSheet(records));
  console.log(`Capture package: ${output}`);
  console.log(`Captured viewports: ${records.length}`);
  console.log(`Result: ${failures.length ? 'BLOCKED_WITH_DOCUMENTED_DEFECTS' : 'CANDIDATE_BASELINE_CAPTURE_READY_FOR_HUMAN_REVIEW'}`);
  if (failures.length) process.exit(1);
})().catch(error => {
  try {
    fs.mkdirSync(output, {recursive: true});
    writeJson(path.join(output, 'defect-log.json'), {schema_version: '1.0.0', status: 'BLOCKED_WITH_DOCUMENTED_DEFECTS', defects: [{id: 'CAPTURE-EXECUTION-001', finding: String(error.stack || error)}]});
  } catch {}
  console.error(error);
  process.exit(1);
});
