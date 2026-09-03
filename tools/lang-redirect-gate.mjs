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
/* 🔒 THIS ALSO ASSERTED r.stored === 'es' UNTIL 2026-09-03, AND THAT CLAUSE WAS PINNING A
   DEFECT RATHER THAN A REQUIREMENT. The head script wrote os-lang on the automatic path, so a
   guess about a browser and a person's click became the same value on disk, and this line held
   that in place as though it were the intent. The requirement is that a Spanish browser reaches
   the Spanish site, which is what remains here; what it must NOT leave behind now has its own
   check below, where it can be read as the rule it is. */
check(`a Spanish browser at / lands on the Spanish site (list ${r.list})`,
  r.path === '/es/' && r.htmlLang.startsWith('es'));

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

/* ══ THE LOOP TEST, ON EVERY PAGE AND NOT ONLY THE HOME PAGE ══════════════════════════════
   🔒 IT WALKED ONE PAIR OUT OF TEN, AND A REAL LOOP WAS LIVE IN ONE OF THE OTHER NINE
   (2026-09-03, proven against production). Neither 404 page loaded site.js, and site.js holds
   the ONLY writer of os-lang, so on the Spanish 404 the English link went to /404.html, which
   stored nothing, detected Spanish and replaced straight back. Measured on the live domain:
   stored=null, no site.js, and following that link returned to /es/404 in Spanish every time.
   The English link on that page could never work, for any browser that lists Spanish at all.

   🔒 AND THE ONE-PAGE VERSION OF THIS TEST IS WHY IT SHIPPED. The rule it proves is a property
   of a PAGE, because it depends on that page loading the script that records the choice, and it
   was asserted about the home page and generalised by hope. A gate that checks one member of a
   set and prints a verdict about the set is the same instrument as a gate that checks nothing.

   🔒 IT MUST CLICK, NOT NAVIGATE. Reading the link's href and calling goto is the obvious
   shortcut and it tests nothing: the storing happens in a click handler, so a goto walks past
   the exact mechanism that was broken and lands on green. */
const PAIRS = [['/', '/es/'], ['/how-it-works/', '/es/how-it-works/'], ['/stronger/', '/es/stronger/'],
               ['/record/', '/es/record/'], ['/verify/', '/es/verify/'], ['/join/', '/es/join/'],
               ['/support/', '/es/support/'], ['/terms/', '/es/terms/'],
               ['/app-privacy/', '/es/app-privacy/'], ['/404.html', '/es/404.html'],
               ['/receipt/', '/es/receipt/'], ['/spec/', '/es/spec/']];

/* 🔒 ONE BROWSER FOR ALL TEN, BECAUSE EACH PAIR ALREADY CLEARS ITS OWN STORAGE. The first
   draft opened a fresh Chrome per pair, which is ten launches to establish a clean state that
   one localStorage.clear() establishes, and it made this gate the slowest thing in check.sh for
   no coverage at all. Whatever the previous pair stored, the clear at the top of each iteration
   removes it, and the goto that follows re-decides from nothing. */
await withPage(async (page) => {
  for (const [en, es] of PAIRS) {
    await page.goto(B + en);
    await page.evaluate(`(()=>{try{localStorage.clear()}catch(e){}return 1})()`);
    await page.goto(B + en);
    await page.evaluate(`new Promise(r=>setTimeout(r,700))`);
    const sent = await page.evaluate(`location.pathname`);
    const clicked = await page.evaluate(`(()=>{const a=document.querySelector('a[hreflang="en"]'); if(!a) return 0; a.click(); return 1})()`);
    /* the click starts a navigation, and an evaluate that races it gets "target navigated";
       one retry after the document settles is the whole fix, and it is not papering over
       anything: the assertion below is about where the browser ENDS UP */
    let after = null;
    for (let t = 0; t < 3 && !after; t++) {
      try {
        await page.evaluate(`new Promise(r=>setTimeout(r,700))`);
        after = JSON.parse(await page.evaluate(`JSON.stringify({p:location.pathname,s:localStorage.getItem('os-lang')})`));
      } catch (e) { /* still navigating */ }
    }
    const norm = p => p.replace(/\/index\.html$/, '/').replace(/\.html$/, '');
    check(`🔒 ${es} sends a Spanish browser there, and its English link lands on ${en} and STAYS`,
      norm(sent) === norm(es) && !!clicked && after && norm(after.p) === norm(en) && after.s === 'en');
  }
}, { width: 900, height: 700, dsf: 1, args: ['--lang=es-419', '--accept-lang=es-419,es'] });

/* ══ AN AUTOMATIC REDIRECT IS NOT A CHOICE (2026-09-03) ═══════════════════════════════════
   The detected path used to write os-lang=es on its way out, which made a guess about a
   browser indistinguishable, on disk, from a person clicking "Español". The site could then
   never re-ask, never tell the two apart, and nobody could get a clean state back without
   developer tools. Only a click writes it now. */
r = await run('es-419');
check('🔒 an automatic redirect leaves NO stored choice behind', r.path === '/es/' && r.stored === null);

r = await run('en-US,en,es');
check('🔒 nor does the third-ranked case', r.path === '/es/' && r.stored === null);

