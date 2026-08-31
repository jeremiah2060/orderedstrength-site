#!/usr/bin/env python3
"""Every ring on the dashboard is explained by ITS OWN input, never a neighbour's.

WHY THIS EXISTS (2026-08-30, CEO device, CD-009). The site published a caption reading
"the middle ring still says Calibration (Building), because this athlete never once told
Jerry how sore he was". That is false. Soreness feeds the RECOVERY ring. The Calibration
ring reads how consistently the athlete reports HIS OWN RESERVE, and the proof that the
sentence was wrong was already on the same page, one phone to the right: `answered.webp`
shows the very same athlete WITH his soreness reported, and the Calibration ring is still
empty. The site contradicted itself across two adjacent photographs and shipped.

WHAT WAS BLIND TO IT. `shot-gate.py` asserts every quoted phrase is really in the pixels,
and it passed, correctly: `Calibration (Building)` IS in that photograph. A phrase checker
cannot see a false CAUSE, only a false QUOTE. This is the failure mode CLAUDE.md names as
"a check structurally incapable of seeing what is wrong, whose green is then real and
meaningless": it answered the question ADJACENT to the one that mattered.

THE RULE. Within ONE SENTENCE, a ring's state may not be explained by another ring's input.
Sentence-scoped rather than caption-scoped on purpose: a caption is allowed to discuss
soreness AND calibration, which the corrected caption does. What it may not do is put them
in the same breath, because that is what reads as causation.

THE COUPLING IS THE POINT, and it is to the app repo's own source:
  * Calibration  <- the athlete's TYPED reserve. `RIRBeliefDistribution.update` returns
    early unless `rirAuthored` (JerryKernel.swift: "Jerry's own guess may not validate
    Jerry"), and the write is additionally gated on `strengthCurveDataPoints >= 3`, which
    counts DISTINCT REP VALUES. Label source: `RingPalette.calibrationLabel`.
  * Fatigue / Recovery <- population priors until an individual recovery rate is measured
    from user-reported SORENESS, at which point the sublabel turns to "(Your Data)".
If either mechanism changes in the app, this map changes with it, and until it does the
gate says so out loud rather than vouching for a sentence it can no longer check.
"""
import re, sys, glob, os, html as _html

# Each ring: the on-screen strings that NAME its state, and the vocabulary belonging to a
# DIFFERENT ring's input. A sentence carrying both is the defect.
RINGS = {
    'Calibration': {
        'state': [r'calibration \(building\)', r'calibration \(your rir\)'],
        'foreign': [r'\bsore\b', r'\bsoreness\b', r'how sore', r'recovery rate'],
        'own': 'the athlete\'s own typed reserve (rirAuthored + >= 3 distinct rep buckets)',
    },
    'Recovery': {
        'state': [r'recovery \(pop\. est\.\)', r'recovery \(your data\)'],
        'foreign': [r'\breserve\b', r'\brir\b', r'typed it in', r'rep buckets'],
        'own': 'population priors until an individual rate is fitted from reported soreness',
    },
}


def sentences(text):
    """Caption prose, tags stripped but <code> CONTENT kept, split on sentence ends."""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = _html.unescape(text)
    text = re.sub(r'\s+', ' ', text)
    # Split on a period that ends a sentence. "Pop. Est." and "(Building)." must not split
    # the sentence they sit in, so a period is only a boundary before a capital or an end.
    parts, buf = [], ''
    for tok in re.split(r'(?<=[.!?])\s+', text):
        buf = (buf + ' ' + tok).strip()
        if re.search(r'(Est\.|Pop\.|e\.g\.|i\.e\.)$', buf):
            continue
        parts.append(buf); buf = ''
    if buf:
        parts.append(buf)
    return parts


def audit(path):
    src = open(path, encoding='utf-8').read()
    issues = []
    for cap in re.findall(r'<figcaption>(.*?)</figcaption>', src, re.S):
        for sent in sentences(cap):
            low = sent.lower()
            for ring, spec in RINGS.items():
                if not any(re.search(p, low) for p in spec['state']):
                    continue
                for f in spec['foreign']:
                    if re.search(f, low):
                        issues.append(
                            f'{ring} ring explained with another ring\'s input '
                            f'({f.strip(chr(92)+"b")!r}) in one sentence. {ring} reads '
                            f'{spec["own"]}. Sentence: "{sent.strip()[:150]}"')
    return issues


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pages = sorted(glob.glob(os.path.join(root, '*.html'))) + \
            sorted(glob.glob(os.path.join(root, '*', 'index.html')))
    print("RING CAUSES")
    fails = 0
    for p in pages:
        issues = audit(p)
        name = os.path.relpath(p, root)
        if issues:
            for i in issues:
                print(f"  {name:28} {i}")
                fails += 1
        else:
            print(f"  {name:28} OK")
    print(f"\nRING CAUSE FAILURES: {fails}")
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
