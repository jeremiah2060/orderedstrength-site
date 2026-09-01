#!/usr/bin/env python3
"""THE CALLOUT PINS, CHECKED AGAINST THE PIXELS THEY POINT AT.

WHY THIS EXISTS (2026-09-01). The home page overlays three numbered pins on a screenshot and
writes a callout for each one. The pins are absolute percentages in a `style` attribute. Every
other number on this site is checked against something; these were checked against nobody's
eyes, and `shot-gate.py` deliberately STRIPS `style="..."` before reading claims, so the one
gate looking at that section is blind to them by design.

🔒 A NUMBER THAT POSITIONS SOMETHING OVER A PHOTOGRAPH IS A CLAIM ABOUT THAT PHOTOGRAPH.
It says "the thing I am describing is HERE". Treat it like any other claim: resolve it against
the pixels, or do not publish it. That is the whole justification, and it is enough.

🔒 IT IS ENOUGH BECAUSE THE MORE DRAMATIC JUSTIFICATION I WROTE HERE FIRST WAS FALSE, AND I
MEASURED IT FALSE RATHER THAN SHIPPING IT. This paragraph originally claimed that carrying the
English percentages onto the Spanish frame "would have put all three pins on the wrong controls",
since Spanish runs 20-30% longer and that frame carries an extra banner. So I injected exactly
that: all three English values onto the Spanish page. GREEN, all three, at 0.0% vertical gap.
The elements do move down, by 2 to 8 points, but their boxes are 2 to 7 points TALL, so the old
coordinates still land inside them. The English pins would have been fine.

A gate justified by a scenario that does not fail is a gate whose first reader will not trust its
comments. What this DOES catch, proven by injection: pin 2 moved from its sublabel to the absence
banner, 45.1% off, RED; and the smallest miss worth catching, pin 1 moved from the badge to the
headline one target-height below, 9.9% off, RED.

HOW. `tools/ocr.swift --boxes` returns each recognised run with its box in 0..1 coordinates,
top-left origin. For each pin, this reads the phrase its callout quotes, finds that phrase in
the frame, and asserts the pin sits within TOLERANCE of that box. The pin is allowed to sit
just outside its target, because that is how a marker avoids covering the text it marks; it is
not allowed to be somewhere else on the screen.

    python3 tools/pin-gate.py
"""
import re, os, sys, subprocess, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 🔒 THE TWO AXES ARE NOT THE SAME KIND OF CLAIM, AND CALIBRATING THEM THE SAME WAY MAKES THIS
# GATE USELESS IN ONE DIRECTION AND WRONG IN THE OTHER.
#
# VERTICAL is what binds a marker to its subject: a reader maps a numbered pin to a row. It is
# also the axis the defect this gate exists for moves along. Spanish text is 20-30% longer and
# the Spanish frame carries an extra banner, so carrying the English percentages across pushes
# every target DOWN past its pin. Tight: 8% of frame height, about two lines of body text.
#
# HORIZONTAL is a design choice, not a claim. Pin 3 marks a full-width paragraph and sits in the
# right margin at 91%, which is deliberate: a marker beside a block, not on top of the words. My
# first cut set both axes to roughly the same tolerance and immediately failed that pin for being
# 19% to the right of text it correctly marks. Tightening a real design into a red is how a gate
# gets switched off, so this axis only catches a pin that has left the frame entirely.
# 🔒 8% WAS TOO LOOSE AND IT PASSED TWO PINS THAT WERE POINTING AT THE WRONG THING.
# An independent sweep found English pin 2 sitting at 67.5% while its label spans
# 61.5-63.2%: a 4.3-point miss, comfortably inside an 8% budget, and in the render it
# physically covered the '56.3 kg' the caption quotes. Pin 3 was 3.5 points past its line,
# in blank space. Both were wrong WHEN AUTHORED, not stale from a re-shoot: the pre-shoot
# frame has identical element positions.
# 3% of frame height is about 79px, roughly one line of body text: enough slack for a
# marker to sit beside its subject, not enough for it to sit on the next control.
TOL_X, TOL_Y = 0.35, 0.03

# Which page, which frame, and what each pin claims to be pointing at. The phrase is matched
# against the OCR the same way shot-gate matches a caption, so a phrase that moves in the app
# fails here too rather than silently unbinding the pin.
PINS = {
    'index.html': [
        ('Building',      'the mode badge'),
        ('(Pop. Est.)',   'the fatigue sublabel'),
        ('open on evidence, not time', 'the evidence line'),
    ],
    'es/index.html': [
        ('Construyendo',  'the mode badge'),
        ('(Est. pobl.)',  'the fatigue sublabel'),
        ('se abren con evidencia, no con tiempo', 'the evidence line'),
    ],
}
LANG = {'index.html': 'en', 'es/index.html': 'es'}
OCR_LANG = {'en': 'en-US', 'es': 'es-ES'}


