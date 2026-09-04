#!/usr/bin/env python3
"""Structural checks that a browser screenshot cannot give you, and one that keeps
biting: a rule edited in the SHARED stylesheet does nothing when the same selector
also lives in a page's own <style>, because the page block loads last and wins.
That mistake cost three separate rounds (.stack overflow, .dialhead cap, ol.loop
centring): each time the edit looked applied and changed nothing."""
import re, glob, sys, os, html, hashlib

SHORTHANDS = {
    'margin': ['margin-top','margin-right','margin-bottom','margin-left'],
    'padding': ['padding-top','padding-right','padding-bottom','padding-left'],
    'inset': ['top','right','bottom','left'],
    'background': ['background-color','background-image','background-size','background-position',
                   'background-repeat','background-attachment'],
    'border': ['border-width','border-style','border-color'],
    'border-radius': ['border-radius'],
    'font': ['font-family','font-size','font-weight','line-height'],
    'flex': ['flex-grow','flex-shrink','flex-basis'],
    'grid-area': ['grid-row','grid-column'],
    'transition': ['transition-property','transition-duration','transition-timing-function'],
    'animation': ['animation-name','animation-duration','animation-timing-function','animation-fill-mode'],
}

def props(decl):
    """The property names a declaration block sets, with shorthands expanded.

    🔒 THE SELECTOR IS NOT THE FAILURE; THE SELECTOR PLUS THE PROPERTY IS. Comparing
    selector names alone made this check fire on four rules that set entirely different
    properties in the two sheets, which is the fastest way to teach a person to ignore a
    gate. Expanding shorthands is not optional either: the one REAL collision the day this
    was written was a page saying `margin:0` against a shared sheet saying
    `margin-top:auto`, and a naive name comparison sees two different properties."""
    out = set()
    for line in decl.split(';'):
        if ':' not in line:
            continue
        name = line.split(':', 1)[0].strip().lower()
        if not name or name.startswith('--'):
            continue
        out.update(SHORTHANDS.get(name, [name]))
        if name in SHORTHANDS:
            out.add(name)
    return out


def split_selectors(sel):
    """Split a selector list on TOP-LEVEL commas only.

    🔒 A NAIVE sel.split(',') TEARS :is(), :where() AND :not() IN HALF, and the halves are
    plausible selectors, so the damage is silent. Measured 2026-09-02: the shared sheet gained
    `:where(a,button,summary,input,textarea,select,[tabindex]):focus-visible` and this file
    immediately reported that /verify/'s `textarea{border-radius:10px}` was shadowing the
    shared sheet, because the split had manufactured a bare `textarea` rule that sets
    border-radius. Two pages, one imaginary defect, from a comma inside brackets.

    This file's own docstring says a gate that fires on a non-collision is the fastest way to
    teach someone to ignore it, so the parser owes the same care as the comparison."""
    out, depth, buf = [], 0, ''
    for ch in sel:
        if ch in '([': depth += 1
        elif ch in ')]': depth = max(0, depth - 1)
        if ch == ',' and depth == 0:
            out.append(buf); buf = ''
        else:
            buf += ch
    out.append(buf)
    return out


def rules(css):
    """(selector, properties) for every declaration in a stylesheet, @media unwrapped."""
    flat = re.sub(r'/\*.*?\*/', ' ', css, flags=re.S)
    for _ in range(6):
        flat = re.sub(r'@[a-z-]+[^{}]*\{((?:[^{}]|\{[^{}]*\})*)\}', r'\1', flat)
    for sel, decl in re.findall(r'([^{}]+)\{([^{}]*)\}', flat):
        pr = props(decl)
        if not pr:
            continue
        for part in split_selectors(sel):
            part = part.strip()
            if part and not part.startswith('@'):
                yield part, pr


