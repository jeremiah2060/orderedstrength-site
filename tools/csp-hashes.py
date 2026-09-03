#!/usr/bin/env python3
"""Put every inline script's hash in the CSP so the policy can stop trusting inline script.

WHY THIS EXISTS. `script-src 'self' 'unsafe-inline'` is the one line in `_headers` that undoes
most of what the rest of that file buys: it tells a browser to execute any <script> that appears
in the markup, which is precisely the payload an injection delivers. Naming each script by the
SHA-256 of its body means the browser runs the eight blocks this site actually ships and refuses
anything else, including a block that is byte-identical to one of ours except for one character.

🔒 style-src KEEPS 'unsafe-inline', AND THAT IS A MEASUREMENT, NOT AN OVERSIGHT. There are 83
inline `style="..."` attributes across these pages, most of them the callout pins that position
themselves over a photograph by percentage. A CSP hash cannot name an attribute: CSP 3 would need
'unsafe-hashes', which re-allows every inline handler as a side effect and is worse than what it
replaces. Scripts are where injection executes; a style attribute is a far narrower door. So this
hardens the directive the handoff named, script-src, and says plainly that the other one stands.

🔒 AND A STALE HASH KILLS A SCRIPT SILENTLY, WHICH IS THE FAILURE MODE THIS REPO HAS ALREADY
SHIPPED ONCE. check-site.py's own comment records it: "A BROKEN INLINE SCRIPT IS INVISIBLE TO
EVERY SOURCE GATE. A duplicated catch killed the language script on all ten English pages;
nesting, hygiene, stamp, contrast, type, align and measure all passed." A hash that no longer
matches produces exactly that page, and `node --check` will happily parse a script the browser
was told not to run. So this ships with two checks and neither is optional: `--check` proves
`_headers` names every script in the tree, and tools/csp-gate.mjs serves the site under the real
policy and asserts the scripts RAN.

    python3 tools/csp-hashes.py            rewrite _headers from the pages
    python3 tools/csp-hashes.py --check    fail if _headers is out of date
    python3 tools/csp-hashes.py --selftest
"""
import re, sys, os, glob, hashlib, base64

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEADERS = os.path.join(ROOT, '_headers')


def pages(root=ROOT):
    """🔒 DERIVED, NEVER TYPED, and the first draft of this function missed es/404.html because
    its globs were the ones copied from check-site.py, which walks `*/index.html` and never
    `*/*.html`. A page list that is wrong by one is a policy that kills one page."""
    out = []
    for pat in ('*.html', '*/*.html', '*/index.html', '*/*/index.html'):
        out += glob.glob(os.path.join(root, pat))
    return sorted(set(p for p in out if '/assets/' not in p and '/tools/' not in p))


def inline_scripts(src):
    return [m.group(2) for m in re.finditer(r'<script\b([^>]*)>(.*?)</script>', src, re.S)
            if 'src=' not in m.group(1)]


def hashes(root=ROOT):
    """Distinct, sorted, so the header is stable across runs and a diff shows real movement."""
    out = {}
    for p in pages(root):
        for body in inline_scripts(open(p, encoding='utf-8').read()):
            h = 'sha256-' + base64.b64encode(hashlib.sha256(body.encode()).digest()).decode()
            out.setdefault(h, []).append(os.path.relpath(p, root))
    return dict(sorted(out.items()))


SCRIPT_SRC = re.compile(r"script-src [^;]*;")


def rewrite(check=False, root=ROOT, headers=None):
    headers = headers or HEADERS
    hs = hashes(root)
    want = "script-src 'self' " + ' '.join(f"'{h}'" for h in hs) + ';'
    src = open(headers, encoding='utf-8').read()
    have = SCRIPT_SRC.search(src)
    if not have:
        print('  no script-src directive in _headers'); return 1
    if have.group(0) == want:
        print(f"  _headers names all {len(hs)} inline script(s), and nothing else"); return 0
    if check:
        cur = set(re.findall(r"'(sha256-[A-Za-z0-9+/=]+)'", have.group(0)))
        missing = [h for h in hs if h not in cur]
        extra = [h for h in cur if h not in hs]
        if "'unsafe-inline'" in have.group(0):
            print("  script-src still carries 'unsafe-inline'")
        for h in missing:
            print(f"  NOT IN THE POLICY: {h}  ({', '.join(hs[h][:3])})  that script will not run")
        for h in extra:
            print(f"  stale hash, no script matches it: {h}")
        return 1
    open(headers, 'w', encoding='utf-8').write(SCRIPT_SRC.sub(want.replace('\\', '\\\\'), src, count=1))
    print(f"  script-src now names {len(hs)} inline script(s); 'unsafe-inline' is gone")
    return 0


def selftest():
    """🔒 NAME THE INPUT THAT TURNS --check RED. A policy generator that has only been run
    against the tree it was written for has been observed, not tested."""
    import tempfile, shutil
    ok = True
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, 'index.html'), 'w').write('<script>var a=1;</script>')
        hdr = os.path.join(d, '_headers')
        open(hdr, 'w').write("/*\n  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; font-src 'self'\n")
        r1 = rewrite(check=True, root=d, headers=hdr)
        print(f"  {'PASS' if r1 == 1 else 'FAIL'}  --check is RED while 'unsafe-inline' stands")
        ok &= r1 == 1
        rewrite(root=d, headers=hdr)
        r2 = rewrite(check=True, root=d, headers=hdr)
        print(f"  {'PASS' if r2 == 0 else 'FAIL'}  --check is GREEN once the hash is written")
        ok &= r2 == 0
        open(os.path.join(d, 'other.html'), 'w').write('<script>var b=2;</script>')
        r3 = rewrite(check=True, root=d, headers=hdr)
        print(f"  {'PASS' if r3 == 1 else 'FAIL'}  --check goes RED again when a page adds a script")
        ok &= r3 == 1
        body = open(hdr).read()
        print(f"  {'PASS' if 'unsafe-inline' not in body.split('style-src')[0] else 'FAIL'}"
              "  and 'unsafe-inline' is not left behind in script-src")
        ok &= 'unsafe-inline' not in body.split('style-src')[0]
    return ok


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        print('CSP HASH SELFTEST')
        good = selftest()
        print('SELFTEST OK' if good else 'SELFTEST FAILED')
        sys.exit(0 if good else 1)
    check = '--check' in sys.argv
    print('CSP: every inline script named by hash' if check else 'CSP: writing script-src hashes')
    rc = rewrite(check=check)
    print('CSP HASHES OK' if rc == 0 else 'CSP HASHES FAILURES: 1')
    sys.exit(rc)
