#!/usr/bin/env python3
"""THE SCREENSHOT GATE: the pixels, checked against the claims.

This site's whole argument is that its numbers can be checked. It publishes photographs of
the app and then makes statements about what is in them. Nothing was checking that those
statements were true, and on 2026-08-23 three of them were not:

  * the hero capture said "You were away for 26 days" directly above "3 sessions logged",
    a contradiction inside one photograph, on the front page;
  * a caption said "three sessions" while the plan banner and the badge said otherwise;
  * every scrolled capture in the newest run was an Apple Health permission sheet rather
    than the app, and nothing noticed because nobody opened all 43 of them.

So: read the text out of every published screenshot with the OS's own Vision framework,
and assert that every quoted phrase and every number the page states about that screenshot
is actually present in it. A claim the pixels do not support fails the build.

It also refuses a capture that is not native resolution, one that is a system permission
sheet rather than the product, and one whose "Best on record" line names a movement the
seeded athlete does not train.

🔒 THAT LAST ONE EXISTS BECAUSE FIXING THE NUMBER LEFT THE SENTENCE WRONG. The published
dashboard read "Best on record: Arnold Press (Smith Machine) . Estimated 1RM 152.4 kg".
The load was corrected to a plausible 53 kg and shipped, and the line still named a
movement that cannot be performed: an Arnold press is defined by rotating the wrists
through the press, and a Smith bar is fixed in a track. The CEO found it on the front
page. One sentence, two independent claims, and only one of them was being checked.
"""
import re, sys, os, subprocess, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NATIVE = (1206, 2622)

# The six movements JerryEnvironment.seedColdStartSessions names, normalised the way norm()
# leaves them. This IS a coupling to the app repo and the coupling is the point: the site
# publishes a photograph of one specific seeded athlete, and the only way to know the
# photograph shows HIM is to know who he is. When the fixture's six change, this changes
# with them, and until it does the gate says so rather than vouching for a screen it can no
# longer vouch for. tools/audit-captures.py carries the same list for the upstream pass.
SEEDED_LIFTS = {
    'overhead press', 'barbell row', 'barbell bench press',
    'lat pulldown', 'romanian deadlift', 'barbell back squat',
}


def ocr(path):
    out = subprocess.run(['swift', os.path.join(ROOT, 'tools', 'ocr.swift'), path],
                         capture_output=True, text=True, cwd=ROOT)
    if out.returncode != 0:
        raise SystemExit(f"OCR failed for {path}: {out.stderr.strip()}")
    return out.stdout


def norm(s):
    """Fold the differences that are transcription noise rather than meaning: OCR renders
    the middle dot as a bullet, splits lines mid-sentence, and varies on quote glyphs."""
    s = unicodedata.normalize('NFKC', s)
    s = (s.replace('·', '/').replace('•', '/').replace('‧', '/')
           .replace('’', "'").replace('‘', "'")
           .replace('“', '"').replace('”', '"'))
    s = re.sub(r'&middot;', '/', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = re.sub(r'[^a-z0-9%/\'". ]+', ' ', s.lower())
    return re.sub(r'\s+', ' ', s).strip()


def claims(text):
    """Every checkable claim in a caption: each <code> phrase, and each number stated as a
    percentage. Prose is not checked, because prose is the next pass's job; these are the
    parts that assert something about the pixels."""
    out = []
    for c in re.findall(r'<code[^>]*>(.*?)</code>', text, re.S):
        out.append(('phrase', norm(c)))
    # 🔒 STRIP INLINE STYLES FIRST. The gallery pins carry `style="left:79%;top:36.9%"`,
    # and a naive number sweep read those as claims about the photograph: it demanded the
    # pixels show "79%", "9%" and "5%". A checker that invents claims is as useless as one
    # that misses them, and it fails in the direction that gets checkers switched off.
    text = re.sub(r'\sstyle="[^"]*"', ' ', text)
    body = re.sub(r'<code[^>]*>.*?</code>', ' ', text, flags=re.S)
    for n in re.findall(r'\b(\d{1,3})\s*(?:percent|%)', body):
        out.append(('number', n + '%'))
    return [c for c in out if c[1]]


def main():
    html = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    fail = 0
    cache = {}

    def text_of(src):
        path = os.path.join(ROOT, src.split('?')[0].lstrip('/'))
        if path not in cache:
            if not os.path.exists(path):
                print(f"  MISSING  {src}"); return None
            cache[path] = norm(ocr(path))
        return cache[path]

    # every capture the page publishes, with the block that talks about it
    blocks = []
    for m in re.finditer(r'<figure class="state">(.*?)</figure>', html, re.S):
        src = re.search(r'device__screen" src="([^"]+)"', m.group(1))
        cap = re.search(r'<figcaption>(.*?)</figcaption>', m.group(1), re.S)
        if src: blocks.append(('pressure test', src.group(1), (cap.group(1) if cap else '') +
                              (re.search(r'alt="([^"]*)"', m.group(1)).group(1) if re.search(r'alt="([^"]*)"', m.group(1)) else '')))
    # the gallery's claims are its CALLOUTS and its alt text, not the whole section: the
    # caption underneath names the capture script, which is a fact about how the photograph
    # was taken and not a claim about what is in it.
    gal = re.search(r'<div class="gallery.*?</section>', html, re.S)
    if gal:
        src = re.search(r'device__screen" src="([^"]+)"', gal.group(0))
        alt = re.search(r'device__screen"[^>]*alt="([^"]*)"', gal.group(0), re.S)
        outs = re.search(r'<ul class="callouts">.*?</ul>', gal.group(0), re.S)
        if src:
            blocks.append(('gallery', src.group(1),
                           (outs.group(0) if outs else '') + ' ' + (alt.group(1) if alt else '')))
    hero = re.search(r'<div class="hero-shot">(.*?)</div>\s*</section>', html, re.S)
    if hero:
        for dm in re.finditer(r'<img class="device__screen" src="([^"]+)"[^>]*alt="([^"]*)"', hero.group(1), re.S):
            blocks.append(('hero', dm.group(1), dm.group(2)))

    print("SCREENSHOTS")
    seen = set()
    for where, src, said in blocks:
        t = text_of(src)
        if t is None: fail += 1; continue
        name = src.split('/')[-1].split('?')[0]
        issues = []
        if name not in seen:
            seen.add(name)
            from PIL import Image
            im = Image.open(os.path.join(ROOT, src.split('?')[0].lstrip('/')))
            if im.size != NATIVE:
                issues.append(f"not native resolution: {im.size[0]}x{im.size[1]}, expected {NATIVE[0]}x{NATIVE[1]}")
            if 'health access' in t or 'access your health data' in t:
                issues.append("this is a system permission sheet, not the product")
            m_best = re.search(r'best on record[:/\s]+(.+?)(?:\s*[/|-]\s*estimated|\s+estimated|$)', t)
            if m_best:
                movement = re.sub(r'\s+', ' ', m_best.group(1)).strip(" .,:-/'\"")
                if movement and movement not in SEEDED_LIFTS:
                    issues.append(f'"Best on record: {movement}" names a movement the fixture '
                                  f'does not seed, so this photograph is of an athlete the app '
                                  f'never built')
        for kind, c in claims(said):
            if c not in t:
                issues.append(f"{where} states {kind} \"{c}\" and the pixels do not show it")
        print(f"  {name:26} {where:14} {'OK' if not issues else issues[0]}")
        for extra in issues[1:]:
            print(f"  {'':26} {'':14} {extra}")
        fail += len(issues)

    print(f"\nSCREENSHOT FAILURES: {fail}")
    return 1 if fail else 0


sys.exit(main())
