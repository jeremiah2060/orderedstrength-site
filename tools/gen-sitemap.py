#!/usr/bin/env python3
"""Write sitemap.xml from the pages that actually exist, with dates from git.

WHY THIS EXISTS. The sitemap was hand-typed, and a hand-typed list of every page on a
site is the same shape as every other hand-typed list this repo has been bitten by: it
is correct on the day it is written and nothing tells you the day it stops being. It
happened to be complete when this was written, 22 URLs for 22 pages, which is exactly
how a list looks the day before someone adds a page and forgets it. A page missing from
the sitemap is not a visible defect. It is a page Google may simply never come back for.

🔒 THE DATES WERE ALSO A CLAIM NOBODY WAS CHECKING. Every entry said 2026-09-01 or
2026-09-03 while the pages had been rewritten since, so the file told crawlers that
nothing had changed on the one day everything had. lastmod now comes from `git log`
for that exact file, so it cannot be wrong without the commit being wrong.

Priority is the one genuinely editorial number here, so it stays declared, by path, in
PRIORITY below rather than derived from something that only looks like importance.

    python3 tools/gen-sitemap.py           rewrite sitemap.xml
    python3 tools/gen-sitemap.py --check   fail if the file on disk is not what this writes
"""
import glob, os, re, subprocess, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://www.orderedstrength.com'

# The editorial call, and the only hand-set number in this file. Keyed by the URL path
# WITHOUT the /es/ prefix, because a page and its translation are equally important.
PRIORITY = {
    '/':               '1.0',
    '/how-it-works/':  '0.9',
    '/stronger/':      '0.9',
    '/record/':        '0.9',
    '/join/':          '0.8',
    '/verify/':        '0.8',
    '/receipt/':       '0.7',
    '/spec/':          '0.6',
    '/app-privacy/':   '0.4',
    '/support/':       '0.4',
    '/terms/':         '0.4',
}


def pages(root=ROOT):
    """Every page a person can land on. 404s are excluded: a sitemap is a list of things
    that exist, and `tools/` holds generator inputs that are never served."""
    found = set()
    for pat in ('*.html', '*/index.html', '*/*/index.html'):
        for abs_p in glob.glob(os.path.join(root, pat)):
            found.add(os.path.relpath(abs_p, root))
    out = []
    for p in sorted(found):
        if p.startswith(('tools/', 'assets/')) or os.path.basename(p) == '404.html':
            continue
        out.append(p)
    return out


def url_path(page):
    """`stronger/index.html` -> `/stronger/`, `index.html` -> `/`."""
    d = os.path.dirname(page)
    return '/' + (d + '/' if d else '')


def lastmod(page, root=ROOT):
    """The date this file last actually changed, from git. A sitemap date is a claim to a
    crawler; deriving it from the commit is the only way it cannot drift from the truth."""
    try:
        out = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', page],
                             cwd=root, capture_output=True, text=True, timeout=20)
        d = out.stdout.strip()
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}', d):
            return d
    except Exception:
        pass
    return datetime.date.today().isoformat()


def build(root=ROOT):
    rows = []
    for page in pages(root):
        path = url_path(page)
        es = path.startswith('/es/')
        shared = path[3:] if es else path          # '/es/join/' -> '/join/'
        en_url, es_url = BASE + shared, BASE + '/es' + shared
        rows.append((BASE + path, lastmod(page, root), PRIORITY.get(shared, '0.5'),
                     en_url, es_url))
    rows.sort(key=lambda r: r[0])

    x = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
         '        xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for loc, mod, pri, en, es in rows:
        x += ['  <url>',
              f'    <loc>{loc}</loc>',
              f'    <lastmod>{mod}</lastmod>',
              f'    <priority>{pri}</priority>',
              f'    <xhtml:link rel="alternate" hreflang="en" href="{en}"/>',
              f'    <xhtml:link rel="alternate" hreflang="es" href="{es}"/>',
              f'    <xhtml:link rel="alternate" hreflang="x-default" href="{en}"/>',
              '  </url>']
    x.append('</urlset>')
    return '\n'.join(x) + '\n'


def main():
    want = build()
    path = os.path.join(ROOT, 'sitemap.xml')
    have = open(path, encoding='utf-8').read() if os.path.exists(path) else ''
    n = want.count('<url>')
    if '--check' in sys.argv:
        print('SITEMAP: every page listed, every date from git')
        if have == want:
            print(f'  sitemap.xml is exactly what the tree generates  ({n} URLs)')
            return 0
        hl = set(re.findall(r'<loc>(.*?)</loc>', have))
        wl = set(re.findall(r'<loc>(.*?)</loc>', want))
        for missing in sorted(wl - hl):
            print(f'  PAGE EXISTS AND IS NOT IN THE SITEMAP: {missing}')
        for gone in sorted(hl - wl):
            print(f'  SITEMAP LISTS A PAGE THAT DOES NOT EXIST: {gone}')
        if hl == wl:
            print('  the URL set is right; a lastmod or priority is stale')
        print('  run: python3 tools/gen-sitemap.py')
        print('SITEMAP FAILURES: 1')
        return 1
    open(path, 'w', encoding='utf-8').write(want)
    print(f'SITEMAP: wrote {n} URLs to sitemap.xml')
    return 0


if __name__ == '__main__':
    sys.exit(main())
