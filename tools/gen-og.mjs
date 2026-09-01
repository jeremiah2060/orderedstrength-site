#!/usr/bin/env node
/* Render the share cards, both locales. Run after any brand change:
 *     python3 -m http.server 8899 &   node tools/gen-og.mjs
 *
 * 🔒 THIS WROTE assets/og.png AND EVERY PAGE REFERENCES assets/og.jpg. There was no conversion
 * step and never had been, so the generator's output was not the artefact the site serves: the
 * published card could not be updated by running the tool built to update it. Found 2026-09-01
 * alongside the two dead screenshot paths in og.html. It now writes the .jpg the pages name, and
 * asserts the file it produced is the file they reference.
 */
import { withPage } from './measure.mjs';
import { existsSync, statSync, unlinkSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';

const BASE = process.env.BASE || 'http://127.0.0.1:8899';

async function card(lang, out) {
  await withPage(async page => {
    await page.goto(`${BASE}/tools/og.html${lang === 'es' ? '?lang=es' : ''}`);
    await page.evaluate(`(async()=>{await document.fonts.ready;
       await Promise.all([...document.images].map(i=>i.complete?0:new Promise(r=>{i.onload=i.onerror=r})));
       return 1;})()`);
    await page.evaluate('new Promise(r=>setTimeout(r,400))');
    await page.shot(out + '.png');
  }, { width: 1200, height: 630, dsf: 1 });
  // sips ships with macOS; no dependency to install, same principle as tools/ocr.swift.
  execFileSync('sips', ['-s', 'format', 'jpeg', '-s', 'formatOptions', '82',
                        out + '.png', '--out', out + '.jpg'], { stdio: 'ignore' });
  unlinkSync(out + '.png');
  console.log(`${out}.jpg written  (${statSync(out + '.jpg').size} bytes)`);
}

await card('en', 'assets/og');
await card('es', 'assets/og-es');

// 🔒 PROVE THE OUTPUT IS WHAT THE PAGES ASK FOR, rather than trusting the filename above.
let bad = 0;
for (const [page, want] of [['index.html', '/assets/og.jpg'], ['es/index.html', '/assets/og-es.jpg']]) {
  const html = readFileSync(page, 'utf8');
  const ok = html.includes(want) && existsSync('.' + want);
  if (!ok) { console.error(`MISMATCH: ${page} does not reference an existing ${want}`); bad++; }
}
process.exit(bad ? 1 : 0);
