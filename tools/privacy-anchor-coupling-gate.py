#!/usr/bin/env python3
"""Item 6 of the privacy policy must agree with what the app ACTUALLY sends.

WHY THIS EXISTS (2026-09-05). app-privacy item 6 describes the sealed-prediction fingerprint
and ends with a sentence in bold:

    "In the version you can install today, this does not happen."

That sentence was true when it was written and it is a promise with an expiry date. The moment
a build ships that actually sends a fingerprint, it becomes a published falsehood on the one
page whose entire subject is what leaves the phone, and nothing anywhere would have noticed.

WHAT WAS BLIND TO IT. `privacy-status-gate.py` already checks item 6, and it is a good gate,
and it is structurally incapable of catching this. It compares the HEADING's status clause
against the page's OWN paragraph, so it proves the page is self-consistent. A page can be
perfectly self-consistent and completely wrong about the app. That is the failure CLAUDE.md
names: a check that runs correctly and answers the question ADJACENT to the one that matters.

  🔒 THE ONLY THING THAT CAN SETTLE THIS IS THE APP'S SOURCE, SO THIS GATE READS IT.
  Three tools here already reach into the app repository for exactly this reason
  (`app-strings.py`, `icon-gate.py`, `audit-captures.py`), and the coupling is the point.

THE RULE, in both languages:
  * If the app SENDS (the outbox records at the seal seam AND something calls flush), then
    item 6 may not say "not yet" and may not carry the dormant sentence.
  * If the app does NOT send, item 6 must say "not yet" and must carry the dormant sentence,
    because describing a live flow that does not exist is the same defect pointing the other way.

🔒 AND IT REFUSES TO VOUCH WHEN IT CANNOT SEE THE APP. A missing app repository is reported as
UNKNOWN and exits non-zero rather than passing quietly: a gate that silently degrades to
all-clear when its evidence disappears is worse than no gate, because everyone believes it.
"""
import os, re, sys
import html as _html

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_REPO = os.environ.get("OS_APP_REPO", os.path.expanduser("~/Desktop/OrderedStrength22"))

PAGES = [os.path.join(SITE, 'app-privacy', 'index.html'),
         os.path.join(SITE, 'es', 'app-privacy', 'index.html')]

SEAL_FILE = os.path.join(APP_REPO, 'OrderedStrength2', 'Jerry', 'PredictionCommitment.swift')
APP_FILE = os.path.join(APP_REPO, 'OrderedStrength2', 'OrderedStrengthApp.swift')

HEADING = re.compile(r'<h3>\s*(\d+)\.\s*(.+?)\s*(?:&middot;|·)\s*(.+?)\s*</h3>(.*?)(?=<h3>|<h2>|\Z)',
                     re.S | re.I)
NOT_YET = re.compile(r'^(?:not yet\b|todav[ií]a no\b)', re.I)
DORMANT = re.compile(r'this does not happen|esto no (?:pasa|sucede|ocurre)', re.I)

fail = 0


def bad(msg):
    global fail
    print('privacy-anchor-coupling: FAIL: %s' % msg)
    fail = 1


def app_sends():
    """True when the shipping app both RECORDS at the seal seam and SENDS what it recorded.

    Both halves are required and neither is sufficient. A recorder with no sender fills a
    store nobody empties; a sender with no recorder posts an empty list forever. Either one
    alone means no fingerprint reaches the record, so the page's dormant sentence stays true.
    """
    if not os.path.exists(SEAL_FILE) or not os.path.exists(APP_FILE):
        return None
    seal = open(SEAL_FILE, encoding='utf-8').read()
    app = open(APP_FILE, encoding='utf-8').read()
    # Comments are stripped so a law ABOUT the call is never mistaken for the call.
    seal_code = re.sub(r'//.*', '', seal)
    app_code = re.sub(r'//.*', '', app)
    records = 'AnchorOutbox.record(' in seal_code
    sends = 'AnchorOutbox.flush(' in app_code
    return records and sends


def item_six(path):
    src = open(path, encoding='utf-8').read()
    for m in HEADING.finditer(src):
        if m.group(1) != '6':
            continue
        body = _html.unescape(re.sub(r'<[^>]+>', ' ', m.group(4)))
        return _html.unescape(m.group(3)).strip(), re.sub(r'\s+', ' ', body).strip()
    return None, None


sends = app_sends()
if sends is None:
    print('privacy-anchor-coupling: UNKNOWN. The app repository is not readable at %s, so this '
          'gate cannot say whether item 6 is true. It refuses to vouch.' % APP_REPO)
    sys.exit(1)

for page in PAGES:
    if not os.path.exists(page):
        bad('%s is missing' % page)
        continue
    status, body = item_six(page)
    if status is None:
        bad('%s has no numbered item 6, so this gate vouches for nothing'
            % os.path.relpath(page, SITE))
        continue
    says_not_yet = bool(NOT_YET.match(status))
    says_dormant = bool(DORMANT.search(body))
    rel = os.path.relpath(page, SITE)

    if sends and (says_not_yet or says_dormant):
        bad('%s item 6 says the fingerprint is not sent, and the app SENDS IT. '
            'The app records at the seal seam and calls AnchorOutbox.flush. Update the heading '
            'and remove the dormant sentence in the same edit.' % rel)
    elif not sends and not (says_not_yet and says_dormant):
        bad('%s item 6 describes a live flow, and the app does NOT send. Nothing calls '
            'AnchorOutbox.flush, or nothing records at the seal seam.' % rel)
    else:
        print('privacy-anchor-coupling: ok   %-28s item 6 matches the app (%s)'
              % (rel, 'sending' if sends else 'not sending'))

if fail:
    print('privacy-anchor-coupling: what this page promises about the phone must be what the '
          'phone does.')
    sys.exit(1)

print('privacy-anchor-coupling: OK. Both privacy pages agree with the app source.')
