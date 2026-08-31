#!/usr/bin/env node
/* THE ALIGNMENT GATE.
   ONE AXIS: inside a section, every block that STACKS on another block starts on the
   same left edge, and that edge is the one the nav wordmark uses.

   This exists because a screenshot cannot tell you a heading and the paragraph under it
   disagree by 400 px; it only tells you something feels wrong. Measured on 2026-08-23
   before the fix, at a 1920 px viewport: the wordmark sat at x=48 while every section's
   content box sat at x=128, and inside single sections a left-aligned h2 at x=128 was
   followed by its own body list at x=592.

   WHAT IT DOES NOT FLAG, deliberately: children of a flex or grid parent (they are meant
   to sit side by side), out-of-flow elements, and inline-level boxes. The rule is only
   about blocks in normal flow inside a block parent, which is exactly the case where a
   different left edge is always a mistake.
*/
import { withPage } from './measure.mjs';

const BASE  = process.env.BASE || 'http://127.0.0.1:8899';
const PAGES_EN = ['/', '/how-it-works/', '/stronger/', '/join/', '/record/', '/verify/', '/support/', '/app-privacy/', '/404.html'];
// The locale pages are DERIVED from the English list, never retyped: a second
// hand-maintained list is a list that goes stale the first time a page is added.
const PAGES = [...PAGES_EN, ...PAGES_EN.map(p => p === '/404.html' ? '/es/404.html' : '/es' + p)];
const WIDTHS = process.argv.slice(2).map(Number).filter(Boolean);
const TOL = 1.5;

const PROBE = `(() => {
  const BLOCK = /^(block|flow-root|list-item|grid|flex)$/;
  const sel = el => {
    let s = el.tagName.toLowerCase();
    if (el.id) s += '#' + el.id;
    const c = typeof el.className === 'string' ? el.className.trim() : '';
    if (c) s += '.' + c.split(/\\s+/).slice(0,3).join('.');
    return s;
  };
  const findings = [];
  const wordmark = document.querySelector('.wordmark');
  const wmLeft = wordmark ? +wordmark.getBoundingClientRect().left.toFixed(1) : null;

  const axisOf = (r, cs) => +(r.left + parseFloat(cs.borderLeftWidth) + parseFloat(cs.paddingLeft)).toFixed(1);
  const sections = [...document.querySelectorAll('main > section, main > .scene, body > footer')];
  for (const section of sections) {
    const sr = section.getBoundingClientRect();
    const scs = getComputedStyle(section);
    // the content axis is border-box left + BORDER + padding. Leaving the border out
    // reported <cite> inside a 2px-bordered blockquote as 2px misaligned: a gate that
    // cries wolf is a gate nobody runs.
    const axis = axisOf(sr, scs);
    if (wmLeft !== null && Math.abs(axis - wmLeft) > ${TOL})
      findings.push({ kind: 'section off the nav axis', sel: sel(section), left: axis, want: wmLeft });

    const walk = (parent, parentAxis) => {
      const pcs = getComputedStyle(parent);
      const parentIsBlock = /^(block|flow-root|list-item)$/.test(pcs.display);
      for (const c of parent.children) {
        if (!(c instanceof HTMLElement)) continue;
        const cs = getComputedStyle(c);
        if (cs.display === 'none' || cs.position === 'absolute' || cs.position === 'fixed'
            || cs.float !== 'none' || c.hasAttribute('data-align-exempt')) continue;
        const r = c.getBoundingClientRect();
        if (r.width < 2 || r.height < 2) continue;
        if (parentIsBlock && BLOCK.test(cs.display)) {
          const d = +(r.left - parentAxis).toFixed(1);
          if (Math.abs(d) > ${TOL})
            findings.push({ kind: 'block off its container axis', sel: sel(c),
                            inside: sel(parent), left: +r.left.toFixed(1), want: parentAxis, delta: d });
        }
        const own = axisOf(r, cs);
        walk(c, /^(block|flow-root|list-item)$/.test(cs.display) ? own : parentAxis);
      }
    };
    walk(section, axis);
  }
  return { url: location.pathname, vw: innerWidth, docW: document.documentElement.scrollWidth,
           wordmark: wmLeft, findings };
})()`;

let total = 0;
for (const width of WIDTHS) {
  await withPage(async page => {
    for (const p of PAGES) {
      await page.goto(BASE + p);
      await page.evaluate(`document.querySelectorAll('.reveal').forEach(e=>e.classList.add('in'));"ok"`);
      const d = await page.evaluate(PROBE);
      const over = d.docW > d.vw + 1;
      const bad = d.findings.length || over;
      console.log(`${bad ? 'FAIL' : 'ok  '}  ${String(width).padStart(5)}px  ${d.url}` +
                  (over ? `   HORIZONTAL OVERFLOW: document ${d.docW} > viewport ${d.vw}` : ''));
      for (const f of d.findings)
        console.log(`         ${f.kind}: ${f.sel}` +
                    (f.inside ? ` inside ${f.inside}` : '') +
                    `   left ${f.left} want ${f.want}` + (f.delta !== undefined ? ` (off by ${f.delta}px)` : ''));
      total += d.findings.length + (over ? 1 : 0);
    }
  }, { width, height: 900, dsf: 1 });
}
console.log(`\nALIGNMENT FAILURES: ${total}`);
process.exit(total ? 1 : 0);
