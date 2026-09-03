#!/usr/bin/env node
/* CAN A PERSON CHANGE LANGUAGE WITHOUT SCROLLING. Not: does the link work.
 *
 * WHY THIS EXISTS (2026-09-03). The CEO said the site was "stuck" in one language. Every gate
 * here was green, and one of them, lang-redirect-gate.mjs, walks the whole two-language loop and
 * passes: it finds the link with querySelector and calls .click(). That proves the link WORKS.
 * Nobody had ever asked whether a reader could FIND it.
 *
 * 🔒 MEASURED BEFORE IT WAS FIXED, because a defect described in adjectives gets argued about and
 * a defect with a number gets closed. Driven over CDP at 390x844, the only language link on this
 * site sat 13,566px down the English home page and 14,512px down the Spanish one. 16.1 and 17.2
 * SCREENS. In the same week the site gained the power to move a reader into a language they never
 * chose, silently. The exit existed, was correct, was tested, and was seventeen screens below it.
 *
 * 🔒 querySelector IS NOT A READER, AND THAT IS THE WHOLE BLIND SPOT. Every check that reaches an
 * element by selector has already solved the reader's only problem. A gate about findability has
 * to read GEOMETRY: is the control rendered, does it have a box, and is that box on the first
 * screen. Those three questions have no selector in them.
 *
 * PASSING MEANS ONE OF TWO THINGS, and the design intends both. A language link visible in the
 * header costs zero taps. Below the collapse breakpoints the header holds a <details> instead, so
 * the summary must be on the first screen and opening it must reveal the link: one tap. Anything
 * else, including a link that exists but renders at zero size, is a failure.
 *
 *     BASE=http://127.0.0.1:8899 node tools/lang-switch-gate.mjs [--selftest]
 */
