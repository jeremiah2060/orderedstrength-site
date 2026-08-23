#!/usr/bin/env python3
"""Contrast, computed rather than eyeballed.

A dark palette is exactly where designers get this wrong, because low-contrast text LOOKS
tasteful on a black screen in a dark room and is unreadable on a phone in daylight. This
round moved every neutral in the stylesheet, so every ink-on-surface pair is recomputed
here against WCAG 2.1, and the build fails if one drops below its threshold.

The pairs are read OUT OF the stylesheet's own :root block, so a token edited tomorrow is
checked tomorrow without anyone remembering to update a list."""
import re, sys, itertools

CSS = open('assets/site.css', encoding='utf-8').read()
root = re.search(r':root\{(.*?)\n\}', CSS, re.S)
if not root:
    print("could not find :root"); sys.exit(2)
TOK = dict(re.findall(r'(--[a-z0-9-]+)\s*:\s*([^;]+);', root.group(1)))

def resolve(v, depth=0):
    v = v.strip()
    if depth > 6: return v
    m = re.fullmatch(r'var\((--[a-z0-9-]+)\)', v)
    return resolve(TOK[m.group(1)], depth + 1) if m and m.group(1) in TOK else v

def parse(v):
    v = resolve(v)
    m = re.fullmatch(r'#([0-9a-fA-F]{6})', v)
    if m:
        h = m.group(1); return (int(h[0:2],16), int(h[2:4],16), int(h[4:6],16), 1.0)
    m = re.fullmatch(r'rgba?\(([^)]+)\)', v)
    if m:
        p = [x.strip() for x in m.group(1).split(',')]
        return (float(p[0]), float(p[1]), float(p[2]), float(p[3]) if len(p) > 3 else 1.0)
    return None

def over(fg, bg):
    """fg composited onto an opaque bg."""
    a = fg[3]
    return tuple(fg[i] * a + bg[i] * (1 - a) for i in range(3))

def lum(c):
    def ch(x):
        x /= 255.0
        return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(x) for x in c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def ratio(fg, bg):
    a, b = lum(fg), lum(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)

SURFACES = ['--e0', '--e1', '--e2', '--e3', '--e4']
# (token, minimum, what it is used for). Thresholds are WCAG 2.1 AA: 4.5 for body text,
# 3.0 for text at 18.66px bold or 24px regular, and for meaningful non-text marks.
INKS = [('--ink', 4.5, 'headings and body'),
        ('--ink2', 4.5, 'body copy'),
        ('--ink3', 4.5, 'captions and legends'),
        ('--teal', 3.0, 'the signal, used large or as a mark'),
        ('--amber', 3.0, 'the broken-seal signal'),
        ('--red', 3.0, 'failure state'),
        ('--stone', 3.0, 'population tag'),
        ('--azure', 3.0, 'building tag')]

fail = 0
print(f"{'ink':10} {'on':7} {'ratio':>7}  {'min':>4}   used for")
for ink, need, why in INKS:
    fgv = parse(TOK.get(ink, ''))
    if fgv is None:
        print(f"  ?? cannot parse {ink}"); fail += 1; continue
    for surf in SURFACES:
        bgv = parse(TOK.get(surf, ''))
        if bgv is None: continue
        r = ratio(over(fgv, bgv[:3]), bgv[:3])
        bad = r < need
        fail += bad
        print(f"{ink:10} {surf:7} {r:7.2f}  {need:4.1f}   {'FAIL  ' if bad else '      '}{why}")

print(f"\nCONTRAST FAILURES: {fail}")
sys.exit(1 if fail else 0)