def selectors(css):
    """Selectors declared in a stylesheet.

    🔒 STRIP @media WRAPPERS FIRST. A naive ([^{}]+)\{([^{}]*)\} sweep cannot parse a
    nested block: it swallows the @media prelude and everything after it silently, so
    the checker skipped real rules and reported a clean sheet. It missed .stack being
    capped at 23rem in a page style while the shared sheet said 100%, which is the exact
    defect class this file exists to catch. Found 2026-08-23 by measuring a card that
    would not stretch."""
    # 🔒 STRIP COMMENTS FIRST. A rule preceded by a /* comment */ parses as the selector
    # "/* comment */\n.stack", which matches nothing, so the rule is invisible to the
    # comparison. The very comment I wrote to explain a rule is what hid it. Measured
    # 2026-08-23: .stack was capped at 23rem in a page style while the shared sheet said
    # 100%, and the checker reported a clean sheet.
    flat = re.sub(r'/\*.*?\*/', ' ', css, flags=re.S)
    for _ in range(6):
        flat = re.sub(r'@[a-z-]+[^{}]*\{((?:[^{}]|\{[^{}]*\})*)\}', r'\1', flat)
    out = set()
    for sel, _decl in re.findall(r'([^{}]+)\{([^{}]*)\}', flat):
        for part in split_selectors(sel):
            part = part.strip()
            if part and not part.startswith('@'):
                out.add(part)
    return out

# 🔒 `es/404.html` MATCHED NONE OF THESE PATTERNS AND SO WAS GATED BY NOTHING.
# `*.html` is root-only, `*/index.html` and `*/*/index.html` both require the name
# `index.html`. A locale's 404 page is the one file that is neither, so it silently sat
# outside every source gate: on 2026-09-01 it was found carrying a duplicated hreflang
# trio, a relative og:image pointing at the ENGLISH share card, no og:locale and no terms
# link, every one of which had been fixed on all nineteen of its siblings. A page nothing
# reads is not a page with no defects. `*/*.html` closes it; the set dedupes the overlap.

# `tools/` holds GENERATOR INPUTS, not published pages: tools/og.html is the share-card
# template and is rendered to a JPEG, never served. Widening the glob to reach es/404.html
# swept it in, and gating a template as though it were a page is how a gate earns the
# reputation that gets it switched off.
pages = sorted(p for p in set(glob.glob('*.html') + glob.glob('*/*.html')
                    + glob.glob('*/*/index.html'))
                    if not p.startswith(('tools/', 'assets/')))
shared = open('assets/site.css', encoding='utf-8').read()
shared_sel = selectors(shared)
fail = 0

shared_rules = {}
for sel, pr in rules(shared):
    shared_rules.setdefault(sel, set()).update(pr)

print("SHADOWED DECLARATIONS (a page style silently beats the shared sheet)")
for f in pages:
    s = open(f, encoding='utf-8').read()
    for blk in re.findall(r'<style[^>]*>(.*?)</style>', s, re.S):
        for sel, pr in rules(blk):
            clash = pr & shared_rules.get(sel, set())
            if clash:
                print(f"  {f}: {sel} {{ {', '.join(sorted(clash))} }}"); fail += 1
print("  none" if not fail else "")

print("\nNESTING")
# 🔒 A TAG-COUNT CHECK CANNOT SEE A MIS-NESTING, AND TWO OPPOSITE ERRORS CANCEL.
# This block used to count `<div` against `</div>` per page. /how-it-works had a .head
# that was never closed (so the four "moments" cards rendered INSIDE the centred 52rem
# header) AND a stray </div> in the last section. Open 6, close 6: the counter reported
# the page clean while the layout it was written to protect was visibly wrong. A stack
# tells you WHERE, and it is the only form of this check worth running.
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param',
        'source','track','wbr'}
