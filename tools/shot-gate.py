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
    'en': {
        'overhead press', 'barbell row', 'barbell bench press',
        'lat pulldown', 'romanian deadlift', 'barbell back squat',
    },
    # The same six as the app's own catalog renders them in Spanish. norm() folds accents, so
    # these are written the way norm LEAVES them: `sentadilla trasera con barra`, not `Sentadilla`.
    'es': {
        'press militar', 'remo con barra', 'press de banca con barra',
        'jalon al pecho', 'peso muerto rumano', 'sentadilla trasera con barra',
    },
}

# 🔒 THIS GATE READ ONE PAGE WHILE THE SITE SHIPPED TWO (2026-09-01). `main()` opened
# `index.html` and nothing else, so /es/ published four photographs and twenty-one claims about
# them that NOTHING had ever compared against a pixel. That is not a gap in coverage, it is the
# gate's entire subject missing: the Spanish page is the one whose captions were hardest to
# write, because its author does not read the language the screenshots are in.
PAGES = [('index.html', 'en'), ('es/index.html', 'es')]

# The two content checks above the claim loop are LANGUAGE-SPECIFIC and were written as English
# literals. Left that way they would silently pass on every Spanish frame: a Spanish permission
# sheet does not contain "health access", and the "Best on record" guard would never fire, so the
# one check that proves the photograph is of the RIGHT ATHLETE would have been decorative on /es/.
PERMISSION_SHEET = {
    'en': ('health access', 'access your health data'),
    'es': ('acceso a salud', 'acceder a tus datos de salud'),
}
BEST_ON_RECORD = {
    'en': r'best on record[:/\s]+(.+?)(?:\s*[/|-]\s*estimated|\s+estimated|$)',
    'es': r'mejor registrado[:/\s]+(.+?)(?:\s*[/|-]\s*1rm|\s+1rm|$)',
}


OCR_LANG = {'en': 'en-US', 'es': 'es-ES'}


def ocr(path, lang='en'):
    cmd = ['swift', os.path.join(ROOT, 'tools', 'ocr.swift'), path]
    if lang != 'en':
        cmd += ['--lang', OCR_LANG[lang]]
    out = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    if out.returncode != 0:
        raise SystemExit(f"OCR failed for {path}: {out.stderr.strip()}")
    return out.stdout


def norm(s):
    """Fold the differences that are transcription noise rather than meaning: OCR renders
    the middle dot as a bullet, splits lines mid-sentence, and varies on quote glyphs.

    🔒 ACCENTS ARE FOLDED TO THEIR BASE LETTER, AND THE OLD BEHAVIOUR WAS WORSE THAN NO RULE
    (2026-09-01, when this gate first had to read Spanish). The character class below is
    `[^a-z0-9%/'". ]`, which does not admit a single accented letter, so every one of them was
    replaced by a SPACE: `día` became `d a` and `Calibración` became `calibraci n`. That is
    survivable while both sides carry the same accent, and it fails the moment they do not,
    which is routine: this repo's own OCR reads the SAME frame as "Buenos dias" and "ausente 3
    días" in one pass. So a true caption passed or failed on whether Vision happened to see a
    diacritic. Folding to the base letter makes both spellings converge instead of diverge, and
    it is a no-op on English, which carries no accents to fold."""
    s = unicodedata.normalize('NFKC', s)
    s = (s.replace('·', '/').replace('•', '/').replace('‧', '/')
           .replace('’', "'").replace('‘', "'")
           .replace('“', '"').replace('”', '"'))
    s = re.sub(r'&middot;', '/', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    # Decompose, then drop the combining marks: á -> a, ñ -> n, ü -> u.
    s = ''.join(c for c in unicodedata.normalize('NFKD', s)
                if not unicodedata.combining(c))
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
    # 🔒 TWO DEFECTS IN ONE LINE, AND THE SECOND ONE HID BEHIND THE FIX FOR THE FIRST.
    #
    # (1) THE UNIT WAS ENGLISH-ONLY. The pattern was `(?:percent|%)`, and Spanish alt text says
    #     "por ciento", so every prose number on /es/ was asserted by nothing at all.
    #
    # (2) AND IT ONLY EVER SAW THE LAST NUMBER OF A LIST, IN BOTH LANGUAGES. Adding the Spanish
    #     unit was not enough: in "9 y 92 por ciento" (and equally in "6 and 95 percent") only
    #     the number ADJACENT to the unit matches, so the first value of every pair this site
    #     writes has never been checked. I proved the incomplete fix by injecting
    #     "9 y 92" -> "41 y 92" and watching the gate stay GREEN, which is exactly the
    #     shape of check that runs correctly and answers an adjacent question.
    #
    # So: match the whole numeric chain that ENDS in a unit, and claim every number in it.
    for chain in re.finditer(
            r'\b(\d{1,3}(?:\s*(?:,|y|and|&)\s*\d{1,3})*)\s*(?:percent|per\s*cent|por\s*ciento|%)',
            body, re.I):
        for n in re.findall(r'\d{1,3}', chain.group(1)):
            out.append(('number', n + '%'))
    return [c for c in out if c[1]]


_cache = {}


def check_page(page, lang):
    """Every claim ONE page makes about its photographs, against those pixels."""
    html = open(os.path.join(ROOT, page), encoding='utf-8').read()
    fail = 0

    def text_of(src):
        path = os.path.join(ROOT, src.split('?')[0].lstrip('/'))
        key = (path, lang)
        if key not in _cache:
            if not os.path.exists(path):
                print(f"  MISSING  {src}"); return None
            _cache[key] = norm(ocr(path, lang))
        return _cache[key]

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
            if any(p in t for p in PERMISSION_SHEET[lang]):
                issues.append("this is a system permission sheet, not the product")
            m_best = re.search(BEST_ON_RECORD[lang], t)
            if m_best:
                movement = re.sub(r'\s+', ' ', m_best.group(1)).strip(" .,:-/'\"")
                if movement and movement not in SEEDED_LIFTS[lang]:
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

    return len(blocks), fail


# The minimum number of captures each page is known to publish. A page that suddenly claims
# fewer has not become cleaner: its markup has moved and this gate has stopped finding it.
EXPECTED_BLOCKS = {'index.html': 5, 'es/index.html': 5}


def main():
    fail = 0
    print("SCREENSHOTS")
    for page, lang in PAGES:
        print(f"  -- {page} ({lang}) " + "-" * (44 - len(page) - len(lang)))
        n, page_fail = check_page(page, lang)
        fail += page_fail
        # 🔒 A CHECK THAT COVERS ZERO ITEMS REPORTS GREEN, AND THIS ONE DID. Renaming the three
        # container classes on es/index.html (`figure class="state"`, `gallery`, `hero-shot`)
        # produced the section header, ZERO rows, and exit 0. The gate had just been widened to
        # read a second page under a lock marker reading "THIS GATE READ ONE PAGE WHILE THE SITE
        # SHIPPED TWO", and it had no defence against the successor failure: read the page, find
        # nothing in it, and call that success. An absence reads as all-clear unless something
        # is counting.
        want = EXPECTED_BLOCKS.get(page)
        if want is not None and n < want:
            print(f"  {'':26} {'':14} FOUND {n} capture(s), expected at least {want}. "
                  f"The markup this gate matches on has moved, so it is now checking less "
                  f"than the page publishes.")
            fail += 1
    print(f"\nSCREENSHOT FAILURES: {fail}")
    return 1 if fail else 0


sys.exit(main())
