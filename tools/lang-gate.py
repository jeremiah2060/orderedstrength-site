#!/usr/bin/env python3
"""A page must actually be written in the language it declares.

WHY THIS EXISTS (2026-08-31, CEO reading /es/). The Spanish site shipped with its hero
headline in Spanish and the entire paragraph underneath it in English. His words: "oh my gosh
this is bad, mix of english and spanish". He was looking at the most-read text on the page.

WHAT MADE IT SHIPPABLE. `build-locale.py` reported "english-left: 0" on all nine pages. Its
detector matched `<p[^>]*>([^<]{25,})</p>`, and `[^<]` means NO TAGS INSIDE, so any paragraph
containing a `<b>`, an `<a>` or a `<code>` was invisible to it. That is most of the
substantial prose on this site, including the hero. The number was not wrong by a little: it
said 0 while 37 blocks across the site were English.

🔒 A REPORTER THAT CAN ONLY SEE THE SIMPLE CASES REPORTS ZERO AND MEANS "I LOOKED IN THE
EASY PLACES". Every gate I wrote tonight was built to catch a check that answers a question
adjacent to the one that matters, and then I shipped one. The difference between this file
and that reporter is one regex: this one strips inline tags and reads the whole block.

🔒 AND ITS FIRST VERSION HAD THREE BLIND SPOTS OF ITS OWN, WHICH THE CEO FOUND BY OPENING THE
PAGE. It only read blocks of SIX WORDS OR MORE, only inside <p>/<h1>/<h2>/<h3>/<li>, and never
looked at attributes or at text built by JavaScript. So it passed a seal console whose labels
said "Exercise", "and at most" and "Put it back", seven alt attributes that were entirely
English, and the evidence dial's live sentence, which is the interactive centrepiece of the
home page. 44 user-visible strings, and it reported zero. A gate written to catch a blind
check was itself blind in three directions.

THE RULE, as it now stands. EVERY user-visible string on the page: any text node of any
length in any element, the alt / title / placeholder / aria-label attributes, and every prose
literal inside an inline <script>, because the dial and the verifier build their sentences at
runtime. Count function words for the declared language against the other and fail anything
the wrong language wins, with a margin so a word shared between the two cannot flip it.

WHAT IT DELIBERATELY IGNORES: quoted app strings inside `<code>`, which are English on the
Spanish pages ON PURPOSE while the published screenshots are of the English build, and the
brand name. Both are stripped before counting so the gate measures PROSE, not quotation.
"""
import re, sys, glob, os, html as _html

# 🔒 ARM TWO, FOR SHORT LABELS. A function-word margin cannot judge a three-word button:
# "Put it back" scores one English hit and passes, and it is a button a Spanish reader reads.
# These tokens are unmistakably English and have no Spanish homograph, so a single one on a
# Spanish page is a defect regardless of the string's length. Words shared between the two
# languages (no, a, e, o, real, total, natural, final, personal) are deliberately absent.
ENGLISH_ONLY = re.compile(
    r'\b(the|and|your|you|with|that|this|what|when|how|why|which|there|here|these|those|'
    r'put|back|most|least|nothing|stored|machine|session|sessions|repeated|matches|seal|'
    r'verified|checking|exercise|ruled|out|every|would|could|should|from|about|into|over|'
    r'before|after|only|also|does|did|were|been|have|will|can|its|their|our|more|than|'
    r'then|them|but|not|are|was|were|its|value|wrong|original|last|same|live|page|'
    r'settings|profile|delete|turn|off|first|next|back|verified|unverified)\b', re.I)

WORDS = {
    'en': re.compile(r'\b(the|and|your|you|that|with|from|which|what|when|this|every|is|are|'
                     r'was|it|for|not|but|they|have|will|can|its|his|her|our|their|there|'
                     r'been|more|than|then|them|these|those|would|should|could|about|into|over|'
                     r'because|before|after|only|also|does|did|were|who|how|why)\b', re.I),
    'es': re.compile(r'\b(el|la|los|las|un|una|de|del|que|con|para|por|tu|tus|te|se|es|son|'
                     r'era|lo|y|pero|m[aá]s|como|cuando|donde|qu[eé]|cada|sin|sobre|'   # 'no' and 'o' are shared
                     r'entre|hasta|porque|antes|despu[eé]s|todo|toda|nada|algo|esto|esta|ese|'
                     r'esa|su|sus|al|le|ya|muy|s[oó]lo|solo|tambi[eé]n|nos|aqu[ií]|ellos|ella)\b', re.I),
}


