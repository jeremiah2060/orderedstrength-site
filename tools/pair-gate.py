#!/usr/bin/env python3
"""THE TWO LANGUAGES MUST PHOTOGRAPH THE SAME ATHLETE.

WHY THIS EXISTS (2026-09-01, CEO-found, for the second time). The home page exists in English
and Spanish and each shows five screenshots of the app. They are supposed to be the same five
moments in a lifter's life, photographed twice. The CEO opened the two pages side by side, saw
different numbers, and wrote: "do you see the pictures are different spanish vs english there
now this is proof you are not checking at all."

He was right, and the reason no gate caught it is structural: EVERY OTHER GATE HERE READS ONE
PAGE AT A TIME. shot-gate proves each caption matches its own frame, lang-gate proves each page
is written in its declared language, pin-gate proves each pin sits on its own target. A Spanish
frame showing a 6% fatigue ring under a Spanish caption saying 6% is internally perfect and
passes all three. The defect only exists BETWEEN the pages, which is exactly where nobody looked.

🔒 A SET OF PER-PAGE GATES CANNOT SEE A DEFECT THAT IS A RELATIONSHIP BETWEEN PAGES.
Adding a tenth per-page check would not have found this one. The comparison itself is the check.

WHAT MOVED THE NUMBERS. The frames are captured by a simulator run. When English and Spanish are
photographed in the SAME run the pairs agree exactly, measured five for five. A later run that
re-shot only the Spanish frames (to fix a grammar defect in the phase chip) produced correct
Spanish over a DIFFERENT athlete: 6%/95% against the English 10%/92%. So the operational rule is
that both languages are shot together, and this gate is what proves the rule was followed rather
than remembered.

WHAT IS COMPARED, AND WHY NOT EVERYTHING. Raw OCR of the two frames differs harmlessly: the
status bar battery reads 081 or 088 depending on the run, and the recovery timeline's hour chips
(24/48/72) are picked up on one frame and not the other depending on contrast. Those are not
claims. What a reader actually compares across the two pages, and what every caption quotes, is
the PERCENTAGES and the WEIGHTS. Those must be identical, and on the shipped frames they are:
10%/92% + 56.3, 15%/88% + 61.1, 33%/84%/74% + 129.2, 33%/84%/73% + 129.2, 5%.

    python3 tools/pair-gate.py
"""
import re, os, sys, subprocess, hashlib, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 🔒 DERIVED FROM THE PUBLISHED PAGES, NEVER TYPED. A hand-kept list of pairs is a list that
# goes stale the first time a frame is added, and this repo has already shipped three gates
# whose hand-typed page lists silently skipped a page (align, type, measure: all missed /terms/).
EN_PAGE, ES_PAGE = 'index.html', 'es/index.html'


def frames(page):
    src = open(os.path.join(ROOT, page), encoding='utf-8').read()
    # 🔒 CASE-SENSITIVE HERE MEANS INVISIBLE, NOT MISMATCHED. A `[a-z0-9.-]` class does not
    # merely fail to pair `es-Evidence.webp`, it never captures it at all, so the frame drops out
    # of BOTH sides of the comparison and the gate reports a clean pair set it never looked at.
    # Caught in this gate's own falsification, where the injected extra frame produced only half
    # the expected red.
    return sorted(set(re.findall(r'assets/shots/([A-Za-z0-9._-]+\.(?:webp|jpg|png))', src)))


def ocr(path, lang):
    cmd = ['swift', os.path.join(ROOT, 'tools', 'ocr.swift'), path]
    if lang == 'es':
        cmd += ['--lang', 'es-ES']
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0:
        raise SystemExit(f"OCR failed for {path}: {r.stderr.strip()[:200]}")
    return r.stdout


def claims(text):
    """The numbers a reader compares across the two pages: percentages and decimal weights.

    Spanish may render a decimal with a comma. That is the same VALUE in a different costume,
    so it is folded rather than reported, which keeps this gate about the athlete and not about
    number formatting.
    """
    t = unicodedata.normalize('NFKC', text)
    t = re.sub(r'(?<=\d),(?=\d)', '.', t)
    pct = re.findall(r'\b(\d{1,3})\s*%', t)
    dec = re.findall(r'\b(\d{1,4}\.\d{1,2})\b', t)
    return sorted(pct, key=int), sorted(dec, key=float)


def main():
    print("LANGUAGE PAIRS")
    fail = 0
    en, es = frames(EN_PAGE), frames(ES_PAGE)

    # Arm 1: the two pages must publish the same set of moments, one prefixed `es-`.
    want = {f'es-{f}' for f in en if not f.startswith('es-')}
    have = {f for f in es if f.startswith('es-')}
    if not want:
        print(f"  no english frames found in {EN_PAGE}"); return 1
    for missing in sorted(want - have):
        print(f"  {ES_PAGE} is missing {missing}"); fail += 1
    for extra in sorted(have - want):
        print(f"  {ES_PAGE} publishes {extra} with no english twin"); fail += 1

    # Arm 2: the same athlete, in both languages.
    digests = {}
    for f in sorted(f for f in en if not f.startswith('es-')):
        twin = f'es-{f}'
        if twin not in have:
            continue
        pe, ps = os.path.join(ROOT, 'assets/shots', f), os.path.join(ROOT, 'assets/shots', twin)
        if not (os.path.exists(pe) and os.path.exists(ps)):
            print(f"  {f:22} a file is missing from assets/shots"); fail += 1; continue
        te, ts = ocr(pe, 'en'), ocr(ps, 'es')
        # 🔒 REFUSE AN EMPTY READ RATHER THAN PASS IT: two frames that OCR to nothing have
        # identical claims, and this gate would call that a match.
        if not te.strip() or not ts.strip():
            print(f"  {f:22} OCR returned no text"); fail += 1; continue
        (pe_pct, pe_dec), (ps_pct, ps_dec) = claims(te), claims(ts)
        if pe_pct != ps_pct or pe_dec != ps_dec:
            print(f"  {f:22} DIFFERENT ATHLETE")
            print(f"      en  {' '.join(x + '%' for x in pe_pct)}  {' '.join(pe_dec)}")
            print(f"      es  {' '.join(x + '%' for x in ps_pct)}  {' '.join(ps_dec)}")
            fail += 1
        else:
            print(f"  {f:22} OK  {' '.join(x + '%' for x in pe_pct)}  {' '.join(pe_dec)}")
        # Arm 3 data: the CEO also asked that no one photograph be reused as another.
        for name, path in ((f, pe), (twin, ps)):
            digests[name] = hashlib.sha256(open(path, 'rb').read()).hexdigest()

    # Arm 3: every published frame is its own photograph.
    seen = {}
    for name, d in sorted(digests.items()):
        if d in seen:
            print(f"  {name} is byte-identical to {seen[d]}"); fail += 1
        else:
            seen[d] = name

    print(f"\nPAIR FAILURES: {fail}")
    return 1 if fail else 0


sys.exit(main())
