#!/usr/bin/env python3
"""Two rules in _headers that set the same header for the same file do not override. They append.

WHY THIS EXISTS (2026-09-03, shipped and measured within minutes). This file carried
`/assets/*` at one hour followed by specific rules at a year, written on the belief that a later,
more specific rule wins for a header both set. Cloudflare Pages concatenates them. The live
response was:

    cache-control: public, max-age=3600, must-revalidate, public, max-age=31536000, immutable

Two max-age directives and must-revalidate sitting beside immutable, in one header. A parser
takes the first max-age, so the effect was the hour that was already there: no regression, and
none of the improvement either, which is the worst shape a change can have because it looks
deployed. 🔒 THE DEFECT IS INVISIBLE IN THE FILE. Both rules read correctly on their own and the
conflict exists only in a response header nobody reads unless something is already wrong.

WHAT IT CHECKS

  ARM 1  No two rules set the same header for a path both of them match. Rather than trying to
         intersect two glob patterns in the abstract, which is where a check like this usually
         gets quietly wrong, it walks the REAL files in the repository and asks which rules match
         each one. Exact for every path that exists, which is every path a reader can request.

  ARM 2  No page may reference an `immutable` file without a stamp. immutable tells a browser
         it never needs to ask again, so an unstamped reference pins whatever bytes that reader
         happened to get, for a year, and no deploy can reach them.
         🔒 THE RULE IS ABOUT REFERENCES, NOT FILES, AND THE FIRST DRAFT GOT THAT WRONG. It asked
         whether each file under an immutable rule was stamped, and reported thirteen: the shot
         MASTERS, which no page links, and assets/site.css, which stopped being linked when the
         pages moved to the generated twin. A file nobody references cannot pin a stale copy in
         anybody's browser, so those thirteen were the check misreading its own question. What
         is dangerous is an unstamped REFERENCE, and that is what it looks for now.
         🔒 THE FONTS ARE STILL EXEMPT BY NAME AND WITH THE REASON: they are referenced from
         @font-face and from a preload, both without `?v=`, and check-site.py has always exempted
         them, because a woff2 under a versioned name has bytes fixed by that name.

  ARM 3  /assets/lang-check is never immutable. It is the diagnostic a person is sent to when the
         language redirect is behaving oddly, and a year-long cache hands them last month's
         answer to this month's question.

    python3 tools/headers-gate.py [--selftest]
"""
import os, re, sys, glob, fnmatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 🔒 BY NAME, WITH THE REASON, never by pattern. type-floor-gate learned that one first.
IMMUTABLE_WITHOUT_A_STAMP = {
    '/assets/fonts/*': 'woff2 files are referenced from @font-face and a preload without ?v=, '
                       'and check-site.py has always exempted them: the bytes are fixed by the name',
}


def rules(text):
    """[(pattern, {header: value})] in file order. A line at column 0 opens a rule."""
    out, cur = [], None
    for line in text.split('\n'):
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if not line[0].isspace():
            cur = (line.strip(), {}); out.append(cur)
        elif cur is not None:
            m = re.match(r'\s+([A-Za-z-]+):\s*(.*)$', line)
            if m: cur[1][m.group(1).lower()] = m.group(2)
    return out


# 🔒 tools/ IS NOT SERVED, AND THIS GATE SWEPT IT IN ON ITS FIRST RUN. tools/og.html is the
# share-card template, rendered to a JPEG and never published, and it links the stylesheet and
# two screenshots with no ?v= because it does not need one. Reading it as a page produced three
# confident failures about files that are correctly stamped everywhere a reader can reach them.
# stamp-assets.py already carries this warning in its own words: "gating a template as though it
# were a page is how a gate earns the reputation that gets it switched off."
def _pages(root):
    out = []
    for pat in ('*.html', '*/*.html', '*/*/index.html'):
        out += glob.glob(os.path.join(root, pat))
    return sorted({p for p in out
                   if not os.path.relpath(p, root).startswith(('tools/', 'assets/'))})


