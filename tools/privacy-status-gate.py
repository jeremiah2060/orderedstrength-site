#!/usr/bin/env python3
"""A status label on the privacy policy must agree with the paragraph underneath it.

WHY THIS EXISTS (2026-09-03, CD-015, the CEO on his own phone). The policy lists six things
that can leave your device, and every heading carries a status after a middle dot:

    1. Jerry's voice           . on when the spoken coaching voice is on
    2. Ask Jerry               . OFF unless you turn it on
    3. A daily usage summary   . on by default, and you can turn it off
    4. Your logged sets        . removed from the code, gone the moment you update
    5. A push notification token . on, so a notification can reach you        <- WRONG
    6. A fingerprint of each sealed prediction . on, and it carries no identifier at all <- WRONG

Five and six said `on`, in the same shape as one and three which really are on, while the
paragraph directly beneath each one said "In the build you can install today, this does not
happen." The policy overstated what leaves the phone, in the headings, which is the part of
a privacy policy people actually read. He circled the word.

WHY NOTHING CAUGHT IT. Fourteen gates read this page. check-site.py counts the SIX and proves
every page agrees on the number, which is a relationship BETWEEN pages; lang-gate proves the
Spanish is Spanish; contrast, type, align and measure prove it renders. Not one of them
compares a heading to the sentence under it, so the page was internally contradictory and
uniformly green. This is CLAUDE.md's decorative-check law: they answered the question
adjacent to the one that mattered.

THE RULE, AND IT IS TWO-SIDED ON PURPOSE.

  ARM A, OVERCLAIM: a status that asserts the flow is ACTIVE, over a body that says it does
  not happen today. This is the arm that catches CD-015.

  ARM B, STALE: a status that says NOT YET, over a body that does NOT say it is dormant.
  This is the arm that fires the day push notifications are provisioned and somebody updates
  the paragraph without updating the label. A gate that can only catch the defect in the
  direction it already happened is a gate that expires the moment it is fixed.

Run --selftest to watch each arm go red against a page built to break it. An instrument
never proven capable of going red is documentation, not protection.

    python3 tools/privacy-status-gate.py [--selftest]
"""
import glob
import html as _html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 🔒 DERIVED FROM THE FILESYSTEM, NEVER TYPED. A hand-kept page list in this repo has been
# wrong twice, and a gate that misses a page prints the same clean line as one that checked it.
def privacy_pages():
    out = []
    for pat in ('app-privacy/index.html', '*/app-privacy/index.html'):
        out += glob.glob(os.path.join(ROOT, pat))
    return sorted(out)


# The status clause is whatever follows the middle dot in the heading. Both spellings, because
# the pages are hand-maintained and one of them is entity-encoded.
HEADING = re.compile(r'<h3>\s*(\d+)\.\s*(.+?)\s*(?:&middot;|·)\s*(.+?)\s*</h3>(.*?)(?=<h3>|<h2>|\Z)',
                     re.S | re.I)

# A status ASSERTS ACTIVE when it opens by saying so. Anchored at the start, because "OFF
# unless you turn it on" ends in the word "on" and is the clearest possible non-active status:
# a substring test here would have called item 2 active and taught everyone to skim this gate.
ACTIVE = re.compile(r'^(?:on\b|encendid[oa]\b|activ[oa]\b)', re.I)

# A status says NOT YET when it opens by saying so.
NOT_YET = re.compile(r'^(?:not yet\b|todav[ií]a no\b)', re.I)

# The body's own admission that the flow is dormant in the shipping version.
DORMANT = re.compile(r'this does not happen|esto no pasa', re.I)


def status_rows(src):
    """(number, name, status, body_text) for every numbered heading on the page."""
    rows = []
    for m in HEADING.finditer(src):
        body = re.sub(r'<[^>]+>', ' ', m.group(4))
        rows.append((m.group(1),
                     _html.unescape(m.group(2)).strip(),
                     _html.unescape(m.group(3)).strip(),
                     _html.unescape(re.sub(r'\s+', ' ', body)).strip()))
    return rows


def audit_status_labels(src, label='<page>', verbose=True):
    """Return the number of headings whose status contradicts their own paragraph."""
    fails = 0
    rows = status_rows(src)
    if not rows:
        if verbose:
            print(f"  {label:32} NO NUMBERED HEADINGS FOUND, so this gate vouches for nothing")
        return 1
    for num, name, status, body in rows:
        active, notyet, dormant = ACTIVE.match(status), NOT_YET.match(status), DORMANT.search(body)
        if active and dormant:
            fails += 1
            if verbose:
                print(f"  {label:32} OVERCLAIM  item {num} \"{name[:34]}\"")
                print(f"       status says   : \"{status[:74]}\"")
                print(f"       its own body  : \"...{body[max(0, dormant.start() - 30):dormant.end() + 44]}...\"")
        elif notyet and not dormant:
            fails += 1
            if verbose:
                print(f"  {label:32} STALE      item {num} \"{name[:34]}\"")
                print(f"       status says   : \"{status[:74]}\"")
                print(f"       but the body no longer says the flow is dormant")
        elif verbose:
            state = 'active' if active else ('not yet' if notyet else 'other')
            print(f"  {label:32} ok   item {num} {state:8} agrees with its paragraph")
    return fails


def main():
    print("\nPRIVACY STATUS (a heading's status label against its own paragraph)")
    total = 0
    pages = privacy_pages()
    if not pages:
        print("  NO PRIVACY PAGES FOUND")
        return 1
    for p in pages:
        total += audit_status_labels(open(p, encoding='utf-8').read(),
                                     os.path.relpath(p, ROOT))
    print(f"\nPRIVACY STATUS FAILURES: {total}")
    return 1 if total else 0


def selftest():
    """Both arms must be able to go RED, and the honest page must stay green."""
    good = ('<h3>5. A token &middot; not yet, because Apple has not enabled it</h3>'
            '<p>In the version you can install today, this does not happen.</p>'
            '<h3>6. A voice &middot; on when the spoken voice is on</h3>'
            '<p>It is sent to our server.</p>')
    overclaim = ('<h3>5. A token &middot; on, so a notification can reach you</h3>'
                 '<p>In the version you can install today, this does not happen.</p>')
    stale = ('<h3>5. A token &middot; not yet, because Apple has not enabled it</h3>'
             '<p>The token is sent to our server every launch.</p>')
    es_overclaim = ('<h3>5. Un token &middot; activo, para que llegue</h3>'
                    '<p>En la versión que puedes instalar hoy, esto no pasa.</p>')
    off_is_not_active = ('<h3>2. Ask Jerry &middot; OFF unless you turn it on</h3>'
                         '<p>In the version you can install today, this does not happen.</p>')

    cases = [('honest page stays green', good, 0),
             ('ARM A overclaim, English', overclaim, 1),
             ('ARM A overclaim, Spanish', es_overclaim, 1),
             ('ARM B stale not-yet label', stale, 1),
             ('"OFF ... turn it on" is not an active claim', off_is_not_active, 0)]
    bad = 0
    for name, src, want in cases:
        got = audit_status_labels(src, 'selftest', verbose=False)
        ok = got == want
        bad += 0 if ok else 1
        print(f"  {'PASS' if ok else 'FAIL'}  want={want} got={got}  {name}")
    print(f"\nSELFTEST {'PASSED' if not bad else 'FAILED'}: {len(cases)} cases. The load-bearing "
          f"arms are the three REDS: a gate that cannot go red is documentation.")
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(selftest() if '--selftest' in sys.argv else main())
