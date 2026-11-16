#!/usr/bin/env node
/*
 * Headless render check for an interactive story page.
 *
 *   node render_check.js <page.html> [--out <dir>] [--only id1,id2] [--no-shots]
 *
 * For every scene: opens it at its last beat, waits for the entrance animations,
 * takes a screenshot (<dir>/<nn>-<id>.png) and measures every text box for clipped
 * or overflowing text and for boxes outside the 1600 x 900 stage. Then runs a short
 * interaction pass (drawer, notes, chapters, main tree, walk mode, keyboard).
 * Writes <dir>/render-report.json; exit code 1 on any console error, page error,
 * overflow or out-of-stage box.
 *
 * Finds playwright-core and a Chromium build by itself; override with the
 * PLAYWRIGHT_CORE and CHROME_PATH environment variables.
 */
const fs = require('fs');
const path = require('path');

function findPlaywright() {
  const tries = [process.env.PLAYWRIGHT_CORE, 'playwright-core', 'playwright',
    '/usr/local/lib/node_modules/docgen-utils/node_modules/playwright-core',
    '/usr/local/lib/node_modules/playwright-core', '/usr/lib/node_modules/playwright-core'].filter(Boolean);
  for (const t of tries) { try { return require(t); } catch (e) { /* next */ } }
  return null;
}
function findChrome() {
  if (process.env.CHROME_PATH && fs.existsSync(process.env.CHROME_PATH)) return process.env.CHROME_PATH;
  const roots = ['/opt/docgen-browsers', path.join(process.env.HOME || '/root', '.cache/ms-playwright')];
  for (const r of roots) {
    if (!fs.existsSync(r)) continue;
    for (const d of fs.readdirSync(r)) {
      for (const sub of ['chrome-headless-shell-linux64/chrome-headless-shell', 'chrome-linux/chrome', 'chrome-linux64/chrome']) {
        const p = path.join(r, d, sub);
        if (fs.existsSync(p)) return p;
      }
    }
  }
  return null; // let playwright use its own default
}

const args = process.argv.slice(2);
if (!args[0]) { console.error('usage: node render_check.js <page.html> [--out dir] [--only ids] [--no-shots]'); process.exit(2); }
const file = path.resolve(args[0]);
const opt = (k, d) => { const i = args.indexOf(k); return i > 0 ? args[i + 1] : d; };
const outDir = path.resolve(opt('--out', path.join(path.dirname(file), 'render-check')));
const only = opt('--only', null) ? opt('--only').split(',') : null;
const shots = !args.includes('--no-shots');

const pw = findPlaywright();
if (!pw) { console.log(JSON.stringify({status: 'unavailable', reason: 'playwright-core not found'})); process.exit(3); }