def files(root=ROOT):
    out = list(_pages(root))
    for pat in ('assets/*', 'assets/*/*'):
        out += [p for p in glob.glob(os.path.join(root, pat)) if os.path.isfile(p)]
    return sorted({'/' + os.path.relpath(p, root) for p in out if os.path.isfile(p)})


def matches(pattern, path):
    """Cloudflare's globbing, restricted to what this file uses: a trailing or embedded *."""
    return fnmatch.fnmatchcase(path, pattern)


def unstamped_reference(path, root=ROOT):
    """Does any page link this file WITHOUT a version? That, and only that, is what makes
    immutable unsafe: a reference with no stamp is a URL that never changes."""
    ref = re.escape(path)
    for p in _pages(root):
        s = open(p, encoding='utf-8').read()
        for m in re.finditer(ref + r'(\?v=[0-9a-f]+)?', s):
            if not m.group(1): return True
    return False


def audit(text, root=ROOT, verbose=True):
    iss, rs = [], rules(text)
    # ARM 1
    for path in files(root):
        for header in {h for _, hs in rs for h in hs}:
            hit = [pat for pat, hs in rs if header in hs and matches(pat, path)]
            if len(hit) > 1:
                iss.append(f'{path}: {len(hit)} rules set {header} ({", ".join(hit)}); '
                           'Pages appends them into one header')
    # ARM 2 and 3
    for pat, hs in rs:
        cc = hs.get('cache-control', '')
        if 'immutable' not in cc:
            continue
        if pat in IMMUTABLE_WITHOUT_A_STAMP:
            continue
        for path in files(root):
            if not matches(pat, path):
                continue
            if '/lang-check' in path:
                iss.append(f'{path} is immutable, and it is the language diagnostic')
            elif unstamped_reference(path, root):
                iss.append(f'{path} is immutable and a page links it with no ?v=, '
                           'so that reader is pinned to those bytes for a year')
    if verbose:
        seen = set()
        for i in iss:
            if i not in seen: print('  ' + i); seen.add(i)
        if not iss: print(f'  {len(rs)} rule(s), no two set the same header for one file')
    return len({i for i in iss})


def selftest():
    import tempfile
    ok = True
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, 'assets'))
        open(os.path.join(d, 'index.html'), 'w').write(
            '<link href="/assets/a.css?v=abc123"><img src="/assets/b.png">')
        open(os.path.join(d, 'assets/a.css'), 'w').write('a{}')
        # 🔒 THE THIRD CASE NEEDS A FILE NOTHING STAMPS, and the first draft of this selftest
        # used the stamped one and then reported the gate broken. A fixture that cannot exhibit
        # the defect proves nothing about the check; it proves something about the fixture.
        open(os.path.join(d, 'assets/b.png'), 'w').write('x')
        clean = "/assets/a.css\n  Cache-Control: public, max-age=31536000, immutable\n"
        overlap = "/assets/*\n  Cache-Control: public, max-age=3600\n" + clean
        unstamped = "/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n"
        masters_only = "/assets/c.png\n  Cache-Control: public, max-age=31536000, immutable\n"
        open(os.path.join(d, 'assets/c.png'), 'w').write('y')     # linked by nothing
        for name, text, want_red in [
            ('a single rule per file is clean', clean, False),
            ('two rules setting Cache-Control for one file', overlap, True),
            ('immutable over a file a page links with no stamp', unstamped, True),
            ('immutable over a file nothing links at all is fine', masters_only, False),
        ]:
            n = audit(text, root=d, verbose=False)
            good = (n > 0) == want_red
            ok &= good
            print(f"  {'PASS' if good else 'FAIL'}  {name}  ({n} issue(s))")
    return ok


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        print('HEADERS SELFTEST'); good = selftest()
        print('SELFTEST OK' if good else 'SELFTEST FAILED'); sys.exit(0 if good else 1)
    print('HEADERS: one rule per header per file, and immutable only where a stamp backs it')
    n = audit(open(os.path.join(ROOT, '_headers'), encoding='utf-8').read())
    print(f"\nHEADERS {'OK' if not n else 'FAILURES: %d' % n}")
    sys.exit(1 if n else 0)