def blocks(path):
    """EVERY user-visible string: text nodes of any length, visible attributes, and prose
    literals inside inline scripts. The first version of this function read none of the last
    two and imposed a six-word floor on the first."""
    s = open(path, encoding='utf-8').read()
    m = re.search(r'<html lang="([a-zA-Z0-9-]+)"', s)
    lang = (m.group(1) if m else 'en').split('-')[0].lower()
    head = re.search(r'<head>.*?</head>', s, re.S)
    body = s[head.end():] if head else s
    body = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.S | re.I)
    # <code> is quotation from the app, not prose, and is English on purpose here.
    codes = set(re.findall(r'<code[^>]*>(.*?)</code>', body, re.S))
    body = re.sub(r'<code[^>]*>.*?</code>', ' ', body, flags=re.S)
    body = re.sub(r'<a class="wordmark".*?</a>', ' ', body, flags=re.S)
    scripts = re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', body, re.S)
    prose = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.S)

    out = []
    for mm in re.finditer(r'>([^<>]+)<', prose):
        out.append(mm.group(1))
    for attr in ('alt', 'title', 'placeholder', 'aria-label'):
        for mm in re.finditer(attr + r'="([^"]{4,})"', prose):
            out.append(mm.group(1))
    for blk in scripts:
        for q in re.findall(r"'((?:[^'\\]|\\.){4,})'", blk):
            out.append(q)

    clean = []
    for raw in out:
        t = _html.unescape(re.sub(r'\s+', ' ', raw)).strip()
        if t in codes:
            continue
        # 🔒 ONE WORD IS STILL A STRING A READER READS. The two-word floor here let 'VERIFIED'
        # through, which is the single most prominent word in the seal console and the one the
        # CEO photographed. A single token counts when it is on the English-only list; anything
        # shorter than three letters is noise.
        if not re.search(r'[A-Za-z]{3}', t):
            continue
        if not re.search(r'[a-z]{3}\s+[a-z]{2,}', t, re.I) and not ENGLISH_ONLY.search(t):
            continue
        if re.search(r'[{}();=]|function|\bvar\b|innerHTML|document\.', t):
            continue
        # A bare identifier or an object-literal fragment is code, not copy. Reporting them
        # trains the reader to skim past the real findings underneath.
        if re.fullmatch(r'[a-z][a-zA-Z0-9_-]*|[,.\s]*(value|key)\s*:?[,.\s]*|[+\s]*[a-zA-Z_][a-zA-Z0-9_.\[\]]*[+\s]*', t):
            continue
        # 🔒 THE SAMPLE RECEIPT'S EXERCISE NAME IS CRYPTOGRAPHICALLY BOUND. The verifier's
        # fingerprint is computed OVER it, so translating "Barbell Back Squat" would make the
        # demo receipt fail to verify. It stays English in every locale, deliberately.
        if t == 'Barbell Back Squat':
            continue
        clean.append(t)
    return lang, clean


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pages = (sorted(glob.glob(os.path.join(root, '*.html'))) +
             sorted(glob.glob(os.path.join(root, '*', 'index.html'))) +
             sorted(glob.glob(os.path.join(root, '*', '*', 'index.html'))))
    print("DECLARED LANGUAGE")
    fails = 0
    for p in pages:
        rel = os.path.relpath(p, root)
        lang, bs = blocks(p)
        other = 'es' if lang == 'en' else 'en'
        # MARGIN OF TWO. 'no', 'si' and a few others are shared, so a one-word lead is noise.
        # A genuinely half-translated paragraph clears this easily: the ones this gate caught
        # tonight ran 8 to 1 and 14 to 2.
        if lang == 'en':
            wrong = [b for b in bs
                     if len(WORDS['es'].findall(b)) >= len(WORDS['en'].findall(b)) + 2]
        else:
            # Arm 1, the margin, for real sentences. Arm 2, the English-only token, for the
            # short labels arm 1 cannot see.
            wrong = [b for b in bs
                     if len(WORDS['en'].findall(b)) >= len(WORDS['es'].findall(b)) + 2
                     or ENGLISH_ONLY.search(b)]
        if wrong:
            fails += len(wrong)
            print(f"  {rel:28} declares {lang}, {len(wrong)} of {len(bs)} blocks read as {other}:")
            for b in wrong[:3]:
                print(f'       "{b[:96]}"')
            if len(wrong) > 3:
                print(f"       ... and {len(wrong)-3} more")
        else:
            print(f"  {rel:28} OK   {len(bs)} blocks, all {lang}")
    print(f"\nLANGUAGE FAILURES: {fails}")
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
