#!/usr/bin/env python3
"""THE FAVICON MUST BE THE PRODUCT'S OWN MARK, WITH THE CORNERS iOS WOULD HAVE DRAWN.

WHY THIS EXISTS (2026-09-01, CEO-found twice, dossier CD-012).

FIRST HE ASKED whether the favicon was deliberate or a bug. It was a bug: the site needed a
tab icon so I DREW one, a teal ring with a vertical bar through the top, which reads as a power
button. The shipping mark is an "OS" MONOGRAM, generated and locked June 2026: a teal ring
around a real SF Pro "S" glyph unioned with its own 180-degree rotation. Its own README says
the S is a real glyph "NOT a hand-drawn bezier, because that looked fake". I hand-drew a bezier.

THEN HE LOOKED AT THE FIX AND ASKED WHY THE ICON HAD SHARP CORNERS. Also a bug, and a more
interesting one. 🔒 AN iOS ICON MASTER IS A FULL-BLEED SQUARE BY CONTRACT: the rounded shape
everyone pictures is a MASK THE OS APPLIES AT RENDER TIME and is deliberately absent from the
file. I had copied the master straight to favicon.png, where nothing masks it, and published
the raw square. The file was right; my assumption about what it was for was wrong. That is the
same error as drawing my own mark, one step later.

🔒 AND THE FIRST VERSION OF THIS GATE COULD NOT HAVE CAUGHT THE SECOND DEFECT. It compared the
favicon to the master at 32x32 in RGB, and `convert("RGB")` DROPS THE ALPHA CHANNEL, which is
the only place the corners exist. Measured: it scored the sharp-cornered favicon at 0.03 and
passed it. A check that runs correctly, reports green, and is structurally incapable of seeing
the failure it was written for. Falsifying it against the FIRST defect proved only that it
could see that one.

WHAT IS CHECKED, and why the corner arm is separate from the pixel arm: a mean difference over
the whole image averages the corners away, so "close enough overall" and "has the mask" are two
different questions and must be two assertions.
  1. The corners are actually masked: all four corner pixels fully transparent.
  2. The favicon is EXACTLY what tools/gen-favicon.py builds from the vendored master, compared
     in RGBA so the mask counts. Not "close to the master", which is the trap above.
  3. The vendored master is byte-identical to the app's shipping icon. Vendoring without this
     arm just moves the drift one file along.
  4. Every page's icon links resolve on disk and agree with each other.

🔒 AN UNREACHABLE APP REPO IS RED, NOT A SKIP. "I could not look" reported as green is the
absence-reads-as-all-clear trap, and it is how a favicon nobody compared reached twenty pages.
Override the path with OS_APP_REPO.

    python3 tools/icon-gate.py
"""
import os, re, sys, glob, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_REPO = os.environ.get("OS_APP_REPO", os.path.expanduser("~/Desktop/OrderedStrength22"))
APP_ICON = os.path.join(APP_REPO, "OrderedStrength2/Assets.xcassets/AppIcon.appiconset/icon_1024.png")
VENDORED = os.path.join(ROOT, "assets/appicon-1024.png")
FAVICON = os.path.join(ROOT, "favicon.png")
GENERATOR = os.path.join(ROOT, "tools", "gen-favicon.py")

# Compared against a fresh build from the same generator, so the only honest tolerance is
# re-encode noise. Measured on the shipping pair: 0.00.
TOLERANCE = 1.0


def expected():
    """Run the generator's builder without its CLI (it calls sys.exit at module scope)."""
    src = open(GENERATOR, encoding="utf-8").read().split("def main()")[0]
    # __file__ must be supplied: the generator derives its own paths from it.
    ns = {"__name__": "genfav", "__file__": GENERATOR}
    exec(compile(src, GENERATOR, "exec"), ns)
    return ns["build"]()


