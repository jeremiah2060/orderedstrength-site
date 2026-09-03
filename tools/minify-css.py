#!/usr/bin/env python3
"""Generate the stylesheet the browser gets, from the stylesheet a person edits.

WHY THIS EXISTS, WITH THE MEASUREMENT THAT DECIDED IT. assets/site.css is 96,745 bytes and 58%
of it is comment, because the comments in this repo are the documentation: they carry the laws,
the CDP measurements and the reasons a breakpoint is the number it is. That is right for the
source and wrong for the wire, and the stylesheet is render-blocking, so every first visit pays
for it before anything paints. Measured with brotli at quality 11, which is what Cloudflare
serves: 26,918 bytes as published, 7,813 with the comments removed. 19,105 bytes, 71%, off the
critical path of every first visit.

🔒 IT REMOVES COMMENTS AND BLANK LINES AND NOTHING ELSE. No shorthand collapsing, no selector
merging, no colour rewriting, no newline stripping. Every one of those is a transformation that
can change rendering, and brotli already recovers most of what they would save: the conservative
pass is within a kilobyte of an aggressive one after compression, at a fraction of the risk.

🔒 AND THE STRIPPER IS STRING-AWARE, WHICH IS NOT A DETAIL HERE. A naive `/\\*.*?\\*/` pass would
be correct on almost any stylesheet and wrong on this one: --grain holds an SVG data URI and
several rules hold quoted content, and eating a `/*` that lives inside a string truncates a
declaration into something that still parses. The kind of break that renders.

🔒 WHY IT IS A SECOND FILE AND NOT AN EDIT IN PLACE. Cloudflare Pages serves this repository as
it stands, with no build step, so the file in git is the file on the wire. Minifying in place
would delete the laws; renaming the source would leave `assets/site.css` reading as soup to the
next person who opens it. So `assets/site.css` stays the file a human edits and reads, every
source gate keeps reading it, and the pages link the generated twin. Drift is impossible rather
than unlikely: --check regenerates and byte-compares, and it runs in check.sh.

    python3 tools/minify-css.py            write assets/site.min.css
    python3 tools/minify-css.py --check    fail if it is not what the source generates
    python3 tools/minify-css.py --selftest
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets/site.css')
OUT = os.path.join(ROOT, 'assets/site.min.css')
BANNER = "/* GENERATED from assets/site.css by tools/minify-css.py. Do not edit: check.sh regenerates\n   this file and byte-compares it. The comments, and every law in them, live in the source. */\n"


def strip(css):
    """Remove /* */ comments and the blank lines they leave. Quotes are tracked so a comment
    opener inside a string or a data URI is text, not a comment."""
    out, i, n, quote = [], 0, len(css), None
    while i < n:
        c = css[i]
        if quote:
            out.append(c)
            if c == '\\' and i + 1 < n:
                out.append(css[i + 1]); i += 2; continue
            if c == quote: quote = None
            i += 1; continue
        if c in '"\'':
            quote = c; out.append(c); i += 1; continue
        if c == '/' and i + 1 < n and css[i + 1] == '*':
            j = css.find('*/', i + 2)
            i = (j + 2) if j >= 0 else n
            continue
        out.append(c); i += 1
    t = ''.join(out)
    t = re.sub(r'[ \t]+\n', '\n', t)
    t = re.sub(r'\n{2,}', '\n', t)
    return t.strip() + '\n'


def build(check=False, src=SRC, out=OUT):
    want = BANNER + strip(open(src, encoding='utf-8').read())
    have = open(out, encoding='utf-8').read() if os.path.exists(out) else None
    if have == want:
        print(f"  {os.path.relpath(out, ROOT)} is exactly what {os.path.relpath(src, ROOT)} generates"
              f"  ({len(want)} bytes from {os.path.getsize(src)})")
        return 0
    if check:
        if have is None:
            print(f"  {os.path.relpath(out, ROOT)} does not exist; the pages link a file that is not there")
        else:
            print(f"  {os.path.relpath(out, ROOT)} is {len(have)} bytes, the source generates {len(want)}: "
                  "it is stale, so the site is serving CSS that is not this source")
        return 1
    open(out, 'w', encoding='utf-8').write(want)
    print(f"  wrote {os.path.relpath(out, ROOT)}: {os.path.getsize(src)} bytes of source to {len(want)}")
    return 0


def selftest():
    import tempfile
    ok = True
    cases = [
        ('a comment goes',                 'a{color:red}/* gone */\nb{color:blue}',      'a{color:red}\nb{color:blue}'),
        ('a comment INSIDE a string stays', 'a{content:"/* not a comment */"}',           'a{content:"/* not a comment */"}'),
        ('a data URI with slashes survives', "a{background:url(\"data:image/svg+xml,%3Csvg/%3E\")}", "a{background:url(\"data:image/svg+xml,%3Csvg/%3E\")}"),
        ('an escaped quote does not end the string', r'a{content:"\" /* x */"}',          r'a{content:"\" /* x */"}'),
        ('an unterminated comment eats to the end',  'a{color:red}/* oops',               'a{color:red}'),
    ]
    for name, src, want in cases:
        got = strip(src).strip()
        good = got == want.strip()
        ok &= good
        print(f"  {'PASS' if good else 'FAIL'}  {name}")
        if not good: print(f"        wanted {want.strip()!r}\n        got    {got!r}")
    with tempfile.TemporaryDirectory() as d:
        s, o = os.path.join(d, 's.css'), os.path.join(d, 'o.css')
        open(s, 'w').write('a{color:red}/* c */')
        r1 = build(check=True, src=s, out=o)
        print(f"  {'PASS' if r1 == 1 else 'FAIL'}  --check is RED when the generated file is missing")
        ok &= r1 == 1
        build(src=s, out=o)
        r2 = build(check=True, src=s, out=o)
        print(f"  {'PASS' if r2 == 0 else 'FAIL'}  --check is GREEN once it is generated")
        ok &= r2 == 0
        open(s, 'a').write('\nb{color:blue}')
        r3 = build(check=True, src=s, out=o)
        print(f"  {'PASS' if r3 == 1 else 'FAIL'}  --check is RED again when the source moves under it")
        ok &= r3 == 1
    return ok


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        print('MINIFY SELFTEST')
        good = selftest()
        print('SELFTEST OK' if good else 'SELFTEST FAILED')
        sys.exit(0 if good else 1)
    check = '--check' in sys.argv
    print('MINIFY: the stylesheet the browser gets' if check else 'MINIFY: generating')
    rc = build(check=check)
    print('MINIFY OK' if rc == 0 else 'MINIFY FAILURES: 1')
    sys.exit(rc)