def norm(s):
    """Same folding shot-gate uses, so the two agree about what a phrase is."""
    s = unicodedata.normalize('NFKC', s)
    s = s.replace('·', '/').replace('•', '/').replace('‧', '/')
    s = re.sub(r'<[^>]+>', ' ', s)
    s = ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))
    s = re.sub(r'[^a-z0-9%/\'". ]+', ' ', s.lower())
    return re.sub(r'\s+', ' ', s).strip()


def boxes(path, lang):
    cmd = ['swift', os.path.join(ROOT, 'tools', 'ocr.swift'), path, '--boxes']
    if lang != 'en':
        cmd += ['--lang', OCR_LANG[lang]]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0:
        raise SystemExit(f"OCR failed for {path}: {r.stderr.strip()[:200]}")
    out = []
    for line in r.stdout.splitlines():
        parts = line.split('\t')
        if len(parts) == 5:
            x, y, w, h, txt = parts
            out.append((float(x), float(y), float(w), float(h), norm(txt)))
    return out


def main():
    print("CALLOUT PINS")
    fail = 0
    for page, pins in PINS.items():
        src = open(os.path.join(ROOT, page), encoding='utf-8').read()
        gal = re.search(r'<div class="gallery.*?</section>', src, re.S)
        if not gal:
            print(f"  {page:24} no gallery section found"); fail += 1; continue
        img = re.search(r'device__screen" src="([^"?]+)', gal.group(0))
        found = re.findall(r'<span class="pin" style="left:([\d.]+)%;top:([\d.]+)%"', gal.group(0))
        if not img or len(found) != len(pins):
            print(f"  {page:24} expected {len(pins)} pin(s), found {len(found)}"); fail += 1; continue

        frame = img.group(1).lstrip('/')
        bs = boxes(os.path.join(ROOT, frame), LANG[page])
        # 🔒 REFUSE AN EMPTY READ RATHER THAN PASS IT. If OCR returns nothing, every phrase below
        # is "not found" and a naive gate would report three failures for one cause, or worse,
        # skip them all and go green.
        if not bs:
            print(f"  {page:24} OCR returned no text for {frame}"); fail += 1; continue

        for (px, py), (phrase, what) in zip(found, pins):
            px, py = float(px) / 100, float(py) / 100
            want = norm(phrase)
            hits = [b for b in bs if want in b[4]]
            # 🔒 A SENTENCE WRAPS, SO IT IS IN NO SINGLE BOX. OCR returns one run per LINE, and
            # "se abren con evidencia, no con tiempo" spans two of them, so the containment test
            # above declared the phrase missing from a frame it is plainly in.
            #
            # 🔒 AND MY FIRST REPAIR FOR THAT WAS ALSO WRONG, FOR A CHARACTER. It looked for runs
            # that are substrings OF the phrase, and the OCR line reads "evidencia, no con
            # tiempo." WITH A TRAILING FULL STOP, which the phrase does not have, so the fragment
            # matched nothing either. Guessing at fragment shapes is the wrong move twice over.
            #
            # Do what shot-gate does and join the runs, which is the only representation in which
            # a wrapped sentence exists at all, then map the match back to the runs it spans and
            # take their union. Same matching rule as the caption gate, so the two cannot disagree
            # about whether a phrase is present.
            if not hits:
                joined, owner = '', []
                for i, b in enumerate(bs):
                    if joined:
                        joined += ' '; owner.append(i)
                    joined += b[4]; owner.extend([i] * len(b[4]))
                at = joined.find(want)
                if at != -1:
                    spans = sorted(set(owner[at:at + len(want)]))
                    parts = [bs[i] for i in spans]
                    x0 = min(b[0] for b in parts); y0 = min(b[1] for b in parts)
                    x1 = max(b[0] + b[2] for b in parts); y1 = max(b[1] + b[3] for b in parts)
                    hits = [(x0, y0, x1 - x0, y1 - y0, want)]
            if not hits:
                print(f"  {page:24} pin for {what}: the phrase {phrase!r} is not in {frame}")
                fail += 1
                continue
            # Nearest matching run, if the phrase appears more than once (the sublabels do).
            def gap(b):
                x, y, w, h, _ = b
                dx = max(0.0, x - px, px - (x + w))
                dy = max(0.0, y - py, py - (y + h))
                return (dx, dy)
            dx, dy = min((gap(b) for b in hits), key=lambda g: g[0] ** 2 + g[1] ** 2)
            if dx > TOL_X or dy > TOL_Y:
                b = min(hits, key=lambda b: gap(b)[0] ** 2 + gap(b)[1] ** 2)
                print(f"  {page:24} pin for {what} sits at ({px*100:.1f}%, {py*100:.1f}%) but "
                      f"{phrase!r} is at ({b[0]*100:.1f}%, {b[1]*100:.1f}%), "
                      f"off by ({dx*100:.1f}%, {dy*100:.1f}%)")
                fail += 1
            else:
                print(f"  {page:24} pin for {what:22} OK  ({dx*100:.1f}%, {dy*100:.1f}%) from target")

    print(f"\nPIN FAILURES: {fail}")
    return 1 if fail else 0


sys.exit(main())
