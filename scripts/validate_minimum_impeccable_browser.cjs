#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {launchBrowser} = require('./mivf_browser_driver.cjs');

const root = path.resolve(__dirname, '..');
const html = path.join(root, 'foundation-library/visual-foundations/MINIMUM-IMPECCABLE-VISUAL-FOUNDATION-001/MINIMUM_IMPECCABLE_BASE_001.html');
const target = pathToFileURL(html).href;
const reportPath = process.env.MIVF_BROWSER_REPORT || '';
const failures = [];
const measurements = [];
const stateMeasurements = [];
let activeBrowser = null;

const check = (condition, message) => { if (!condition) failures.push(message); };
const sameRect = (a, b, tolerance = 0.01) => ['x', 'y', 'width', 'height'].every(key => Math.abs(a[key] - b[key]) <= tolerance);

function widths() {
  const values = [];
  for (let width = 320; width <= 1920; width += 16) values.push(width);
  for (const width of [360, 390, 640, 768, 1024, 1280, 1440, 1920]) if (!values.includes(width)) values.push(width);
  return values.sort((a, b) => a - b);
}

const pageMeasurementExpression = `(() => {
  const round = value => Math.round(value * 1000) / 1000;
  const rect = element => { const r = element.getBoundingClientRect(); return {x:round(r.x),y:round(r.y),width:round(r.width),height:round(r.height),left:round(r.left),right:round(r.right),top:round(r.top),bottom:round(r.bottom)}; };
  const root = document.documentElement;
  const regionRect = selector => rect(document.querySelector(selector));
  const nav = regionRect('.nav');
  const hero = regionRect('.hero__grid');
  const principles = regionRect('#principios .container');
  const process = regionRect('#proceso .container');
  const contact = regionRect('#contacto .container');
  const footer = regionRect('.footer__grid');
  const status = document.querySelector('.footer__status');
  const statusTerms = [...status.querySelectorAll('dt')].map(rect);
  const statusValues = [...status.querySelectorAll('dd')].map(rect);
  const socialLinks = [...document.querySelectorAll('.footer__social-link')];
  const socials = socialLinks.map(control => {
    const svg = control.querySelector('svg');
    const controlBox = rect(control);
    const svgBox = rect(svg);
    const optical = svg.getBBox();
    const style = getComputedStyle(svg);
    return {
      name: control.getAttribute('aria-label'),
      href: control.href,
      control_box: controlBox,
      svg_box: svgBox,
      center_delta: {x:round((svgBox.left + svgBox.width / 2) - (controlBox.left + controlBox.width / 2)),y:round((svgBox.top + svgBox.height / 2) - (controlBox.top + controlBox.height / 2))},
      optical_box: {x:round(optical.x),y:round(optical.y),width:round(optical.width),height:round(optical.height),span:round(Math.max(optical.width,optical.height))},
      metadata: {category:svg.dataset.iconCategory,render:svg.dataset.iconRender,size:Number(svg.dataset.iconSize),box:Number(svg.dataset.iconBox)},
      style: {width:style.width,height:style.height,filter:style.filter,transform:style.transform},
      aria_hidden: svg.getAttribute('aria-hidden')
    };
  });
  const socialRects = socials.map(item => item.control_box);
  const socialOverlap = socialRects.some((current, index) => socialRects.slice(index + 1).some(other => current.left < other.right && current.right > other.left && current.top < other.bottom && current.bottom > other.top));
  const sections = [...document.querySelectorAll('main > section')].map(rect);
  const sectionOverlap = sections.some((current, index) => index < sections.length - 1 && current.bottom > sections[index + 1].top + 1);
  return {
    scroll_width: root.scrollWidth,
    client_width: root.clientWidth,
    diagnostic: window.__MIVF_DIAGNOSTIC__,
    left_edges: [nav.left,hero.left,principles.left,process.left,contact.left,footer.left],
    right_edges: [nav.right,hero.right,principles.right,process.right,contact.right,footer.right],
    section_overlap: sectionOverlap,
    header_position: getComputedStyle(document.querySelector('.site-header')).position,
    header_background: getComputedStyle(document.querySelector('.site-header')).backgroundColor,
    focus_visible_rule: [...document.styleSheets[0].cssRules].some(rule => rule.selectorText === ':focus-visible'),
    reduced_motion: matchMedia('(prefers-reduced-motion: reduce)').matches,
    status: {semantic_tag:status.tagName,display:getComputedStyle(status).display,term_count:statusTerms.length,value_count:statusValues.length,term_left_edges:statusTerms.map(item=>item.left),value_left_edges:statusValues.map(item=>item.left)},
    socials: {count:socials.length,items:socials,overlap:socialOverlap}
  };
})()`;

