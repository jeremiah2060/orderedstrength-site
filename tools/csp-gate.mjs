#!/usr/bin/env node
/* SERVE THE SITE UNDER ITS REAL POLICY AND PROVE THE SCRIPTS STILL RUN.
 *
 * WHY THIS EXISTS. `script-src` names eight hashes now instead of trusting 'unsafe-inline', and
 * the failure mode of a hash is the worst one this repo has: a stale hash does not error, it
 * makes the browser refuse the script, and the page then renders perfectly and does nothing.
 * check-site.py's own comment records that exact page: "A BROKEN INLINE SCRIPT IS INVISIBLE TO
 * EVERY SOURCE GATE. A duplicated catch killed the language script on all ten English pages;
 * nesting, hygiene, stamp, contrast, type, align and measure all passed."
 *
 * 🔒 AND `python3 -m http.server` CANNOT CATCH IT, BECAUSE IT DOES NOT SEND `_headers`. Every
 * browser-driven gate in this repo runs against a server that omits the very policy in question,
 * so all of them would stay green with every script on the site blocked in production. This one
 * reads `_headers`, applies the `/*` block, and is the only place the policy is ever exercised.
 *
 * 🔒 IT ASSERTS WHAT EACH SCRIPT PRODUCES, NOT THAT NOTHING WAS LOGGED. A violation-counting
 * check answers "did the browser complain", which is one inference away from the question, and
 * it is silent if the script was never reached for some other reason. Every inline block here
 * has an observable: the 40-byte one sets a class, the head block on the English pages moves a
 * Spanish browser to /es/, and the console blocks paint a 64-character fingerprint and a verdict.
 * Naming the effect makes the check impossible to satisfy by accident.
 *
 *     node tools/csp-gate.mjs [--selftest]
 */
