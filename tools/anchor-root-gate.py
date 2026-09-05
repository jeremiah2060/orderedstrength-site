#!/usr/bin/env python3
"""The record page prints the MERKLE ROOT, never git's hash of the file that holds it.

WHY THIS EXISTS (2026-09-05). /record/ promises, in both languages, that each published line
carries "the root hash covering every prediction sealed that day". It rendered `a.sha`, which
is the GIT BLOB HASH the GitHub contents API returns for the file: a hash OF the document, not
the Merkle root INSIDE it. The two are both 40-to-64 hex characters and neither the page nor a
reader could tell them apart by looking.

A stranger who did the one thing this page invites, recompute the day's root from the published
fingerprints, would have got a number that did not match ours, on the single page whose entire
purpose is that they can check us. That is the Narrative-Engine Coherence law applied to the
website: what we SAY must be what we COMPUTED.

WHAT WAS BLIND TO IT, and this is the reason a gate exists rather than a fix alone. Every
existing check passed. `check-site.py` verifies copy. `csp-gate` verifies hosts. `shot-gate`
verifies quoted phrases against pixels. None of them reads a JavaScript expression and asks
whether the field it renders is the field the sentence beside it promised. And the defect was
UNREACHABLE, because no anchor has ever been published, so nothing rendered at all: it would
have fired for the first time on the most important day this record will ever have.

  🔒 A DEFECT THAT CAN ONLY APPEAR ON THE DAY THE FEATURE FIRST WORKS IS NOT A SMALL DEFECT.
  Its blast radius is the launch, and an empty page is exactly the state in which nobody looks.

THE RULE, three parts:
  1. Neither record page may render `.sha` into the anchor list.
  2. Both must render a field named `root`, and validate it as 64 lowercase hex before printing.
  3. The mirror must take that root from the FILE'S CONTENT, never from the listing entry.
"""
import re, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = [os.path.join(ROOT, 'record', 'index.html'),
         os.path.join(ROOT, 'es', 'record', 'index.html')]
MIRROR = os.path.join(ROOT, 'tools', 'mirror-anchors.py')

fail = 0


def bad(msg):
    global fail
    print('anchor-root-gate: FAIL: %s' % msg)
    fail = 1


for page in PAGES:
    if not os.path.exists(page):
        bad('%s is missing' % page)
        continue
    src = open(page, encoding='utf-8').read()

    # Comments are allowed to DISCUSS the old field; markup may not RENDER it. Strip block
    # comments before looking, so the fix's own explanation cannot trip its own gate.
    code = re.sub(r'/\*.*?\*/', '', src, flags=re.S)

    if re.search(r'\ba\.sha\b', code):
        bad('%s renders a.sha, which is git\'s hash of the file, not the Merkle root inside it'
            % os.path.relpath(page, ROOT))

    if not re.search(r'\ba\.root\b', code):
        bad('%s never reads a.root, so it cannot be printing the published root'
            % os.path.relpath(page, ROOT))

    # 🔒 IT MUST VALIDATE BEFORE IT PRINTS. A page that prints whatever the mirror handed it
    # would republish a malformed root in our own voice.
    if not re.search(r'\[0-9a-f\]\{64\}', code):
        bad('%s prints a root without checking it is 64 lowercase hex characters first'
            % os.path.relpath(page, ROOT))

if os.path.exists(MIRROR):
    m = open(MIRROR, encoding='utf-8').read()
    body = re.sub(r'#.*', '', m)
    body = re.sub(r'""".*?"""', '', body, flags=re.S)
    if re.search(r"'sha'\s*:", body):
        bad('mirror-anchors.py still stores a listing sha as an anchor field')
    if not re.search(r"'root'\s*:", body):
        bad('mirror-anchors.py does not store a root')
    if 'fetch_document' not in body:
        bad('mirror-anchors.py does not read each anchor file\'s content, so any root it '
            'stores cannot have come from inside the file')
else:
    bad('tools/mirror-anchors.py is missing')

if fail:
    print('anchor-root-gate: the record page must print the root it promises.')
    sys.exit(1)

print('anchor-root-gate: OK. Both record pages print a validated Merkle root read from the file.')