import { withPage } from './measure.mjs';
import { readdirSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const B = process.env.BASE || 'http://127.0.0.1:8899';
const SELFTEST = process.argv.includes('--selftest');

/* 🔒 DERIVED FROM THE FILESYSTEM. check.sh's own header carried a stale page count for months
   because someone typed one, and a gate that silently skips a page prints the same clean line
   as one that checked it. */
function pages(dir = ROOT, prefix = '/') {
  const out = [];
  for (const name of readdirSync(dir, { withFileTypes: true })) {
    if (name.name === 'assets' || name.name === 'tools' || name.name.startsWith('.')) continue;
    const p = join(dir, name.name);
    if (name.isDirectory()) { if (existsSync(join(p, 'index.html'))) out.push(prefix + name.name + '/');
                              out.push(...pages(p, prefix + name.name + '/')); }
    else if (name.name === 'index.html') { if (prefix === '/') out.push('/'); }
    else if (name.name === '404.html') out.push(prefix + '404.html');
  }
  return [...new Set(out)].sort();
}

const WIDTHS = (process.env.WIDTHS || '390 768 1280 1920').split(/\s+/).map(Number);
const PAGES = pages();
let pass = 0, fail = 0;
const failures = [];

const PROBE = (hideCss) => `(() => {
  ${hideCss ? `{const st=document.createElement('style');st.textContent=${JSON.stringify(hideCss)};document.head.appendChild(st);}` : ''}
  /* 🔒 A LAYOUT BOX IS NOT A PAINTED PIXEL, AND THIS GATE BELIEVED IT WAS (2026-09-03, caught
     by taking a screenshot instead of trusting the number). A closed <details> hides its panel
     with content-visibility, and under that the children still return a real
     getBoundingClientRect: 200 by 242 at y=53, visibility "visible", painting nothing. So the
     first draft reported "0 tap" on every phone, meaning a reader could change language without
     opening the menu, when the truth is one tap. It was measuring geometry that no one can see.
     checkVisibility asks the browser the question that was actually meant, and the closed
     <details> is named as well, because a control behind a disclosure costs a tap by design and
     that is a different answer, not a failure. */
  const vis = el => {
    if (!el) return null;
    if (el.closest && el.closest('details:not([open])') && el.tagName !== 'SUMMARY') return null;
    if (el.checkVisibility && !el.checkVisibility(
        {contentVisibilityAuto: true, opacityProperty: true, visibilityProperty: true})) return null;
    const r = el.getBoundingClientRect();
    return (r.width > 0 && r.height > 0) ? r : null;
  };
  const H = window.innerHeight;
  /* 🔒 A VISIBLE BOX IS NOT A CORRECT ONE, AND THIS GATE PASSED A DEFECT ON ITS FIRST RUN
     (2026-09-03). The first insertion put the disclosure copy of the link OUTSIDE
     .menu__panel, as a bare child of <details>, so at 390px a stray "Español" rendered on
     top of the MENU pill on all twenty pages. The gate found an element, measured a real box
     on the first screen, and printed ok. Finding SOMETHING is not the question. */
  const others = [...document.querySelectorAll('.bar .wordmark, .bar details.menu > summary, .bar nav a.cta')]
                   .map(vis).filter(Boolean);
  const overlaps = r => others.some(o =>
    r.left < o.right - 1 && o.left < r.right - 1 && r.top < o.bottom - 1 && o.top < r.bottom - 1);
  // zero taps: a language link rendered in the header, on the first screen, colliding with nothing
  for (const a of document.querySelectorAll('.bar a[hreflang]')) {
    const r = vis(a);
    if (!r || r.top < 0 || r.top >= H) continue;
    if (overlaps(r)) return {ok:false, why:'a header language link overlaps another header control at ' +
                                            Math.round(r.left) + ',' + Math.round(r.top)};
    return {ok:true, taps:0, label:a.textContent.trim(), top:Math.round(r.top+window.scrollY)};
  }
  // one tap: the disclosure is on the first screen and opening it reveals one
  const d = document.querySelector('.bar details.menu'), s = d && d.querySelector('summary');
  const sr = vis(s);
  if (d && sr && sr.top >= 0 && sr.top < H) {
    /* 🔒 checkVisibility ANSWERS FROM THE LAST STYLE PASS, SO OPENING THE DISCLOSURE AND ASKING
       IN THE SAME BREATH GETS THE OLD ANSWER. Measured: immediately after d.open = true it
       returns false, and true after a single forced flush, with the element's rect unchanged
       either way. Without the flush this gate failed all twenty pages at 390px and blamed the
       markup, which was correct at the time. Reading offsetHeight is the flush. */
    d.open = true;
    void document.body.offsetHeight;
    const a = d.querySelector('a[hreflang]'), r = vis(a);
    d.open = false;
    if (r) return {ok:true, taps:1, label:a.textContent.trim(), top:Math.round(sr.top+window.scrollY)};
    return {ok:false, why:'the header disclosure opens and holds no language link'};
  }
  /* and the measurement that named the defect: how far down IS the only one. 🔒 VISIBLE ONLY.
     The first draft took the first a[hreflang] in the document, and a display:none element
     returns an all-zero rect, so it reported the header's own hidden copy as "0px down, 0.0
     screens". A gate whose failure MESSAGE is wrong sends the next reader to the wrong place. */
  const rr = [...document.querySelectorAll('a[hreflang]')].map(vis).filter(Boolean)[0];
  if (!rr) return {ok:false, why:'no language link is rendered anywhere on the page'};
  const y = Math.round(rr.top + window.scrollY);
  return {ok:false, why:'the only language link is ' + y + 'px down, ' +
          (y / H).toFixed(1) + ' screens, and nothing in the header offers one'};
})()`;

for (const width of WIDTHS) {
  await withPage(async (page) => {
    for (const path of PAGES) {
      await page.goto(B + path);
      await page.evaluate(`new Promise(r=>setTimeout(r,220))`);
      const out = JSON.parse(await page.evaluate(`JSON.stringify(${PROBE(SELFTEST ? '.bar a[hreflang],.bar details.menu{display:none!important}' : '')})`));
      if (out.ok) { pass++; if (!SELFTEST) console.log(`  ok   ${String(width).padStart(4)}px ${path.padEnd(22)} ${out.taps} tap  "${out.label}"`); }
      else { fail++; failures.push(`${width}px ${path}: ${out.why}`); }
    }
  }, { width, height: width === 390 ? 844 : 900, dsf: 1 });
}

if (SELFTEST) {
  /* 🔒 NAME THE INPUT THAT TURNS THIS RED. With the header's language link and its disclosure
     hidden, every page must fail, and the message must be the measurement that found the real
     defect rather than a bare "not found". If this ever passes, the gate is decorative. */
  console.log(`SELFTEST: header language control hidden on every page`);
  console.log(`  went red on ${fail} of ${fail + pass} page-widths`);
  if (failures.length) console.log(`  sample verdict: ${failures[0]}`);
  const good = pass === 0 && fail > 0 && /screens/.test(failures[0] || '');
  console.log(good ? 'SELFTEST OK' : 'SELFTEST FAILED');
  process.exit(good ? 0 : 1);
}

failures.forEach(f => console.error('FAIL: ' + f));
console.log(`\nLANGUAGE SWITCH: ${pass} reachable, ${fail} not, across ${PAGES.length} pages at ${WIDTHS.length} widths`);
process.exit(fail ? 1 : 0);
