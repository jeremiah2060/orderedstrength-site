#!/usr/bin/env node
/* Render the share card. Run after any brand change: `node tools/gen-og.mjs` */
import { withPage } from './measure.mjs';
import { copyFileSync, mkdirSync } from 'node:fs';
mkdirSync('assets', { recursive: true });
await withPage(async page => {
  await page.goto((process.env.BASE || 'http://127.0.0.1:8899') + '/tools/og.html');
  await page.evaluate(`(async()=>{await document.fonts.ready;
     await Promise.all([...document.images].map(i=>i.complete?0:new Promise(r=>{i.onload=i.onerror=r})));
     return 1;})()`);
  await page.evaluate('new Promise(r=>setTimeout(r,400))');
  await page.shot('assets/og.png');
}, { width: 1200, height: 630, dsf: 1 });
console.log('assets/og.png written');
