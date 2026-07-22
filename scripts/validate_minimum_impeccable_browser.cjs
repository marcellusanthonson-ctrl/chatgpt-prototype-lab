#!/usr/bin/env node
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require('playwright');

const root = path.resolve(__dirname, '..');
const html = path.join(root, 'foundation-library/visual-foundations/MINIMUM-IMPECCABLE-VISUAL-FOUNDATION-001/MINIMUM_IMPECCABLE_BASE_001.html');
const target = pathToFileURL(html).href;
const failures = [];
const measurements = [];

function check(condition, message) {
  if (!condition) failures.push(message);
}

(async () => {
  const browser = await chromium.launch({headless: true});
  const context = await browser.newContext({reducedMotion: 'reduce'});
  const page = await context.newPage();
  const consoleErrors = [];
  const pageErrors = [];
  const externalRequests = [];
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => pageErrors.push(String(error)));
  page.on('request', request => { if (!request.url().startsWith('file:')) externalRequests.push(request.url()); });

  const widths = [];
  for (let width = 320; width <= 1920; width += 16) widths.push(width);
  for (const width of [360, 390, 640, 768, 1024, 1280, 1440, 1920]) if (!widths.includes(width)) widths.push(width);
  widths.sort((a, b) => a - b);

  for (const width of widths) {
    await page.setViewportSize({width, height: width < 640 ? 800 : 900});
    await page.goto(target, {waitUntil: 'load'});
    await page.waitForFunction(() => window.__MIVF_DIAGNOSTIC__?.pass === true);
    const result = await page.evaluate(() => {
      const root = document.documentElement;
      const rect = selector => document.querySelector(selector).getBoundingClientRect();
      const nav = rect('.nav');
      const hero = rect('.hero__grid');
      const principles = rect('#principios .container');
      const process = rect('#proceso .container');
      const contact = rect('#contacto .container');
      const footer = rect('.footer__grid');
      const sections = [...document.querySelectorAll('main > section')].map(element => element.getBoundingClientRect());
      const sectionOverlap = sections.some((current, index) => index < sections.length - 1 && current.bottom > sections[index + 1].top + 1);
      return {
        scrollWidth: root.scrollWidth,
        clientWidth: root.clientWidth,
        diagnostic: window.__MIVF_DIAGNOSTIC__,
        leftEdges: [nav.left, hero.left, principles.left, process.left, contact.left, footer.left],
        rightEdges: [nav.right, hero.right, principles.right, process.right, contact.right, footer.right],
        sectionOverlap,
        headerPosition: getComputedStyle(document.querySelector('.site-header')).position,
        headerBackground: getComputedStyle(document.querySelector('.site-header')).backgroundColor,
        focusVisibleRule: [...document.styleSheets[0].cssRules].some(rule => rule.selectorText === ':focus-visible')
      };
    });
    check(result.scrollWidth <= result.clientWidth + 1, `${width}px: horizontal overflow ${result.scrollWidth}/${result.clientWidth}`);
    check(result.diagnostic.pass, `${width}px: local diagnostic failed ${result.diagnostic.failures.join(', ')}`);
    check(!result.sectionOverlap, `${width}px: sections overlap`);
    check(result.headerPosition === 'sticky', `${width}px: navbar is not in stable sticky band`);
    check(result.headerBackground !== 'rgba(0, 0, 0, 0)', `${width}px: navbar lacks own surface`);
    check(Math.max(...result.leftEdges) - Math.min(...result.leftEdges) <= 1, `${width}px: left grid edges drift`);
    check(Math.max(...result.rightEdges) - Math.min(...result.rightEdges) <= 1, `${width}px: right grid edges drift`);
    check(result.focusVisibleRule, `${width}px: focus-visible rule missing`);
    measurements.push({width, scrollWidth: result.scrollWidth, clientWidth: result.clientWidth});
  }

  await page.setViewportSize({width: 390, height: 844});
  await page.goto(target, {waitUntil: 'load'});
  const menu = page.locator('.menu-button');
  check(await menu.isVisible(), '390px: mobile menu button is not visible');
  await menu.click();
  check(await menu.getAttribute('aria-expanded') === 'true', '390px: mobile menu did not expose expanded state');
  check(await page.locator('#primary-links').getAttribute('data-open') === 'true', '390px: mobile menu did not open');
  await page.locator('#primary-links a').first().click();
  check(await menu.getAttribute('aria-expanded') === 'false', '390px: mobile menu did not close after navigation');

  const opener = page.locator('[data-open-dialog]').last();
  await opener.click();
  check(await page.locator('#limits-dialog').evaluate(node => node.open), 'dialog did not open');
  await page.locator('[data-close-dialog]').click();
  check(await opener.evaluate(node => document.activeElement === node), 'dialog did not restore focus to opener');

  const form = page.locator('#example-form');
  await form.locator('[type="submit"]').click();
  check(await page.locator('#name').getAttribute('aria-invalid') === 'true', 'empty form did not mark name invalid');
  check((await page.locator('#form-status').textContent()).includes('conservaron'), 'invalid form did not report data preservation');
  await page.locator('#name').fill('Jonathan Martínez');
  await page.locator('#email').fill('correo-invalido');
  await page.locator('#message').fill('Texto suficientemente extenso.');
  await form.locator('[type="submit"]').click();
  check(await page.locator('#email').getAttribute('aria-invalid') === 'true', 'invalid email was not identified');
  check(await page.locator('#name').inputValue() === 'Jonathan Martínez', 'validation error discarded entered name');
  await page.locator('#email').fill('jonathan@example.com');
  await form.locator('[type="submit"]').click();
  await page.waitForFunction(() => document.querySelector('#form-status')?.dataset.state === 'success');
  check((await page.locator('#form-status').textContent()).includes('No se enviaron datos'), 'valid form did not reach local success');

  await page.evaluate(() => {
    document.querySelector('h1').textContent = 'Una base técnica deliberadamente extensa que debe conservar jerarquía, contención y legibilidad sin quebrar la retícula compartida.';
    document.querySelector('.lede').textContent = 'Contenido expandido para tensionar el diseño con una longitud considerablemente mayor, comprobar el reflujo y detectar cualquier recorte, colisión o desbordamiento estructural inesperado.';
  });
  const stress = await page.evaluate(() => ({scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth}));
  check(stress.scrollWidth <= stress.clientWidth + 1, 'content stress produced horizontal overflow');

  check(consoleErrors.length === 0, `console errors: ${consoleErrors.join(' | ')}`);
  check(pageErrors.length === 0, `page errors: ${pageErrors.join(' | ')}`);
  check(externalRequests.length === 0, `external requests: ${externalRequests.join(' | ')}`);

  await page.screenshot({path: '/tmp/MINIMUM_IMPECCABLE_BASE_001_390.png', fullPage: true});
  await page.setViewportSize({width: 1440, height: 1000});
  await page.goto(target, {waitUntil: 'load'});
  await page.screenshot({path: '/tmp/MINIMUM_IMPECCABLE_BASE_001_1440.png', fullPage: true});
  await browser.close();

  if (failures.length) {
    failures.forEach(message => console.error(`FAIL: ${message}`));
    console.error(`Browser validation: FAIL (${failures.length} failure(s))`);
    process.exit(1);
  }
  console.log(`Browser width sweep: PASS (${widths.length} widths, 320–1920px, maximum step 16px)`);
  console.log('DOM geometry, common-grid alignment and overflow: PASS');
  console.log('Navbar, menu, dialog and focus restoration: PASS');
  console.log('Form invalid, preservation and local success behavior: PASS');
  console.log('Content stress, console, resources and offline boundary: PASS');
  console.log('Optical screenshots: CAPTURED_FOR_MANUAL_INSPECTION');
  console.log('Human visual approval: NOT_ESTABLISHED');
  console.log('WCAG conformance: NOT_ESTABLISHED');
})().catch(error => {
  console.error(error);
  process.exit(1);
});
