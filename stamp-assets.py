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
# 🔒 TWO LEVELS DEEP, BECAUSE THE SPANISH SUBPAGES LIVE THERE. This globbed `*/index.html`
# only, so every page under es/<name>/ was invisible to the stamper: /es/join/, /es/verify/,
# /es/terms/ and five more. They carried whatever asset version the English skeleton had at
# the moment they were built, and _headers caches /assets/* for an hour, which is the exact
# stale-pairing failure this whole file exists to make impossible.
# 🔒 `es/404.html` MATCHED NONE OF THESE PATTERNS AND SO WAS GATED BY NOTHING.
# `*.html` is root-only, `*/index.html` and `*/*/index.html` both require the name
# `index.html`. A locale's 404 page is the one file that is neither, so it silently sat
# outside every source gate: on 2026-09-01 it was found carrying a duplicated hreflang
# trio, a relative og:image pointing at the ENGLISH share card, no og:locale and no terms
# link, every one of which had been fixed on all nineteen of its siblings. A page nothing
# reads is not a page with no defects. `*/*.html` closes it; the set dedupes the overlap.

# `tools/` holds GENERATOR INPUTS, not published pages: tools/og.html is the share-card
# template and is rendered to a JPEG, never served. Widening the glob to reach es/404.html
# swept it in, and gating a template as though it were a page is how a gate earns the
# reputation that gets it switched off.
PAGES = sorted(p for p in set(glob.glob('*.html') + glob.glob('*/*.html')
                    + glob.glob('*/*/index.html'))
                    if not p.startswith(('tools/', 'assets/')))
for f in PAGES:
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
for f in PAGES:
    s = src = open(f, encoding='utf-8').read()
    # 🔒 THIS MATCHED `<b class="stamp">` AND THE MARKUP IS `<b class="stamp" translate="no">`.
    # The attribute arrived with the Spanish site (commit ac716f4, "Seven gates were green while
    # every non-English reader got a broken page"), and from that moment this substitution
    # matched nothing on any page. It reported "written into 0 page(s)" every run, which is also
    # what a no-op run correctly prints, so the number never looked wrong.
    s = re.sub(r'(<b class="stamp"[^>]*>)[^<]*(</b>)', r'\g<1>' + build + r'\g<2>', s)
    if s != src:
        open(f, 'w', encoding='utf-8').write(s); stamped_build += 1
# The footer display was removed 2026-09-01; this substitution is kept so a page that
# still carries one cannot drift, and it now reports honestly when there are none.
print(f"build stamp {build} written into {stamped_build} page(s)"
      if stamped_build else f"build {build} (no page displays it, by design)")

print(f"stamped {len(assets)} assets into {changed} page(s)")
for a, v in assets.items(): print(f"  {a}?v={v}")
