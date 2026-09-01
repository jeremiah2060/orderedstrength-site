#!/usr/bin/env python3
"""BUILD THE FAVICON FROM THE APP'S MASTER, WITH THE CORNERS iOS WOULD HAVE DRAWN.

WHY THIS EXISTS (2026-09-01, CEO-found, the second half of CD-012). Having been caught drawing
my own mark, I fixed it by copying the app's 1024 master straight to favicon.png. The CEO looked
at the browser tab and asked why the icon had sharp corners.

🔒 AN iOS ICON MASTER IS A FULL-BLEED SQUARE BY CONTRACT. The rounded shape everybody thinks of
as the icon is a MASK THE OS APPLIES AT RENDER TIME, and it is deliberately not in the file: the
asset catalog wants the square so the system can mask it per-platform. Copy that master anywhere
nothing masks it, a browser tab or a share card, and you publish the raw square. The file was
right and my assumption about it was wrong, which is the same error as drawing my own mark one
step later: I used an artefact without reading what it is for.

THE SHAPE. Not a rounded rectangle. Apple's is a continuous-curvature squircle, and a plain
corner radius reads subtly wrong beside real app icons. This uses the superellipse

    |2x/w - 1|^n + |2y/h - 1|^n <= 1,    n = 5

which is the standard approximation of that curve. Anti-aliased by building the mask at 4x and
downsampling, because a hard mask at 180px shows stair-stepping on the diagonals.

    python3 tools/gen-favicon.py            # writes favicon.png from assets/appicon-1024.png
    python3 tools/gen-favicon.py --check    # writes nothing; prints whether it is current
"""
import os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER = os.path.join(ROOT, "assets", "appicon-1024.png")
OUT = os.path.join(ROOT, "favicon.png")
SIDE = 180            # apple-touch-icon's native size; browsers downscale it for the tab
EXPONENT = 5.0
SUPERSAMPLE = 4


def squircle_mask(side, exponent=EXPONENT, ss=SUPERSAMPLE):
    n = side * ss
    mask = Image.new("L", (n, n), 0)
    px = mask.load()
    for y in range(n):
        ny = abs(2.0 * (y + 0.5) / n - 1.0) ** exponent
        if ny > 1.0:
            continue
        for x in range(n):
            if abs(2.0 * (x + 0.5) / n - 1.0) ** exponent + ny <= 1.0:
                px[x, y] = 255
    return mask.resize((side, side), Image.LANCZOS)


def build():
    master = Image.open(MASTER).convert("RGB").resize((SIDE, SIDE), Image.LANCZOS)
    out = master.convert("RGBA")
    out.putalpha(squircle_mask(SIDE))
    return out


def main():
    if not os.path.exists(MASTER):
        sys.stderr.write(f"missing {MASTER}\n"); return 2
    built = build()
    if "--check" in sys.argv:
        if not os.path.exists(OUT):
            print("favicon.png is missing"); return 1
        cur = Image.open(OUT).convert("RGBA")
        if cur.size != built.size:
            print(f"favicon.png is {cur.size}, expected {built.size}"); return 1
        a, b = list(cur.getdata()), list(built.getdata())
        diff = sum(abs(x - y) for pa, pb in zip(a, b) for x, y in zip(pa, pb)) / (len(a) * 4)
        print(f"favicon.png differs from a fresh build by {diff:.2f}")
        return 0 if diff <= 1.0 else 1
    built.save(OUT)
    print(f"favicon.png written  ({SIDE}x{SIDE}, squircle n={EXPONENT}, "
          f"{os.path.getsize(OUT)} bytes)")
    return 0


sys.exit(main())
