#!/usr/bin/env node
/* THE MEASURE GATE.
   Flags any block of running text whose lines are absurdly short, which is what a broken
   grid or flex placement looks like from the outside: the words are all there, the colours
   are right, every gate above this one passes, and the paragraph is one word per line.

   It exists because that failure has now happened twice on this site. The first time, a
   list's <b> and <span> auto-placed into a 2.5rem grid column and the body text wrapped one
   word per line on /how-it-works. The second time, the same component was moved into the
   shared stylesheet in two halves, and the half that pins those children to column 2 was
   left behind, so /join/ reproduced the identical break the moment it reused the component.

   The rule: a text block with more than one line must average at least 18 characters per
   line. Real prose at this site's smallest size averages 45 to 90.

   🔒 THE FIRST VERSION OF THIS GATE SKIPPED ANY BLOCK NARROWER THAN 128px, WHICH IS EXACTLY
   THE BLOCK IT EXISTS TO CATCH. Re-introducing the real defect left it reporting a clean
   site: the broken column is 52px wide, so the floor meant to exclude labels excluded the
   bug. A check that cannot see the failure it was written for is worse than no check,
   because it is also a green nobody questions. The floor is now 40px and short strings are
   excluded by LENGTH instead, which is the property that actually distinguishes a label
   from a paragraph. Falsified both ways before being trusted. */
import { withPage } from './measure.mjs';

const BASE  = process.env.BASE || 'http://127.0.0.1:8899';
import { readdirSync, existsSync } from 'node:fs';

// 🔒 THE THIRD COPY OF A HAND-TYPED PAGE LIST, AND THE ONE THAT WAS MISSED. align-gate and
// type-gate were both moved onto a derived list on 2026-09-01 under a lock marker naming the
// defect ("/terms/ landed, this array did not change, and a page carrying a legal document
// required by App Store review was measured by nothing"). This file was the same nine-entry
// array and was not touched, so the fix was two-thirds applied and a fourth reader of the same
// stale list went on reporting green about 18 pages of a 20-page site.
// 🔒 FIXING A DUPLICATED CONSTANT MEANS GREPPING FOR ITS OTHER COPIES, NOT FIXING THE COPIES
// YOU HAPPENED TO OPEN.
const ROOT = new URL('..', import.meta.url).pathname;
const PAGES_EN = [
  '/',
  ...readdirSync(ROOT, { withFileTypes: true })
    .filter(d => d.isDirectory() && !['assets', 'tools', 'es', '.git'].includes(d.name))
    .filter(d => existsSync(ROOT + d.name + '/index.html'))
    .map(d => '/' + d.name + '/')
    .sort(),
  '/404.html',
];
// The locale pages are DERIVED from the English list, never retyped: a second
// hand-maintained list is a list that goes stale the first time a page is added.
const PAGES = [...PAGES_EN, ...PAGES_EN.map(p => p === '/404.html' ? '/es/404.html' : '/es' + p)];
const WIDTHS = process.argv.slice(2).map(Number).filter(Boolean);
const MIN_CHARS_PER_LINE = 18;

const PROBE = `(() => {
  const bad = [];
  const sel = el => {
    let s = el.tagName.toLowerCase();
    if (el.id) s += '#' + el.id;
    const c = typeof el.className === 'string' ? el.className.trim() : '';
    if (c) s += '.' + c.split(/\\s+/).slice(0,2).join('.');
    return s;
  };
  document.querySelectorAll('p,span,li,dd,b,figcaption,div').forEach(el => {
    // only leaf-ish blocks of running text
    if ([...el.children].some(c => getComputedStyle(c).display !== 'inline')) return;
    const text = (el.textContent || '').trim();
    if (text.length < 40) return;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return;
    if (/vertical/.test(cs.writingMode)) return;   // the margin scale's label is meant to be narrow
    const r = el.getBoundingClientRect();
    if (r.width < 40 || r.height < 8) return;
    const lh = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.4;
    /* 🔒 PADDING IS NOT A LINE OF TEXT, AND COUNTING IT AS ONE INVENTS DEFECTS. The border
       box was divided by the line height, so any padded block reported one more line than it
       has, and the characters-per-line average was pushed down by exactly that much. Measured
       2026-09-02: p#selftest is two lines of 12px in a 19.2px rhythm with 16px of bottom
       padding, so 38.4px of text in a 54.4px box read as THREE lines, and a 45-character
       sentence scored 15 per line against a floor of 18. The paragraph was correct, the page
       was correct, and this gate said otherwise. Subtract what is not text. */
    const notText = (parseFloat(cs.paddingTop) || 0) + (parseFloat(cs.paddingBottom) || 0)
                  + (parseFloat(cs.borderTopWidth) || 0) + (parseFloat(cs.borderBottomWidth) || 0);
    const lines = Math.max(1, Math.round((r.height - notText) / lh));
    if (lines < 2) return;
    const perLine = text.length / lines;
    if (perLine < ${MIN_CHARS_PER_LINE})
      bad.push({ sel: sel(el), chars: text.length, lines, perLine: +perLine.toFixed(1),
                 w: +r.width.toFixed(0), sample: text.slice(0, 46) });
  });
  return { url: location.pathname, bad };
})()`;

/* SECOND CHECK: the evidence dial must not resize as you drag it.
   The two comparison cards carry three different sentences, and the height they need
   varies with BOTH the copy and the viewport: measured across nine widths it runs from
   220px at 1300 to 287px at 660. The page reserves the tallest state at load, measured
   from the real strings at the real width. This asserts that the reservation is actually
   working, because the failure is a page that shifts under the reader's thumb, which no
   screenshot and no other gate here can see. */
const DIAL = `(() => {
  const s = document.getElementById('sessions'); if (!s) return null;
  const box = document.querySelector('.versus'); if (!box) return null;
  const keep = s.value, heights = [];
  for (const v of [1, 4, 5, 12, 19, 20, 35, 60]) {
    s.value = v; s.dispatchEvent(new Event('input', { bubbles: true }));
    document.body.offsetHeight;
    heights.push(Math.round(box.getBoundingClientRect().height));
  }
  s.value = keep; s.dispatchEvent(new Event('input', { bubbles: true }));
  return { heights, swing: Math.max(...heights) - Math.min(...heights) };
})()`;

let total = 0;
for (const width of WIDTHS) {
  await withPage(async page => {
    for (const p of PAGES) {
      await page.goto(BASE + p);
      const d = await page.evaluate(PROBE);
      console.log(`${d.bad.length ? 'FAIL' : 'ok  '}  ${String(width).padStart(5)}px  ${d.url}`);
      for (const b of d.bad)
        console.log(`         ${b.sel}  ${b.perLine} chars/line over ${b.lines} lines in ${b.w}px  "${b.sample}"`);
      total += d.bad.length;
      if (p === '/') {
        await page.evaluate(`new Promise(r=>setTimeout(r,700))`);
        const dial = await page.evaluate(DIAL);
        if (dial && dial.swing > 0) {
          console.log(`         the evidence dial RESIZES as you drag it: ${dial.swing}px swing across ${dial.heights.length} states ${JSON.stringify(dial.heights)}`);
          total += 1;
        }
      }
    }
  }, { width, height: 950, dsf: 1 });
}
console.log(`\nMEASURE FAILURES: ${total}`);
process.exit(total ? 1 : 0);
