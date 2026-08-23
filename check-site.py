#!/usr/bin/env python3
"""Structural checks that a browser screenshot cannot give you, and one that keeps
biting: a rule edited in the SHARED stylesheet does nothing when the same selector
also lives in a page's own <style>, because the page block loads last and wins.
That mistake cost three separate rounds (.stack overflow, .dialhead cap, ol.loop
centring): each time the edit looked applied and changed nothing."""
import re, glob, sys

def selectors(css):
    """Selectors declared in a stylesheet.

    🔒 STRIP @media WRAPPERS FIRST. A naive ([^{}]+)\{([^{}]*)\} sweep cannot parse a
    nested block: it swallows the @media prelude and everything after it silently, so
    the checker skipped real rules and reported a clean sheet. It missed .stack being
    capped at 23rem in a page style while the shared sheet said 100%, which is the exact
    defect class this file exists to catch. Found 2026-08-23 by measuring a card that
    would not stretch."""
    # 🔒 STRIP COMMENTS FIRST. A rule preceded by a /* comment */ parses as the selector
    # "/* comment */\n.stack", which matches nothing, so the rule is invisible to the
    # comparison. The very comment I wrote to explain a rule is what hid it. Measured
    # 2026-08-23: .stack was capped at 23rem in a page style while the shared sheet said
    # 100%, and the checker reported a clean sheet.
    flat = re.sub(r'/\*.*?\*/', ' ', css, flags=re.S)
    for _ in range(6):
        flat = re.sub(r'@[a-z-]+[^{}]*\{((?:[^{}]|\{[^{}]*\})*)\}', r'\1', flat)
    out = set()
    for sel, _decl in re.findall(r'([^{}]+)\{([^{}]*)\}', flat):
        for part in sel.split(','):
            part = part.strip()
            if part and not part.startswith('@'):
                out.add(part)
    return out

pages = sorted(glob.glob('*.html') + glob.glob('*/index.html'))
shared = open('assets/site.css', encoding='utf-8').read()
shared_sel = selectors(shared)
fail = 0

print("SHADOWED SELECTORS (page style beats the shared sheet)")
for f in pages:
    s = open(f, encoding='utf-8').read()
    for blk in re.findall(r'<style[^>]*>(.*?)</style>', s, re.S):
        for sel in sorted(selectors(blk) & shared_sel):
            print(f"  {f}: {sel}"); fail += 1
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