def main():
    print("APP ICON")
    fail = 0
    from PIL import Image

    # ── Arm 3 first: if the vendored source is wrong, everything below measures the wrong thing.
    if not os.path.exists(APP_ICON):
        print(f"  the app's icon is not readable at {APP_ICON}")
        print("   set OS_APP_REPO. RED rather than skipped on purpose: a gate that cannot see")
        print("   its subject must say so, never pass.")
        fail += 1
    elif not os.path.exists(VENDORED):
        print("  assets/appicon-1024.png is missing; nothing vendors the app's mark"); fail += 1
    else:
        a = hashlib.sha256(open(APP_ICON, "rb").read()).hexdigest()
        b = hashlib.sha256(open(VENDORED, "rb").read()).hexdigest()
        if a != b:
            print("  assets/appicon-1024.png is NOT the app's shipping icon")
            print(f"      app {a[:16]} · vendored {b[:16]}")
            print(f"   re-vendor:  cp {APP_ICON} {VENDORED}")
            fail += 1
        else:
            print(f"  vendored master matches the app's shipping icon  ({a[:12]})")

    if not os.path.exists(FAVICON):
        print("  favicon.png is missing"); fail += 1
    else:
        have = Image.open(FAVICON).convert("RGBA")

        # ── Arm 1: the corners. Its own assertion, because a whole-image mean averages them away.
        corners = [have.getpixel(p)[3] for p in
                   [(0, 0), (have.width - 1, 0), (0, have.height - 1),
                    (have.width - 1, have.height - 1)]]
        if any(corners):
            print(f"  favicon.png has SQUARE CORNERS (corner alpha {corners}). An iOS icon "
                  f"master is a full-bleed square and the rounded shape is a mask the OS "
                  f"applies; published unmasked, a browser draws the raw square.")
            print("   rebuild it:  python3 tools/gen-favicon.py")
            fail += 1
        else:
            print("  favicon.png carries the squircle mask  (all four corners transparent)")

        # ── Arm 2: it is the generator's output, alpha included.
        if os.path.exists(VENDORED) and os.path.exists(GENERATOR):
            want = expected()
            if have.size != want.size:
                print(f"  favicon.png is {have.size}, the generator builds {want.size}"); fail += 1
            else:
                x, y = list(have.getdata()), list(want.getdata())
                d = sum(abs(p - q) for pa, pb in zip(x, y) for p, q in zip(pa, pb)) / (len(x) * 4)
                if d > TOLERANCE:
                    print(f"  favicon.png is not what tools/gen-favicon.py builds: {d:.2f} "
                          f"mean RGBA difference (tolerance {TOLERANCE})")
                    print("   rebuild it:  python3 tools/gen-favicon.py")
                    fail += 1
                else:
                    print(f"  favicon.png is the generator's output  ({d:.2f} RGBA difference)")

    # ── Arm 4: every page points at it, and at the same one.
    pages = sorted(p for p in glob.glob(os.path.join(ROOT, "*.html"))
                   + glob.glob(os.path.join(ROOT, "*/*.html"))
                   + glob.glob(os.path.join(ROOT, "*/*/*.html"))
                   if "/tools/" not in p and "/assets/" not in p)
    hrefs, pageless = set(), []
    for p in pages:
        src = open(p, encoding="utf-8").read()
        found = re.findall(r'<link rel="(?:apple-touch-)?icon"[^>]*href="([^"?]+)', src)
        if not found:
            pageless.append(os.path.relpath(p, ROOT)); continue
        for h in found:
            hrefs.add(h)
            if not os.path.exists(os.path.join(ROOT, h.lstrip("/"))):
                print(f"  {os.path.relpath(p, ROOT)} links {h}, which is not on disk"); fail += 1
    if pageless:
        print(f"  {len(pageless)} page(s) carry no icon link: {', '.join(pageless[:4])}"); fail += 1
    if len(hrefs) > 1:
        print(f"  pages disagree about the icon path: {sorted(hrefs)}"); fail += 1
    elif hrefs:
        print(f"  all {len(pages)} pages point at {hrefs.pop()}")

    print(f"\nICON FAILURES: {fail}")
    return 1 if fail else 0


sys.exit(main())
