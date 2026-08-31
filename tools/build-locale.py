#!/usr/bin/env python3
"""Build a localised page from the English one by SUBSTITUTION, never by rewriting.

WHY SUBSTITUTION. Every page here carries structure the gates depend on: the section
scaffold align-gate measures, the ids the seal console drives, the `<code translate="no">`
runs shot-gate asserts against pixels, the build stamp check-site verifies. Hand-rewriting a
page in Spanish would silently drop one of those and the first anyone would know is a red
gate at best, or a quietly unverified Spanish page at worst. So the English file is the
skeleton and only visible text moves.

WHAT THIS REFUSES TO DO, and the refusal is the point:

  * It will not translate a `<code>` run. Those quote the app verbatim. Their Spanish comes
    from the app's own catalog through `app-strings.py`, and any that the catalog cannot
    answer must be passed in EXPLICITLY, so a missing one fails loudly here instead of
    reaching a Spanish reader as an English fragment or an invented sentence.
  * It will not leave an untranslated string silently. Anything not covered by the map is
    reported, with a count, and the caller decides.

USAGE
    from build_locale import build
    build('index.html', 'es/index.html', TEXT, CODES, lang='es-419')
"""
import re, os, sys, html as _html

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _protect(s):
    """Regions whose text must never be touched by a text substitution pass.

    🔒 <code> IS IN HERE, AND IT WAS NOT UNTIL 2026-08-31. Those runs quote the app, so their
    language is decided by the code_map alone. Leaving them exposed to the prose pass let the
    chrome key 'Build' -> 'Compilación' rewrite the quoted string "Calibration (Building)"
    into "Calibration (Compilacióning)" on the Spanish home page: a corrupted word inside a
    claim about what the product says, which is the worst possible place for one. The type
    gate caught it by measuring the literal, not by reading it.
    """
    spans = []
    for m in re.finditer(r'<script[^>]*>.*?</script>|<style[^>]*>.*?</style>|<code[^>]*>.*?</code>',
                         s, re.S):
        spans.append((m.start(), m.end()))
    return spans


def build(src_rel, out_rel, text_map, code_map, lang='es-419', link_prefix='/es',
          script_map=None):
    src = open(os.path.join(REPO, src_rel), encoding='utf-8').read()
    s = src

    # 1. QUOTED APP STRINGS FIRST, and only from the map handed in. An unmapped <code> run is
    #    an error, not a fallback: shipping the English inside a Spanish sentence is exactly
    #    the mixed-language mess browser auto-translate produced.
    unmapped = []
    for m in re.findall(r'<code[^>]*>(.*?)</code>', s, re.S):
        t = re.sub(r'<[^>]+>', '', m).strip()
        # A fragment containing a JS concatenation is markup this page BUILDS, not a string it
        # quotes from the app. Reporting it as unmapped teaches the reader to ignore the report.
        if (t and t not in code_map and "'+" not in t
                and not re.fullmatch(r'[\d.,%\s]+|.*\d+\.\d+ kg', t)):
            unmapped.append(t)
    for en, es in code_map.items():
        s = s.replace(f'>{en}<', f'>{es}<')

    # 2. VISIBLE PROSE, longest first so a short key cannot eat part of a longer sentence.
    #
    # 🔒 MATCHED WHITESPACE-TOLERANTLY, BECAUSE THE SOURCE WRAPS ITS PARAGRAPHS. The first cut
    #    used a literal find(), so every key spanning a line break in the HTML silently missed
    #    and the page shipped that sentence in English. The reporter below caught it, which is
    #    the only reason it is not still happening: a substitution that quietly does nothing is
    #    indistinguishable from one that had nothing to do.
    protected = _protect(s)
    def in_protected(i):
        return any(a <= i < b for a, b in protected)
    for en in sorted(text_map, key=len, reverse=True):
        es = text_map[en]
        pat = re.compile(r'\s+'.join(re.escape(w) for w in en.split()))
        out, i = [], 0
        for m in pat.finditer(s):
            if m.start() < i:
                continue
            out.append(s[i:m.start()])
            out.append(m.group(0) if in_protected(m.start()) else es)
            i = m.end()
        out.append(s[i:])
        s = ''.join(out)
        protected = _protect(s)

    # 2b. USER-FACING TEXT BUILT BY SCRIPTS. The pass above deliberately skips script bodies,
    #     because substituting blind inside JavaScript rewrites identifiers and breaks the page.
    #     But several pages BUILD sentences a reader reads (the record ledger's empty states,
    #     the verifier's verdicts), and leaving those English is how a Spanish page ends up
    #     bilingual the moment anything loads. They are passed in explicitly, one at a time.
    if script_map:
        def sub_scripts(m):
            blk = m.group(0)
            for en, es in sorted(script_map.items(), key=lambda kv: -len(kv[0])):
                blk = blk.replace(en, es)
            return blk
        s = re.sub(r'<script(?![^>]*\bsrc=)[^>]*>.*?</script>', sub_scripts, s, flags=re.S)

    # 3. LANGUAGE AND LINKS.
    s = s.replace('<html lang="en">', f'<html lang="{lang}">', 1)
    # Page links move into the locale. Assets do NOT: they are shared, and rewriting them
    # would 404 every font and stylesheet. An in-page anchor on the home page ("/#seal") is a
    # PAGE link and was missed by the first cut of this regex, which sent a Spanish reader
    # back to the English home page from inside the Spanish site.
    s = re.sub(r'href="/(?!es/|assets/)([a-z0-9-]*/?)(#[a-zA-Z0-9-]+)?"',
               lambda m: f'href="{link_prefix}/{m.group(1)}{m.group(2) or ""}"', s)

    # 3b. THE LANGUAGE SWITCHER POINTS THE OTHER WAY, and it has to be flipped AFTER the link
    #     rewrite above or it gets dragged into /es/ with every other page link, leaving the
    #     Spanish site with a button to itself labelled "Español".
    s = s.replace('<a href="/es/" class="opt" hreflang="es" lang="es" translate="no">Espa&ntilde;ol</a>',
                  '<a href="/" class="opt" hreflang="en" lang="en" translate="no">English</a>')

    # 4. hreflang, so a search engine and a browser both know the pair exists.
    canon = '/' + out_rel.replace('es/', '', 1).replace('index.html', '')
    alt = (f'<link rel="alternate" hreflang="en" href="https://www.orderedstrength.com{canon}">\n'
           f'<link rel="alternate" hreflang="es" href="https://www.orderedstrength.com/es{canon}">\n'
           f'<link rel="alternate" hreflang="x-default" href="https://www.orderedstrength.com{canon}">\n')
    s = s.replace('<link rel="stylesheet"', alt + '<link rel="stylesheet"', 1)

    os.makedirs(os.path.dirname(os.path.join(REPO, out_rel)), exist_ok=True)
    open(os.path.join(REPO, out_rel), 'w', encoding='utf-8').write(s)

    # 5. WHAT IS STILL ENGLISH. Reported, never swallowed.
    body = re.sub(r'<(script|style|head)[^>]*>.*?</\1>', '', s, flags=re.S)
    left = []
    for m in re.finditer(r'<(p|h1|h2|h3|span|b|li|figcaption)[^>]*>([^<]{25,})</\1>', body):
        t = _html.unescape(m.group(2)).strip()
        if t in text_map.values():
            continue
        # A crude but effective tell: English function words a Spanish sentence never carries.
        if re.search(r'\b(the|and|your|that|with|from|which|what|when|this|every)\b', t, re.I):
            left.append(t)
    return {'unmapped_code': unmapped, 'untranslated': left}


if __name__ == '__main__':
    print(__doc__)
