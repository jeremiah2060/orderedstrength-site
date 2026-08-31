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

THE RULE. For every page, take each visible block of six words or more, count function words
belonging to the page's declared language against those of the other, and fail the block if
the wrong language wins. Function words are the right instrument because they are frequent,
short, and impossible to avoid in real prose, which is exactly what a half-translated
paragraph is full of.

WHAT IT DELIBERATELY IGNORES: quoted app strings inside `<code>`, which are English on the
Spanish pages ON PURPOSE while the published screenshots are of the English build, and the
brand name. Both are stripped before counting so the gate measures PROSE, not quotation.
"""
import re, sys, glob, os, html as _html

WORDS = {
    'en': re.compile(r'\b(the|and|your|you|that|with|from|which|what|when|this|every|is|are|'
                     r'was|it|for|not|but|they|have|has|will|can|its|his|her|our|their|there|'
                     r'been|more|than|then|them|these|those|would|should|could|about|into|over|'
                     r'because|before|after|only|also|does|did|were|who|how|why)\b', re.I),
    'es': re.compile(r'\b(el|la|los|las|un|una|de|del|que|con|para|por|tu|tus|te|se|es|son|'
                     r'era|lo|y|pero|m[aá]s|como|cuando|donde|qu[eé]|cada|sin|sobre|'   # 'no' and 'o' are shared
                     r'entre|hasta|porque|antes|despu[eé]s|todo|toda|nada|algo|esto|esta|ese|'
                     r'esa|su|sus|al|le|ya|muy|s[oó]lo|solo|tambi[eé]n|nos|aqu[ií]|ellos|ella)\b', re.I),
}


def blocks(path):
    s = open(path, encoding='utf-8').read()
    # [a-zA-Z-] cannot match es-419: the region subtag has DIGITS in it, so every Spanish
    # page read as English and the gate reported the whole site backwards on its first run.
    m = re.search(r'<html lang="([a-zA-Z0-9-]+)"', s)
    lang = (m.group(1) if m else 'en').split('-')[0].lower()
    s = re.sub(r'<(script|style|head)[^>]*>.*?</\1>', '', s, flags=re.S | re.I)
    # Quoted app strings and the wordmark are not prose and must not be counted.
    s = re.sub(r'<code[^>]*>.*?</code>', ' ', s, flags=re.S)
    s = re.sub(r'<a class="wordmark".*?</a>', ' ', s, flags=re.S)
    out = []
    for m in re.finditer(r'<(p|h1|h2|h3|li|figcaption)[^>]*>(.*?)</\1>', s, re.S):
        t = _html.unescape(re.sub(r'<[^>]+>', ' ', m.group(2)))
        t = re.sub(r'\s+', ' ', t).strip()
        if len(t.split()) >= 6:
            out.append(t)
    return lang, out


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
        wrong = [b for b in bs
                 if len(WORDS[other].findall(b)) >= len(WORDS[lang].findall(b)) + 2]
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
