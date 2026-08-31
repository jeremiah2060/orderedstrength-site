#!/usr/bin/env python3
"""Pull the app's OWN wording for every string this site quotes, in any locale it ships.

THE RULE THIS TOOL EXISTS TO ENFORCE, and it is the whole localisation strategy in one line:

    THIS SITE DOES NOT TRANSLATE THE APP. IT QUOTES IT.

Every `<code>` run on this site is a claim that the product says exactly that, and
`shot-gate.py` proves it against the pixels of a published screenshot. A translated site
therefore cannot be a translation of THIS site. Its quoted strings have to come out of the
app's own catalog for that locale, and its screenshots have to be the app running in it.
Hand those quotations to a translator, human or machine, and the Spanish page starts claiming
the app says things it does not, in a language no gate here can check.

The CEO hit the machine version of this on 2026-08-31 with browser auto-translate. This is the
door that makes the honest version cheap: the app is 9,874 of 9,875 strings translated into
Spanish, so the expensive half of a Spanish site is already paid for and sitting in
Localizable.xcstrings.

    python3 tools/app-strings.py es          # every quoted string, with the app's Spanish
    python3 tools/app-strings.py es --missing # only the ones the catalog cannot answer

WHAT "MISSING" MEANS, because it is not always a defect: a run of text that the app composes
at runtime out of several catalog keys has no single row to look up. Those are the ones a
human has to handle deliberately, and naming them is most of this tool's value.
"""
import json, re, sys, glob, os

CATALOG = os.path.expanduser(
    '~/Desktop/OrderedStrength22/OrderedStrength2/Localizable.xcstrings')


def quoted_strings():
    """Every distinct app string the site puts in a <code> run."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    found = set()
    for f in sorted(glob.glob(os.path.join(root, '*.html'))) + \
             sorted(glob.glob(os.path.join(root, '*', 'index.html'))):
        src = open(f, encoding='utf-8').read()
        for m in re.findall(r'<code[^>]*>(.*?)</code>', src, re.S):
            t = re.sub(r'<[^>]+>', '', m).strip()
            # Percentages and numbers are readings, not wording: they change per capture and
            # are not catalog rows. The shot gate already checks them against the pixels.
            if t and not re.fullmatch(r'[\d.,%\s]+|.*\d+\.\d+ kg', t):
                found.add(t)
    return sorted(found)


def catalog(locale):
    d = json.load(open(CATALOG, encoding='utf-8'))['strings']
    out = {}
    for k, v in d.items():
        unit = ((v.get('localizations') or {}).get(locale) or {}).get('stringUnit') or {}
        if unit.get('value'):
            out[k] = unit['value']
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip().split('\n\n')[-1]); return 2
    locale = sys.argv[1]
    only_missing = '--missing' in sys.argv
    if not os.path.exists(CATALOG):
        print(f"  the app catalog is not at {CATALOG}, so this run can vouch for nothing")
        return 1
    cat = catalog(locale)
    strings = quoted_strings()
    have = [s for s in strings if s in cat]
    miss = [s for s in strings if s not in cat]

    print(f"THE APP'S OWN {locale.upper()} FOR WHAT THIS SITE QUOTES\n")
    if not only_missing:
        for s in have:
            print(f"  {s[:46]:48} -> {cat[s]}")
        print()
    if miss:
        print(f"  NOT A SINGLE CATALOG ROW ({len(miss)}). Composed at runtime or a fragment of a")
        print("  longer key; a human decides these, and they are where the real work is:")
        for s in miss:
            print(f"    {s}")
        print()
    print(f"  {len(have)} of {len(strings)} come free from the app. "
          f"{len(miss)} need a person.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