TAG = re.compile(r'<(/?)([a-zA-Z][a-zA-Z0-9]*)([^>]*?)(/?)>')
for f in pages:
    s = open(f, encoding='utf-8').read()
    body = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', s, flags=re.S)
    body = re.sub(r'<!--.*?-->', '', body, flags=re.S)
    stack, iss = [], []
    for m in TAG.finditer(body):
        closing, name, attrs, selfclose = m.group(1), m.group(2).lower(), m.group(3), m.group(4)
        if name in VOID or selfclose or name == '!doctype':
            continue
        line = body[:m.start()].count('\n') + 1
        if not closing:
            stack.append((name, line))
        else:
            if not stack:
                iss.append(f'line {line}: </{name}> with nothing open'); continue
            if stack[-1][0] == name:
                stack.pop()
            elif any(n == name for n, _ in stack):
                while stack and stack[-1][0] != name:
                    n, l = stack.pop()
                    iss.append(f'line {line}: </{name}> closes <{n}> opened at line {l}')
                stack.pop()
            else:
                iss.append(f'line {line}: </{name}> with no matching open tag')
    for n, l in stack:
        if n not in ('html', 'body', 'head'):
            iss.append(f'<{n}> opened at line {l} is never closed')
    print(f"  {f:28} {'OK' if not iss else iss[0]}")
    for extra in iss[1:]:
        print(f"  {'':28} {extra}")
    fail += len(iss)

print("\nHYGIENE")
for f in pages:
    s = open(f, encoding='utf-8').read()
    iss = []
    ids = re.findall(r'id="([^"]+)"', s)
    if [i for i in set(ids) if ids.count(i) > 1]: iss.append('duplicate ids')
    if [a[1:] for a in re.findall(r'href="(#[^"]+)"', s) if a[1:] not in ids]: iss.append('dead anchor')
    # 🔒 FONTS ARE EXEMPT FROM VERSIONING, AND THE REASON IS NOT LAZINESS. A font file is
    # already content-addressed by its own name: family, weight and subset fully determine
    # its bytes. Worse, versioning it would DOUBLE-DOWNLOAD it, because the preload lives in
    # the HTML (which the stamper rewrites) while the src lives inside @font-face in the
    # stylesheet (which it does not), so the two URLs would disagree and the browser would
    # fetch the same glyphs twice. They are served immutable for a year instead.
    # 🔒 srcset IS AN ASSET-BEARING ATTRIBUTE AND WAS READ BY NOTHING. This pair of checks
    # looked at href and src only, so the moment responsive images landed (2026-09-02) two
    # thirds of every picture on the home page, twenty files, sat outside both the version
    # check and the existence check. A missing srcset candidate is INVISIBLE by design: the
    # browser silently falls back to another candidate, so the page still looks right on the
    # machine that built it and is wrong on somebody's phone.
    refs = re.findall(r'(?:href|src)="(/assets/[^"]*)"', s)
    for ss in re.findall(r'srcset="([^"]*)"', s):
        for cand in ss.split(','):
            cand = cand.strip().split()
            if cand and cand[0].startswith('/assets/'):
                refs.append(cand[0])
    unversioned = [r for r in refs
                   if '?v=' not in r and not r.startswith('/assets/fonts/')]
    if unversioned: iss.append('unversioned asset: ' + unversioned[0])
    # ...but an asset that does not EXIST is the failure fonts actually risk: a typo in a
    # @font-face src or a preload is invisible, because the page simply falls back to a
    # system face and still looks like a website.
    missing = [r.split('?')[0] for r in refs
               if not os.path.exists('.' + r.split('?')[0])]
    if missing: iss.append('missing asset: ' + missing[0])
    if 'scene narrow' in s: iss.append('stale narrow width')
    # 🔒 DECODE ENTITIES FIRST. This check looked for the literal characters only, so seven
    # banned arrows written as `&rarr;` sat on two live pages while it reported both clean.
    # A rule about what the READER sees has to be applied to what the reader sees.
    decoded = html.unescape(s)
    hits = [ch for ch in ['\u2014', '\u00d7', '\u2192', '\u2190', '\u2191', '\u2193',
                          '\u2265', '\u2264', '\u00b1', '\u2713', '\u2717']
            if ch in decoded]
    if hits: iss.append('banned symbol: ' + ' '.join(hits))
    for m in re.finditer(r'<img\b[^>]*>', s):
        if 'alt=' not in m.group(0): iss.append('img with no alt text')
    print(f"  {f:28} {'OK' if not iss else '; '.join(iss)}")
    fail += len(iss)

