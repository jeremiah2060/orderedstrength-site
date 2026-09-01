#!/usr/bin/env bash
# THE ONE DOOR for this site. Two checks, and neither can be replaced by looking at it.
#
#   check-site.py    what the source says: shadowed selectors, real tag NESTING (a stack,
#                    not a count: two opposite errors cancel in a count), dead anchors,
#                    unversioned assets, banned symbols, images with no alt text.
#   shot-gate.py     THE PIXELS, CHECKED AGAINST THE CLAIMS. Reads the text out of every
#                    published screenshot with the OS's Vision framework and asserts that
#                    every quoted phrase and every number the page states about it is
#                    actually in it. It also refuses a capture that is not native
#                    resolution, or that is a system permission sheet rather than the app.
#                    (tools/audit-captures.py is its upstream twin: point it at a capture
#                    directory BEFORE choosing which frames to publish.)
#   ring-cause-gate.py A CAPTION MAY NOT EXPLAIN ONE RING WITH ANOTHER RING'S INPUT.
#                    shot-gate proves a quoted phrase is in the pixels; it is blind to a
#                    false CAUSE, and on 2026-08-30 the site shipped "the middle ring
#                    still says Calibration (Building), because this athlete never once
#                    told Jerry how sore he was". Soreness feeds RECOVERY. The refutation
#                    was already on the page: answered.webp shows that same athlete WITH
#                    soreness reported and the ring still empty. Sentence-scoped, so a
#                    caption may still discuss both, just not in one breath.
#   pin-gate.py      THE CALLOUT PINS, AGAINST THE PIXELS THEY POINT AT. The gallery overlays
#                    three numbered pins on a screenshot at hard-coded percentages, and
#                    shot-gate STRIPS `style="..."` before reading claims, so those numbers
#                    were the only figures on this site checked by nobody. A number that
#                    positions something over a photograph is a claim about it.
#   icon-gate.py     THE FAVICON MUST BE THE PRODUCT'S OWN MARK, NOT A DRAWING OF IT. I drew
#                    one: a teal ring with a bar through the top, correct palette, valid SVG,
#                    on all twenty pages, and a picture of a power button. The real mark is a
#                    generated "OS" monogram whose own README says the S is a real SF Pro glyph
#                    "NOT a hand-drawn bezier". 🔒 NOTHING HERE COULD SEE IT: every gate on this
#                    site reads THIS SITE, and the mark it should be checked against lives in
#                    the app's repo. Measured 0.64 for a true downscale, 33.36 for my drawing.
#   pair-gate.py     THE TWO LANGUAGES MUST PHOTOGRAPH THE SAME ATHLETE. Every other gate
#                    here reads ONE PAGE AT A TIME, so a Spanish frame showing a 6% ring under
#                    a Spanish caption saying 6% is internally perfect and passes all of them.
#                    The CEO opened the two home pages side by side on 2026-09-01 and saw two
#                    different lifters. 🔒 A SET OF PER-PAGE GATES CANNOT SEE A DEFECT THAT IS
#                    A RELATIONSHIP BETWEEN PAGES. Also refuses one photograph published twice.
#   voice-gate.py    A SELLING PAGE TALKS TO THE LIFTER, NOT ABOUT ITSELF. Commit b8755c8
#                    closed this on 2026-08-23 ("the site stops describing itself"), and
#                    /stronger/ reopened it seven days later with "We spend most of these
#                    pages proving that Jerry is honest ... This page is the other half".
#                    Two arms: the OPENING may carry zero site-subject sentences, and page
#                    wide the reader must outnumber the site. 🔒 THE FIRST DRAFT HAD ONLY
#                    THE SECOND ARM AND COULD NOT GO RED ON THE REAL PARAGRAPH (6 to 2 on a
#                    page with ten reader sentences). Falsification caught that, not review.
#   translate-gate.py WHAT A NON-ENGLISH READER GETS. The CEO turned on browser auto-translate
#                    to Spanish on 2026-08-31 and the page fell apart, while all seven gates
#                    were green: every one of them reads the ENGLISH DOM. A translator rewrites
#                    the <code> runs that quote the app verbatim, and the hex digests the seal
#                    console and /verify/ depend on, so the translated page claims the app says
#                    things it does not and the one interactive proof stops verifying. Prose
#                    stays translatable on purpose.
#   lang-gate.py     A PAGE IS ACTUALLY WRITTEN IN THE LANGUAGE IT DECLARES. The Spanish site
#                    shipped with a Spanish headline over an English paragraph, and the
#                    BUILDER reported "english-left: 0" on every page because its detector
#                    matched [^<] and could not see a paragraph containing a <b> or an <a>.
#                    37 blocks were English. This one strips inline tags, reads whole blocks,
#                    and counts function words with a margin so a shared word cannot flip a
#                    verdict. It ignores <code>, which is quotation, not prose.
#   (authoring)      tools/quotable.py <image> is shot-gate RUN BACKWARDS: it prints what a
#                    caption is ALLOWED to quote from a frame, and --check tests one phrase.
#                    shot-gate tells you a quote is wrong AFTER you wrote it; this tells you
#                    what the right one is BEFORE. Every caption defect this repo has shipped
#                    came from authoring off MEMORY of a screenshot instead of off the pixels.
#   contrast-gate.py what the EYE cannot judge on a dark screen in a dark room: every
#                    ink-on-surface pair, computed against WCAG 2.1, read out of the
#                    stylesheet's own tokens so it cannot go stale.
#   measure-gate.mjs one specific browser failure that every other check here reports as
#                    clean: a block of running text wrapping one word per line because a
#                    grid or flex placement broke. It has happened twice.
#   type-gate.mjs    THE OPTICAL SIZE OF EVERY INLINE LITERAL, against the sentence holding
#                    it. Whether a quoted <code> run READS as the same size as its prose is
#                    decided by x-height, not by the font-size number, and two families at
#                    one declared size can differ by a fifth. This site shipped .8125em on a
#                    pairing whose x-heights already matched, so 25 literals across three
#                    pages stood 10 to 20% short mid-sentence. Valid CSS, aligned, wrapped,
#                    legible, and reading as a different smaller typeface. Nothing else here
#                    could see it.
#   type-floor-gate.mjs THE RENDERED TYPE FLOOR. Fourteen gates and not one of them looked at
#                    a font SIZE: type-gate compares an inline literal's optical size to its
#                    sentence, contrast reads colour, align reads edges, measure reads
#                    wrapping. So 10px uppercase mono shipped to twenty pages and the CEO
#                    found it. 🔒 IT MEASURES THE RENDER, NOT THE STYLESHEET: an `em` chain
#                    compounds, a media query shrinks at one width only, and an inline style
#                    is in no stylesheet at all. Exemptions are BY NAME, never by pattern.
#   align-gate.mjs   what the BROWSER does: every stacked block inside a section starts on
#                    the same left edge, that edge is the nav wordmark's, and no page
#                    scrolls sideways. Run across the widths people actually use.
#                    🔒 IT COVERS 8 PAGES, NOT 7. This line said 7 until 2026-08-23, when
#                    /join/ made it 8 and nobody re-counted, and the stale number was then
#                    copied out of this comment into two commit messages as though it had
#                    been measured. Derive it: the gate walks $PAGES, so COUNT THE OUTPUT
#                    rather than quoting this header.
#
# A screenshot tells you something feels wrong. These tell you by how many pixels, where.
set -uo pipefail
cd "$(dirname "$0")"
WIDTHS="${WIDTHS:-390 768 1280 1440 1920 2560}"
PORT="${PORT:-8899}"
fail=0

