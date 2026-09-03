#!/usr/bin/env python3
"""A page that IS a translation must refuse to be machine-translated. A page that is not, must not.

WHY THIS EXISTS (2026-09-03, the CEO, on his own phone). "if you switch to spanish it only
appears for a split second then goes back to english again, but all the screenshots are in
spanish, only the content is bouncing." Every one of the seventeen gates was green while he said
it, and the last clause is the whole diagnosis: text that changes while the images do not is not
a navigation and it is not this site. It is Chrome's translator, replaying the "always translate
Spanish" he turned on for /es/ on 2026-08-31, and nothing on the Spanish pages had ever told a
browser not to.

🔒 translate-gate.py GUARDS THE PIECES AND NOBODY GUARDED THE PAGE. That gate is right about
every element it names: a <code> run is a quotation from the app and a hex digest is not a word,
so both carry translate="no". It was written for a reader whose language we do not publish,
where a machine pass is the only version there is. It has no opinion about a page where a REAL
translation already exists one tap away, and on that page a machine pass can only subtract: it
rewrites the app strings shot-gate checks against the pixels, and it breaks the seal console's
fingerprint, so the page most committed to being checkable becomes the one that fails its own
check. The right answer there is not to guard the pieces. It is to decline.

🔒 AND IT HAS TO BE TWO-SIDED OR IT IS NOT A CHECK. "Everything declares notranslate" is a rule
this site must NOT satisfy: the English pages stay translatable on purpose, because for a reader
whose language we do not publish the machine is the only way in. So this asserts the declaration
on /es/ and its ABSENCE on the English pages, and it can go red in both directions. Run
--selftest to see each arm fail against a page built to break it.

    python3 tools/notranslate-gate.py [--selftest]
"""
import re, sys, glob, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 🔒 DERIVED FROM THE FILESYSTEM, NEVER TYPED. A hand-kept page list in this repo has been
# wrong twice (check.sh's align header said 7 pages for months while it walked 8), and a gate
# that misses a page reports the same clean line as a gate that checked it.
def pages():
    out = []
    for pat in ('*.html', '*/index.html', '*/*/index.html'):
        out += glob.glob(os.path.join(ROOT, pat))
    return sorted(p for p in out if '/assets/' not in p and '/tools/' not in p)

META = re.compile(r'<meta\s+name="google"\s+content="notranslate"\s*/?>', re.I)
HTML_ATTR = re.compile(r'<html\b[^>]*\btranslate="no"', re.I)


def declares(src):
    """Both signals, because they are honoured by different things and one is not a fallback
    for the other. The meta is what Chrome's translate reads. The attribute is the HTML
    standard's own, and it is what a conforming element-level implementation reads."""
    return bool(META.search(src)), bool(HTML_ATTR.search(src))


def audit(paths, verbose=True):
    fail = 0
    for p in paths:
        rel = os.path.relpath(p, ROOT)
        src = open(p, encoding='utf-8').read()
        meta, attr = declares(src)
        spanish = rel.startswith('es/')
        if spanish:
            iss = []
            if not meta: iss.append('no <meta name="google" content="notranslate">')
            if not attr: iss.append('no translate="no" on <html>')
            ok = not iss
        else:
            # 🔒 THE ENGLISH SIDE MUST STAY OPEN. A reader whose language this site does not
            # publish has exactly one way to read it, and it is the machine. Declaring
            # notranslate here would close the door on every language but two.
            iss = []
            if meta: iss.append('declares notranslate, but English prose is translatable on purpose')
            if attr: iss.append('translate="no" on <html>, but English prose is translatable on purpose')
            ok = not iss
        if verbose:
            print(f"  {rel:28} {'OK' if ok else '; '.join(iss)}")
        fail += len(iss)
    return fail


def selftest():
    """🔒 A CHECK THAT CAN ONLY EVER SAY NO IS NOT A CHECK (check-mail-dns.sh, 2026-09-02, whose
    first draft failed its own selftest). Both arms are shown going red here against source built
    to break them, and green against source built to pass."""
    import tempfile
    ok = True
    cases = [
        ('es/x/index.html', '<html lang="es-419" translate="no">\n<meta name="google" content="notranslate">', 0),
        ('es/x/index.html', '<html lang="es-419">\n<meta charset="utf-8">',                                    2),
        ('es/x/index.html', '<html lang="es-419" translate="no">\n<meta charset="utf-8">',                      1),
        ('x/index.html',    '<html lang="en">\n<meta charset="utf-8">',                                         0),
        ('x/index.html',    '<html lang="en" translate="no">\n<meta name="google" content="notranslate">',      2),
    ]
    with tempfile.TemporaryDirectory() as d:
        global ROOT
        keep, ROOT = ROOT, d
        for rel, src, want in cases:
            f = os.path.join(d, rel)
            os.makedirs(os.path.dirname(f), exist_ok=True)
            open(f, 'w', encoding='utf-8').write(src)
            got = audit([f], verbose=False)
            mark = 'PASS' if got == want else 'FAIL'
            if got != want: ok = False
            print(f"  {mark}  {rel:20} expected {want} issue(s), got {got}   [{src.splitlines()[0][:44]}]")
            os.remove(f)
        ROOT = keep
    return ok


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        print("NOTRANSLATE GATE SELFTEST")
        good = selftest()
        print("SELFTEST OK" if good else "SELFTEST FAILED")
        sys.exit(0 if good else 1)
    print("NOTRANSLATE: a real translation declines a machine one; English stays open")
    f = audit(pages())
    print(f"\nNOTRANSLATE {'OK' if not f else 'FAILURES: %d' % f}")
    sys.exit(1 if f else 0)
