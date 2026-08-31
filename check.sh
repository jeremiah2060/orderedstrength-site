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
python3 tools/contrast-gate.py | tail -3 || fail=1

if ! curl -sf -o /dev/null "http://127.0.0.1:${PORT}/"; then
  python3 -m http.server "$PORT" >/dev/null 2>&1 &
  server=$!; trap 'kill $server 2>/dev/null' EXIT
  for _ in $(seq 40); do curl -sf -o /dev/null "http://127.0.0.1:${PORT}/" && break; sleep .25; done
fi
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
