#!/usr/bin/env python3
"""Audit a directory of app captures before any of them reaches the website.

Reads every full-screen capture with the OS's Vision framework and reports the four
failures that actually shipped to the front page on 2026-08-23:

  1. the frame is a system permission sheet, not the product;
  2. the lapse banner contradicts the session count ("away for 26 days" above
     "3 sessions logged");
  3. "Estimated 1RM" is a number no human in an acclimation block lifts;
  4. the Calibration ring carries no percentage, which means the RIR belief never
     updated, which means the reserve was logged unauthored;
  5. the movement named beside that number is not one the seeded athlete trains.

Number 5 is here because number 3 was fixed on its own and the sentence stayed wrong.
The load was corrected to a plausible 53 kg and the line still read "Best on record:
Arnold Press (Smith Machine)", which is a movement that cannot be performed: an Arnold
press is defined by rotating the wrists through the press, and a Smith bar is fixed in a
track. It reached the front page of the website and the CEO caught it there. The cause
was a fixture taking `database.prefix(6)` of a catalog sorted alphabetically, so the
photographed athlete trained the first six rows of the letter A. Checking the NUMBER and
not the NAME is checking half of one sentence.

Usage: python3 tools/audit-captures.py <capture-dir>
"""
import re, sys, os, subprocess, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAUSIBLE_1RM = (20.0, 90.0)     # an acclimation-block beginner, in kilograms
MAX_LAPSE_DAYS = 10              # the fixture trains every 3 days

# The six movements JerryEnvironment.seedColdStartSessions names, lower-cased. This IS a
# coupling to the app repo and the coupling is the point: the site publishes a photograph
# of one specific seeded athlete, and the only way to know the photograph shows him is to
# know who he is. If the fixture's six change, this list changes with them, and until it
# does the audit says so out loud rather than passing a screen it can no longer vouch for.
SEEDED_LIFTS = {
    'overhead press', 'barbell row', 'barbell bench press',
    'lat pulldown', 'romanian deadlift', 'barbell back squat',
}


def ocr(path):
    r = subprocess.run(['swift', os.path.join(ROOT, 'tools', 'ocr.swift'), path],
                       capture_output=True, text=True)
    return r.stdout


def audit(path):
    t = ocr(path)
    flat = ' '.join(t.split())
    low = flat.lower()
    issues = []

    if 'health access' in low or 'access your health data' in low:
        return ['system permission sheet, not the product']

    m_sess = re.search(r'(\d+)\s+sessions?\s+logged', low) or re.search(r'\b(one)\s+session\s+logged', low)
    sessions = 1 if (m_sess and m_sess.group(1) == 'one') else (int(m_sess.group(1)) if m_sess else None)

    m_lapse = re.search(r'away for (\d+) days?', low)
    if m_lapse:
        d = int(m_lapse.group(1))
        if d > MAX_LAPSE_DAYS:
            issues.append(f'lapse banner says "away for {d} days"'
                          + (f' while the screen says {sessions} session(s) logged' if sessions else ''))

    m_1rm = re.search(r'estimated 1rm\s*([\d.]+)\s*kg', low)
    if m_1rm:
        v = float(m_1rm.group(1))
        if not (PLAUSIBLE_1RM[0] <= v <= PLAUSIBLE_1RM[1]):
            issues.append(f'"Estimated 1RM {v} kg" is outside {PLAUSIBLE_1RM[0]:.0f}-{PLAUSIBLE_1RM[1]:.0f} kg')

    # THE NAME BESIDE THE NUMBER. Matched on a normalised copy because Vision returns the
    # separator as a hyphen, a middle dot or an interpunct depending on the render, and a
    # checker that only knows one of them reports clean on the other two.
    m_best = re.search(r'best on record[:\s]+(.+?)(?:\s*[-\u00b7\u2022|]\s*estimated|\s+estimated|$)', low)
    if m_best:
        movement = re.sub(r'\s+', ' ', m_best.group(1)).strip(' .,:-\u00b7')
        if movement and movement not in SEEDED_LIFTS:
            issues.append(f'"Best on record: {movement}" is not one of the six lifts the '
                          f'fixture seeds, so this frame photographs an athlete the fixture '
                          f'did not build')

    if 'calibration' in low:
        # the ring's own centre text is a percentage; building renders none
        if '(building)' in low and sessions and sessions >= 2:
            issues.append('Calibration ring still reads (Building) with no percentage at '
                          f'{sessions} sessions: the reserve was logged unauthored')
    return issues


def main():
    d = sys.argv[1] if len(sys.argv) > 1 else '.'
    files = sorted(glob.glob(os.path.join(d, '*.png')))
    from PIL import Image
    full = [f for f in files if Image.open(f).size == (1206, 2622)]
    print(f"{len(full)} full-screen captures in {d}\n")
    bad = 0
    for f in full:
        name = os.path.basename(f).split('__')[-1].replace('_0.png', '')
        if 'es419' in name or 'AX5' in name:
            continue
        iss = audit(f)
        print(f"  {name[:56]:56} {'OK' if not iss else iss[0]}")
        for e in iss[1:]:
            print(f"  {'':56} {e}")
        bad += len(iss)
    print(f"\nCAPTURE FAILURES: {bad}")
    return 1 if bad else 0


sys.exit(main())
