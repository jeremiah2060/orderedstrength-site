import { withPage } from './measure.mjs';
const BASE = process.env.BASE || 'http://127.0.0.1:8899';
const PROBE = `(() => {
  const hero = document.querySelector('.hero');
  const shot = document.querySelector('.hero-shot');
  const ph = document.querySelector('.hero-shot .phone');
  const scr = ph && ph.querySelector('.screen');
  const img = scr && scr.querySelector('img');
  const fl = document.querySelector('.hero-shot .appcard.float');
  const facts = document.querySelector('.hero .facts');
  const r = e => e ? (({x,y,width,height,top,bottom,left,right})=>({left:+left.toFixed(1),top:+top.toFixed(1),right:+right.toFixed(1),bottom:+bottom.toFixed(1),w:+width.toFixed(1),h:+height.toFixed(1)}))(e.getBoundingClientRect()) : null;
  const cs = e => e ? getComputedStyle(e) : null;
  return {
    vh: innerHeight, vw: innerWidth,
    hero: r(hero), heroMinH: cs(hero).minHeight,
    shot: r(shot), phone: r(ph), screen: r(scr), img: r(img), float: r(fl), facts: r(facts),
    phoneRadius: cs(ph).borderRadius, phonePad: cs(ph).padding,
    imgNatural: img ? [img.naturalWidth, img.naturalHeight] : null,
    imgFit: img ? cs(img).objectFit : null,
    phoneOverflowsHero: ph && hero ? +(r(ph).bottom - r(hero).bottom).toFixed(1) : null,
    phoneOverflowsViewport: ph ? +(r(ph).bottom - innerHeight).toFixed(1) : null,
    floatOverflowsViewport: fl ? +(r(fl).bottom - innerHeight).toFixed(1) : null,
    factsTop: facts ? +(r(facts).top - innerHeight).toFixed(1) : null
  };
})()`;
for (const [w,h] of [[1440,900],[1728,1080],[1920,1200],[390,844]]) {
  await withPage(async page => {
    await page.goto(BASE + '/');
    const d = await page.evaluate(PROBE);
    console.log(`\n=== ${w}x${h} ===`);
    console.log(JSON.stringify(d,null,1));
  }, { width: w, height: h, dsf: 1 });
}