python3 check-site.py || fail=1
echo
python3 tools/shot-gate.py || fail=1
echo
python3 tools/ring-cause-gate.py || fail=1
echo
python3 tools/pin-gate.py || fail=1
echo
python3 tools/icon-gate.py || fail=1
echo
python3 tools/pair-gate.py || fail=1
echo
python3 tools/voice-gate.py || fail=1
echo
python3 tools/translate-gate.py || fail=1
echo
python3 tools/lang-gate.py || fail=1
echo
python3 tools/contrast-gate.py | tail -3 || fail=1

if ! curl -sf -o /dev/null "http://127.0.0.1:${PORT}/"; then
  python3 -m http.server "$PORT" >/dev/null 2>&1 &
  server=$!; trap 'kill $server 2>/dev/null' EXIT
  for _ in $(seq 40); do curl -sf -o /dev/null "http://127.0.0.1:${PORT}/" && break; sleep .25; done
fi
echo
BASE="http://127.0.0.1:${PORT}" node tools/type-floor-gate.mjs || fail=1
echo
BASE="http://127.0.0.1:${PORT}" node tools/align-gate.mjs $WIDTHS || fail=1
echo
BASE="http://127.0.0.1:${PORT}" node tools/measure-gate.mjs 1550 390 | tail -3 || fail=1
echo
BASE="http://127.0.0.1:${PORT}" node tools/type-gate.mjs || fail=1
echo
BASE="http://127.0.0.1:${PORT}" WIDTH=390 node tools/type-gate.mjs | tail -3 || fail=1

echo
[ $fail -eq 0 ] && echo "SITE OK" || echo "SITE NOT OK"
exit $fail
