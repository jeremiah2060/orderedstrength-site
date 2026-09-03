#!/usr/bin/env node
/* THE LANGUAGE REDIRECT, DRIVEN BY A BROWSER THAT REALLY SPEAKS SPANISH.
 *
 * WHY THIS EXISTS (2026-09-02). A Spanish reader who lands on the English site does not read
 * English: Chrome offers to machine-translate, and this repo has already measured what that
 * does. The CEO turned auto-translate on for /es/ on 2026-08-31 and the page fell apart,
 * because a translator rewrites the <code> runs that quote the app verbatim and the hex digests
 * the seal console depends on. tools/translate-gate.py exists because of that morning. So the
 * English pages send a Spanish phone to the Spanish site once, before anything renders.
 *
 * 🔒 IT CANNOT BE TESTED WITHOUT A BROWSER THAT REPORTS A DIFFERENT LANGUAGE, AND STUBBING
 * navigator IS TESTING THE STUB. So this launches Chrome with a real locale, which is why
 * `withPage` gained an `args` option on the same day.
 *
 * 🔒 AND --lang IS THE WRONG FLAG, WHICH THIS GATE FOUND BY PRINTING WHAT IT GOT. The first run
 * used `--lang=es-419` alone, four checks failed, and the diagnostic line showed
 * navigator.language was still en-US: --lang sets the UI language, not the one JavaScript reads.
 * `--accept-lang` is the one that moves it. Four "failures" in correct code, and the only reason
 * they were not "fixed" is that the test printed the value it was branching on.
 *
 * 🔒 THE LOOP CHECK IS THE LOAD-BEARING ONE. Two language links that each send a reader to the
 * other bounce forever, and the rule that prevents it, redirect ONLY while nothing is stored, is
 * invisible in the source. The last check walks it: Spanish phone to /, lands on /es/, clicks
 * English, must land on / and STAY.
 *
 *     BASE=http://127.0.0.1:8899 node tools/lang-redirect-gate.mjs
 */
import { withPage } from './measure.mjs';
const B = process.env.BASE || 'http://127.0.0.1:8899';
let pass = 0, fail = 0;
const check = (n, c) => { if (c) { pass++; console.log('PASS: ' + n); } else { fail++; console.error('FAIL: ' + n); } };

async function run(lang, setup, path = '/') {
  let out;
  await withPage(async (page) => {
    await page.goto(B + '/404.html');                       // same origin, so localStorage is writable
    await page.evaluate(`(()=>{try{localStorage.clear();${setup||''}}catch(e){}return 1})()`);
    await page.goto(B + path);
    await page.evaluate(`new Promise(r=>setTimeout(r,400))`);
    out = JSON.parse(await page.evaluate(`JSON.stringify({
      path: location.pathname,
      lang: navigator.language,
      stored: (function(){try{return localStorage.getItem('os-lang')}catch(e){return 'ERR'}})(),
      htmlLang: document.documentElement.lang
    })`));
  }, { width: 900, height: 700, dsf: 1, args: [`--lang=${lang}`, `--accept-lang=${lang}`] });
  return out;
}

let r = await run('es-419');
check(`a Spanish phone at / lands on the Spanish site (was ${r.path}, navigator.language=${r.lang})`,
  r.path === '/es/' && r.htmlLang.startsWith('es'));
check('and the choice is stored, so it happens once and never loops', r.stored === 'es');

r = await run('es-419', "localStorage.setItem('os-lang','en');");
check('a Spanish phone that already chose English is left alone', r.path === '/' && r.htmlLang === 'en');

r = await run('en-US');
check('an English phone is not touched at all', r.path === '/' && r.stored === null);

r = await run('es-419', '', '/how-it-works/');
check('a deep link maps to its own Spanish twin, not to the home page', r.path === '/es/how-it-works/');

r = await run('fr-FR');
check('a language with no version of this site stays on English', r.path === '/');

// the loop test: land on /es/ from Spanish, then follow the English footer link
await withPage(async (page) => {
  await page.goto(B + '/404.html');
  await page.evaluate(`(()=>{try{localStorage.clear()}catch(e){}return 1})()`);
  await page.goto(B + '/');
  await page.evaluate(`new Promise(r=>setTimeout(r,400))`);
  const onEs = await page.evaluate(`location.pathname`);
  const links = await page.evaluate(`JSON.stringify([...document.querySelectorAll('a[hreflang]')].map(a=>a.getAttribute('hreflang')+':'+a.getAttribute('href')))`);
  console.log('  (diagnostic) path after load:', onEs, ' language links:', links);
  await page.evaluate(`(()=>{const a=[...document.querySelectorAll('a[hreflang="en"]')][0]; if(!a) return 0; a.click(); return 1})()`);
  await page.evaluate(`new Promise(r=>setTimeout(r,600))`);
  const after = JSON.parse(await page.evaluate(`JSON.stringify({p:location.pathname,s:localStorage.getItem('os-lang')})`));
  check('clicking English from /es/ lands on / and STAYS there, no bounce',
    onEs === '/es/' && after.p === '/' && after.s === 'en');
}, { width: 900, height: 700, dsf: 1, args: ['--lang=es-419', '--accept-lang=es-419,es'] });

console.log(`\nLANGUAGE REDIRECT FAILURES: ${fail}`);
process.exit(fail ? 1 : 0);
