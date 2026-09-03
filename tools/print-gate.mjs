#!/usr/bin/env node
/* WHAT THIS SITE LOOKS LIKE ON PAPER, WHICH NOTHING HERE HAS EVER ASKED.
 *
 * WHY THIS EXISTS. There was no `@media print` block in the stylesheet at all, and that is not
 * a cosmetic gap. A browser does not print background colours unless the page asks it to, so
 * near-white ink on a ground the printer drops comes out white on white. The two pages most
 * likely to be printed are the two the app itself links to, /terms/ and /app-privacy/, and they
 * were the ones printing blank.
 *
 * 🔒 NO GATE HERE COULD SEE IT, AND THE REASON IS ONE WORD: EVERY ONE OF THEM MEASURES THE
 * SCREEN. contrast-gate reads the stylesheet's :root, which is the screen palette. align, type,
 * measure, hero and bar drive a browser in screen media. A whole OUTPUT MEDIUM was untested, in
 * the same shape as the viewport-height axis hero-gate closed and the browser engine
 * engine-gate covers. Emulation.setEmulatedMedia is the one call that closes it, which is why
 * measure.mjs gained setMedia on the same day.
 *
 * 🔒 AND ITS SELFTEST IS THE ORIGINAL DEFECT, NOT A MUTATION OF THE CHECK. Running the same
 * assertions in `screen` media reproduces exactly what a printer was being handed before this
 * block existed: a dark ground it will drop and pale ink it will keep. If those assertions do
 * not go red there, this gate is not reading the emulated medium and proves nothing.
 *
 *     BASE=http://127.0.0.1:8899 node tools/print-gate.mjs [--selftest]
 */
