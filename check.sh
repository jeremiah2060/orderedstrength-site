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
#   hero-gate.mjs    THE ONE AXIS NOTHING ELSE HERE VARIES: VIEWPORT HEIGHT. Every other gate
#                    sweeps width from 320 to 2560 and fixes height at 900 or 950, which is
#                    taller than most laptops. The hero device is sized by HEIGHT and the
#                    floating card was capped in rem, so on a Windows laptop at 125% scaling the
#                    illustration rendered wider than the product it annotates and its labels
#                    wrapped. Two invariants, neither visible in the source: a floating
#                    annotation is never wider than the thing it annotates, and nothing in it
#                    wraps. Six real device shapes, including the CEO's.
#   lang-redirect-gate.mjs A SPANISH PHONE MUST REACH THE SPANISH SITE, and must not then be
#                    bounced back and forth by two language links that each point at the other.
#                    Driven by a Chrome launched with a real Spanish locale, because stubbing
#                    navigator.language would be testing the stub. 🔒 --lang IS THE WRONG FLAG
#                    and this gate found that by printing the value it branches on.
#   notranslate-gate.py A PAGE THAT IS ALREADY A REAL TRANSLATION MUST DECLINE A MACHINE ONE,
#                    AND A PAGE THAT IS NOT MUST NOT. The CEO, 2026-09-03: "if you switch to
#                    spanish it only appears for a split second then goes back to english
#                    again, but all the screenshots are in spanish, only the content is
#                    bouncing". Text changing while images do not is not a navigation. It was
#                    Chrome's translator, from the "always translate Spanish" he set on
#                    2026-08-31, and nothing on /es/ had ever told a browser not to.
#                    translate-gate guards the ELEMENTS a translator must not rewrite and is
#                    right about every one; it has no opinion about whether the PAGE should be
#                    translated at all, and on a page where a real translation already exists a
#                    machine pass can only subtract. 🔒 TWO-SIDED: English stays translatable on
#                    purpose, so this goes red in both directions. --selftest proves both arms.
#   lang-switch-gate.mjs CAN A PERSON CHANGE LANGUAGE WITHOUT SCROLLING. Not: does the link
#                    work. lang-redirect-gate walks the whole loop green, because it reaches the
#                    link with querySelector and clicks it. Measured at 390px before the fix:
#                    the only language link on this site sat 13,566px down the English home page
#                    and 14,512px down the Spanish one, 16.1 and 17.2 SCREENS, in the same week
#                    the site gained the power to move a reader into a language they never
#                    chose. 🔒 AND A LAYOUT BOX IS NOT A PAINTED PIXEL: its first draft read
#                    getBoundingClientRect, which a closed <details> still answers, and reported
#                    zero taps on every phone. checkVisibility asks what was meant.
#   minify-css.py --check  THE STYLESHEET THE BROWSER GETS IS WHAT THIS SOURCE GENERATES.
#                    assets/site.css is 96,745 bytes and 58% of it is comment, because the
#                    comments here carry the laws and the CDP measurements. Right for the source,
#                    wrong for the wire, and it is render-blocking. Measured with brotli at
#                    quality 11, which is what Cloudflare serves: 26,918 bytes as published,
#                    7,813 with comments removed, so 19,105 bytes off every first visit. The
#                    pages link the generated twin and every source gate keeps reading the
#                    source; --check regenerates and byte-compares so the two cannot drift.
#   css-equiv.mjs    AND THE GENERATED STYLESHEET MUST PARSE INTO THE SAME STYLESHEET AS ITS
#                    SOURCE. minify-css.py --check proves the artifact is what the CURRENT
#                    stripper produces, which is a statement about the generator agreeing with
#                    itself: edit one line of that function and it stays green on a sheet that
#                    renders differently. This links both files from a bare page and reads them
#                    back through the CSSOM, where cssText on a grouping rule serializes its
#                    children, so the comparison is the browser's own canonical form of the whole
#                    sheet. 260 rules and 41,923 characters on both sides. One deleted
#                    declaration turns it red and it prints the character where they diverge.
#   print-gate.mjs   WHAT THIS SITE LOOKS LIKE ON PAPER, which nothing here had ever asked.
#                    There was no @media print block at all, and a browser does not print
#                    background colours unless the page asks, so near-white ink on a ground the
#                    printer drops came out white on white. The two pages most likely to be
#                    printed are the two the app itself links to, /terms/ and /app-privacy/.
#                    🔒 EVERY OTHER GATE HERE MEASURES THE SCREEN, so a whole output medium was
#                    untested, the same shape as the viewport-height axis hero-gate closed.
#                    Its selftest runs the same assertions in screen media, which is exactly what
#                    a printer was handed before: 60 of 80 go red there.
#   headers-gate.py  TWO RULES IN _headers THAT SET THE SAME HEADER FOR ONE FILE DO NOT
#                    OVERRIDE, THEY APPEND. Written after shipping exactly that on 2026-09-03:
#                    `/assets/*` at an hour followed by specific rules at a year produced
#                    `cache-control: public, max-age=3600, must-revalidate, public,
#                    max-age=31536000, immutable` on the live domain. Two max-age directives and
#                    must-revalidate beside immutable, in one header, so the effect was the hour
#                    that was already there: no regression and none of the improvement, which is
#                    the worst shape a change can have because it looks deployed. 🔒 THE DEFECT
#                    IS INVISIBLE IN THE FILE; both rules read correctly alone. It walks the real
#                    files rather than intersecting globs in the abstract, and it also refuses an
#                    immutable rule over a file some page links with no ?v=.
#   webkit-gate.mjs  THE SAME SITE, IN THE OTHER ENGINE. Every other browser-driven gate in this
#                    file launches /Applications/Google Chrome.app through measure.mjs, so the
#                    engine was the one axis nothing here had ever varied, the same shape as the
#                    viewport height before hero-gate. 🔒 AND IT WAS ALMOST FILED AS IMPOSSIBLE:
#                    the first attempt reached for `safaridriver --enable`, which asks for an
#                    administrator password, and the conclusion drafted from that was that the
#                    axis could not be closed without the CEO. That was a conclusion about one
#                    ROUTE. A WebKit build is a download and needs no password. It is a MACHINE
#                    PREREQUISITE, exactly like the Chrome binary measure.mjs hard-codes, and it
#                    lives OUTSIDE this repository on purpose:
#                      npm install --prefix ~/.orderedstrength-site-tools playwright
#                      npx --prefix ~/.orderedstrength-site-tools playwright install webkit
#                    🔒 A package.json AND node_modules IN THE TREE BROKE THE VERY NEXT RUN:
#                    bar-gate reported "24 colliding, over 6 widths on 24" for a twenty-page
#                    site, because nineteen of the walkers here derive their own page list, on
#                    purpose, and node_modules is full of HTML. Patching all nineteen is a fix
#                    that is wrong the first time someone writes the twentieth.
#                    It asks the five things that differ between engines rather than between
#                    widths: every inline script runs, the header language control is reachable,
#                    the bar does not collide and no page scrolls sideways, a Spanish locale
#                    reaches the Spanish site and its English link comes back and stays, and
#                    print media lays down a light ground. 🔒 ITS FIRST SELFTEST DEFEATED ITSELF
#                    on a specificity tie and bit 5 times out of 40; it bits 60 of 122 now, and
#                    5 of 40 is a number worth being suspicious of.
#   csp-hashes.py --check  THE POLICY MUST NAME EVERY INLINE SCRIPT IN THE TREE. script-src
#                    stopped saying 'unsafe-inline' and started naming eight SHA-256 hashes, and
#                    the failure mode of a hash is the worst one here: a stale one does not
#                    error, the browser simply refuses the script, and the page renders perfectly
#                    and does nothing. This is the source half, exact and instant.
#   csp-gate.mjs     AND THE RUNTIME HALF, BECAUSE python3 -m http.server DOES NOT SEND _headers.
#                    Every other browser-driven gate here runs against a server that omits the
#                    policy, so all of them would stay green with every script on the site
#                    blocked in production. This one serves the repo under the real `/*` block
#                    and asserts what each script PRODUCES. 🔒 ITS OWN SELFTEST CAUGHT TWO OF ITS
#                    FIRST CHECKS BEING DECORATIVE: #hash and #verdict ship as static no-script
#                    markup, so reading them reported on the HTML, not the script. It counts the
#                    64 per-character elements only the script can render, and presses a preset
#                    to make the fingerprint recompute. 24 of 24 go red on a corrupted policy.
#   engine-gate.py   WHAT A BROWSER THAT IS NOT CHROME GETS. Every browser-driven check in this
#                    file launches the same binary, so the engine is the axis nothing here has
#                    ever varied, which is the shape of the height hole hero-gate closed. Driving
#                    a second engine needs an administrator password (safaridriver --enable) or a
#                    vendored WebKit, so this checks the DISCIPLINE instead: a Chrome-first
#                    property is declared inside an @supports that TESTS it, that guard has a
#                    matching "@supports not" fallback, and a prefixed property keeps its pair.
#                    🔒 The stylesheet's own comment states the failure: without the guard "a
#                    browser that does not know animation-timeline would run these keyframes once
#                    against the document timeline". Exemptions by name, with the reason.
#   bar-gate.mjs     THE ONE COMPONENT ON EVERY SCREEN OF THIS SITE MUST NOT COLLIDE WITH ITSELF.
#                    Adding one header link on 2026-09-03 put the wordmark and the nav at a gap of
#                    0px from 900 to 980px in English and 1000 to 1072px in Spanish, on all twenty
#                    pages, with every gate here green: align reads left edges, measure reads
#                    wrapping, type reads size, hero reads the hero, and none asks whether two
#                    things in the bar are touching. 🔒 THIS MEASUREMENT WAS TAKEN BY HAND TWICE
#                    AND WRITTEN INTO A COMMENT BOTH TIMES, which protects the width it was taken
#                    at and nothing else. Thirty widths, and it counts TOP offsets rather than box
#                    heights, because padding raises a height and only a top says a label wrapped.
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
python3 tools/notranslate-gate.py || fail=1
echo
python3 tools/minify-css.py --check || fail=1
echo
python3 tools/csp-hashes.py --check || fail=1
echo
python3 tools/headers-gate.py || fail=1
echo
python3 tools/engine-gate.py || fail=1
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
BASE="http://127.0.0.1:${PORT}" node tools/hero-gate.mjs | tail -3 || fail=1
echo
BASE="http://127.0.0.1:${PORT}" node tools/lang-redirect-gate.mjs | tail -3 || fail=1
echo
BASE="http://127.0.0.1:${PORT}" node tools/lang-switch-gate.mjs | tail -3 || fail=1
echo
BASE="http://127.0.0.1:${PORT}" node tools/bar-gate.mjs | tail -3 || fail=1
echo
node tools/csp-gate.mjs | tail -3 || fail=1
echo
BASE="http://127.0.0.1:${PORT}" node tools/css-equiv.mjs | tail -3 || fail=1
echo
BASE="http://127.0.0.1:${PORT}" node tools/print-gate.mjs | tail -3 || fail=1
echo
BASE="http://127.0.0.1:${PORT}" node tools/webkit-gate.mjs | tail -3 || fail=1
echo
BASE="http://127.0.0.1:${PORT}" node tools/type-gate.mjs || fail=1
echo
BASE="http://127.0.0.1:${PORT}" WIDTH=390 node tools/type-gate.mjs | tail -3 || fail=1

echo
[ $fail -eq 0 ] && echo "SITE OK" || echo "SITE NOT OK"
exit $fail
