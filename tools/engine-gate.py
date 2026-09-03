#!/usr/bin/env python3
"""EVERY GATE IN THIS REPO DRIVES CHROME. This one asks what the other engines get.

WHY THIS EXISTS (CEO, 2026-09-03): "he was also fixing the site so it can look great in all
devices not just iOS, but all of them and look exactly the same in all browsers."

🔒 SEVENTEEN GATES, ONE ENGINE. measure.mjs launches /Applications/Google Chrome.app and every
browser-driven check here is built on it: align, measure, type, type-floor, hero, lang-redirect,
lang-switch. They sweep width, and since 2026-09-02 height, and they have never once varied the
thing most likely to differ. This repo has already learned that lesson on the height axis, in
those words: "EVERY GATE IN THIS REPO VARIED WIDTH AND FIXED HEIGHT... a whole axis went
untested, and that is why the site looked right on every machine here and broken on a Windows
laptop." The engine is the same shape of hole.

WHY IT IS SOURCE-LEVEL AND NOT A SECOND BROWSER. Driving Safari needs `safaridriver --enable`,
which asks for an administrator password and is therefore not something a gate can arrange, and
vendoring a WebKit build would trade this harness's one real virtue, that it has no dependencies
beyond a browser already on the machine. So this checks the DISCIPLINE that makes a Chrome-only
harness safe, which is the thing that can actually rot:

  ARM 1  A CHROME-FIRST FEATURE IS DECLARED INSIDE AN @supports THAT TESTS IT. The site already
         does this correctly for scroll-driven animations, and the rule's own comment says why:
         "without it, a browser that does not know animation-timeline would run these keyframes
         once against the document timeline." That is the failure mode. An unsupported TIMELINE
         does not disable an animation, it re-points it at the document clock, so the page plays
         its whole reveal in the first second and then sits still. Silent in Chrome, wrong
         everywhere else.

  ARM 2  AND A GUARDED FEATURE HAS AN UNGUARDED FALLBACK. A guard alone is only half: it stops
         the wrong thing happening and puts nothing in its place. Every @supports that gates a
         visual feature must have a matching `@supports not (...)` or the property must be one
         whose absence changes nothing.

  ARM 3  A PREFIXED PROPERTY KEEPS ITS PAIR. mask and mask-composite carry -webkit- twins here
         because WebKit needed them, and a later edit that touches one line and not the other
         removes a whole ring from one engine and nothing from the other.

🔒 EXEMPTIONS ARE BY NAME AND CARRY THEIR REASON, never by pattern. type-floor-gate learned that
one first. text-wrap:balance is exempt because a browser that does not know it wraps the heading
normally, which is the design's own starting point, not a broken state.

    python3 tools/engine-gate.py [--selftest]
"""
import re, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Chrome-first, and what a browser without it actually DOES. The second field is the whole
# argument for whether a guard is required.
CHROME_FIRST = {
    'animation-timeline': 'the animation re-points at the document clock and plays once, immediately',
    'scroll-timeline':    'the animation re-points at the document clock and plays once, immediately',
    'timeline-scope':     'the named timeline does not resolve and its animation falls to the document clock',
    'field-sizing':       'the control keeps its default width',
    'anchor-name':        'the anchored element positions against its containing block instead',
    'position-anchor':    'the anchored element positions against its containing block instead',
}

# Named, with the reason, because a pattern would have swallowed the ones above.
HARMLESS = {
    'text-wrap': 'a browser without it wraps the heading normally, which is the design starting point',
}

PREFIX_PAIRS = [('mask', '-webkit-mask'), ('mask-composite', '-webkit-mask-composite')]


def rules(css):
    """Walk declarations while tracking which @supports conditions are open above them.
    A brace scan rather than a parser: this stylesheet is hand-written and nests at-rules
    only, so depth is enough, and a dependency to read one file is not worth it."""
    out, stack, i, n = [], [], 0, len(css)
    css = re.sub(r'/\*.*?\*/', lambda m: ' ' * len(m.group(0)), css, flags=re.S)
    buf, start = '', 0
    while i < n:
        c = css[i]
        if c == '{':
            head = buf.strip()
            stack.append(head)
            buf, start = '', i + 1
        elif c == '}':
            for decl in buf.split(';'):
                if ':' in decl:
                    out.append((decl.strip(), list(stack), start))
            stack.pop() if stack else None
            buf, start = '', i + 1
        else:
            buf += c
            if c == ';' and stack:
                for decl in buf.split(';'):
                    if ':' in decl:
                        out.append((decl.strip(), list(stack), start))
                buf = ''
        i += 1
    return out


