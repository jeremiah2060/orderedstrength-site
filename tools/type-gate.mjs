#!/usr/bin/env node
/* THE OPTICAL SIZE OF AN INLINE LITERAL, MEASURED AGAINST THE SENTENCE HOLDING IT.
 *
 * A run of text quoted out of the product is set in the mono face. Whether it READS as
 * the same size as the prose around it is not decided by the font-size number: it is
 * decided by the x-height, which is font-size x that family's own x-height ratio. Two
 * families at the same declared size can differ by a fifth, and this site shipped the
 * opposite mistake, a declared reduction on top of families that already matched.
 *
 * Nothing else in this repo can see it. check-site.py reads declarations; the align gate
 * reads left edges; the measure gate reads characters per line; the contrast gate reads
 * colour. A 19%-short literal is valid CSS, correctly aligned, well wrapped and legible.
 * It just looks like a different, smaller typeface in the middle of a sentence, which on
 * a page whose whole argument is precision is the wrong impression to give.
 *
 * METHOD: for every element whose computed font-family differs from its parent's, render
 * an 'x' in each font at each computed size on a canvas and read actualBoundingBoxAscent,
 * which is the INKED height of the glyph rather than a metric anyone declared. Compare.
 *
 * FALSIFIABLE BOTH WAYS: at the .8125em this site shipped it reports -19% and exits 1; at
 * the .96em it now ships it reports -4.2% and exits 0. Run it against an old stylesheet to
 * see the red, which is the only reason to trust the green.
 */
import { withPage } from './measure.mjs';

const BASE = process.env.BASE || 'http://127.0.0.1:8899';
const TOL = Number(process.env.TYPE_TOL || 7);   // percent of x-height
// The ratio this gate measures is width-independent TODAY, because every inline literal is
// sized in `em` and therefore tracks its host. It is parameterised anyway, and check.sh runs
// a phone width as well as a desktop one, because the failure this gate exists to catch is
// an ABSOLUTE size on a literal, and an absolute size is exactly what a media query adds.
const W = Number(process.env.WIDTH || 1440);
const PAGES = (process.env.PAGES || '/,/how-it-works/,/record/,/join/,/verify/,/support/,/app-privacy/,/404.html').split(',');

const PROBE = `JSON.stringify((() => {
  const c = document.createElement('canvas').getContext('2d');
  const ink = (fam, weight, px) => {
    c.font = weight + ' ' + px + 'px ' + fam;
    const m = c.measureText('x');
    return m.actualBoundingBoxAscent;
  };
  const fam = cs => cs.fontFamily.split(',')[0].replace(/["']/g, '').trim();
  const out = [];
  document.querySelectorAll('body *').forEach(el => {
    const par = el.parentElement;
    if (!par || el.closest('script,style,noscript,svg')) return;
    // only elements that actually hold their own text
    const own = [...el.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join('').trim();
    if (own.length < 2) return;
    const cs = getComputedStyle(el), ps = getComputedStyle(par);
    if (fam(cs) === fam(ps)) return;                 // same face: not a literal mark
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) return;
    // AN INLINE LITERAL IS MID-SENTENCE, AND THAT IS THE WHOLE DEFINITION. Two conditions,
    // and the first draft of this gate had neither, so it returned 123 findings of which
    // 120 were headings and standalone mono blocks doing exactly what they should: a
    // heading is SUPPOSED to be a different size from body copy, and a mono readout that
    // is the only thing in its row is a readout, not a literal inside prose. A gate that
    // reports every deliberate size change alongside the defect is a gate nobody reads.
    //   (1) display:inline. A heading, a <pre>, a <dt>, a <p class=frozen> is a BLOCK, and
    //       its size is a decision about hierarchy, not about matching a neighbour.
    //   (2) THE PARENT HOLDS ITS OWN TEXT. That is what makes the run mid-sentence rather
    //       than the sole occupant of its container. It is the condition that separates
    //       'Fatigue <code>6%</code> and recovery' from a .setline whose two spans ARE
    //       the line, and it is what excludes the wordmark from its own bar.
    if (cs.display !== 'inline') return;
    const hostOwn = [...par.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join('').trim();
    if (hostOwn.length < 3) return;
    if (cs.textTransform === 'uppercase' || ps.textTransform === 'uppercase') return; // a label, not prose
    const xs = ink(cs.fontFamily, cs.fontWeight, parseFloat(cs.fontSize));
    const xp = ink(ps.fontFamily, ps.fontWeight, parseFloat(ps.fontSize));
    if (!xs || !xp) return;
    out.push({
      text: own.slice(0, 34),
      selfFam: fam(cs), selfPx: +parseFloat(cs.fontSize).toFixed(2), selfX: +xs.toFixed(2),
      hostFam: fam(ps), hostPx: +parseFloat(ps.fontSize).toFixed(2), hostX: +xp.toFixed(2),
      delta: +(100 * (xs / xp - 1)).toFixed(1),
      where: el.tagName.toLowerCase() + (typeof el.className === 'string' && el.className ? '.' + el.className.split(' ')[0] : ''),
    });
  });
  return out;
})())`;

const bad = [];
let checked = 0;
await withPage(async page => {
  for (const p of PAGES) {
    await page.goto(BASE + p);
    await page.evaluate(`document.querySelectorAll('.reveal').forEach(e=>e.classList.add('in'));"ok"`);
    await page.evaluate(`document.fonts.ready`);
    const rows = JSON.parse(await page.evaluate(PROBE));
    for (const r of rows) {
      checked++;
      if (Math.abs(r.delta) > TOL) bad.push({ page: p, ...r });
    }
    const worst = rows.reduce((a, b) => (Math.abs(b.delta) > Math.abs(a?.delta ?? 0) ? b : a), null);
    console.log(`  ${p.padEnd(16)} ${String(rows.length).padStart(3)} inline literal(s)` +
      (worst ? `  worst ${worst.delta > 0 ? '+' : ''}${worst.delta}%  ${JSON.stringify(worst.text)}` : ''));
  }
}, { width: W, height: 900, dsf: 1 });

console.log(`\ntype-gate: ${checked} inline literal(s) measured at ${W}px, tolerance ${TOL}% of x-height`);
if (bad.length) {
  console.log(`\nOPTICAL SIZE MISMATCH (${bad.length}):`);
  for (const b of bad) {
    console.log(`  ${b.page} ${b.where}  ${b.selfFam} ${b.selfPx}px (x ${b.selfX}) inside ` +
      `${b.hostFam} ${b.hostPx}px (x ${b.hostX})  = ${b.delta > 0 ? '+' : ''}${b.delta}%  ${JSON.stringify(b.text)}`);
  }
  console.log('\nTYPE NOT OK');
  process.exit(1);
}
console.log('TYPE OK');
