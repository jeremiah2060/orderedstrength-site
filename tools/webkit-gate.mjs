#!/usr/bin/env node
/* THE SAME SITE, IN THE OTHER ENGINE.
 *
 * WHY THIS EXISTS (CEO, 2026-09-03): "look great in all devices not just iOS, but all of them
 * and look exactly the same in all browsers."
 *
 * 🔒 EVERY OTHER BROWSER-DRIVEN GATE IN THIS REPO LAUNCHES THE SAME BINARY. tools/measure.mjs
 * opens /Applications/Google Chrome.app, and align, measure, type, type-floor, hero, bar,
 * lang-switch, lang-redirect, csp, css-equiv and print are all built on it. They sweep width,
 * and since 2026-09-02 height, and had never varied the engine. That is the same shape of hole
 * as the viewport-height axis hero-gate closed, and this repo had already written the law for
 * it: a whole axis untested is why a site looks right on every machine here and wrong elsewhere.
 *
 * 🔒 AND IT WAS ALMOST FILED AS IMPOSSIBLE. The first attempt reached for `safaridriver
 * --enable`, which asks for an administrator password, and the conclusion drafted from that was
 * that the engine axis could not be closed without the CEO. That was a conclusion about one
 * route. A WebKit build is a download, it needs no password, and it is the same shape of
 * prerequisite as the Chrome binary measure.mjs already requires: `npm run setup`.
 *
 * WHAT IT ASKS, chosen because these are the things that differ BETWEEN engines rather than
 * between widths, which the Chrome gates already cover in far more detail:
 *   1. every inline script runs, which is where a CSP hash or a parse difference would show
 *   2. the header language control is reachable, zero taps or one
 *   3. the bar does not collide with itself and no page scrolls sideways
 *   4. a Spanish locale reaches the Spanish site, and its English link comes back and stays
 *   5. print media lays down a light ground with dark ink
 *
 *     BASE=http://127.0.0.1:8899 node tools/webkit-gate.mjs [--selftest]
 */
/* 🔒 THE DRIVER LIVES OUTSIDE THIS REPOSITORY, AND THE FIRST ATTEMPT PUT IT INSIDE. A
   package.json and a node_modules in the tree looked like the standard, discoverable answer, and
   it broke the very next run: bar-gate reported "180 clean, 24 colliding, over 6 widths on 24"
   on a site with twenty pages, because it walks the tree for pages and node_modules is full of
   HTML. Nineteen of the twenty-one walkers in this repo derive their own list, on purpose, and
   patching every one of them to exclude a directory is a fix that is wrong the first time
   someone adds the twenty-second walker.
   🔒 SO THE DEPENDENCY IS A MACHINE PREREQUISITE, WHICH IS THE PATTERN THIS HARNESS ALREADY
   USES: measure.mjs hard-codes /Applications/Google Chrome.app and installs nothing. One
   command, once, and the repository keeps having no files of its own:

       npm install --prefix ~/.orderedstrength-site-tools playwright
       npx --prefix ~/.orderedstrength-site-tools playwright install webkit

   OS2_SITE_TOOLS overrides the location. This gate FAILS LOUDLY when the driver is missing,
   because a cross-engine check that skips quietly is a check that can only ever say yes. */
