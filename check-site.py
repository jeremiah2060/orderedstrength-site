#!/usr/bin/env python3
"""Structural checks that a browser screenshot cannot give you, and one that keeps
biting: a rule edited in the SHARED stylesheet does nothing when the same selector
also lives in a page's own <style>, because the page block loads last and wins.
That mistake cost three separate rounds (.stack overflow, .dialhead cap, ol.loop
centring): each time the edit looked applied and changed nothing."""
import re, glob, sys

pages = sorted(glob.glob('*.html') + glob.glob('*/index.html'))
shared = open('assets/site.css', encoding='utf-8').read()
shared_sel = {s.strip() for s, _ in re.findall(r'([^{}]+)\{([^{}]*)\}', shared)}
fail = 0

print("SHADOWED SELECTORS (page style beats the shared sheet)")
for f in pages:
    s = open(f, encoding='utf-8').read()
    for blk in re.findall(r'<style[^>]*>(.*?)</style>', s, re.S):
        for sel, _ in re.findall(r'([^{}]+)\{([^{}]*)\}', blk):
            if sel.strip() in shared_sel:
                print(f"  {f}: {sel.strip()}"); fail += 1
print("  none" if not fail else "")

print("\nSTRUCTURE")
for f in pages:
    s = open(f, encoding='utf-8').read()
    body = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', s, flags=re.S)
    iss = []
    for t in ['div','section','ul','ol','li','p','h1','h2','h3','dl','main','footer','nav']:
        o = len(re.findall(r'<' + t + r'[\s>]', body)); c = len(re.findall(r'</' + t + r'>', body))
        if o != c: iss.append(f'{t} {o}/{c}')
    ids = re.findall(r'id="([^"]+)"', s)
    if [i for i in set(ids) if ids.count(i) > 1]: iss.append('duplicate ids')
    if [a[1:] for a in re.findall(r'href="(#[^"]+)"', s) if a[1:] not in ids]: iss.append('dead anchor')
    if [r for r in re.findall(r'(?:href|src)="(/assets/[^"]*)"', s) if '?v=' not in r]: iss.append('unversioned asset')
    if 'scene narrow' in s: iss.append('stale narrow width')
    if any(s.count(ch) for ch in ['—', '×', '→']): iss.append('banned symbol')
    print(f"  {f:28} {'OK' if not iss else '; '.join(iss)}")
    fail += len(iss)

print(f"\nFAILURES: {fail}")
sys.exit(1 if fail else 0)
