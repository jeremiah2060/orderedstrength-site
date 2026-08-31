#!/usr/bin/env python3
"""What a caption is ALLOWED to quote from a given capture. shot-gate.py, run backwards.

WHY THIS EXISTS. `shot-gate.py` checks a caption against the pixels AFTER the caption is
written, which is the right place for a gate and the wrong place to be doing the thinking. It
tells you a quote is wrong; it never tells you what the right one was. Every caption on this
site so far was written by reading a screenshot with my eyes and typing what I believed it
said, and this session that produced "the middle ring still says Calibration (Building)
because he never told Jerry how sore he was" (false cause), "Estimated 1RM 129.2 kg" over a
frame showing 131.8, and a hero alt claiming 92 percent when the capture read 95.

Three defects, one shape: the caption was authored from MEMORY of the screen rather than from
the screen. This tool removes the memory step.

    python3 tools/quotable.py <image.png>              every quotable phrase in it
    python3 tools/quotable.py <image.png> --check "…"  is this exact phrase in the pixels?

🔒 IT IS THE SAME OCR shot-gate USES, DELIBERATELY. If the two disagreed, a caption could be
authored from one and rejected by the other, and the author would have no way to tell which
was lying. One reader, one truth.
"""
import re, sys, os, subprocess, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ocr(path):
    r = subprocess.run(['swift', os.path.join(ROOT, 'tools', 'ocr.swift'), path],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"ocr failed on {path}: {r.stderr.strip()[:200]}")
    return r.stdout


def norm(s):
    """Same folding shot-gate applies, so what this prints is what that will accept."""
    s = unicodedata.normalize('NFKC', s)
    s = (s.replace('·', '/').replace('•', '/').replace('‧', '/')
           .replace('’', "'").replace('‘', "'")
           .replace('“', '"').replace('”', '"'))
    s = re.sub(r'[^a-z0-9%/\'".,()à-ÿÀ-ß ]+', ' ', s.lower())
    return re.sub(r'\s+', ' ', s).strip()


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip()); return 2
    path = sys.argv[1]
    raw = ocr(path)
    flat = norm(' '.join(raw.split()))

    if '--check' in sys.argv:
        phrase = sys.argv[sys.argv.index('--check') + 1]
        ok = norm(phrase) in flat
        print(f"  {'IN THE PIXELS' if ok else 'NOT IN THE PIXELS'}: {phrase!r}")
        return 0 if ok else 1

    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    print(f"QUOTABLE FROM {os.path.basename(path)}\n")
    print("  Lines the OCR reads, in order. Anything here can be quoted verbatim in a caption;")
    print("  anything NOT here cannot, and shot-gate will refuse it.\n")
    for l in lines:
        print(f"    {l}")
    nums = sorted(set(re.findall(r'\b\d+(?:[.,]\d+)?\s*(?:%|kg)?', ' '.join(lines))))
    print(f"\n  NUMBERS PRESENT ({len(nums)}), because these are what a caption gets wrong:")
    print("   ", ' · '.join(n.strip() for n in nums if n.strip()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