print("\nSTAMP")
# 🔒 EVERY PAGE MUST CARRY THE SAME BUILD, AND IT MUST BE THE REAL ONE. Committing with
# explicit paths is correct, and it is also how three pages got left behind: the stamper had
# touched them, the commit had not, so /how-it-works/, /join/ and /record/ shipped pointing
# at a stylesheet version that was one build old and printed a build stamp in the footer
# that was simply wrong. On a site whose argument is that its numbers can be checked, the
# one number nobody types being wrong is not a small thing. This compares every page against
# the stylesheet's ACTUAL hash, so a missed page cannot reach the deploy.
real = hashlib.sha256(open('assets/site.css','rb').read()).hexdigest()[:10]
for f in pages:
    s = open(f, encoding='utf-8').read()
    iss = []
    refs = set(re.findall(r'/assets/site\.css\?v=([0-9a-f]+)', s))
    if refs and refs != {real}: iss.append(f'stylesheet version {"/".join(sorted(refs))}, build is {real}')
    # 🔒 THE FOOTER ARM IS GONE BECAUSE THE FOOTER NUMBER IS GONE (2026-09-01, CEO asked
    # "what is this: Build 110c5b0919, do we even need it really?"). It was a ten-character
    # hex on a page for lifters, and nothing a reader could act on: the verifiability this
    # product actually offers lives at /verify/ and /record/, which are real and checkable.
    # What that arm protected is NOT lost. The load-bearing invariant is the one above: every
    # page's stylesheet ?v= must equal the stylesheet's real hash, which is what stops a page
    # being left behind on a stale cached build. That is the defect that actually happened
    # (three pages shipped one build old), and the footer number was only its symptom.
    # 🔒 SO DO NOT RE-ADD A DISPLAY ARM WITHOUT RE-ADDING A DISPLAY. An absence check for an
    # element that is deliberately absent fails every page forever, which is how a gate gets
    # switched off.
    stamps = set(re.findall(r'<b class="stamp"[^>]*>([^<]*)</b>', s))
    if stamps and stamps != {real}:
        iss.append(f'footer stamp {"/".join(sorted(stamps))}, build is {real}')
    print(f"  {f:28} {'OK' if not iss else '; '.join(iss)}")
    fail += len(iss)

print("\nINLINE SCRIPTS PARSE")
# 🔒 A BROKEN INLINE SCRIPT IS INVISIBLE TO EVERY OTHER GATE IN THIS REPO, AND I SHIPPED ONE
# TODAY. Editing the language-redirect script left a duplicated `catch`, so the whole block was a
# syntax error and did nothing at all. check-site read the HTML and found it well formed. The
# nesting stack, the hygiene sweep, the stamp check, contrast, type, align and measure ALL passed,
# because none of them asks whether the JavaScript on the page can run. Only the browser-driven
# language gate caught it, minutes later and by accident of what it happened to be testing.
# A page can be perfectly valid HTML and completely dead.
#
# node is already a hard dependency of check.sh, so this costs nothing new.
import subprocess, tempfile
SCRIPT = re.compile(r'<script(?![^>]*\ssrc=)[^>]*>(.*?)</script>', re.S)
for f in pages:
    s = open(f, encoding='utf-8').read()
    iss = []
    for i, m in enumerate(SCRIPT.finditer(s)):
        js = m.group(1)
        if not js.strip():
            continue
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as tmp:
            tmp.write(js); tmp_path = tmp.name
        r = subprocess.run(['node', '--check', tmp_path], capture_output=True, text=True)
        os.unlink(tmp_path)
        if r.returncode:
            line = next((l for l in r.stderr.splitlines() if 'Error' in l), r.stderr[:90])
            iss.append(f'script #{i + 1} does not parse: {line.strip()[:90]}')
    print(f"  {f:28} {'OK' if not iss else iss[0]}")
    for extra in iss[1:]:
        print(f"  {'':28} {extra}")
    fail += len(iss)

