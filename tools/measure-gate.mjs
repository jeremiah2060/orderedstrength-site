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
const PAGES = ['/', '/how-it-works/', '/join/', '/record/', '/verify/', '/support/', '/app-privacy/', '/404.html'];
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
    const lines = Math.max(1, Math.round(r.height / lh));
    if (lines < 2) return;
    const perLine = text.length / lines;
    if (perLine < ${MIN_CHARS_PER_LINE})
      bad.push({ sel: sel(el), chars: text.length, lines, perLine: +perLine.toFixed(1),
                 w: +r.width.toFixed(0), sample: text.slice(0, 46) });
  });
  return { url: location.pathname, bad };
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
    }
  }, { width, height: 950, dsf: 1 });
}
console.log(`\nMEASURE FAILURES: ${total}`);
process.exit(total ? 1 : 0);