import { withPage } from './measure.mjs';
import { readdirSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const B = process.env.BASE || 'http://127.0.0.1:8899';
const SELFTEST = process.argv.includes('--selftest');
const MEDIA = SELFTEST ? 'screen' : 'print';
let pass = 0, fail = 0;
const check = (n, c) => { if (c) { pass++; if (!SELFTEST) console.log('PASS: ' + n); }
                          else { fail++; if (!SELFTEST) console.error('FAIL: ' + n); } };

function pages(dir = ROOT, prefix = '/') {
  const out = [];
  for (const n of readdirSync(dir, { withFileTypes: true })) {
    if (n.name === 'assets' || n.name === 'tools' || n.name.startsWith('.')) continue;
    const p = join(dir, n.name);
    if (n.isDirectory()) { if (existsSync(join(p, 'index.html'))) out.push(prefix + n.name + '/');
                           out.push(...pages(p, prefix + n.name + '/')); }
    else if (n.name === 'index.html') { if (prefix === '/') out.push('/'); }
    else if (n.name === '404.html') out.push(prefix + n.name);
  }
  return [...new Set(out)].sort();
}

const PROBE = `JSON.stringify((() => {
  const px = c => { const m = c.match(/[\\d.]+/g) || [0,0,0]; return m.slice(0,3).map(Number); };
  const lum = rgb => { const f = x => { x /= 255; return x <= 0.04045 ? x/12.92 : Math.pow((x+0.055)/1.055, 2.4); };
    const [r,g,b] = rgb.map(f); return 0.2126*r + 0.7152*g + 0.0722*b; };
  const ratio = (a,b) => { const [hi,lo] = [lum(a),lum(b)].sort((x,y)=>y-x); return (hi+0.05)/(lo+0.05); };
  /* 🔒 THE GROUND A PRINTER LAYS DOWN IS A COMPOSITE, AND THE FIRST VERSION OF THIS FUNCTION
     STOPPED AT THE FIRST BACKGROUND THAT WAS NOT FULLY TRANSPARENT. The seal console sits in a
     well styled with a background-color of rgba(0,0,0,.32), and reading that as opaque black made
     gate report the home pages printing text at 2.58:1 and 1.38:1 on a black ground, which is
     not what any printer would produce: 32% black over white paper is light grey. A check that
     invents a ground reports a defect that is not there, and the next person spends the night
     fixing the page instead of the instrument.
     So the chain is collected inward-to-outward and composited outward-to-inward, exactly as a
     renderer does, and it stops when the accumulated alpha reaches opacity. */
  const groundOf = el => {
    const chain = [];
    for (let n = el; n; n = n.parentElement) {
      const m = getComputedStyle(n).backgroundColor.match(/[\\d.]+/g);
      if (!m) continue;
      const a = m.length > 3 ? Number(m[3]) : 1;
      if (a === 0) continue;
      chain.push({ rgb: m.slice(0, 3).map(Number), a });
      if (a === 1) break;
    }
    let out = [255, 255, 255];                       /* paper */
    for (let i = chain.length - 1; i >= 0; i--) {
      const { rgb, a } = chain[i];
      out = out.map((c, k) => rgb[k] * a + c * (1 - a));
    }
    return out;
  };
  const ground = px(getComputedStyle(document.body).backgroundColor);
  const head = document.querySelector('h1') || document.querySelector('h2');
  const ink = head ? px(getComputedStyle(head).color) : [0,0,0];
  const bar = document.querySelector('.bar');
  const barShown = !!(bar && bar.checkVisibility && bar.checkVisibility({contentVisibilityAuto:true}));
  /* the blank-page failure, looked for directly: running text whose ink is within a whisker of
     the ground it sits on. Sampled over every paragraph, list item and heading on the page. */
  let faint = null, faintCount = 0;
  for (const el of document.querySelectorAll('p, li, h1, h2, h3, dd, dt')) {
    if (!el.textContent.trim()) continue;
    if (el.checkVisibility && !el.checkVisibility({contentVisibilityAuto:true})) continue;
    const r = ratio(px(getComputedStyle(el).color), groundOf(el));
    if (r < 3) { faintCount++; if (!faint) faint = {text: el.textContent.trim().slice(0,40), ratio: +r.toFixed(2)}; }
  }
  return { groundLum:+lum(ground).toFixed(3), inkLum:+lum(ink).toFixed(3),
           contrast:+ratio(ink, ground).toFixed(2), barShown, faintCount, faint };
})())`;

await withPage(async (page) => {
  await page.setMedia(MEDIA);
  for (const path of pages()) {
    await page.goto(B + path);
    await page.setMedia(MEDIA);            /* the override survives a navigation, but say it anyway */
    await page.evaluate(`new Promise(r=>setTimeout(r,300))`);
    const o = JSON.parse(await page.evaluate(PROBE));
    check(`${path.padEnd(20)} ground is paper-light (luminance ${o.groundLum})`, o.groundLum >= 0.8);
    check(`${path.padEnd(20)} ink is dark enough to read (luminance ${o.inkLum}, contrast ${o.contrast}:1)`,
      o.inkLum <= 0.25 && o.contrast >= 4.5);
    check(`${path.padEnd(20)} the fixed header is not on the page`, !o.barShown);
    check(`${path.padEnd(20)} nothing prints under 3:1` +
      (o.faint ? ` (${o.faintCount} faint, e.g. "${o.faint.text}" at ${o.faint.ratio}:1)` : ''), o.faintCount === 0);
  }
}, { width: 1100, height: 1400, dsf: 1 });

if (SELFTEST) {
  console.log('SELFTEST: the same assertions in screen media, which is what a printer was handed before');
  console.log(`  ${fail} of ${fail + pass} went red on a dark ground with pale ink`);
  const good = fail > 0;
  console.log(good ? 'SELFTEST OK' : 'SELFTEST FAILED: screen and paper look identical to this gate, so it reads neither');
  process.exit(good ? 0 : 1);
}
console.log(`\nPRINT FAILURES: ${fail}`);
process.exit(fail ? 1 : 0);
