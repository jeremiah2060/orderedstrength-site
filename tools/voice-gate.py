#!/usr/bin/env python3
"""A selling page talks TO the lifter. It does not talk ABOUT itself.

WHY THIS EXISTS (2026-08-30, CEO reading the page, CD-010). `/stronger/` opened with
"We spend most of these pages proving that Jerry is honest ... This page is the other half".
Two of that page's sentences had the WEBSITE as their subject, in the first paragraph, on a
page whose job is the reader's body. The CEO read it and asked whether it could go out.

IT WAS A REOPENED DEFECT, NOT A NEW ONE. Commit b8755c8 on 2026-08-23 is titled "The site
stops describing itself and starts talking to the man holding the bar", and its message
records the audit's headline measurement: on the whole homepage exactly ONE sentence had the
reader as its subject. That was raised to five. Seven days later I shipped a new page at a
1:1 ratio and nothing noticed, because nothing was counting.

WHAT ELSE WAS BLIND. shot-gate checks quoted phrases against pixels. ring-cause-gate checks
that one ring is not explained by another's input. type, align, contrast and measure check
rendering. Every one of them passed a paragraph that argued with the company's own stated
moat, because none of them reads for SUBJECT. This is CLAUDE.md's "a check structurally
incapable of seeing what is wrong": they answered the question adjacent to the one that
mattered.

THE RULE, IN TWO ARMS, AND THE FIRST DRAFT HAD ONLY THE SECOND ONE.

  ARM 1, POSITIONAL: the OPENING of a selling page, its h1 and the paragraph under it, may
  contain ZERO sentences whose subject is the site. This is the arm that catches the real
  defect, and position is why. The opening is the only paragraph most readers finish.

  ARM 2, RATIO: across the whole page, reader-subject sentences must outnumber site-subject
  ones. Not "no we", which would be absurd and would gut the honest disclosures this site is
  built on: outnumber.

🔒 ARM 2 ALONE CANNOT SEE THIS DEFECT, AND I SHIPPED IT THAT WAY FOR ONE MINUTE. Falsified
against the CEO's actual paragraph: the page carries ten reader-subject sentences, so two
site-subject ones in the FIRST PARAGRAPH still passed a ratio test 6 to 2. A gate that
cannot go red on the defect it was written for is documentation, not protection, and the
only reason this one is not still documentation is that the falsification step was run
rather than assumed.

WHY THE OTHER PAGES ARE EXEMPT, each named rather than waved at. /record/ is a page about
our own published record, so "we" IS its subject. /app-privacy/, /terms/ and /support/ are legal and
utility pages where first-person plural is what a policy is written in. /verify/ is a tool.
/404.html has two sentences. Gating those would be a checker inventing a defect, which is as
useless as one that misses the real thing and fails in the direction that gets checkers
switched off.
"""
import re, sys, glob, os, html as _html

# The pages whose job is to sell. Only these are gated; see the docstring for the rest.
_SELLING_EN = ['index.html', 'how-it-works/index.html', 'stronger/index.html', 'join/index.html']
# 🔒 THE LOCALE SET IS DERIVED, NEVER RETYPED. A hand-copied second list is how this repo's
# screens gate ended up naming three classes while the files held ten.
SELLING = set(_SELLING_EN) | {'es/' + p for p in _SELLING_EN}

# 🔒 A GATE WITH ONLY ENGLISH PATTERNS SCORES A SPANISH PAGE 0 TO 0 AND CALLS IT A FAILURE.
# Shipped that way for one run on 2026-08-31: /es/how-it-works/ and /es/join/ both came back
# "reader 0, site 0", which is not a verdict about the page, it is the gate admitting it
# cannot read it. A checker that returns the same number for "perfect" and "unintelligible"
# is worse than no checker, because the number looks like a measurement.
READER = re.compile(
    r'^(you|your|he\b|jerry\b|both halves|muscle comes|the (set|weight|reps|bar|plate|number|second half)'
    r'|t[uú]\b|te\b|tus\b|usted\b|[ée]l\b|decide|mira|mantiene|cada|una bit[aá]cora|un plan'
    r'|un wearable|un chatbot|el (peso|m[uú]sculo|coach|n[uú]mero|d[ií]a|registro)|la (carga|serie|fuerza|mayor[ií]a)'
    r'|no viniste|terminas|agregas|sigues|estrategia|acercarse|ponerse)', re.I)
SITE   = re.compile(
    r'^(we\b|this (page|site)\b|these pages\b|the (page|site)\b|our (site|pages)\b'
    r'|nosotros\b|esta (p[aá]gina|web|secci[oó]n)\b|estas p[aá]ginas\b|nuestro sitio\b|este sitio\b)', re.I)


def prose(path):
    s = open(path, encoding='utf-8').read()
    s = re.sub(r'<(script|style|head|nav|footer)[^>]*>.*?</\1>', '', s, flags=re.S | re.I)
    blocks = re.findall(r'<(?:p|h1|h2|h3)[^>]*>(.*?)</(?:p|h1|h2|h3)>', s, re.S)
    txt = ' '.join(_html.unescape(re.sub(r'<[^>]+>', ' ', b)) for b in blocks)
    txt = re.sub(r'\s+', ' ', txt)
    return [x.strip() for x in re.split(r'(?<=[.!?])\s+', txt) if len(x.split()) > 3]


def prose_opening(path):
    """The h1 and the paragraph directly under it. A reader who bounces read only this."""
    s = open(path, encoding='utf-8').read()
    head = re.search(r'<h1[^>]*>.*?</p>', s, re.S)
    if not head:
        return []
    txt = _html.unescape(re.sub(r'<[^>]+>', ' ', head.group(0)))
    txt = re.sub(r'\s+', ' ', txt)
    return [x.strip() for x in re.split(r'(?<=[.!?])\s+', txt) if len(x.split()) > 3]


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("VOICE")
    fails = 0
    for name in sorted(SELLING):
        path = os.path.join(root, name)
        if not os.path.exists(path):
            print(f"  {name:28} MISSING from the repo, so this gate cannot vouch for it")
            fails += 1
            continue
        sents = prose(path)
        opening = prose_opening(path)
        reader = [x for x in sents if READER.match(x)]
        site = [x for x in sents if SITE.match(x)]
        bad_open = [x for x in opening if SITE.match(x)]
        page_fail = False
        if bad_open:                                    # ARM 1, the one that matters
            page_fail = True
            print(f"  {name:28} OPENING talks about the site, not to the reader. "
                  f"{len(bad_open)} sentence(s) in the h1 and the paragraph under it:")
            for x in bad_open:
                print(f"       site-subject: \"{x[:110]}\"")
        if len(site) >= len(reader):                    # ARM 2, the page-wide drift
            page_fail = True
            print(f"  {name:28} reader {len(reader)}, site {len(site)} page-wide. A selling page "
                  f"may not talk about itself as often as it talks to the reader.")
        if page_fail:
            fails += 1
        else:
            print(f"  {name:28} OK   opening clean, reader {len(reader)}, site {len(site)}")
    print(f"\nVOICE FAILURES: {fails}")
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
