#!/usr/bin/env python3
"""A browser translator must never rewrite a string this site quotes from the app.

WHY THIS EXISTS (2026-08-31, CEO in his own browser). He turned on auto-translate to Spanish
and the page fell apart. The cause is not the translation quality; it is that nothing on this
site told the translator which strings are NOT prose.

WHAT IT DESTROYS, and why each one is worse than a typo:

  <code> runs quote the app's EXACT on-screen text, and shot-gate.py asserts every one of them
  against the pixels of the published screenshot. Translate "Calibration (Your RIR)" into
  Spanish and the page now claims the app says something the app does not say, in a language
  the shot gate cannot check, on the one site whose entire argument is that it quotes its own
  product verbatim. The English page stays honest while every translated page lies.

  HEX DIGESTS are not words. A translated nonce or root hash is not a hash: the seal console's
  live fingerprint stops matching, and the /verify/ demo hands the reader a receipt that fails
  verification for a reason that has nothing to do with the receipt. The one interactive proof
  on the site breaks first, for exactly the audience least willing to give it a second try.

  THE VERDICT ELEMENTS on /verify/ hold server output. Translating VERIFIED or NOT VERIFIED
  turns the answer into an opinion.

WHAT IS DELIBERATELY LEFT TRANSLATABLE: all the prose. A Spanish speaker should be able to
read this site. The rule is not "do not translate", it is "do not translate the things that
are quotations and machine output", which is the same line the app's own i18n gates draw.

🔒 THE ENGLISH PAGE PASSING EVERY OTHER GATE IS NOT EVIDENCE ABOUT THE TRANSLATED ONE. Seven
gates ran green on this site all night while every non-English reader got a broken page,
because every one of them reads the English DOM. This gate is the only one that asks what
happens to a reader who does not speak it.
"""
import re, sys, glob, os

# Content that must survive a translator intact, and how to recognise it.
RULES = [
    ('quoted app string', r'<code(?![^>]*translate="no")[^>]*>'),
    ('hex digest',        r'<(?:span|div|pre|b)(?![^>]*translate="no")[^>]*>\s*[0-9a-f]{32,}\s*<'),
    ('brand wordmark',    r'<a class="wordmark"(?![^>]*translate="no")'),
    ('build stamp',       r'<b class="stamp"(?![^>]*translate="no")'),
]

# Elements whose CONTENT is machine output, addressed by id because they are filled at runtime.
MACHINE_IDS = {
    'index.html':        ['hash', 'rawdump', 'hstate', 'hi', 'nv'],
    'verify/index.html': ['out', 'in', 'led'],
}


def audit(path, rel):
    src = open(path, encoding='utf-8').read()
    # 🔒 A SCRIPT BODY IS NOT TRANSLATED, BUT THE MARKUP IT INJECTS IS. The first draft of this
    # gate stripped script bodies wholesale, on the true-but-irrelevant grounds that a browser
    # does not translate JavaScript. It translates the DOM, and the seal console and the
    # verifier both BUILD `<code>` elements at runtime out of string literals in those bodies.
    # Stripping them meant the gate was blind to exactly the two interactive surfaces whose
    # breakage the CEO would notice first. Markup literals inside scripts are checked; the
    # surrounding code is not.
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', src, flags=re.S)
    body = re.sub(r'<script[^>]*>.*?</script>', '', src, flags=re.S)
    injected = ' '.join(re.findall(r'<(?:code|span|div|pre|b)[^>]*>', ' '.join(scripts)))
    body = body + ' ' + injected
    issues = []
    for name, pat in RULES:
        n = len(re.findall(pat, body))
        if n:
            issues.append(f'{n} {name}(s) with no translate="no"')
    for i in MACHINE_IDS.get(rel, []):
        m = re.search(r'<[a-zA-Z]+[^>]*\bid="' + i + r'"[^>]*>', body)
        if m and 'translate="no"' not in m.group(0):
            issues.append(f'#{i} renders machine output and is translatable')
    return issues


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pages = sorted(glob.glob(os.path.join(root, '*.html'))) + \
            sorted(glob.glob(os.path.join(root, '*', 'index.html')))
    print("TRANSLATION")
    fails = 0
    for p in pages:
        rel = os.path.relpath(p, root)
        issues = audit(p, rel)
        if issues:
            fails += len(issues)
            for i in issues:
                print(f"  {rel:28} {i}")
        else:
            print(f"  {rel:28} OK")
    print(f"\nTRANSLATION FAILURES: {fails}")
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