def audit(css, label='assets/site.css', verbose=True):
    iss = []
    decls = rules(css)

    # ARM 1
    for decl, stack, _ in decls:
        prop = decl.split(':', 1)[0].strip().lower()
        if prop not in CHROME_FIRST:
            continue
        guarded = any(a.lower().startswith('@supports') and prop in a.lower()
                      and not re.search(r'@supports\s+not\b', a, re.I) for a in stack)
        if not guarded:
            iss.append(f'{prop} declared with no @supports that tests it; '
                       f'without it {CHROME_FIRST[prop]}')

    # ARM 2
    positive = {a for _, stack, _ in decls for a in stack
                if a.lower().startswith('@supports') and not re.search(r'@supports\s+not\b', a, re.I)}
    negative_src = ' '.join(re.findall(r'@supports\s+not\s*\(([^)]*\)?[^{]*)', css, re.I)).lower()
    for cond in positive:
        feat = re.search(r'\(([a-z-]+)\s*:', cond)
        if not feat:
            continue
        f = feat.group(1)
        if f in HARMLESS:
            continue
        if f not in negative_src:
            iss.append(f'@supports ({f}: ...) has no matching "@supports not" fallback, '
                       f'so an engine without it gets the guard and no replacement')

    # ARM 3
    for plain, pref in PREFIX_PAIRS:
        a = len(re.findall(r'(?<![-\w])' + re.escape(plain) + r'\s*:', css))
        b = len(re.findall(re.escape(pref) + r'\s*:', css))
        if a and b < a:
            iss.append(f'{plain} appears {a} time(s) but {pref} only {b}: '
                       f'a WebKit reader loses what the unprefixed line draws')

    if verbose:
        print(f"  {label:28} {'OK' if not iss else ''}")
        for i2 in iss:
            print(f"      {i2}")
    return len(iss)


def selftest():
    """🔒 NAME THE INPUT THAT TURNS EACH ARM RED. A gate that has only ever been green against
    the file it was written for has not been tested, it has been observed."""
    cases = [
        ('guarded animation-timeline with a fallback',
         '@supports (animation-timeline:view()){.a{animation-timeline:view()}}'
         '@supports not (animation-timeline:view()){.a{opacity:1}}', 0),
        ('animation-timeline with NO guard at all',
         '.a{animation:x linear both;animation-timeline:view()}', 1),
        ('guarded, but nothing put in its place',
         '@supports (animation-timeline:view()){.a{animation-timeline:view()}}', 1),
        ('mask without its webkit twin',
         '.a{mask:linear-gradient(#000 0 0);mask-composite:exclude}', 2),
        ('mask with its webkit twin',
         '.a{-webkit-mask:linear-gradient(#000 0 0);mask:linear-gradient(#000 0 0);'
         '-webkit-mask-composite:xor;mask-composite:exclude}', 0),
        ('text-wrap is exempt by name, and says why',
         '@supports (text-wrap:balance){h1{text-wrap:balance}}', 0),
    ]
    ok = True
    for name, css, want in cases:
        got = audit(css, verbose=False)
        good = got == want
        ok &= good
        print(f"  {'PASS' if good else 'FAIL'}  expected {want} issue(s), got {got}   {name}")
    return ok


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        print("ENGINE GATE SELFTEST")
        good = selftest()
        print("SELFTEST OK" if good else "SELFTEST FAILED")
        sys.exit(0 if good else 1)
    print("ENGINE: what a browser that is not Chrome gets")
    total = audit(open(os.path.join(ROOT, 'assets/site.css'), encoding='utf-8').read())
    # 🔒 AND THE PAGES' OWN <style> BLOCKS, which is where check-site.py already found a rule
    # silently shadowing the shared sheet. A stylesheet-only reading of this repo is a reading
    # of most of it, and "most" is the word that made every other blind spot here.
    import glob
    for pat in ('*.html', '*/index.html', '*/*/index.html'):
        for f in sorted(glob.glob(os.path.join(ROOT, pat))):
            if '/assets/' in f or '/tools/' in f:
                continue
            src = open(f, encoding='utf-8').read()
            blocks = '\n'.join(re.findall(r'<style[^>]*>(.*?)</style>', src, re.S))
            if not blocks.strip():
                continue
            total += audit(blocks, os.path.relpath(f, ROOT) + ' <style>')
    print(f"\nENGINE {'OK' if not total else 'FAILURES: %d' % total}")
    sys.exit(1 if total else 0)
