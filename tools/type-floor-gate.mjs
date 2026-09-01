/* THE RENDERED TYPE FLOOR. No text a person is meant to read renders below the floor.

   WHY THIS EXISTS (2026-09-01, CEO-found, dossier CD-013). He looked at the footer and said
   some fonts are too small. They were: the price-chip legends ("EN PRUEBAS", "AL AÑO") and the
   footer column headings rendered at 10px, uppercase mono with .17em tracking, on a dark
   ground. Two more roles sat at 11px. Three different sizes were doing one job because they
   accreted rather than were chosen.

   🔒 FOURTEEN GREEN GATES AND NOT ONE OF THEM LOOKED AT A FONT SIZE. type-gate.mjs measures
   the OPTICAL size of an inline <code> against the sentence around it, which is a question
   about two fonts matching each other, not about whether either is legible. contrast-gate
   reads colour. align-gate reads edges. measure-gate reads wrapping. The size itself was
   checked by nobody, so 10px shipped to twenty published pages.

   🔒 AND IT MEASURES THE RENDER, NOT THE STYLESHEET. A CSS scan is the obvious version and it
   is weaker in three ways that matter here: an `em` chain compounds (.875em inside .9em is
   12.6px, and neither number looks wrong on its own line), a media query can shrink type only
   at one width, and an inline style never appears in the stylesheet at all. The browser is the
   only thing that knows the answer, so ask it.

   FLOOR: 12px. Below that, uppercase mono with wide tracking on a dark ground stops being
   small and starts being a squint. Decorative marks with no reading role are exempt BY NAME,
   never by pattern, so an exemption is a decision somebody wrote down.

     BASE=http://127.0.0.1:8899 node tools/type-floor-gate.mjs [widths...]
*/
import { withPage } from './measure.mjs';
import { readdirSync, existsSync } from 'node:fs';

const BASE = process.env.BASE || 'http://127.0.0.1:8899';
const FLOOR = 12;
const WIDTHS = process.argv.slice(2).map(Number).filter(Boolean);
const AT = WIDTHS.length ? WIDTHS : [390, 1440];

/* 🔒 EXEMPT BY NAME. A pattern-based exemption ("anything in a footer") grows to cover the
   next defect silently. Each entry here is a decision with a reason attached. */
const EXEMPT = [
  // The fixed side rail is a margin ornament shown only above 95rem: vertical, rotated,
  // decorative section ticks that carry no sentence. It is not read, it is glanced at.
  { sel: '.rail', why: 'decorative margin rail, rotated vertical ticks, not a reading surface' },
];

function pages() {
  const out = [];
  const walk = (dir, prefix) => {
    for (const e of readdirSync(dir, { withFileTypes: true })) {
      if (['tools', 'assets', 'node_modules', '.git'].includes(e.name)) continue;
      if (e.isDirectory()) walk(`${dir}/${e.name}`, `${prefix}${e.name}/`);
      else if (e.name.endsWith('.html')) {
        out.push(e.name === 'index.html' ? (prefix || '/') : `${prefix}${e.name}`);
      }
    }
  };
  walk(new URL('..', import.meta.url).pathname.replace(/\/$/, ''), '/');
  return [...new Set(out)].sort();
}

let fail = 0;
console.log('TYPE FLOOR');
for (const width of AT) {
  await withPage(async (page) => {
    for (const path of pages()) {
      await page.goto(BASE + path);
      const bad = await page.evaluate(`(() => {
        const EX = ${JSON.stringify(EXEMPT.map(e => e.sel))};
        const out = [];
        for (const el of document.querySelectorAll('*')) {
          if (EX.some(s => el.closest(s))) continue;
          // Only elements that render their OWN text: a wrapper inherits its size but its
          // children are what a reader sees, and counting both double-reports one defect.
          const own = [...el.childNodes]
            .filter(n => n.nodeType === 3 && n.textContent.trim())
            .map(n => n.textContent.trim()).join(' ');
          if (!own) continue;
          const cs = getComputedStyle(el);
          if (cs.visibility === 'hidden' || cs.display === 'none') continue;
          const px = parseFloat(cs.fontSize);
          if (px < ${FLOOR}) {
            out.push({ px: Math.round(px * 10) / 10,
                       sel: el.tagName.toLowerCase() + (el.className && typeof el.className === 'string'
                            ? '.' + el.className.trim().split(/\\s+/).join('.') : ''),
                       text: own.slice(0, 42) });
          }
        }
        // One line per distinct selector+size, so a repeated component reports once.
        const seen = new Map();
        for (const b of out) { const k = b.sel + '@' + b.px; if (!seen.has(k)) seen.set(k, b); }
        return [...seen.values()];
      })()`);
      if (bad.length) {
        fail += bad.length;
        console.log(`  ${String(width).padStart(4)}px  ${path}`);
        for (const b of bad.slice(0, 6)) {
          console.log(`          ${String(b.px).padStart(5)}px  ${b.sel}  "${b.text}"`);
        }
      }
    }
  }, { width, height: 900, dsf: 1 });
}

if (!fail) console.log(`  every rendered text node is >= ${FLOOR}px across ${pages().length} page(s) at ${AT.join('px, ')}px`);
console.log(`\nTYPE FLOOR FAILURES: ${fail}`);
process.exit(fail ? 1 : 0);
