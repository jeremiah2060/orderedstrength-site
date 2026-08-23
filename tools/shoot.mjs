import { withPage } from './measure.mjs';
const BASE = process.env.BASE || 'http://127.0.0.1:8899';
const out  = process.argv[2] || '/tmp/os-shots';
const pages = (process.argv[3] || '/,/how-it-works/,/record/,/verify/').split(',');
const width = Number(process.argv[4] || 1440), height = Number(process.argv[5] || 900);
await withPage(async page => {
  for (const p of pages) {
    await page.goto(BASE + p);
    await page.evaluate(`document.querySelectorAll('.reveal').forEach(e=>e.classList.add('in'));"ok"`);
    const name = (p === '/' ? 'home' : p.replace(/\//g,'')) ;
    await page.shot(`${out}/${width}-${name}-viewport.png`);
    await page.shot(`${out}/${width}-${name}-full.png`, { full: true });
    console.log('shot', name);
  }
}, { width, height, dsf: 2 });