print("\nCOUNTS ACROSS PAGES")
# 🔒 A NUMBER STATED ON FIVE PAGES IS ONE FACT WITH FIVE PLACES TO BE WRONG. The privacy
# policy said "The five things that can leave your device" while /join/, /how-it-works/ and
# the privacy page's OWN meta description said four, in both languages, for two weeks. Every
# per-page gate was green because every page was internally consistent: the defect is a
# RELATIONSHIP between pages, which is the same class pair-gate.py exists for on photographs.
# 🔒 THE TRUTH IS DERIVED, NOT TYPED. The <h2> on the policy is the authority, so correcting
# the policy corrects the gate, and nobody can satisfy this by editing a constant here.
WORDS = {'four': 4, 'five': 5, 'six': 6, 'cuatro': 4, 'cinco': 5, 'seis': 6}
AUTH = [('app-privacy/index.html', r'The (\w+) things that can leave your device'),
        ('es/app-privacy/index.html', r'Las (\w+) cosas que pueden salir de tu dispositivo')]
# 🔒 SCOPED TO THE PRIVACY CLAIM, BECAUSE THE FIRST DRAFT WAS NOT AND REPORTED A HEADLINE.
# The home page says "Four things most apps never show you" about four SCREENSHOTS, and a
# gate that calls that a privacy-count defect is a gate that teaches you to skim its output.
# The relative clause is the discriminator: this count is always followed by what those
# things DO, "that can leave", "that could", "que pueden", "que podian".
# 🔒 AND THE FIRST SCOPING WAS TOO TIGHT, WHICH IS THE OTHER WAY THIS GATE CAN LIE. It required
# the relative clause, "things THAT can leave", "cosas QUE pueden", and on 2026-09-02 the count
# went from five to six and this reported every page clean while the Spanish policy's own
# opening sentence still read "Cinco cosas pueden salir de tu dispositivo". No relative clause,
# same claim, invisible. A gate that is scoped narrowly enough to avoid false positives can be
# scoped narrowly enough to miss the real thing, and the only way to know which is to write the
# sentence out and check the pattern against it.
CLAIMS = re.compile(r'\b(four|five|six)\s+things\s+(?:that\s+c|can\s+leave)|'
                    r'\b(cuatro|cinco|seis)\s+cosas\s+(?:que\s+p|pueden)', re.I)
for auth_page, auth_rx in AUTH:
    lang = 'es/' if auth_page.startswith('es/') else ''
    src = open(auth_page, encoding='utf-8').read()
    m = re.search(auth_rx, src)
    if not m:
        print(f"  {auth_page}: the authoritative heading is gone, so this gate cannot vouch for the count")
        fail += 1
        continue
    truth = WORDS.get(m.group(1).lower())
    print(f"  authority {auth_page:28} {m.group(1).lower()} = {truth}")
    for f in pages:
        if (f.startswith('es/')) != (lang == 'es/'):
            continue
        text = html.unescape(open(f, encoding='utf-8').read())
        for hit in CLAIMS.finditer(text):
            n = WORDS.get((hit.group(1) or hit.group(2)).lower())
            if n != truth:
                line = text[:hit.start()].count('\n') + 1
                print(f"  {f}:{line} says {hit.group(0)!r}, the policy says {truth}")
                fail += 1

print("\nINPUT SIZE (iOS zooms a focused input below 16px, so tampering fights Safari)")
# 🔒 THE CONSOLE IS THE ONE THING ON THIS SITE A VISITOR IS INVITED TO BREAK, and on a phone
# every tap into it zoomed the page, because iOS Safari zooms any focused control whose text
# is under 16px. Nothing here read a font size: type-floor-gate.mjs measures the RENDER and
# owns legibility at 12px, which a 14px input passes. This is a different question with a
# different floor, and it is a source scan because the rule is about the declared size on a
# control, not about a computed cascade.
# LIMIT, stated rather than hidden: an `em` chain is not resolved here. An em value on a
# control is reported as unmeasurable rather than passed, so it cannot hide under the floor.
CTRL = re.compile(r'\b(input|textarea|select)\b')
def _px(v):
    v = v.strip().lower()
    m = re.fullmatch(r'([\d.]+)(px|rem|em|%)?', v)
    if not m: return None
    n = float(m.group(1)); u = m.group(2) or 'px'
    return n if u == 'px' else n * 16 if u == 'rem' else None
