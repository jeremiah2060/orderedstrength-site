#!/usr/bin/env python3
"""Stamp a content hash onto every /assets/ reference in every page.

WHY THIS EXISTS. _headers caches /assets/* for an hour. The pages referenced
/assets/site.css with no version, so a returning visitor paired an HOUR-OLD
stylesheet with freshly deployed HTML and saw a mangled layout. Server correct,
browser correct, pairing wrong. A content hash in the URL makes a changed file a
changed URL, so a stale pairing becomes impossible rather than unlikely.
"""
import hashlib, re, glob, sys

def h(path):
    return hashlib.sha256(open(path,'rb').read()).hexdigest()[:10]

assets = {'/assets/site.css': h('assets/site.css'), '/assets/site.js': h('assets/site.js')}
for img in sorted(glob.glob('assets/shots/*.png')) + sorted(glob.glob('assets/shots/*.jpg')):
    assets['/' + img] = h(img)
changed = 0
for f in glob.glob('*.html') + glob.glob('*/index.html'):
    s = src = open(f, encoding='utf-8').read()
    for a, v in assets.items():
        s = re.sub(re.escape(a) + r'(\?v=[0-9a-f]+)?', f'{a}?v={v}', s)
    if s != src:
        open(f, 'w', encoding='utf-8').write(s); changed += 1
print(f"stamped {len(assets)} assets into {changed} page(s)")
for a, v in assets.items(): print(f"  {a}?v={v}")
