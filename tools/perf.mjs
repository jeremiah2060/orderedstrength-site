#!/usr/bin/env node
/* SPEED AND SMOOTHNESS, MEASURED ON THE DEPLOYED SITE.
   Two numbers matter and neither is a Lighthouse score. How long until the page has
   painted something real, and whether a full scroll ever misses a frame. Everything else
   is commentary. */
import { withPage } from './measure.mjs';
const BASE = process.env.BASE || 'https://redesign-elite.orderedstrength-site.pages.dev';
const PAGES = (process.env.PAGES || '/,/how-it-works/,/join/').split(',');

const PROBE = `(async () => {
  const long = []; 
  try { new PerformanceObserver(l => long.push(...l.getEntries().map(e => Math.round(e.duration))))
          .observe({ type: 'longtask', buffered: true }); } catch {}
  const frames = []; let last = performance.now();
  const max = document.documentElement.scrollHeight - innerHeight;
  await new Promise(res => {
    let y = 0;
    const step = () => { const n = performance.now(); frames.push(n - last); last = n;
      y += Math.max(20, max / 110); window.scrollTo(0, y);
      if (y < max) requestAnimationFrame(step); else res(); };
    requestAnimationFrame(step);
  });
  frames.shift(); frames.shift();
  const sorted = [...frames].sort((a,b) => a-b);
  const nav = performance.getEntriesByType('navigation')[0];
  const fcp = (performance.getEntriesByType('paint').find(e => e.name === 'first-contentful-paint') || {}).startTime;
  let lcp = 0;
  try { const po = performance.getEntriesByType('largest-contentful-paint'); if (po.length) lcp = po[po.length-1].startTime; } catch {}
  let cls = 0;
  try { new PerformanceObserver(l => l.getEntries().forEach(e => { if (!e.hadRecentInput) cls += e.value; }))
          .observe({ type: 'layout-shift', buffered: true }); } catch {}
  await new Promise(r => setTimeout(r, 120));
  return {
    docH: document.documentElement.scrollHeight,
    frames: frames.length,
    meanMs: +(frames.reduce((a,b)=>a+b,0)/frames.length).toFixed(2),
    p95Ms: +sorted[Math.floor(sorted.length*0.95)].toFixed(2),
    worstMs: +sorted[sorted.length-1].toFixed(2),
    over16: frames.filter(f => f > 16.7).length,
    over33: frames.filter(f => f > 33).length,
    longTasks: long.length, longTaskMax: long.length ? Math.max(...long) : 0,
    fcpMs: fcp ? Math.round(fcp) : null,
    lcpMs: lcp ? Math.round(lcp) : null,
    cls: +cls.toFixed(4),
    domInteractiveMs: Math.round(nav.domInteractive),
    loadMs: Math.round(nav.loadEventEnd),
  };
})()`;

for (const [label, w, h, dsf] of [['desktop 1550', 1550, 970, 1], ['phone 430 at 3x', 430, 932, 3]]) {
  console.log(`\n${label}`);
  for (const p of PAGES) {
    await withPage(async page => {
      await page.goto(BASE + p);
      const d = await page.evaluate(PROBE);
      console.log(`  ${p.padEnd(16)} page ${String(d.docH).padStart(6)}px | FCP ${String(d.fcpMs).padStart(4)}ms  LCP ${String(d.lcpMs).padStart(4)}ms  interactive ${String(d.domInteractiveMs).padStart(4)}ms  CLS ${d.cls}`);
      console.log(`  ${''.padEnd(16)} scroll: mean ${d.meanMs}ms  p95 ${d.p95Ms}ms  worst ${d.worstMs}ms  frames>33ms ${d.over33}/${d.frames}  long tasks ${d.longTasks}${d.longTasks?' (max '+d.longTaskMax+'ms)':''}`);
    }, { width: w, height: h, dsf });
  }
}