for f in pages + ['assets/site.css']:
    s = open(f, encoding='utf-8').read()
    blocks = re.findall(r'<style[^>]*>(.*?)</style>', s, re.S) if f.endswith('.html') else [s]
    iss = []
    for blk in blocks:
        flat = re.sub(r'/\*.*?\*/', ' ', blk, flags=re.S)
        for _ in range(6):
            flat = re.sub(r'@[a-z-]+[^{}]*\{((?:[^{}]|\{[^{}]*\})*)\}', r'\1', flat)
        for sel, decl in re.findall(r'([^{}]+)\{([^{}]*)\}', flat):
            if not CTRL.search(sel): continue
            for name, val in re.findall(r'([a-z-]+)\s*:\s*([^;]+)', decl):
                if name.strip() != 'font-size': continue
                px = _px(val)
                if px is None:
                    iss.append(f'{sel.strip()} font-size {val.strip()} cannot be resolved here')
                elif px < 16:
                    iss.append(f'{sel.strip()} font-size {val.strip()} = {px:g}px, under the 16px floor')
    print(f"  {f:28} {'OK' if not iss else iss[0]}")
    for extra in iss[1:]:
        print(f"  {'':28} {extra}")
    fail += len(iss)

print("\nEYEBROW PLACEMENT (the number is gone, so the page can no longer tell you)")
# 🔒 THIS CHECK EXISTS BECAUSE A VISIBLE TELL WAS DELETED, 2026-09-04. `.eyebrow` used to
# print the section number through a CSS counter, and site.js hands the SAME index to the
# rail and the bar scale by counting `.eyebrow` elements document-wide. Reusing the class
# as a generic label therefore consumed a number and pushed every real section on that page
# one out of step. It was caught last time because it also SHOWED itself: the verifier's
# `<label class="eyebrow">Receipt JSON</label>` rendered "RECEIPT JSON02" on screen.
#
# The number no longer renders, so that same mistake now renders perfectly and silently
# miscounts the instrument. The failure became an ABSENCE, and absence reads as all-clear.
# The DIAGNOSTIC that decides whether this check is real: name the input that turns it red.
# It is one `<p class="eyebrow">` placed outside `main > .scene`, which is exactly the shape
# of the defect that shipped. --selftest constructs it and proves both arms.
#
# It asks the question site.js asks and not a proxy for it: every `.eyebrow` in the document
# must sit inside a section the rail actually maps, or the indices disagree. It runs on
# pages with three or more scenes because that is the condition site.js builds the rail on.
from html.parser import HTMLParser
EB_VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param',
           'source','track','wbr'}