async function measureState(browser, index) {
  const selector = `.footer__social-link:nth-child(${index + 1})`;
  await browser.evaluate(`document.querySelector('${selector}').scrollIntoView({block:'center'})`);
  const read = () => browser.evaluate(`(() => { const el=document.querySelector('${selector}'); const svg=el.querySelector('svg'); const r=el.getBoundingClientRect(); const s=svg.getBoundingClientRect(); return {control:{x:r.x,y:r.y,width:r.width,height:r.height},svg:{x:s.x,y:s.y,width:s.width,height:s.height},outline:getComputedStyle(el).outlineStyle,focus_visible:el.matches(':focus-visible')}; })()`);
  const normal = await read();
  const centerX = normal.control.x + normal.control.width / 2;
  const centerY = normal.control.y + normal.control.height / 2;
  await browser.dispatchMouse('mouseMoved', centerX, centerY);
  const hover = await read();
  await browser.evaluate(`document.querySelector('${selector}').focus()`);
  const focus = await read();
  await browser.dispatchMouse('mouseMoved', centerX, centerY);
  await browser.dispatchMouse('mousePressed', centerX, centerY, 'left', 1);
  const active = await read();
  await browser.dispatchMouse('mouseMoved', 0, 0, 'none', 1);
  await browser.dispatchMouse('mouseReleased', 0, 0, 'left', 0);
  return {normal, hover, focus, active};
}

