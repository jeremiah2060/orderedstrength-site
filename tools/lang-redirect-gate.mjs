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

async function run(langs, setup, path = '/') {
  let out;
  await withPage(async (page) => {
    await page.goto(B + '/404.html');
    await page.evaluate(`(()=>{try{localStorage.clear();${setup || ''}}catch(e){}return 1})()`);
    await page.goto(B + path);
    await page.evaluate(`new Promise(r=>setTimeout(r,700))`);
    out = JSON.parse(await page.evaluate(`JSON.stringify({
      path: location.pathname,
      list: (navigator.languages||[]).join(','),
      stored: (function(){try{return localStorage.getItem('os-lang')}catch(e){return 'ERR'}})(),
      htmlLang: document.documentElement.lang,
      offer: !!document.querySelector('.langoffer')
    })`));
  }, { width: 900, height: 700, dsf: 1, args: [`--lang=${langs.split(',')[0]}`, `--accept-lang=${langs}`] });
  return out;
}

let r = await run('es-419');
check(`a Spanish browser at / lands on the Spanish site (list ${r.list})`,
  r.path === '/es/' && r.htmlLang.startsWith('es') && r.stored === 'es');

// 🔒 THE BUG THE CEO HIT. Clicking "Español" stored es, and then the bare domain served ENGLISH,
// because the stored value was read only to SUPPRESS the automatic redirect and never acted on.
// A remembered preference that is never honoured is worse than none: the reader believes they chose.
r = await run('en-US', "localStorage.setItem('os-lang','es');");
check('🔒 a reader who already CHOSE Spanish is taken there, even from an English browser',
  r.path === '/es/');

// 🔒 THE CEO'S WIFE'S MAC, MEASURED: a Spanish computer whose Chrome lists en-US, en, es.
// 🔒 THE CEO'S WIFE'S MAC: a Spanish computer whose Chrome still lists en-US first. The first
// version offered a banner here instead of redirecting, on the reasoning that the browser had
// asked for English. Correct about the browser, wrong about the person: Chrome's list is
// inherited from the account and the installer far more often than it is chosen.
r = await run('en-US,en,es');
check(`Spanish listed anywhere is enough, even ranked third (list ${r.list})`, r.path === '/es/');

r = await run('es,en');
check('Spanish ranked ABOVE English is followed', r.path === '/es/');

r = await run('en-US,en,es', "localStorage.setItem('os-lang','en');");
check('a reader who chose English is never sent away again', r.path === '/');

r = await run('en-US');
check('an English browser with no Spanish listed sees nothing at all',
  r.path === '/' && r.stored === null);

r = await run('es-419', '', '/how-it-works/');
check('a deep link maps to its own Spanish twin, not to the home page', r.path === '/es/how-it-works/');

r = await run('fr-FR');
check('a language with no version of this site is left alone', r.path === '/');

// the loop test
await withPage(async (page) => {
  await page.goto(B + '/404.html');
  await page.evaluate(`(()=>{try{localStorage.clear()}catch(e){}return 1})()`);
  await page.goto(B + '/');
  await page.evaluate(`new Promise(r=>setTimeout(r,700))`);
  const onEs = await page.evaluate(`location.pathname`);
  await page.evaluate(`(()=>{const a=[...document.querySelectorAll('a[hreflang="en"]')][0]; if(!a) return 0; a.click(); return 1})()`);
  await page.evaluate(`new Promise(r=>setTimeout(r,900))`);
  const after = JSON.parse(await page.evaluate(`JSON.stringify({p:location.pathname,s:localStorage.getItem('os-lang')})`));
  check('🔒 clicking English from /es/ lands on / and STAYS there, no bounce',
    onEs === '/es/' && after.p === '/' && after.s === 'en');
}, { width: 900, height: 700, dsf: 1, args: ['--lang=es-419', '--accept-lang=es-419,es'] });

console.log(`\nLANGUAGE REDIRECT FAILURES: ${fail}`);
process.exit(fail ? 1 : 0);