import { createRequire } from 'node:module';
const TOOLS = process.env.OS2_SITE_TOOLS || (process.env.HOME + '/.orderedstrength-site-tools');
let webkit;
try {
  /* 🔒 THE ABSOLUTE PATH, NOT THE BARE NAME. `require('playwright')` walks UP from the given
     directory looking for a node_modules at every level, so the check that this gate fails
     loudly without a driver PASSED against a stray /tmp/node_modules left behind by an earlier
     experiment. A resolution that can succeed from somewhere you did not install to is a
     resolution that can silently use a different version than the one you meant. */
  webkit = createRequire(TOOLS + '/x.js')(TOOLS + '/node_modules/playwright').webkit;
} catch (e) {
  console.error('WEBKIT GATE CANNOT RUN: no playwright driver at ' + TOOLS);
  console.error('  npm install --prefix ' + TOOLS + ' playwright');
  console.error('  npx --prefix ' + TOOLS + ' playwright install webkit');
  process.exit(1);
}
import { readdirSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const B = process.env.BASE || 'http://127.0.0.1:8899';
const SELFTEST = process.argv.includes('--selftest');
let pass = 0, fail = 0; const failures = [];
const check = (n, c) => { if (c) { pass++; if (!SELFTEST) console.log('PASS: ' + n); }
                          else { fail++; failures.push(n); if (!SELFTEST) console.error('FAIL: ' + n); } };

/* 🔒 THE SELFTEST BREAKS THE PAGE, NOT THE CHECK. Hiding the header language control and
   forcing the full nav on at every width are the two states the design exists to prevent, so
   arms 2 and 3 must go red on them, in THIS engine. A cross-engine gate that cannot go red in
   the engine it was added for is a second copy of the Chrome result. */
/* 🔒 AND THE FIRST BREAK DEFEATED ITSELF, WHICH IS WHY IT ONLY BIT FIVE TIMES OUT OF FORTY.
   It read `.bar a[hreflang],.bar details.menu{display:none!important}` followed by
   `.bar nav > a:not(.cta){display:inline!important}`, and the second selector is (0,2,2) against
   the first at (0,2,1), so with !important on both the forcing rule WON and quietly restored the
   language link the hiding rule had just removed. The gate was correct throughout; the sabotage
   was not sabotaging. A selftest that mostly passes is a selftest that mostly proves nothing,
   and the only reason it was caught is that 5 of 40 is a number worth being suspicious of.
   The hide now carries `html ` to reach (0,2,2) and is declared last, so it wins the tie. */
const BREAK = '.bar nav > a:not(.cta){display:inline!important}' +
              'html .bar a[hreflang],html .bar details.menu{display:none!important}';

function pages(dir = ROOT, prefix = '/') {
  const out = [];
  for (const n of readdirSync(dir, { withFileTypes: true })) {
    if (n.name === 'assets' || n.name === 'tools' || n.name === 'node_modules' || n.name.startsWith('.')) continue;
    const p = join(dir, n.name);
    if (n.isDirectory()) { if (existsSync(join(p, 'index.html'))) out.push(prefix + n.name + '/');
                           out.push(...pages(p, prefix + n.name + '/')); }
    else if (n.name === 'index.html') { if (prefix === '/') out.push('/'); }
    else if (n.name === '404.html') out.push(prefix + n.name);
  }
  return [...new Set(out)].sort();
}

const SWITCH = () => {
  const seen = el => el && el.checkVisibility ? el.checkVisibility() : !!(el && el.getBoundingClientRect().width);
  const inClosed = el => el.closest && el.closest('details:not([open])') && el.tagName !== 'SUMMARY';
  for (const a of document.querySelectorAll('.bar a[hreflang]')) {
    if (!inClosed(a) && seen(a)) { const r = a.getBoundingClientRect();
      if (r.width > 0 && r.top >= 0 && r.top < innerHeight) return { ok: true, taps: 0 }; }
  }
  const d = document.querySelector('.bar details.menu'), s = d && d.querySelector('summary');
  if (d && s && seen(s) && s.getBoundingClientRect().width > 0) {
    d.open = true; void document.body.offsetHeight;
    const a = d.querySelector('a[hreflang]');
    const r = a && a.getBoundingClientRect();
    d.open = false;
    if (r && r.width > 0) return { ok: true, taps: 1 };
  }
  return { ok: false };
};

const BAR = () => {
  const box = el => el && el.getBoundingClientRect();
  const wm = box(document.querySelector('.bar .wordmark'));
  const nav = document.querySelector('.bar nav');
  if (!wm || !nav) return { ok: false, why: 'no bar' };
  const kids = [...nav.children].filter(e => e.getBoundingClientRect().width > 0);
  if (!kids.length) return { ok: false, why: 'the nav renders nothing' };
  const boxes = kids.map(e => e.getBoundingClientRect());
  const gap = Math.round(Math.min(...boxes.map(b => b.left)) - wm.right);
  const lines = new Set(boxes.map(b => Math.round(b.top))).size;
  const over = document.documentElement.scrollWidth - document.documentElement.clientWidth;
  if (gap < 8) return { ok: false, why: `wordmark and nav are ${gap}px apart` };
  if (lines > 1) return { ok: false, why: `the nav is on ${lines} lines` };
  if (over > 0) return { ok: false, why: `the page scrolls sideways by ${over}px` };
  return { ok: true, gap };
};

const browser = await webkit.launch();
console.log(`WebKit ${browser.version()}  against ${B}`);
try {
  for (const [w, h, label] of [[390, 844, 'iPhone 390'], [1280, 900, 'desktop 1280']]) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h } });
    const page = await ctx.newPage();
    for (const path of pages()) {
      await page.goto(B + path, { waitUntil: 'load' });
      if (SELFTEST) await page.addStyleTag({ content: BREAK });
      await page.waitForTimeout(150);
      const cls = await page.evaluate('document.documentElement.className');
      const hasSetter = await page.evaluate(
        `!!document.querySelector('script:not([src])') && /className="js"/.test(document.documentElement.outerHTML) === false`);
      if (/(^|\s)js(\s|$)/.test(cls) || !hasSetter)
        check(`${label} ${path.padEnd(20)} inline script ran (class "${cls || '(none)'}")`,
          /(^|\s)js(\s|$)/.test(cls) || path.endsWith('404.html'));
      const sw = await page.evaluate(`(${SWITCH.toString()})()`);
      check(`${label} ${path.padEnd(20)} language control reachable${sw.ok ? ` in ${sw.taps} tap` : ''}`, sw.ok);
      const bar = await page.evaluate(`(${BAR.toString()})()`);
      check(`${label} ${path.padEnd(20)} the bar does not collide${bar.ok ? ` (gap ${bar.gap}px)` : `: ${bar.why}`}`, bar.ok);
    }
    await ctx.close();
  }

  /* the language contract, in WebKit, with a real Spanish locale */
  const es = await browser.newContext({ viewport: { width: 900, height: 700 }, locale: 'es-419' });
  const p2 = await es.newPage();
  await p2.goto(B + '/404.html'); await p2.evaluate('try{localStorage.clear()}catch(e){}');
  await p2.goto(B + '/'); await p2.waitForTimeout(700);
  const landed = new URL(p2.url()).pathname;
  check(`a Spanish WebKit reaches the Spanish site (landed ${landed})`, landed === '/es/');
  await p2.evaluate(`(()=>{const a=document.querySelector('a[hreflang="en"]');if(a)a.click();return 1})()`);
  await p2.waitForTimeout(900);
  const back = new URL(p2.url()).pathname;
  const stored = await p2.evaluate(`(function(){try{return localStorage.getItem('os-lang')}catch(e){return null}})()`);
  check(`and its English link lands on / and STAYS (at ${back}, stored ${stored})`, back === '/' && stored === 'en');
  await es.close();

  /* and paper, in the engine whose translator ignores the notranslate declaration anyway */
  const pr = await browser.newContext({ viewport: { width: 1100, height: 1400 } });
  const p3 = await pr.newPage();
  await p3.emulateMedia({ media: 'print' });
  for (const path of ['/terms/', '/es/app-privacy/']) {
    await p3.goto(B + path, { waitUntil: 'load' }); await p3.waitForTimeout(200);
    const o = await p3.evaluate(`(()=>{
      const px=c=>{const m=(c||'').match(/[\\d.]+/g)||[0,0,0];return m.slice(0,3).map(Number)};
      const lum=r=>{const f=x=>{x/=255;return x<=0.04045?x/12.92:Math.pow((x+0.055)/1.055,2.4)};const[a,b,c]=r.map(f);return .2126*a+.7152*b+.0722*c};
      const h=document.querySelector('h1')||document.querySelector('h2');
      return {g:+lum(px(getComputedStyle(document.body).backgroundColor)).toFixed(3),
              i:+lum(px(getComputedStyle(h).color)).toFixed(3)};})()`);
    check(`${path} prints dark on light in WebKit (ground ${o.g}, ink ${o.i})`, o.g >= 0.8 && o.i <= 0.25);
  }
  await pr.close();
} finally { await browser.close(); }

if (SELFTEST) {
  console.log('SELFTEST: header language control hidden and the collapse rules defeated, in WebKit');
  console.log(`  ${fail} of ${fail + pass} went red`);
  const kinds = {};
  for (const f of failures) kinds[f.replace(/^.*?\s{2,}/, '').replace(/\(.*$/, '').replace(/:.*$/, '').trim()] = (kinds[f.replace(/^.*?\s{2,}/, '').replace(/\(.*$/, '').replace(/:.*$/, '').trim()] || 0) + 1;
  for (const [k, n] of Object.entries(kinds)) console.log(`    ${n.toString().padStart(3)}  ${k}`);
  const good = fail > 0 && failures.some(f => /language control/.test(f)) && failures.some(f => /collide/.test(f));
  console.log(good ? 'SELFTEST OK' : 'SELFTEST FAILED: breaking the page in this engine changed nothing');
  process.exit(good ? 0 : 1);
}
console.log(`\nWEBKIT FAILURES: ${fail}`);
process.exit(fail ? 1 : 0);
