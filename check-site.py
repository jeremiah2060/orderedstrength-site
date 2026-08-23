#!/usr/bin/env python3
"""Structural checks that a browser screenshot cannot give you, and one that keeps
biting: a rule edited in the SHARED stylesheet does nothing when the same selector
also lives in a page's own <style>, because the page block loads last and wins.
That mistake cost three separate rounds (.stack overflow, .dialhead cap, ol.loop
centring): each time the edit looked applied and changed nothing."""
import re, glob, sys, os

SHORTHANDS = {
    'margin': ['margin-top','margin-right','margin-bottom','margin-left'],
    'padding': ['padding-top','padding-right','padding-bottom','padding-left'],
    'inset': ['top','right','bottom','left'],
    'background': ['background-color','background-image','background-size','background-position',
                   'background-repeat','background-attachment'],
    'border': ['border-width','border-style','border-color'],
    'border-radius': ['border-radius'],
    'font': ['font-family','font-size','font-weight','line-height'],
    'flex': ['flex-grow','flex-shrink','flex-basis'],
    'grid-area': ['grid-row','grid-column'],
    'transition': ['transition-property','transition-duration','transition-timing-function'],
    'animation': ['animation-name','animation-duration','animation-timing-function','animation-fill-mode'],
}

def props(decl):
    """The property names a declaration block sets, with shorthands expanded.

    🔒 THE SELECTOR IS NOT THE FAILURE; THE SELECTOR PLUS THE PROPERTY IS. Comparing
    selector names alone made this check fire on four rules that set entirely different
    properties in the two sheets, which is the fastest way to teach a person to ignore a
    gate. Expanding shorthands is not optional either: the one REAL collision the day this
    was written was a page saying `margin:0` against a shared sheet saying
    `margin-top:auto`, and a naive name comparison sees two different properties."""
    out = set()
    for line in decl.split(';'):
        if ':' not in line:
            continue
        name = line.split(':', 1)[0].strip().lower()
        if not name or name.startswith('--'):
            continue
        out.update(SHORTHANDS.get(name, [name]))
        if name in SHORTHANDS:
            out.add(name)
    return out


def rules(css):
    """(selector, properties) for every declaration in a stylesheet, @media unwrapped."""
    flat = re.sub(r'/\*.*?\*/', ' ', css, flags=re.S)
    for _ in range(6):
        flat = re.sub(r'@[a-z-]+[^{}]*\{((?:[^{}]|\{[^{}]*\})*)\}', r'\1', flat)
    for sel, decl in re.findall(r'([^{}]+)\{([^{}]*)\}', flat):
        pr = props(decl)
        if not pr:
            continue
        for part in sel.split(','):
            part = part.strip()
            if part and not part.startswith('@'):
                yield part, pr


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

shared_rules = {}
for sel, pr in rules(shared):
    shared_rules.setdefault(sel, set()).update(pr)

print("SHADOWED DECLARATIONS (a page style silently beats the shared sheet)")
for f in pages:
    s = open(f, encoding='utf-8').read()
    for blk in re.findall(r'<style[^>]*>(.*?)</style>', s, re.S):
        for sel, pr in rules(blk):
            clash = pr & shared_rules.get(sel, set())
            if clash:
                print(f"  {f}: {sel} {{ {', '.join(sorted(clash))} }}"); fail += 1
print("  none" if not fail else "")

print("\nNESTING")
# 🔒 A TAG-COUNT CHECK CANNOT SEE A MIS-NESTING, AND TWO OPPOSITE ERRORS CANCEL.
# This block used to count `<div` against `</div>` per page. /how-it-works had a .head
# that was never closed (so the four "moments" cards rendered INSIDE the centred 52rem
# header) AND a stray </div> in the last section. Open 6, close 6: the counter reported
# the page clean while the layout it was written to protect was visibly wrong. A stack
# tells you WHERE, and it is the only form of this check worth running.
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param',
        'source','track','wbr'}
TAG = re.compile(r'<(/?)([a-zA-Z][a-zA-Z0-9]*)([^>]*?)(/?)>')
for f in pages:
    s = open(f, encoding='utf-8').read()
    body = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', s, flags=re.S)
    body = re.sub(r'<!--.*?-->', '', body, flags=re.S)
    stack, iss = [], []
    for m in TAG.finditer(body):
        closing, name, attrs, selfclose = m.group(1), m.group(2).lower(), m.group(3), m.group(4)
        if name in VOID or selfclose or name == '!doctype':
            continue
        line = body[:m.start()].count('\n') + 1
        if not closing:
            stack.append((name, line))
        else:
            if not stack:
                iss.append(f'line {line}: </{name}> with nothing open'); continue
            if stack[-1][0] == name:
                stack.pop()
            elif any(n == name for n, _ in stack):
                while stack and stack[-1][0] != name:
                    n, l = stack.pop()
                    iss.append(f'line {line}: </{name}> closes <{n}> opened at line {l}')
                stack.pop()
            else:
                iss.append(f'line {line}: </{name}> with no matching open tag')
    for n, l in stack:
        if n not in ('html', 'body', 'head'):
            iss.append(f'<{n}> opened at line {l} is never closed')
    print(f"  {f:28} {'OK' if not iss else iss[0]}")
    for extra in iss[1:]:
        print(f"  {'':28} {extra}")
    fail += len(iss)

print("\nHYGIENE")
for f in pages:
    s = open(f, encoding='utf-8').read()
    iss = []
    ids = re.findall(r'id="([^"]+)"', s)
    if [i for i in set(ids) if ids.count(i) > 1]: iss.append('duplicate ids')
    if [a[1:] for a in re.findall(r'href="(#[^"]+)"', s) if a[1:] not in ids]: iss.append('dead anchor')
    # 🔒 FONTS ARE EXEMPT FROM VERSIONING, AND THE REASON IS NOT LAZINESS. A font file is
    # already content-addressed by its own name: family, weight and subset fully determine
    # its bytes. Worse, versioning it would DOUBLE-DOWNLOAD it, because the preload lives in
    # the HTML (which the stamper rewrites) while the src lives inside @font-face in the
    # stylesheet (which it does not), so the two URLs would disagree and the browser would
    # fetch the same glyphs twice. They are served immutable for a year instead.
    unversioned = [r for r in re.findall(r'(?:href|src)="(/assets/[^"]*)"', s)
                   if '?v=' not in r and not r.startswith('/assets/fonts/')]
    if unversioned: iss.append('unversioned asset: ' + unversioned[0])
    # ...but an asset that does not EXIST is the failure fonts actually risk: a typo in a
    # @font-face src or a preload is invisible, because the page simply falls back to a
    # system face and still looks like a website.
    missing = [r.split('?')[0] for r in re.findall(r'(?:href|src)="(/assets/[^"]*)"', s)
               if not os.path.exists('.' + r.split('?')[0])]
    if missing: iss.append('missing asset: ' + missing[0])
    if 'scene narrow' in s: iss.append('stale narrow width')
    if any(s.count(ch) for ch in ['\u2014', '\u00d7', '\u2192']): iss.append('banned symbol')
    for m in re.finditer(r'<img\b[^>]*>', s):
        if 'alt=' not in m.group(0): iss.append('img with no alt text')
    print(f"  {f:28} {'OK' if not iss else '; '.join(iss)}")
    fail += len(iss)

print(f"\nFAILURES: {fail}")
sys.exit(1 if fail else 0)