(async () => {
  fs.mkdirSync(outDir, {recursive: true});
  const exe = findChrome();
  const browser = await pw.chromium.launch(Object.assign({args: ['--no-sandbox']}, exe ? {executablePath: exe} : {}));
  const page = await browser.newPage({viewport: {width: 1600, height: 1012}});
  const errors = [];
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
  page.on('requestfailed', r => errors.push('request failed: ' + r.url()));
  page.on('request', r => { const u = r.url(); if (!u.startsWith('file:') && !u.startsWith('data:') && !u.startsWith('about:')) errors.push('external request: ' + u); });
  await page.goto('file://' + file);
  await page.waitForTimeout(1000);
  const ids = await page.evaluate(() => JSON.parse(document.getElementById('story-data').textContent).scenes.map(s => s.id));
  const hasHook = await page.evaluate(() => !!window.__story);
  if (!hasHook) errors.push('engine test hook window.__story missing — page not built with interactive-deck-story engine 1.0+');
  const scenes = [];
  let n = 0;
  for (const id of ids) {
    n++;
    if (only && !only.includes(id)) continue;
    await page.evaluate(i => window.__story.go(i, true), id);
    await page.waitForTimeout(2800);
    const res = await page.evaluate(() => {
      const st = document.getElementById('stage');
      const sc = st.querySelector('.scene:last-child');
      const sr = st.getBoundingClientRect(), k = sr.width / 1600;
      const bad = [], out = [];
      const label = e => (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\s+/).join('.') : e.tagName.toLowerCase()) + ' "' + (e.textContent || '').trim().slice(0, 50) + '"';
      sc.querySelectorAll('.box, .card, .band, .mband, td, th, .leaf, .chev, .hoplab, .lchip, .formula, .order, .walkbar, .legend, .foot, .subtitle, .title, .toc').forEach(e => {
        const cs = getComputedStyle(e);
        if (cs.display === 'none' || cs.visibility === 'hidden') return;
        const r = e.getBoundingClientRect();
        if (!r.width || !r.height) return;
        if (e.scrollHeight > e.clientHeight + 3 || e.scrollWidth > e.clientWidth + 3) bad.push(label(e) + ` content ${e.scrollWidth}x${e.scrollHeight} > box ${e.clientWidth}x${e.clientHeight}`);
        const x0 = (r.left - sr.left) / k, y0 = (r.top - sr.top) / k, x1 = (r.right - sr.left) / k, y1 = (r.bottom - sr.top) / k;
        if (x0 < -2 || y0 < -2 || x1 > 1602 || y1 > 902) out.push(label(e) + ` at ${x0.toFixed(0)},${y0.toFixed(0)}–${x1.toFixed(0)},${y1.toFixed(0)}`);
      });
      return {state: window.__story.state(), overflow: bad, outOfStage: out};
    });
    const shot = shots ? path.join(outDir, String(n).padStart(2, '0') + '-' + id + '.png') : null;
    if (shot) await page.screenshot({path: shot});
    scenes.push(Object.assign({id: id, shot: shot}, res));
  }
  // interaction pass
  const steps = [];
  async function step(name, fn) { try { await fn(); steps.push({step: name, ok: true}); } catch (e) { steps.push({step: name, ok: false, error: String(e.message || e)}); } }
  await step('first scene, beat stepping with arrow keys', async () => {
    await page.evaluate(() => window.__story.go(window.__story.state().id === undefined ? 0 : 0));
    await page.evaluate(i => window.__story.go(i, false), ids[1] || ids[0]);
    const a = await page.evaluate(() => window.__story.state());
    await page.keyboard.press('ArrowRight'); await page.waitForTimeout(250);
    const b = await page.evaluate(() => window.__story.state());
    if (a.beats > 0 && b.beat !== a.beat + 1) throw new Error('ArrowRight did not advance a beat');
    await page.keyboard.press('ArrowLeft'); await page.waitForTimeout(250);
  });
  await step('details drawer opens and closes', async () => {
    const opened = await page.evaluate(() => { const c = document.querySelector('#stage .scene:last-child .click'); if (!c) return 'none'; c.click(); return document.getElementById('drawer').classList.contains('open') ? 'open' : 'closed'; });
    if (opened === 'closed') throw new Error('drawer did not open');
    await page.keyboard.press('Escape'); await page.waitForTimeout(200);
  });
  await step('notes and chapters toggle', async () => {
    await page.keyboard.press('n'); await page.keyboard.press('c'); await page.waitForTimeout(200);
    const s = await page.evaluate(() => [document.getElementById('notes').classList.contains('open'), document.getElementById('rail').classList.contains('open')]);
    if (!s[0] || !s[1]) throw new Error('notes or chapters did not open');
    await page.keyboard.press('Escape');
  });
  await step('main tree key and dive into a deep dive', async () => {
    const hub = await page.evaluate(() => (JSON.parse(document.getElementById('story-data').textContent).scenes.find(s => s.type === 'map') || {}).id);
    if (!hub) return;
    await page.keyboard.press('m'); await page.waitForTimeout(700);
    const st = await page.evaluate(() => window.__story.state());
    if (st.id !== hub) throw new Error('M did not open the main tree');
    await page.evaluate(() => { const q = document.querySelector('#stage .scene:last-child .qnode'); q && q.click(); });
    await page.waitForTimeout(600);
    const before = st.id;
    await page.evaluate(() => { const d = document.querySelector('#stage .scene:last-child .leaf.show .dive'); d && d.click(); });
    await page.waitForTimeout(900);
    const after = await page.evaluate(() => window.__story.state());
    if (after.id === before) throw new Error('leaf dive did not navigate');
  });
  await step('walk mode on every decision tree', async () => {
    const trees = await page.evaluate(() => JSON.parse(document.getElementById('story-data').textContent).scenes.filter(s => s.type === 'tree').map(s => s.id));
    for (const t of trees) {
      await page.evaluate(i => window.__story.go(i, true), t); await page.waitForTimeout(500);
      await page.keyboard.press('w'); await page.waitForTimeout(250);
      const vis = await page.evaluate(() => { const w = document.querySelector('#stage .scene:last-child .walk'); return w && w.style.display !== 'none'; });
      if (!vis) throw new Error('walk controls missing on ' + t);
      await page.evaluate(() => document.querySelector('#stage .scene:last-child .walk .n').click()); await page.waitForTimeout(150);
      await page.evaluate(() => document.querySelector('#stage .scene:last-child .walk .y').click()); await page.waitForTimeout(800);
      const open = await page.evaluate(() => document.getElementById('drawer').classList.contains('open'));
      if (!open) throw new Error('walk result drawer did not open on ' + t);
      await page.keyboard.press('Escape'); await page.keyboard.press('w');
    }
  });
  await step('deep link by address hash', async () => {
    const last = ids[ids.length - 1];
    await page.goto('file://' + file + '#' + last); await page.waitForTimeout(900);
    const st = await page.evaluate(() => window.__story.state());
    if (st.id !== last) throw new Error('hash did not open ' + last);
  });
  await browser.close();
  const problems = scenes.reduce((a, s) => a + s.overflow.length + s.outOfStage.length, 0) + errors.length + steps.filter(s => !s.ok).length;
  const report = {status: problems ? 'fail' : 'pass', file: file, chromium: exe || 'playwright default', scenes: scenes, interactions: steps, errors: errors};
  fs.writeFileSync(path.join(outDir, 'render-report.json'), JSON.stringify(report, null, 1));
  console.log(JSON.stringify({status: report.status, scenes: scenes.length, overflow: scenes.filter(s => s.overflow.length).map(s => ({id: s.id, items: s.overflow})),
    outOfStage: scenes.filter(s => s.outOfStage.length).map(s => ({id: s.id, items: s.outOfStage})), interactionsFailed: steps.filter(s => !s.ok), errors: errors, report: path.join(outDir, 'render-report.json')}, null, 1));
  process.exit(problems ? 1 : 0);
})().catch(e => { console.error('RENDER CHECK HARNESS ERROR', e); process.exit(2); });
