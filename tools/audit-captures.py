#!/usr/bin/env python3
"""Audit a directory of app captures before any of them reaches the website.

Reads every full-screen capture with the OS's Vision framework and reports the four
failures that actually shipped to the front page on 2026-08-23:

  1. the frame is a system permission sheet, not the product;
  2. the lapse banner contradicts the session count ("away for 26 days" above
     "3 sessions logged");
  3. "Estimated 1RM" is a number no human in an acclimation block lifts;
  4. the Calibration ring carries no percentage. THE STATED CAUSE WAS FIXED AND THE
     SENTENCE STAYED WRONG, twice, which is the very failure number 5 below exists to
     name. It said "the reserve was logged unauthored"; `rirAuthored: true` has been
     passed since 2026-08-23. It then said "an identical reserve on every set"; that was
     a guess and it was also wrong. MEASURED 2026-08-24: the belief write is gated on
     `strengthCurveDataPoints >= 3`, which counts DISTINCT REP VALUES, and this fixture
     logs reps 8 forever. One bucket, gate never opens, zero observations, ring empty by
     construction. The ring is not a defect in any photograph;
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
# 🔒 THIS BAND WAS CALIBRATED WHEN SESSION 3 WAS THE DEEPEST FRAME THAT EXISTED, AND IT
# THEN REJECTED CORRECT FRAMES FOR BEING DEEP (2026-08-24). The app repo's camera now
# photographs session 40 and session 100, and the auditor failed both: "Estimated 1RM
# 129.2 kg is outside 20-90 kg" on a hundred-session athlete whose squat is genuinely
# 1.58x bodyweight. The number in the picture was right and the checker was stale, which
# is the same class as everything else that round: a check answering the question it was
# built for after the question moved.
#
# 160 is not a guess. `ColdStartFixtureLoadTests.test_noSeededLoadIsAbsurdAtAnyDepth` caps
# the seeded WORKING load at 1.5x bodyweight, and the blended estimator turns a working set
# of 8 reps at reserve 2 into roughly 1.26x that load, so the deepest honest estimate the
# fixture can produce is about 1.9x bodyweight: ~155 kg at 82 kg. 160 clears that with a
# little room and still rejects what this band exists to catch, the 292.5 kg squat the
# pre-2026-08-24 fixture arithmetic would have printed at session 100 (~367 kg estimated).
#
# THE FLOOR STAYS AT 20. A day-one athlete really does start there, and lowering the ceiling
# is what a future beginner-only calibration would be tempted to do again.
PLAUSIBLE_1RM = (20.0, 160.0)    # day-one beginner through strong intermediate, in kilograms
# 🔒 THIS CEILING IS DERIVED FROM THE FIXTURE'S REP COUNT, SO IT IS NOT A CONSTANT, IT IS A
# COUPLING. The 160 above is computed from a working set of EIGHT reps at reserve 2 against a
# seeded load capped at 1.5x bodyweight. Vary the seeded reps and the same load yields a
# different estimate, so a CORRECT deep frame can fall outside this band and be rejected for
# a reason that has nothing to do with the photograph. That is this file's 2026-08-24 failure
# exactly: a band calibrated when session 3 was the deepest frame, rejecting a legitimate
# 129.2 kg hundred-session squat. RE-DERIVE IT WHENEVER THE SEEDER'S REP DISTRIBUTION MOVES.
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
            # 🔒 REPORT THE OBSERVATION, NOT A CAUSE THAT WAS FIXED (2026-08-24). This used
            # to assert "the reserve was logged unauthored". That was true when written and
            # false from 2026-08-23, when the seeder began passing `rirAuthored: true`; the
            # ring is empty anyway at every depth ever photographed. A confident wrong reason
            # is worse than no reason: it routes the next engineer to a closed defect. The
            # leading hypothesis is stated AS a hypothesis, because it is not established:
            # this fixture reports reserve 2 on every one of its sets, and a belief
            # distribution with zero variance may have nothing to calibrate against.
            issues.append('Calibration ring still reads (Building) with no percentage at '
                          f'{sessions} sessions. NOT a defect in this screenshot: the ring is '
                          'reporting honestly that no RIR belief has been written. '
                          'THE TWO GATES THAT MUST BOTH OPEN BEFORE IT CAN READ ANYTHING, '
                          'stated as conditions rather than as a claim about any particular '
                          'fixture: (a) the belief write is skipped while '
                          'strengthCurveDataPoints(exercise) < 3, and that count is '
                          'bestAtReps.count, a dict keyed by REPS, so an athlete who logs one '
                          'identical rep count forever holds ONE key and never opens it; and '
                          '(b) RIRBeliefDistribution.update returns early unless rirAuthored, '
                          'so a reserve accepted from a prefill never counts. GO READ THE '
                          'FIXTURE BEFORE NAMING WHICH ONE IS SHUT. As of 2026-08-30 it was '
                          '(a), the seeder logging reps 8 at four sites in JerryEnvironment, '
                          'and a session was in flight to vary them, so that may no longer be '
                          'true when you read this')
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
