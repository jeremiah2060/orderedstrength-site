#!/usr/bin/env python3
"""THE FAVICON MUST BE THE PRODUCT'S OWN MARK, NOT A DRAWING OF IT.

WHY THIS EXISTS (2026-09-01, CEO-found, dossier CD-012). The site needed a favicon, so I drew
one: a teal ring with a vertical bar through the top, on a dark rounded square. It matched the
site's palette, it looked deliberate, and it shipped to every one of the twenty pages. The CEO
opened the preview and asked one question: "the favicon you put on the site doesnt match Jerry's
own icon, did you do that deliberatly or its a bug?"

It was a bug, and not a near-miss. The shipping app icon is an "OS" MONOGRAM, locked June 2026
and GENERATED, never hand-drawn: a teal ring (the O) around a real SF Pro "S" glyph, unioned with
its own 180-degree rotation so the whole mark is point-symmetric. Its own README says the S is a
real glyph "NOT a hand-drawn bezier, because that looked fake". What I drew reads as a power
button. Measured against the real icon at 32x32, my drawing sits at 33.36 mean absolute channel
difference; the correct favicon sits at 0.64.

🔒 THE FAILURE WAS NOT ARTISTIC. I INVENTED AN ARTEFACT THAT ALREADY EXISTED, AND NOTHING IN
TWELVE GREEN GATES ASKED WHETHER IT WAS THE REAL ONE. Every gate on this site reads the site.
The app's icon lives in another repository, so no check here could see the divergence, and the
site's own favicon was internally consistent: correct palette, valid SVG, referenced from every
page, present on disk. Internally consistent and wrong is this project's most-repeated defect
shape, and this is its cheapest instance.

WHAT IS CHECKED
  1. The published favicon is pixel-derived from the vendored app-icon master, not drawn.
     Threshold 5.0 sits between the two MEASURED values above, with ~50x margin either side.
  2. The vendored master is byte-identical to the app's shipping icon. Vendoring without this
     arm just moves the drift one file along: the copy would rot silently the day the app icon
     is regenerated.
  3. Every page's icon links point at a file that exists, and at the SAME file, so one page
     cannot be left behind on a path the others moved off.

🔒 AN UNREACHABLE APP REPO IS A FAILURE, NOT A SKIP. Arm 2 needs the sibling checkout. If it is
absent, this gate goes RED and says so, because "I could not look" reported as green is exactly
the absence-reads-as-all-clear trap this repository has a standing law about. Override the path
with OS_APP_REPO when the checkout lives elsewhere.

    python3 tools/icon-gate.py
"""
import os, re, sys, glob, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_REPO = os.environ.get("OS_APP_REPO", os.path.expanduser("~/Desktop/OrderedStrength22"))
APP_ICON = os.path.join(APP_REPO, "OrderedStrength2/Assets.xcassets/AppIcon.appiconset/icon_1024.png")
VENDORED = os.path.join(ROOT, "assets/appicon-1024.png")
FAVICON = os.path.join(ROOT, "favicon.png")

# Measured 2026-09-01 at 32x32 RGB, mean absolute per-channel difference:
#   the correct favicon, a downscale of the master ... 0.64   (resampling noise only)
#   the mark I hand-drew ........................... 33.36
# 5.0 is between them and near neither. It tolerates a re-encode or a different resampler and
# still fails anything that is a different picture.
TOLERANCE = 5.0


def grid(path, n=32):
    from PIL import Image
    im = Image.open(path).convert("RGB").resize((n, n), Image.LANCZOS)
    return list(im.getdata())


def distance(a, b):
    return sum(abs(x - y) for pa, pb in zip(a, b) for x, y in zip(pa, pb)) / (len(a) * 3)


def main():
    print("APP ICON")
    fail = 0

    # ── Arm 2 first: if the source of truth is wrong, arm 1 is measuring the wrong thing. ──
    if not os.path.exists(APP_ICON):
        print(f"  the app's icon is not readable at {APP_ICON}")
        print("   set OS_APP_REPO to the checkout. This is RED rather than skipped on purpose:")
        print("   a gate that cannot see its subject must say so, never pass.")
        fail += 1
    elif not os.path.exists(VENDORED):
        print(f"  assets/appicon-1024.png is missing; nothing vendors the app's mark")
        fail += 1
    else:
        a = hashlib.sha256(open(APP_ICON, "rb").read()).hexdigest()
        b = hashlib.sha256(open(VENDORED, "rb").read()).hexdigest()
        if a != b:
            print(f"  assets/appicon-1024.png is NOT the app's shipping icon")
            print(f"      app      {a[:16]}")
            print(f"      vendored {b[:16]}")
            print(f"   re-vendor it:  cp {APP_ICON} {VENDORED}")
            fail += 1
        else:
            print(f"  vendored master matches the app's shipping icon  ({a[:12]})")

    # ── Arm 1: the favicon is that master, resized. Not a drawing of it. ──
    if not os.path.exists(FAVICON):
        print("  favicon.png is missing"); fail += 1
    elif os.path.exists(VENDORED):
        d = distance(grid(FAVICON), grid(VENDORED))
        if d > TOLERANCE:
            print(f"  favicon.png is not the app's mark: {d:.2f} mean channel difference "
                  f"against the master (tolerance {TOLERANCE})")
            print(f"   regenerate it:  sips -Z 180 assets/appicon-1024.png --out favicon.png")
            fail += 1
        else:
            print(f"  favicon.png is the app's mark  ({d:.2f} difference, tolerance {TOLERANCE})")

    # ── Arm 3: every page points at it, and at the same one. ──
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
        print(f"  {len(pageless)} page(s) carry no icon link: {', '.join(pageless[:4])}")
        fail += 1
    if len(hrefs) > 1:
        print(f"  pages disagree about the icon path: {sorted(hrefs)}"); fail += 1
    elif hrefs:
        print(f"  all {len(pages)} pages point at {hrefs.pop()}")

    print(f"\nICON FAILURES: {fail}")
    return 1 if fail else 0


sys.exit(main())
