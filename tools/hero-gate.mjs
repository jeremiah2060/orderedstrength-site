#!/usr/bin/env node
/* THE HERO COMPOSITION, AT VIEWPORT HEIGHTS THIS REPO NEVER TESTED.
 *
 * WHY THIS EXISTS (2026-09-02, CEO-found on a Windows laptop). The hero device is sized by
 * viewport HEIGHT (`--device-h: clamp(19rem, 100svh - 21rem, 36rem)`) and the floating card was
 * capped at a fixed 16rem, so the two did not scale together. On a 1259x637 viewport, which is
 * what a common Windows laptop at 125% display scaling produces, the phone rendered 145px wide
 * and the card 193px: the ILLUSTRATION was 1.33 times the width of the product it annotates, its
 * label wrapped to two lines and every lift name wrapped. Nothing was broken. The composition
 * had inverted, and it looked like a bug to the one person who matters.
 *
 * 🔒 EVERY GATE IN THIS REPO VARIES WIDTH AND FIXES HEIGHT. align, type, type-floor and measure
 * all sweep 320 to 2560 pixels ACROSS and all run at 900 or 950 pixels DOWN, which is taller than
 * most laptops. A whole axis of this design was untested, and it is the axis the hero is sized on.
 *
 * The two invariants below are the ones that actually broke, and neither is visible in the source:
 *   1. a floating annotation is never wider than the thing it annotates
 *   2. nothing inside it wraps, because a wrapped label reads as a mistake rather than a caption
 *
 *     BASE=http://127.0.0.1:8899 node tools/hero-gate.mjs
 */
import { withPage } from './measure.mjs';

const BASE = process.env.BASE || 'http://127.0.0.1:8899';
/* Real shapes, not round numbers: a MacBook, a 16:9 laptop at 100% and at 125% and 150% scaling,
   a short desktop window, and a very tall one. The 125% and 150% rows are the CEO's report. */
const SIZES = [
  [1440, 900, 'MacBook-ish'],
  [1888, 955, '16:9 laptop at 100%'],
  [1510, 764, '16:9 laptop at 125%'],
  [1259, 637, '16:9 laptop at 150%'],
  [1600, 700, 'short desktop window'],
  [1440, 1200, 'tall window'],
];

let pass = 0, fail = 0;
const check = (n, c) => { if (c) { pass++; console.log('PASS: ' + n); } else { fail++; console.error('FAIL: ' + n); } };

for (const [w, h, label] of SIZES) {
  await withPage(async (page) => {
    await page.goto(BASE + '/');
    await page.evaluate(`document.querySelectorAll('.reveal').forEach(e=>e.classList.add('in'));"ok"`);
    const r = JSON.parse(await page.evaluate(`(() => {
      const card = document.querySelector('.hero-shot .appcard.float');
      const devs = [...document.querySelectorAll('.hero-shot .device')];
      if (!card || !devs.length) return JSON.stringify({ missing: true });
      const cs = getComputedStyle(card);
      const cw = card.getBoundingClientRect().width;
      const pw = Math.max(...devs.map(d => d.getBoundingClientRect().width));
      // A wrapped row is taller than one line of its own text. Measured, not assumed.
      let wrapped = [];
      for (const row of card.querySelectorAll('.lift, .cap')) {
        const rs = getComputedStyle(row);
        const lh = parseFloat(rs.lineHeight) || parseFloat(rs.fontSize) * 1.4;
        const inner = row.getBoundingClientRect().height
                    - (parseFloat(rs.paddingTop) || 0) - (parseFloat(rs.paddingBottom) || 0);
        if (Math.round(inner / lh) > 1) wrapped.push((row.textContent || '').trim().slice(0, 30));
      }
      return JSON.stringify({ floating: cs.position === 'absolute', cardW: Math.round(cw),
                              phoneW: Math.round(pw), wrapped });
    })()`));

    if (r.missing) { check(`${label} ${w}x${h}: the hero still has a card and devices`, false); return; }
    /* 🔒 THE RATIO ONLY MEANS ANYTHING WHILE THE CARD FLOATS. Once it stacks it is a full-width
       block below the phones, deliberately wider than them, and asserting the ratio there would
       fail on correct layout. */
    if (r.floating) {
      check(`${label} ${w}x${h}: the floating card (${r.cardW}px) is not wider than the phone (${r.phoneW}px)`,
        r.cardW <= r.phoneW);
    } else {
      check(`${label} ${w}x${h}: too short to float, so the card stacks instead of overlapping`, true);
    }
    check(`${label} ${w}x${h}: nothing inside the card wraps${r.wrapped.length ? ' (' + r.wrapped.join(' / ') + ')' : ''}`,
      r.wrapped.length === 0);
  }, { width: w, height: h, dsf: 1 });
}

console.log(`\nHERO FAILURES: ${fail}`);
process.exit(fail ? 1 : 0);
