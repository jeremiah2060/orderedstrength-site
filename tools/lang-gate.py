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

WHAT IT DELIBERATELY IGNORES: quoted app strings inside `<code>` on the ENGLISH pages, and the
brand name. Both are stripped before counting so the gate measures PROSE, not quotation.
Quotations on a Spanish page are no longer ignored wholesale: see the block in blocks() for who
owns them now, and for the decorative fix that falsification caught before it shipped.
"""
import re, sys, glob, os, html as _html, urllib.parse

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
    # 🔒 `original` WAS HERE AND IT IS THE SAME WORD IN SPANISH, so this list violated its own
    # rule three lines up and flagged a perfectly Spanish sentence. A shared word in an
    # "unmistakably English" list is worse than a missing one: a false red teaches the next
    # reader to skim the output.
    r'then|them|but|not|are|was|were|its|value|wrong|last|same|live|page|'
    r'settings|profile|delete|turn|off|first|next|back|verified|unverified|'
    # 🔒 SINGLE-WORD BADGES, WHICH ARM THREE PROVABLY CANNOT SEE. The parallel-text arm
    # compares whole strings and needs two words and six characters to be worth judging, so
    # a one-word status chip is invisible to it by construction. These four are exactly that
    # class: `cut` sat untranslated in the Spanish hero mockup beside `registrada`, and
    # `free` and `testing` sat in the Spanish PRICING chips, and all three arms of this gate
    # passed the page. Keep this list to words that appear as a bare label with no Spanish
    # homograph; it is not the place to chase prose.
    r'cut|logged|withdrawn|free|testing)\b', re.I)

# shot-gate.py reads these two pages, and only these two, because they are the only pages that
# publish photographs. Anything outside this set has no pixel check behind its quotations.
SHOT_GATE_COVERS = {'index.html', 'es/index.html'}

# 🔒 THE SAMPLE RECEIPT'S EXERCISE NAME IS CRYPTOGRAPHICALLY BOUND: the verifier's fingerprint is
# computed OVER it, so translating it would make the demo receipt fail to verify on the Spanish
# page. It stays English in every locale, deliberately, and that is why this is a named list and
# not a blanket skip.
QUOTATIONS_DELIBERATELY_ENGLISH = {'Barbell Back Squat'}

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


def blocks(path, rel_page=''):
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
    # 🔒 THE HEAD AND THE HREFS. A mailto's subject and body are the words the reader SENDS,
    # and on /es/join/ they were English: a Spanish visitor pressing "Escríbenos" got a draft
    # asking three questions in English, which is the primary action this whole site requests.
    # The meta description is what a search engine prints under /es/, and og:description and
    # og:image:alt are what a person sees when the Spanish page is shared. All four were
    # English, and no gate here read an attribute in <head> or an href.
    src_head = head.group(0) if head else ''
    for mm in re.finditer(r'(?:name|property)="(?:description|og:description|og:title|og:image:alt|twitter:description)" content="([^"]+)"', src_head):
        out.append(mm.group(1))
    for mm in re.finditer(r'href="(mailto:[^"]+)"', s):
        q = urllib.parse.unquote(_html.unescape(mm.group(1)))
        for part in re.findall(r'(?:subject|body)=([^&]*)', q):
            out.append(part.replace('\n', ' '))
    # 🔒 PAIR THE QUOTES FIRST, THEN FILTER BY LENGTH. NEVER THE OTHER WAY ROUND.
    #
    # This read `'((?:[^'\\]|\\.){4,})'`, folding a "skip short noise" rule INTO the pairing.
    # A quoted string shorter than four characters therefore fails to match, and the engine
    # walks on and pairs that string's CLOSING quote with the NEXT string's OPENING one. From
    # the first short literal onwards, every boundary is off by one and the gate is reading the
    # gaps BETWEEN strings while believing it is reading the strings.
    #
    # MEASURED on es/index.html, 2026-09-01: two three-character literals, `' / '` and `' : '`,
    # desynchronised the whole block. 131 "strings" came out and the evidence dial's copy was in
    # none of them, so the gate passed a Spanish page whose central interactive proof renders
    # ENTIRELY IN ENGLISH by default: "I do not know you yet. Until your own sets exist I start
    # from population averages...". That is the most important text on /es/ and three arms of
    # this gate reported it clean.
    #
    # 🔒 AN OPTIMISATION INSIDE A MATCHER IS NOT AN OPTIMISATION, IT IS A DIFFERENT MATCHER.
    # Pairing first yields 107 real strings and finds the dial immediately.
    for blk in scripts:
        # A `//` comment is a note to an engineer, not a string a reader sees, and the verifier's
        # own comment ('never say "not verified"') was being reported as untranslated copy.
        # Guard the `://` in a URL so an href inside a script survives.
        blk = re.sub(r'(?<!:)//[^\n]*', '', blk)
        # A CSS class assigned to className is markup, not prose: 'tag you' and 'lstate live'
        # were both reported, and neither is a sentence anybody reads.
        classes = set(re.findall(r'className\s*=\s*[\'"]([^\'"]*)[\'"]', blk))
        for q in re.findall(r"'((?:[^'\\\n]|\\.)*)'", blk):
            if len(q) >= 4 and q not in classes:
                out.append(q)
        # Double-quoted literals were never read at all, and a page that builds a sentence with
        # them would be as invisible as the dial was.
        for q in re.findall(r'"((?:[^"\\\n]|\\.)*)"', blk):
            if len(q) >= 4:
                out.append(q)

    # 🔒 WHO OWNS A QUOTED STRING ON A NON-ENGLISH PAGE, AND WHY IT IS NOT THIS FILE.
    #
    # The <code> exemption here was load-bearing and it expired (2026-09-01). Quotations were
    # skipped because they were English ON PURPOSE on the Spanish pages while the published
    # screenshots were of the English build. That was correct the day it was written and became
    # wrong the evening the Spanish captures started working, and this gate went on reporting
    # /es/ clean while 21 English literals sat inside Spanish sentences.
    #
    # 🔒 MY FIRST FIX WAS DECORATIVE AND FALSIFICATION IS THE ONLY REASON IT IS NOT SHIPPED.
    # I fed non-English quotations through the ENGLISH_ONLY arm, watched the suite stay green,
    # and then injected the exact original defect: `(Construyendo)` back to
    # `Calibration (Building)`. STILL GREEN. Neither word is on that list, which is a list of
    # function words, and an app label is not a function word. The check ran correctly and
    # answered a question adjacent to the one that mattered.
    #
    # THE GATE THAT ACTUALLY HOLDS THIS LINE IS shot-gate.py, for a better reason than vocabulary:
    # an English quotation on the Spanish page is not in the Spanish pixels, so it fails as a
    # false claim about a photograph. Same injection, shot-gate: RED. Do not rebuild a second
    # vocabulary check here and imagine it is a safety net.
    #
    # WHAT IS GENUINELY UNCOVERED, and what the arm below is for: shot-gate reads the two HOME
    # pages only, because they are the only pages that publish photographs. A <code> run added
    # to any OTHER non-English page is therefore checked by NOTHING. There is exactly one today
    # and it is deliberately English (the verifier's sample receipt, whose fingerprint is
    # computed over the exercise name). So the rule is: on a non-English page outside shot-gate's
    # reach, a quotation must be declared here or it is a finding.
    #
    # 🔒 AND THE SECOND ATTEMPT WAS DECORATIVE TOO, FOR A DIFFERENT REASON. I first appended these
    # into `out`, which then runs the prose filter below: it requires `[a-z]{3}\s+[a-z]{2,}`, and
    # `Calibration (Building)` has a bracket where that test wants a letter, so the injection was
    # dropped before it could be judged. TWO decorative fixes in a row on one line of defence.
    # An app label is not a sentence, so it does not go down the sentence path: it returns on its
    # own channel and is reported on its own terms.
    undeclared = []
    if lang != 'en' and rel_page not in SHOT_GATE_COVERS:
        for c in codes:
            t = _html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', c))).strip()
            # A fragment carrying a JS concatenation is markup this page BUILDS at runtime, not
            # a string it quotes from the app, so there are no pixels it could ever be checked
            # against. `build-locale.py` draws the same line with the same test, deliberately:
            # two tools disagreeing about what counts as a quotation is how one of them starts
            # getting ignored. First run of this arm found `calculada '+computed+'` on
            # /es/verify/ and it is exactly that shape.
            if t and "'+" not in t and t not in QUOTATIONS_DELIBERATELY_ENGLISH:
                undeclared.append(t)

    clean = []
    for raw in out:
        t = _html.unescape(re.sub(r'\s+', ' ', raw)).strip()
        if t in codes and lang == 'en':
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
    return lang, clean, undeclared


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 🔒 `es/404.html` MATCHED NONE OF THESE PATTERNS AND SO WAS GATED BY NOTHING.
    # `*.html` is root-only, `*/index.html` and `*/*/index.html` both require the name
    # `index.html`. A locale's 404 page is the one file that is neither, so it silently sat
    # outside every source gate: on 2026-09-01 it was found carrying a duplicated hreflang
    # trio, a relative og:image pointing at the ENGLISH share card, no og:locale and no terms
    # link, every one of which had been fixed on all nineteen of its siblings. A page nothing
    # reads is not a page with no defects. `*/*.html` closes it; the set dedupes the overlap.
    pages = sorted(p for p in set(glob.glob(os.path.join(root, '*.html')) +
                                  glob.glob(os.path.join(root, '*', '*.html')) +
                                  glob.glob(os.path.join(root, '*', '*', 'index.html')))
                   if not os.path.relpath(p, root).startswith(('tools/', 'assets/')))
    print("DECLARED LANGUAGE")
    fails = 0
    for p in pages:
        rel = os.path.relpath(p, root)
        lang, bs, undeclared = blocks(p, rel)
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
        if undeclared:
            fails += len(undeclared)
            print(f"  {rel:28} {len(undeclared)} quoted app string(s) with no pixel check behind them:")
            for q in undeclared:
                print(f'       <code>{q[:80]}</code>')
            print(f"       shot-gate reads only {sorted(SHOT_GATE_COVERS)}, so a quotation here is")
            print(f"       unverifiable. Move the claim to a page with a photograph, or declare it")
            print(f"       in QUOTATIONS_DELIBERATELY_ENGLISH with the reason.")
        if wrong:
            fails += len(wrong)
            print(f"  {rel:28} declares {lang}, {len(wrong)} of {len(bs)} blocks read as {other}:")
            for b in wrong[:3]:
                print(f'       "{b[:96]}"')
            if len(wrong) > 3:
                print(f"       ... and {len(wrong)-3} more")
        elif not undeclared:
            print(f"  {rel:28} OK   {len(bs)} blocks, all {lang}")
    print(f"\nLANGUAGE FAILURES: {fails}")
    return 1 if fails else 0


def run():
    a = main()
    b = parallel_main()
    return 1 if (a or b) else 0


# ═══════════════════════════════════════════════════════════════════════════════════════════
# ARM THREE: PARALLEL TEXT. A Spanish node identical to its English twin is untranslated.
#
# 🔒 WHY A THIRD ARM, AFTER TWO VOCABULARY ARMS ALREADY EXISTED. On 2026-09-01 the Spanish
# home page carried `in testing`, `per year`, `free` and `cut` as visible text, and three of
# those four sat in the PRICING BLOCK, which is the most commercial section on the site. Both
# existing arms read the page and both passed it: the margin arm needs a sentence and these are
# two-word chips, and the ENGLISH_ONLY arm is a list of function words, which "testing", "free",
# "per" and "cut" are not.
#
# 🔒 THE ANSWER TO A LIST THAT KEEPS MISSING WORDS IS NOT A LONGER LIST. Every miss so far was
# a word nobody thought to add, and adding those four would have fixed exactly those four. This
# arm asks a question with no vocabulary in it at all: the Spanish page is built from the English
# one by substitution, so any visible string that survived IDENTICAL is a substitution that did
# not happen. It cannot be defeated by an unusual word, and it needs no dictionary.
#
# WHAT IS LEGITIMATELY IDENTICAL, and therefore declared rather than guessed: the brand, product
# and platform names, physical units and the readouts built from them, and the acronyms the app
# itself does not translate. Anything else identical across the pair is a finding.
SHARED_BY_DESIGN = re.compile(
    r'^(?:'
    r'OrderedStrength|Jerry|iPhone|iOS|Apple|Apple Health|TestFlight|App Store|Anthropic|Microsoft Azure'
    r'|RIR|e1RM|1RM|SHA-256|JSON|GitHub|VERIFIED|Español|English'
    # An address, a URL and a hex digest are the same string in every language, and two of
    # these are CRYPTOGRAPHIC: the seal console's digest and its field block are what the page
    # recomputes in the reader's browser, so translating a character of them breaks the one
    # interactive proof on the site.
    r'|[\w.+-]+@[\w.-]+\.\w+'
    r'|(?:https?://)?(?:www\.)?[\w.-]+\.(?:com|dev|org|io)(?:/\S*)?'
    r'|[0-9a-f]{32,64}'
    r'|scheme os-commit-v1-sha256.*'
    # Pure readouts: "102.5 kg / 6 reps / RIR 1". Units and digits, no words to translate.
    r'|[\d\s.,:%+/·-]*\d[\d\s.,:%+/·-]*(?:\s*(?:kg|h|H|reps?|RIR|min|s)\b[\d\s.,:%+/·-]*)*'
    r')$', re.I)


def parallel_text(es_rel, root):
    """Visible strings on a Spanish page that are byte-identical to the English page's."""
    en_rel = es_rel[3:] if es_rel.startswith('es/') else es_rel
    en_path, es_path = os.path.join(root, en_rel), os.path.join(root, es_rel)
    if not os.path.exists(en_path):
        return None, []

    def visible(path):
        s = open(path, encoding='utf-8').read()
        body = s[s.index('</head>'):] if '</head>' in s else s
        body = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', body, flags=re.S)
        # <code> quotes the app. On /es/ those are the app's Spanish, and the ones that are
        # deliberately identical (the bound receipt name) are declared in the set above.
        body = re.sub(r'<code[^>]*>.*?</code>', ' ', body, flags=re.S)
        out = set()
        for m in re.finditer(r'>([^<>]+)<', body):
            t = _html.unescape(re.sub(r'\s+', ' ', m.group(1))).strip()
            if len(re.findall(r'[A-Za-zÀ-ſ]{2,}', t)) >= 2 and len(t) >= 6:
                out.add(t)
        for attr in ('alt', 'title', 'aria-label', 'placeholder'):
            for m in re.finditer(attr + r'="([^"]{12,})"', body):
                out.add(_html.unescape(re.sub(r'\s+', ' ', m.group(1))).strip())
        return out

    shared = visible(en_path) & visible(es_path)
    return en_rel, sorted(t for t in shared if not SHARED_BY_DESIGN.match(t))


def parallel_main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("\nPARALLEL TEXT (a Spanish string identical to the English one is untranslated)")
    fails = 0
    for p in sorted(glob.glob(os.path.join(root, 'es', '*.html'))) + \
             sorted(glob.glob(os.path.join(root, 'es', '*', 'index.html'))):
        rel = os.path.relpath(p, root)
        en_rel, shared = parallel_text(rel, root)
        if en_rel is None:
            print(f"  {rel:28} no English twin, skipped")
            continue
        if shared:
            fails += len(shared)
            print(f"  {rel:28} {len(shared)} string(s) identical to {en_rel}:")
            for t in shared[:6]:
                print(f'       "{t[:88]}"')
            if len(shared) > 6:
                print(f"       ... and {len(shared)-6} more")
        else:
            print(f"  {rel:28} OK   nothing survived untranslated")
    print(f"\nPARALLEL TEXT FAILURES: {fails}")
    return fails


if __name__ == '__main__':
    sys.exit(run())
