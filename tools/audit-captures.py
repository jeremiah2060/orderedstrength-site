#!/usr/bin/env python3
"""Audit a directory of app captures before any of them reaches the website.

Reads every full-screen capture with the OS's Vision framework and reports the four
failures that actually shipped to the front page on 2026-08-23:

  1. the frame is a system permission sheet, not the product;
  2. the lapse banner contradicts the session count ("away for 26 days" above
     "3 sessions logged");
  3. "Estimated 1RM" is a number no human in an acclimation block lifts;
  4. the Calibration ring carries no percentage, which means the RIR belief never
     updated, which means the reserve was logged unauthored.

Usage: python3 tools/audit-captures.py <capture-dir>
"""
import re, sys, os, subprocess, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAUSIBLE_1RM = (20.0, 90.0)     # an acclimation-block beginner, in kilograms
MAX_LAPSE_DAYS = 10              # the fixture trains every 3 days


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