(async () => {
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
  await browser.setReducedMotion('reduce');
  await browser.setOffline(true);

  for (const dpr of [1, 2]) {
    for (const width of widths()) {
      const height = width < 640 ? 800 : 900;
      await browser.setViewport({width, height, deviceScaleFactor: dpr});
      await browser.navigate(target);
      const result = await browser.evaluate(pageMeasurementExpression);
      check(result.scroll_width <= result.client_width + 1, `${width}px DPR ${dpr}: horizontal overflow ${result.scroll_width}/${result.client_width}`);
      check(result.diagnostic?.pass === true, `${width}px DPR ${dpr}: local diagnostic failed ${(result.diagnostic?.failures || []).join(', ')}`);
      check(!result.section_overlap, `${width}px DPR ${dpr}: sections overlap`);
      check(result.header_position === 'sticky', `${width}px DPR ${dpr}: navbar is not in stable sticky band`);
      check(result.header_background !== 'rgba(0, 0, 0, 0)', `${width}px DPR ${dpr}: navbar lacks own surface`);
      check(Math.max(...result.left_edges) - Math.min(...result.left_edges) <= 1, `${width}px DPR ${dpr}: left grid edges drift`);
      check(Math.max(...result.right_edges) - Math.min(...result.right_edges) <= 1, `${width}px DPR ${dpr}: right grid edges drift`);
      check(result.focus_visible_rule, `${width}px DPR ${dpr}: focus-visible rule missing`);
      check(result.reduced_motion, `${width}px DPR ${dpr}: reduced-motion emulation not active`);
      check(result.status.semantic_tag === 'DL' && result.status.display === 'grid', `${width}px DPR ${dpr}: footer status is not a descriptive grid`);
      check(result.status.term_count === 2 && result.status.value_count === 2, `${width}px DPR ${dpr}: footer status pairs differ`);
      check(Math.max(...result.status.term_left_edges) - Math.min(...result.status.term_left_edges) <= 1, `${width}px DPR ${dpr}: footer status labels drift`);
      check(Math.max(...result.status.value_left_edges) - Math.min(...result.status.value_left_edges) <= 1, `${width}px DPR ${dpr}: footer status values drift`);
      check(result.socials.count === 4, `${width}px DPR ${dpr}: expected four social links`);
      check(!result.socials.overlap, `${width}px DPR ${dpr}: social targets overlap`);
      const controlSizes = result.socials.items.map(item => `${item.control_box.width}:${item.control_box.height}`);
      const svgSizes = result.socials.items.map(item => `${item.svg_box.width}:${item.svg_box.height}`);
      check(new Set(controlSizes).size === 1 && controlSizes[0] === '44:44', `${width}px DPR ${dpr}: social control boxes differ or are not 44px`);
      check(new Set(svgSizes).size === 1 && svgSizes[0] === '22:22', `${width}px DPR ${dpr}: social SVG boxes differ or are not 22px`);
      const opticalSpans = result.socials.items.map(item => item.optical_box.span);
      check(Math.max(...opticalSpans) - Math.min(...opticalSpans) <= 2, `${width}px DPR ${dpr}: optical spans differ excessively (${opticalSpans.join(', ')})`);
      result.socials.items.forEach((item, index) => {
        check(Boolean(item.name), `${width}px DPR ${dpr}: social ${index + 1} accessible name missing`);
        check(/^https:\/\/www\.(instagram|whatsapp|facebook|linkedin)\.com\/$/.test(item.href), `${width}px DPR ${dpr}: social ${index + 1} destination differs`);
        check(item.aria_hidden === 'true', `${width}px DPR ${dpr}: social ${index + 1} SVG is exposed`);
        check(item.metadata.category === 'SOCIAL_OR_BRAND_ASSOCIATED_ICON', `${width}px DPR ${dpr}: social ${index + 1} category invalid`);
        check(['STROKE', 'FILL', 'HYBRID'].includes(item.metadata.render), `${width}px DPR ${dpr}: social ${index + 1} render model invalid`);
        check(item.metadata.size === 22 && item.metadata.box === 44, `${width}px DPR ${dpr}: social ${index + 1} metadata size differs`);
        check(Number.isInteger(item.control_box.width) && Number.isInteger(item.control_box.height) && Number.isInteger(item.svg_box.width) && Number.isInteger(item.svg_box.height), `${width}px DPR ${dpr}: social ${index + 1} CSS size is fractional`);
        check(Math.abs(item.center_delta.x) <= 0.01 && Math.abs(item.center_delta.y) <= 0.01, `${width}px DPR ${dpr}: social ${index + 1} SVG is not centered`);
        check(item.style.filter === 'none' && item.style.transform === 'none', `${width}px DPR ${dpr}: social ${index + 1} glyph has filter or transform`);
      });
      measurements.push({width, height, dpr, scroll_width:result.scroll_width, client_width:result.client_width, social_controls:result.socials.items});
    }
  }

  for (const dpr of [1, 2]) {
    for (const width of [390, 1440]) {
      await browser.setViewport({width, height: width < 640 ? 844 : 1000, deviceScaleFactor: dpr});
      await browser.navigate(target);
      for (let index = 0; index < 4; index += 1) {
        const states = await measureState(browser, index);
        check(sameRect(states.normal.control, states.hover.control) && sameRect(states.normal.control, states.focus.control) && sameRect(states.normal.control, states.active.control), `${width}px DPR ${dpr}: social ${index + 1} control shifts between states`);
        check(sameRect(states.normal.svg, states.hover.svg) && sameRect(states.normal.svg, states.focus.svg) && sameRect(states.normal.svg, states.active.svg), `${width}px DPR ${dpr}: social ${index + 1} SVG shifts between states`);
        check(states.focus.focus_visible && states.focus.outline !== 'none', `${width}px DPR ${dpr}: social ${index + 1} lacks focus-visible`);
        stateMeasurements.push({width, dpr, social_index:index + 1, states});
      }
    }
  }

  await browser.setViewport({width: 390, height: 844, deviceScaleFactor: 1});
  await browser.navigate(target);
  const interaction = await browser.evaluate(`(async () => {
    const menuButton=document.querySelector('.menu-button');
    menuButton.click();
    const menuOpened=menuButton.getAttribute('aria-expanded')==='true' && document.querySelector('#primary-links').dataset.open==='true';
    document.querySelector('#primary-links a').click();
    const menuClosed=menuButton.getAttribute('aria-expanded')==='false';
    const opener=[...document.querySelectorAll('[data-open-dialog]')].at(-1);
    opener.click();
    const dialogOpened=document.querySelector('#limits-dialog').open;
    document.querySelector('[data-close-dialog]').click();
    await new Promise(resolve => requestAnimationFrame(resolve));
    const dialogFocusRestored=document.activeElement===opener;
    const form=document.querySelector('#example-form');
    form.querySelector('[type="submit"]').click();
    const invalidName=document.querySelector('#name').getAttribute('aria-invalid')==='true';
    document.querySelector('#name').value='Jonathan Martinez';
    document.querySelector('#email').value='jonathan@example.com';
    document.querySelector('#message').value='Texto suficientemente extenso.';
    for (const input of form.querySelectorAll('input,textarea')) input.dispatchEvent(new Event('input',{bubbles:true}));
    form.querySelector('[type="submit"]').click();
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
    return {menuOpened,menuClosed,dialogOpened,dialogFocusRestored,invalidName,formSuccess:document.querySelector('#form-status').dataset.state==='success',formMessage:document.querySelector('#form-status').textContent};
  })()`);
  Object.entries(interaction).forEach(([key, value]) => check(key === 'formMessage' ? String(value).includes('No se enviaron datos') : value === true, `interaction failed: ${key}`));

  await browser.evaluate(`(() => { document.querySelector('h1').textContent='Una base tÃ©cnica deliberadamente extensa que debe conservar jerarquÃ­a, contenciÃ³n y legibilidad sin quebrar la retÃ­cula compartida.'; document.querySelector('.lede').textContent='Contenido expandido para tensionar el diseÃ±o con una longitud considerablemente mayor, comprobar el reflujo y detectar cualquier recorte, colisiÃ³n o desbordamiento estructural inesperado.'; })()`);
  const stress = await browser.evaluate(`({scrollWidth:document.documentElement.scrollWidth,clientWidth:document.documentElement.clientWidth})`);
  check(stress.scrollWidth <= stress.clientWidth + 1, 'content stress produced horizontal overflow');
  const zoomReflow = [];
  for (const zoom of [1, 2, 4]) {
    const logicalWidth = Math.round(1280 / zoom);
    await browser.setViewport({width: logicalWidth, height: 900, deviceScaleFactor: 1});
    await browser.navigate(target);
    const result = await browser.evaluate(`({scrollWidth:document.documentElement.scrollWidth,clientWidth:document.documentElement.clientWidth,diagnostic:window.__MIVF_DIAGNOSTIC__})`);
    check(result.scrollWidth <= result.clientWidth + 1 && result.diagnostic?.pass === true, `${zoom}x zoom-equivalent reflow failed at ${logicalWidth}px`);
    zoomReflow.push({zoom, logical_width:logicalWidth, result});
  }

  check(consoleErrors.length === 0, `console errors: ${consoleErrors.join(' | ')}`);
  check(pageErrors.length === 0, `page errors: ${pageErrors.join(' | ')}`);
  check(externalRequests.length === 0, `unexpected requests: ${externalRequests.join(' | ')}`);
  await browser.close();
  activeBrowser = null;

  const report = {
    schema_version: '1.0.0',
    status: failures.length ? 'BLOCKED_WITH_DOCUMENTED_DEFECTS' : 'OPTICAL_GEOMETRY_AND_PIXEL_ALIGNMENT_PASS',
    browser: browser.browserVersion,
    widths: widths(),
    device_scale_factors: [1, 2],
    geometry_configurations: measurements.length,
    state_configurations: stateMeasurements.length,
    offline: true,
    zoom_reflow: zoomReflow,
    console_errors: consoleErrors,
    page_errors: pageErrors,
    external_requests: externalRequests,
    measurements,
    state_measurements: stateMeasurements,
    failures,
    claim_limits: {absolute_sharpness:false,human_visual_approval:false,wcag_conformance:false,benchmark_approval:false}
  };
  if (reportPath) fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
  if (failures.length) {
    failures.forEach(message => console.error(`FAIL: ${message}`));
    console.error(`Browser validation: FAIL (${failures.length} failure(s))`);
    process.exit(1);
  }
  console.log(`Browser width/DPR sweep: PASS (${measurements.length} configurations; ${widths().length} widths at DPR 1 and 2)`);
  console.log('DOM geometry, common-grid alignment, overflow and offline operation: PASS');
  console.log('Social control boxes, SVG centering, optical spans and integer CSS sizes: PASS');
  console.log('Normal, hover, focus-visible and active geometry stability: PASS');
  console.log('Keyboard, menu, dialog, form, content stress, reduced-motion, zoom and reflow: PASS');
  console.log('Console, page errors and unexpected requests: PASS');
  console.log('Result: OPTICAL_GEOMETRY_AND_PIXEL_ALIGNMENT_PASS');
  console.log('Absolute sharpness: NOT_ESTABLISHED_BY_AUTOMATION');
  console.log('Human visual approval: NOT_ESTABLISHED');
  console.log('WCAG conformance: NOT_ESTABLISHED');
})().catch(async error => {
  try { await activeBrowser?.close(); } catch {}
  console.error(error);
  process.exit(1);
});
