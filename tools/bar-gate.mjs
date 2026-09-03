#!/usr/bin/env node
/* THE ONE COMPONENT THAT IS ON EVERY SCREEN OF THIS SITE MUST NOT COLLIDE WITH ITSELF.
 *
 * WHY THIS EXISTS (2026-09-03). Adding one link to the header put the wordmark and the nav at a
 * gap of 0px from 900 to 980px in English and 1000 to 1072px in Spanish, on all twenty pages at
 * once, and every gate in check.sh stayed green. align-gate reads LEFT EDGES and sideways scroll,
 * measure-gate reads paragraph wrapping, type and type-floor read size, hero-gate reads the hero.
 * None of them asks whether two things in the bar are touching.
 *
 * 🔒 THIS HAS BEEN MEASURED BY HAND TWICE AND WRITTEN DOWN BOTH TIMES, WHICH IS THE TELL. The
 * stylesheet carries two long comments recording exactly this measurement over CDP: "the gap
 * between the wordmark's right edge and the nav's left edge is 0px at 320 and 360 in BOTH
 * languages, and 0px at 375 and 390 in Spanish only", and "a collision band fifteen pixels wide
 * is still a collision, and it is the one component that is on every screen of this site". A
 * measurement worth writing into a comment twice is a measurement that should have been a gate
 * the first time, because the comment protects the width that was measured and nothing else.
 *
 * 🔒 AND A BOX HEIGHT CANNOT TELL YOU A LABEL WRAPPED, because padding raises it too. That line
 * is in the stylesheet as well. This counts distinct TOP offsets across the visible items and
 * asks each item for its own client rect count, so a link that broke onto two lines inside its
 * own box is caught as surely as one that pushed a sibling down.
 *
 *     BASE=http://127.0.0.1:8899 node tools/bar-gate.mjs [--selftest]
 */
import { withPage } from './measure.mjs';
import { readdirSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const B = process.env.BASE || 'http://127.0.0.1:8899';
const SELFTEST = process.argv.includes('--selftest');
const MIN_GAP = 8;          /* a gap under this reads as touching, and 15px was called a collision here before */

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

/* 🔒 THE DENSE SWEEP GOES WHERE THE COLLISIONS WERE, AND THE COARSE ONE GOES EVERYWHERE. The
   header is one component with identical markup on all twenty pages, so page-to-page variation
   is small and width-to-width variation is the whole defect. Both are still walked: a coarse
   pass over every page would have caught a page that somehow differs, and the dense pass over
   the two home pages, which carry the longest labels in each language, is what pins the band. */
const DENSE = [320, 360, 375, 390, 414, 428, 480, 600, 700, 768, 800, 880, 896, 900, 940, 980,
               1000, 1008, 1024, 1040, 1072, 1088, 1104, 1120, 1200, 1280, 1440, 1600, 1920, 2560];
const COARSE = [320, 390, 768, 1024, 1280, 1920];
const PAGES = pages();

let pass = 0, fail = 0; const failures = [];

const PROBE = (hide) => `(() => {
  ${hide ? `{const st=document.createElement('style');st.textContent=${JSON.stringify(hide)};document.head.appendChild(st);}` : ''}
  const seen = el => el && el.checkVisibility && el.checkVisibility({contentVisibilityAuto:true,opacityProperty:true,visibilityProperty:true});
  const wm = document.querySelector('.bar .wordmark');
  const nav = document.querySelector('.bar nav');
  if (!wm || !nav) return {ok:false, why:'the bar has no wordmark or no nav'};
  const items = [...nav.children].filter(seen);
  if (!items.length) return {ok:false, why:'the nav renders nothing at all'};
  const w = wm.getBoundingClientRect();
  const boxes = items.map(e => e.getBoundingClientRect());
  const navLeft = Math.min(...boxes.map(b => b.left));
  const gap = Math.round(navLeft - w.right);
  if (gap < ${MIN_GAP}) return {ok:false, why:'the wordmark and the nav are ' + gap + 'px apart'};
  const tops = new Set(boxes.map(b => Math.round(b.top)));
  if (tops.size > 1) return {ok:false, why:'the nav is on ' + tops.size + ' lines'};
  for (const e of items) {
    if (e.getClientRects().length > 1)
      return {ok:false, why:'"' + e.textContent.trim().slice(0,18) + '" wraps inside its own box'};
  }
  const over = document.documentElement.scrollWidth - document.documentElement.clientWidth;
  if (over > 0) return {ok:false, why:'the page scrolls sideways by ' + over + 'px'};
  return {ok:true, gap, items:items.length};
})()`;

async function sweep(paths, widths) {
  for (const width of widths) {
    await withPage(async (page) => {
      for (const path of paths) {
        await page.goto(B + path);
        await page.evaluate(`new Promise(r=>setTimeout(r,180))`);
        const o = JSON.parse(await page.evaluate(`JSON.stringify(${PROBE(SELFTEST ? '.bar nav > a:not(.cta){display:inline!important}.menu{display:none!important}' : '')})`));
        if (o.ok) pass++;
        else { fail++; failures.push(`${width}px ${path}: ${o.why}`); }
      }
    }, { width, height: 900, dsf: 1 });
  }
}

await sweep(['/', '/es/'], DENSE);
await sweep(PAGES, COARSE);

if (SELFTEST) {
  /* 🔒 NAME THE INPUT THAT TURNS IT RED: force the full nav on at every width, which is the
     exact state the collapse rules exist to prevent, and the narrow widths must collide. */
  console.log('SELFTEST: collapse rules defeated, full nav forced on at every width');
  console.log(`  went red on ${fail} of ${fail + pass} page-widths`);
  if (failures.length) console.log(`  sample verdict: ${failures[0]}`);
  const good = fail > 0 && /apart|lines|wraps|sideways/.test(failures[0] || '');
  console.log(good ? 'SELFTEST OK' : 'SELFTEST FAILED');
  process.exit(good ? 0 : 1);
}

failures.forEach(f => console.error('FAIL: ' + f));
console.log(`\nBAR: ${pass} clean, ${fail} colliding, over ${DENSE.length} widths on 2 pages and ${COARSE.length} widths on ${PAGES.length}`);
process.exit(fail ? 1 : 0);