class _Brows(HTMLParser):
    """Every .eyebrow, and the scene count site.js would compute on the same page.

    A real tag stack, never a count of opening tags: two opposite nesting errors cancel in
    a count, which is the reason the nesting check further up this file is a stack too."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []; self.brows = []; self.scenes = 0
    def handle_starttag(self, tag, attrs):
        cls = (dict(attrs).get('class') or '').split()
        if 'eyebrow' in cls:
            inside = any('scene' in c for _, c in self.stack) and any(
                t == 'main' for t, _ in self.stack)
            self.brows.append((self.getpos()[0], inside))
        if tag == 'section' and 'scene' in cls and self.stack and self.stack[-1][0] == 'main':
            self.scenes += 1
        if tag not in EB_VOID:
            self.stack.append((tag, cls))
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]; return

def eyebrow_issues(src):
    p = _Brows(); p.feed(src)
    if p.scenes < 3:
        return []          # site.js returns early; no rail, nothing to put out of step
    return [ln for ln, inside in p.brows if not inside]

if '--selftest' in sys.argv:
    print("  SELFTEST")
    good = ('<main><section class="scene"><p class="eyebrow">A</p></section>'
            '<section class="scene"><p class="eyebrow">B</p></section>'
            '<section class="scene"><p class="eyebrow">C</p></section></main>')
    bad = good.replace('</main>', '</main><label class="eyebrow">Receipt JSON</label>')
    stray = good.replace('<main>', '<main><p class="eyebrow">Stray</p>')
    for name, doc, want in (('clean page', good, 0),
                            ('label after main', bad, 1),
                            ('eyebrow outside a scene', stray, 1),
                            ('one-section page', '<main><section class="scene">'
                             '<p class="eyebrow">A</p></section></main>', 0)):
        got = len(eyebrow_issues(doc))
        ok = got == want
        print(f"    {name:26} expected {want}, got {got}  {'OK' if ok else 'SELFTEST FAILED'}")
        fail += 0 if ok else 1

for f in pages:
    bad = eyebrow_issues(open(f, encoding='utf-8').read())
    print(f"  {f:28} {'OK' if not bad else 'eyebrow outside main > .scene at line ' + ', '.join(map(str, bad))}")
    fail += len(bad)

print("\nTHIRD-PARTY HOSTS (this site makes no request it does not own)")
# 🔒 A LINK IS NOT A REQUEST, AND CONFLATING THEM WOULD MAKE THIS GATE A LIAR. /record/ links
# to the receipts repository on github.com on purpose: a reader following it is the whole
# point of a public record. What is forbidden is a request the PAGE makes on the reader's
# behalf, which is what api.github.com was: an unauthenticated browser fetch, rate-limited to
# 60 an hour per IP and therefore shared behind carrier NAT, rendering "Could not read the
# repository" to a stranger checking our honesty. So <a href> is exempt BY NAME and every
# other host-bearing position is not.
ALLOWED = {'www.orderedstrength.com', 'orderedstrength.com', 'api.orderedstrength.com'}
RESOURCE = re.compile(r'<(?:link|script|img|iframe|video|source|audio|embed|object|form)\b[^>]*?'
                      r'(?:src|href|action|data)="(https?://[^"]+)"', re.I)
URL = re.compile(r'https?://([a-zA-Z0-9._-]+)')
for f in pages:
    s = open(f, encoding='utf-8').read()
    hosts = set()
    for u in RESOURCE.findall(s):
        hosts.add(URL.match(u).group(1))
    for blk in re.findall(r'<script[^>]*>(.*?)</script>', s, re.S):
        # A script that BUILDS an <a href> is still building a link, not making a request.
        # /record/ writes its "check the repository yourself" link from JS, and reading the
        # host out of that string would report the honest half of the page as the dishonest
        # half. Strip anchor markup the script emits, then read what is left.
        blk = re.sub(r'<a\s[^>]*href=\\?["\']https?://[^"\']+', ' ', blk)
        hosts.update(URL.findall(blk))
    bad = sorted(h for h in hosts if h not in ALLOWED)
    print(f"  {f:28} {'OK' if not bad else 'requests ' + ', '.join(bad)}")
    fail += len(bad)
if os.path.exists('_headers'):
    csp = ''.join(l for l in open('_headers', encoding='utf-8') if 'Content-Security-Policy' in l)
    # frame-ancestors, form-action and base-uri constrain what may point AT us; they name no
    # host we contact, so a host there would be a different question.
    csp = re.sub(r'(frame-ancestors|form-action|base-uri)[^;]*;?', '', csp)
    bad = sorted(h for h in set(URL.findall(csp)) if h not in ALLOWED)
    print(f"  {'_headers CSP':28} {'OK' if not bad else 'permits ' + ', '.join(bad)}")
    fail += len(bad)

print(f"\nFAILURES: {fail}")
sys.exit(1 if fail else 0)
