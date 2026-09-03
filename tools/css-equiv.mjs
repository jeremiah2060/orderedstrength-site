#!/usr/bin/env node
/* THE GENERATED STYLESHEET MUST PARSE INTO THE SAME STYLESHEET AS ITS SOURCE.
 *
 * WHY THIS EXISTS, AND WHY minify-css.py --check IS NOT ENOUGH. That check regenerates the file
 * and byte-compares, which proves assets/site.min.css is what the CURRENT stripper produces. It
 * says nothing about whether the stripper is right. Edit one line of that function and --check
 * goes green on a stylesheet that renders differently, because the artifact and the generator
 * agree with each other and both are wrong. A generator's output can only be checked against
 * the thing it claims to preserve.
 *
 * 🔒 SO THE COMPARISON IS THE BROWSER'S OWN, NOT ONE WRITTEN HERE. Both files are linked from a
 * bare page and read back through the CSSOM, and `cssText` on a grouping rule already serializes
 * its children, so joining the top-level rules is the browser's canonical form of the entire
 * sheet: media queries, supports blocks, keyframes and all. Any difference in what a browser
 * actually parsed shows up as a character difference, and this prints where.
 *
 * Measured when it was written: 260 rules and 41,923 characters on both sides, identical.
 *
 *     BASE=http://127.0.0.1:8899 node tools/css-equiv.mjs [--selftest]
 */
import { withPage } from './measure.mjs';
import { readFileSync } from 'node:fs';
import { createServer } from 'node:http';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const SELFTEST = process.argv.includes('--selftest');

/* 🔒 THIS SERVES ITS TWO PROBE PAGES FROM MEMORY, AND THE FIRST VERSION WROTE THEM INTO THE
   REPOSITORY ROOT (2026-09-03). They lived for about four seconds each and were removed in a
   `finally`, and that was long enough: icon-gate walks the tree for pages, ran inside that
   window in the same check.sh, counted twenty-two pages instead of twenty and failed the whole
   suite on `2 page(s) carry no icon link`. It was right, and the temp files were the defect.
   🔒 A GATE THAT WRITES INTO THE TREE IT CHECKS CAN BREAK A GATE THAT READS IT, and the
   collision is timing-dependent, so it is the kind that passes locally and fails in the run
   that matters. Nothing is written to disk now: the probe pages exist only as strings, and
   /assets/ is proxied from the real files so the stylesheets under test are the real ones. */
const page = href => `<!doctype html><html><head><link rel="stylesheet" href="${href}"></head><body></body></html>`;
const TYPES = { '.css': 'text/css', '.html': 'text/html; charset=utf-8', '.woff2': 'font/woff2' };
let broken = null;
if (SELFTEST) {
  /* damage the GENERATED side, because that is the direction the real failure runs: a stripper
     that eats one character too many. One deleted declaration must be enough to turn this red. */
  broken = readFileSync(join(ROOT, 'assets/site.min.css'), 'utf8').replace(/;letter-spacing:[^;}]+/, '');
}
const ROUTES = {
  '/a': page('/assets/site.css'),
  '/b': page(SELFTEST ? '/broken.css' : '/assets/site.min.css'),
};
const server = createServer((req, res) => {
  const url = req.url.split('?')[0];
  if (ROUTES[url]) { res.writeHead(200, {'Content-Type': TYPES['.html']}); return res.end(ROUTES[url]); }
  if (url === '/broken.css' && broken) { res.writeHead(200, {'Content-Type': TYPES['.css']}); return res.end(broken); }
  if (url.startsWith('/assets/')) {
    try {
      const body = readFileSync(join(ROOT, url.replace(/^\//, '')));
      res.writeHead(200, {'Content-Type': TYPES[url.slice(url.lastIndexOf('.'))] || 'application/octet-stream'});
      return res.end(body);
    } catch { /* fall through */ }
  }
  res.writeHead(404); res.end('not found');
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const B = 'http://127.0.0.1:' + server.address().port;
const A = 'a', C = 'b';

const DUMP = `JSON.stringify((()=>{ const s = document.styleSheets[0];
  return {rules: s.cssRules.length, text: [...s.cssRules].map(r => r.cssText).join('\\n')}; })())`;

async function read(path) {
  let out;
  await withPage(async (p) => {
    await p.goto(B + '/' + path);
    await p.evaluate(`new Promise(r=>setTimeout(r,700))`);
    out = JSON.parse(await p.evaluate(DUMP));
  }, { width: 1200, height: 800, dsf: 1 });
  return out;
}

try {
  const a = await read(A), b = await read(C);
  console.log(`  source    assets/site.css      ${a.rules} rules, ${a.text.length} chars of serialized CSSOM`);
  console.log(`  generated assets/site.min.css  ${b.rules} rules, ${b.text.length} chars of serialized CSSOM`);
  const same = a.text === b.text;
  if (!same) {
    for (let i = 0; i < Math.max(a.text.length, b.text.length); i++) {
      if (a.text[i] !== b.text[i]) {
        console.log(`  first divergence at character ${i}:`);
        console.log('    source   : ' + JSON.stringify(a.text.slice(Math.max(0, i - 80), i + 80)));
        console.log('    generated: ' + JSON.stringify(b.text.slice(Math.max(0, i - 80), i + 80)));
        break;
      }
    }
  }
  if (SELFTEST) {
    console.log(same ? '\nSELFTEST FAILED: a deleted declaration changed nothing, so this gate is decorative'
                     : '\nSELFTEST OK: one deleted declaration turns it red');
    process.exit(same ? 1 : 0);
  }
  console.log(same ? '\nCSS EQUIVALENCE OK: the browser parses both into exactly the same stylesheet'
                   : '\nCSS EQUIVALENCE FAILURES: 1');
  process.exit(same ? 0 : 1);
} finally { server.close(); }
