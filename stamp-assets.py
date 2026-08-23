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
for img in (sorted(glob.glob('assets/shots/*.png')) + sorted(glob.glob('assets/shots/*.jpg'))
            + sorted(glob.glob('assets/shots/*.webp'))):
    assets['/' + img] = h(img)
changed = 0
for f in glob.glob('*.html') + glob.glob('*/index.html'):
    s = src = open(f, encoding='utf-8').read()
    for a, v in assets.items():
        s = re.sub(re.escape(a) + r'(\?v=[0-9a-f]+)?', f'{a}?v={v}', s)
    if s != src:
        open(f, 'w', encoding='utf-8').write(s); changed += 1
# THE BUILD STAMP. The footer prints which build of this site you are looking at, and it is
# not a number anyone types: it is the content hash of the stylesheet, the same value that
# versions the asset URL. If the page changed, the stamp changed, and you can check it.
build = assets['/assets/site.css']
stamped_build = 0
for f in glob.glob('*.html') + glob.glob('*/index.html'):
    s = src = open(f, encoding='utf-8').read()
    s = re.sub(r'(<b class="stamp">)[^<]*(</b>)', r'\g<1>' + build + r'\g<2>', s)
    if s != src:
        open(f, 'w', encoding='utf-8').write(s); stamped_build += 1
print(f"build stamp {build} written into {stamped_build} page(s)")

print(f"stamped {len(assets)} assets into {changed} page(s)")
for a, v in assets.items(): print(f"  {a}?v={v}")