/* 🔒 AND THE WRITE COULD SUPPRESS THE REDIRECT IT WAS RECORDING. setItem throws in private
   browsing and it stood BEFORE location.replace inside one try, so the single branch that
   exists to serve a Spanish reader was the branch that failed by leaving them on English.
   The comment above it read EVERY BRANCH FAILS OPEN. It was true of every branch but that one. */
r = await run('es-419', "Object.defineProperty(window,'localStorage',{get(){throw new Error('blocked')}});");
check('🔒 a browser that cannot store a choice is still redirected', r.path === '/es/');

/* ══ THE DIAGNOSTIC MUST NOT DISAGREE WITH THE SITE ═══════════════════════════════════════
   🔒 A DIAGNOSTIC THAT RESTATES A RULE IN ITS OWN WORDS IS A SECOND IMPLEMENTATION OF IT, AND
   THIS ONE DRIFTED. /assets/lang-check read navigator.languages[0] from the day it was written
   and the rule widened one commit later, so on the exact browser the shipped rule was written
   FOR, the Spanish macOS reporting "en-US, en, es", the page printed "it is not asking for
   Spanish" while the site redirected. The one tool built to end the guessing pointed the wrong
   way, and nothing here could see it because no gate had ever opened it. */
async function diagnosisAgrees(langs, setup) {
  let verdict, actual;
  await withPage(async (page) => {
    await page.goto(B + '/404.html');
    await page.evaluate(`(()=>{try{localStorage.clear();${setup || ''}}catch(e){}return 1})()`);
    await page.goto(B + '/assets/lang-check.html');
    await page.evaluate(`new Promise(r=>setTimeout(r,400))`);
    verdict = await page.evaluate(`document.getElementById('verdict').textContent`);
    await page.goto(B + '/404.html');
    await page.evaluate(`(()=>{try{localStorage.clear();${setup || ''}}catch(e){}return 1})()`);
    await page.goto(B + '/');
    await page.evaluate(`new Promise(r=>setTimeout(r,700))`);
    actual = await page.evaluate(`location.pathname`);
  }, { width: 900, height: 700, dsf: 1, args: [`--lang=${langs.split(',')[0]}`, `--accept-lang=${langs}`] });
  const predicts = /WILL redirect|goes to the Spanish site every time/.test(verdict);
  return { agrees: predicts === (actual === '/es/'), predicts, actual, verdict };
}

for (const [langs, setup, label] of [
  ['es-419',       '',                                    'a Spanish browser'],
  ['en-US,en,es',  '',                                    'Spanish ranked third, the case it used to get wrong'],
  ['en-US',        '',                                    'an English browser'],
  ['fr-FR',        '',                                    'a language this site does not publish'],
  ['en-US',        "localStorage.setItem('os-lang','es');", 'a reader who chose Spanish'],
  ['es-419',       "localStorage.setItem('os-lang','en');", 'a reader who chose English'],
]) {
  const d = await diagnosisAgrees(langs, setup);
  check(`the diagnostic agrees with the site for ${label}` +
        (d.agrees ? '' : `  [it predicts ${d.predicts ? 'REDIRECT' : 'STAY'}, the site does ${d.actual}]`), d.agrees);
}

/* ══ A TRANSLATED SPANISH PAGE SAYS SO ════════════════════════════════════════════════════
   THE DEFECT THE CEO ACTUALLY HIT (2026-09-03): "it only appears for a split second then goes
   back to english again, but all the screenshots are in spanish, only the content is bouncing".
   Chrome's translator, from an "always translate Spanish" set on 2026-08-31. The Spanish pages
   now decline translation, which Chrome honours and Safari does not, so the page also watches
   its own headline. 🔒 THE INJECTION IS A REWRITE OF THAT HEADLINE, WHICH IS EXACTLY AND ONLY
   WHAT A TRANSLATOR DOES TO IT. Driving Chrome's real translate UI is not available here, and a
   check that stubbed the class name would only ever see the one browser that sets it. */
async function translatedNotice(path, rewrite) {
  let out;
  await withPage(async (page) => {
    await page.goto(B + path);
    await page.evaluate(`new Promise(r=>setTimeout(r,500))`);
    if (rewrite) await page.evaluate(`(()=>{document.querySelector('h1').textContent='He changes your workout in the middle of it.';return 1})()`);
    await page.evaluate(`new Promise(r=>setTimeout(r,500))`);
    out = JSON.parse(await page.evaluate(`JSON.stringify((()=>{
      const n=document.querySelector('.mtnote');
      const a=n&&n.querySelector('a[hreflang]');
      return {shown:!!n, href:a?a.getAttribute('href'):null,
              stays:n?n.getAttribute('translate'):null,
              first: n ? n.parentElement.firstElementChild === n : null};
    })())`));
  }, { width: 900, height: 700, dsf: 1 });
  return out;
}

let t = await translatedNotice('/es/', true);
check('🔒 a Spanish page whose words were rewritten under it says so', t.shown && t.first);
check('   and the notice cannot itself be translated away', t.stays === 'no');
check('   and it points at the real English page, not a second copy of the mapping', t.href === '/');

t = await translatedNotice('/es/', false);
check('🔒 and an untouched Spanish page says nothing (the arm that makes the one above a check)', !t.shown);

t = await translatedNotice('/', true);
check('🔒 and an English page is left alone: its prose is translatable on purpose', !t.shown);

console.log(`\nLANGUAGE REDIRECT FAILURES: ${fail}`);
process.exit(fail ? 1 : 0);
