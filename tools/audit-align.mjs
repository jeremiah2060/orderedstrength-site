#!/usr/bin/env node
/* THE ALIGNMENT AUDIT.
   For every section, compute the left edge of every block-level child that carries text or a card.
   A section is coherent when every one of those left edges is the SAME number. Anything that
   disagrees with the section's dominant left edge by more than 1px is a misalignment, and the
   report names the element, the selector, and the delta in pixels. */
import { withPage } from './measure.mjs';

const WIDTHS = process.argv[2] ? [Number(process.argv[2])] : [1440, 1920];
const PAGES = ['/', '/how-it-works/', '/record/', '/verify/'];
const BASE = process.env.BASE || 'http://127.0.0.1:8899';

const PROBE = `(() => {
  const out = [];
  const sel = el => {
    let s = el.tagName.toLowerCase();
    if (el.id) s += '#' + el.id;
    if (el.className && typeof el.className === 'string') s += '.' + el.className.trim().split(/\\s+/).join('.');
    return s;
  };
  const hasOwnText = el => [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 2);
  document.querySelectorAll('main > section, main > .scene, footer').forEach(section => {
    const sr = section.getBoundingClientRect();
    const cs = getComputedStyle(section);
    const padL = parseFloat(cs.paddingLeft), padR = parseFloat(cs.paddingRight);
    const contentL = sr.left + padL, contentR = sr.right - padR;
    const items = [];
    const walk = (el, depth) => {
      for (const c of el.children) {
        if (!(c instanceof HTMLElement)) continue;
        const s = getComputedStyle(c);
        if (s.display === 'none' || s.position === 'absolute' || s.position === 'fixed') continue;
        const r = c.getBoundingClientRect();
        if (r.width < 2 || r.height < 2) continue;
        const textish = hasOwnText(c) || /^(H1|H2|H3|P|OL|UL|DL|BLOCKQUOTE)$/.test(c.tagName);
        const card = /card|console|moment|callout|quote|facts|rows|grid|chips|versus|track/.test(c.className || '');
        if (textish || card || depth === 0) {
          items.push({ sel: sel(c), left: +r.left.toFixed(1), right: +r.right.toFixed(1), width: +r.width.toFixed(1), top: +r.top.toFixed(1), textAlign: s.textAlign, depth });
        }
        if (depth < 2 && !textish) walk(c, depth + 1);
      }
    };
    walk(section, 0);
    out.push({ section: sel(section), left: +contentL.toFixed(1), right: +contentR.toFixed(1), width: +(contentR-contentL).toFixed(1), top: +sr.top.toFixed(1), items });
  });
  const bar = document.querySelector('.bar');
  const mark = document.querySelector('.wordmark');
  const nav = document.querySelector('.bar nav');
  return { url: location.pathname, vw: innerWidth,
    bar: bar ? { left: +bar.getBoundingClientRect().left.toFixed(1) } : null,
    wordmark: mark ? +mark.getBoundingClientRect().left.toFixed(1) : null,
    navRight: nav ? +nav.getBoundingClientRect().right.toFixed(1) : null,
    docW: document.documentElement.scrollWidth,
    sections: out };
})()`;

for (const width of WIDTHS) {
  await withPage(async page => {
    console.log(`\n${'='.repeat(78)}\nVIEWPORT ${width}px\n${'='.repeat(78)}`);
    for (const p of PAGES) {
      await page.goto(BASE + p);
      await page.evaluate(`document.querySelectorAll('.reveal').forEach(e=>e.classList.add('in'));"ok"`);
      const d = await page.evaluate(PROBE);
      console.log(`\n── ${d.url}   viewport ${d.vw}  document ${d.docW}${d.docW > d.vw ? '  ⚠ HORIZONTAL OVERFLOW' : ''}`);
      console.log(`   nav wordmark left = ${d.wordmark}   nav right = ${d.navRight}`);
      for (const s of d.sections) {
        const lefts = s.items.map(i => i.left);
        const mode = lefts.sort((a,b)=>a-b)[0];
        const bad = s.items.filter(i => Math.abs(i.left - s.left) > 1.5);
        const barDelta = d.wordmark === null ? 0 : +(s.left - d.wordmark).toFixed(1);
        console.log(`\n  ${s.section}`);
        console.log(`     content box  L=${s.left}  R=${s.right}  W=${s.width}   vs nav wordmark L=${d.wordmark} (Δ${barDelta})`);
        for (const i of s.items) {
          const d1 = +(i.left - s.left).toFixed(1);
          const flag = Math.abs(d1) > 1.5 ? `  ◀── OFF BY ${d1}px` : '';
          console.log(`       L=${String(i.left).padStart(7)} W=${String(i.width).padStart(7)} ${i.sel.slice(0,58).padEnd(58)}${flag}`);
        }
      }
    }
  }, { width, height: 900, dsf: 1 });
}