import { withPage } from './measure.mjs';
import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { createServer } from 'node:http';
import { join, dirname, extname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const SELFTEST = process.argv.includes('--selftest');
let pass = 0, fail = 0;
const check = (n, c) => { if (c) { pass++; console.log('PASS: ' + n); } else { fail++; console.error('FAIL: ' + n); } };

/* the `/*` block of _headers, which is what Cloudflare Pages applies to every response */
function globalHeaders() {
  const lines = readFileSync(join(ROOT, '_headers'), 'utf8').split('\n');
  const out = {}; let inGlobal = false;
  for (const line of lines) {
    if (/^\S/.test(line)) { inGlobal = line.trim() === '/*'; continue; }
    if (!inGlobal) continue;
    const m = line.match(/^\s+([A-Za-z-]+):\s*(.*)$/);
    if (m) out[m[1]] = m[2];
  }
  return out;
}

const TYPES = { '.html':'text/html; charset=utf-8', '.js':'application/javascript', '.css':'text/css',
                '.webp':'image/webp', '.png':'image/png', '.jpg':'image/jpeg', '.json':'application/json',
                '.woff2':'font/woff2', '.svg':'image/svg+xml', '.txt':'text/plain', '.xml':'application/xml' };

function resolve(p) {
  const clean = decodeURIComponent(p.split('?')[0]).replace(/\.\./g, '');
  for (const cand of [clean, clean + 'index.html', clean + '.html', clean + '/index.html']) {
    const f = join(ROOT, cand);
    if (existsSync(f) && !readdirSync(dirname(f)).includes(undefined) && !f.endsWith('/')) {
      try { if (readFileSync(f)) return f; } catch { /* a directory */ }
    }
  }
  return null;
}

/* MUTATE ONE HASH so the policy no longer matches the script it names. That is precisely what a
   stale _headers is, and it is the input that must turn this gate red. */
function poison(h) {
  const csp = h['Content-Security-Policy'];
  return { ...h, 'Content-Security-Policy': csp.replace(/'sha256-([A-Za-z0-9+/=]{6})/g, "'sha256-AAAAAA") };
}

const headers = SELFTEST ? poison(globalHeaders()) : globalHeaders();
const server = createServer((req, res) => {
  const f = resolve(req.url);
  if (!f) { res.writeHead(404, headers); return res.end('not found'); }
  const body = readFileSync(f);
  res.writeHead(200, { ...headers, 'Content-Type': TYPES[extname(f)] || 'application/octet-stream',
                       'Content-Length': body.length });
  res.end(body);
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const B = 'http://127.0.0.1:' + server.address().port;
console.log(`serving ${ROOT} under the real _headers policy at ${B}`);
if (SELFTEST) console.log('SELFTEST: every hash in the policy has been corrupted\n');

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

try {
  await withPage(async (page) => {
    /* ARM 1: the 40-byte block sets one class that the reveal system keys off, so a blocked
       one is a page whose animations never arm.
       🔒 DERIVED FROM THE PAGE, NOT ASSUMED ACROSS THE SET. Its first draft asserted the class
       on all twenty pages and called the two 404s broken; they simply do not ship that script,
       and nothing on them is gated on it (checked: no .reveal, no .rail, no .r). An assertion
       generalised from eighteen members to twenty is the same mistake as the loop test that
       walked one page pair and printed a verdict about ten. Read the source, then assert. */
    const SETS_JS = /<script>document\.documentElement\.className="js";<\/script>/;
    for (const path of pages()) {
      const file = resolve(path);
      if (!file || !SETS_JS.test(readFileSync(file, 'utf8'))) {
        console.log(`  ..   ${path} ships no class-setting block, nothing to observe here`);
        continue;
      }
      await page.goto(B + path);
      await page.evaluate(`new Promise(r=>setTimeout(r,250))`);
      const cls = await page.evaluate(`document.documentElement.className`);
      check(`${path} ran its inline script (documentElement class is "${cls}")`, /(^|\s)js(\s|$)/.test(cls));
    }
    /* ARM 2: the seal console is the largest inline block on the site and the one whose failure
       a reader would notice first, because it is the interactive proof the page is built around. */
    /* 🔒 THE SELFTEST CAUGHT THESE TWO BEING DECORATIVE, WHICH IS WHY IT EXISTS. The first
       draft asked whether #hash held 64 characters and whether #verdict read VERIFIED, and both
       stayed green with every hash in the policy corrupted, because the page SHIPS both as
       static markup: `<p id="hash"><b><span>28168c4...</span></b></p>` and a `VERIFIED` span.
       That is good design, a correct no-script fallback, and it makes the obvious observable
       useless: it was reading the HTML and reporting on the script.
       What only the script can do is REPLACE that one span with sixty-four per-character
       elements, one per hex digit, so it can roll the ones that changed. Count the children. */
    for (const path of ['/', '/es/']) {
      await page.goto(B + path);
      await page.evaluate(`new Promise(r=>setTimeout(r,900))`);
      const n = await page.evaluate(`(document.getElementById('hash')||{children:[]}).children.length`);
      check(`${path} console block ran (#hash rendered ${n} per-character elements, static markup has 1)`, n >= 60);
    }
    /* 🔒 THE VERIFIER'S SCRIPT PRINTS NOTHING ON LOAD, so "is #out empty" is a question about
       the page's design and not about the policy. Its first draft asked exactly that and called
       two good pages broken. What that script DOES on load is attach two listeners, so the
       observable is that one of them fires: press the demo button and the textarea fills. */
    for (const path of ['/verify/', '/es/verify/']) {
      await page.goto(B + path);
      await page.evaluate(`new Promise(r=>setTimeout(r,600))`);
      await page.evaluate(`(()=>{document.getElementById('demo').click();return 1})()`);
      await page.evaluate(`new Promise(r=>setTimeout(r,300))`);
      const filled = await page.evaluate(`(document.getElementById('in')||{value:''}).value.length`);
      check(`${path} wired its listeners under the policy (demo filled ${filled} chars)`, filled > 0);
    }
    /* and the same for the verdict: it ships as VERIFIED in the markup, so reading it proves
       nothing. Pressing a preset moves a field, which recomputes a SHA-256 in the page and must
       flip it. Only a script that ran can do that, and it exercises the crypto path as well. */
    await page.goto(B + '/');
    await page.evaluate(`new Promise(r=>setTimeout(r,900))`);
    const before = await page.evaluate(`document.getElementById('verdict').textContent`);
    await page.evaluate(`(()=>{document.getElementById('pwide').click();return 1})()`);
    await page.evaluate(`new Promise(r=>setTimeout(r,500))`);
    const after = await page.evaluate(`document.getElementById('verdict').textContent`);
    check(`the home page seal recomputes under the policy ("${before}" to "${after}")`,
      before === 'VERIFIED' && after !== before);

    /* 🔒 AND /assets/lang-check, WHICH EVERY OTHER GATE HERE EXCLUDES ON PURPOSE AND WHICH IS
       STILL A SERVED PAGE WITH AN INLINE SCRIPT. Excluding /assets/ is right for a page gate, so
       the diagnostic cannot drift into the sitemap or the page counts, and it was wrong for a
       policy: its hash was left out of script-src and production refused to run it, so the one
       tool built to end the guessing about the language redirect rendered perfectly and did
       nothing. Found by running lang-redirect-gate against the LIVE domain, which is the only
       place the real policy applies. Its fields ship as a single ellipsis; only the script
       fills them. */
    await page.goto(B + '/assets/lang-check.html');
    await page.evaluate(`new Promise(r=>setTimeout(r,500))`);
    const diag = await page.evaluate(`(document.getElementById('verdict')||{textContent:''}).textContent.trim()`);
    check(`/assets/lang-check ran its script (verdict is ${diag.length} chars, its placeholder is 1)`,
      diag.length > 20);
  }, { width: 1280, height: 900, dsf: 1 });

  /* ARM 3: the head redirect block, whose only observable is that a Spanish browser moves. */
  await withPage(async (page) => {
    await page.goto(B + '/404.html');
    await page.evaluate(`(()=>{try{localStorage.clear()}catch(e){}return 1})()`);
    await page.goto(B + '/');
    await page.evaluate(`new Promise(r=>setTimeout(r,800))`);
    const where = await page.evaluate(`location.pathname`);
    check(`the head redirect block ran under the policy (a Spanish browser reached ${where})`, where === '/es/');
  }, { width: 900, height: 700, dsf: 1, args: ['--lang=es-419', '--accept-lang=es-419,es'] });
} finally { server.close(); }

if (SELFTEST) {
  const good = fail > 0;
  console.log(`\n  ${fail} of ${fail + pass} checks went red with every hash corrupted`);
  console.log(good ? 'SELFTEST OK' : 'SELFTEST FAILED: a corrupted policy changed nothing, so this gate is decorative');
  process.exit(good ? 0 : 1);
}
console.log(`\nCSP RUNTIME FAILURES: ${fail}`);
process.exit(fail ? 1 : 0);
