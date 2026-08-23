#!/usr/bin/env bash
# THE ONE DOOR for this site. Two checks, and neither can be replaced by looking at it.
#
#   check-site.py    what the source says: shadowed selectors, real tag NESTING (a stack,
#                    not a count: two opposite errors cancel in a count), dead anchors,
#                    unversioned assets, banned symbols, images with no alt text.
#   align-gate.mjs   what the BROWSER does: every stacked block inside a section starts on
#                    the same left edge, that edge is the nav wordmark's, and no page
#                    scrolls sideways. Run across the widths people actually use.
#
# A screenshot tells you something feels wrong. These tell you by how many pixels, where.
set -uo pipefail
cd "$(dirname "$0")"
WIDTHS="${WIDTHS:-390 768 1280 1440 1920 2560}"
PORT="${PORT:-8899}"
fail=0

python3 check-site.py || fail=1

if ! curl -sf -o /dev/null "http://127.0.0.1:${PORT}/"; then
  python3 -m http.server "$PORT" >/dev/null 2>&1 &
  server=$!; trap 'kill $server 2>/dev/null' EXIT
  for _ in $(seq 40); do curl -sf -o /dev/null "http://127.0.0.1:${PORT}/" && break; sleep .25; done
fi
echo
BASE="http://127.0.0.1:${PORT}" node tools/align-gate.mjs $WIDTHS || fail=1

echo
[ $fail -eq 0 ] && echo "SITE OK" || echo "SITE NOT OK"
exit $fail
