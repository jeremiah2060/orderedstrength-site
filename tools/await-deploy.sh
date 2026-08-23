#!/usr/bin/env bash
# Poll the preview until it serves THIS commit's content.
# 🔒 NEVER POLL THE STYLESHEET HASH. It only moves when the CSS moves, so an HTML-only or
# asset-only deploy reports DEPLOYED instantly and you verify the previous build. That has
# now happened twice. Poll a string the change actually altered, passed in as $1 (must be
# ABSENT once deployed) or $2 (must be PRESENT).
set -uo pipefail
B="${BASE:-https://redesign-elite.orderedstrength-site.pages.dev}"
GONE="${1:-}"; WANT="${2:-}"; PATH_="${3:-/}"
for i in $(seq 1 15); do
  BODY=$(curl -s --max-time 20 "$B$PATH_" || true)
  ok=1
  [ -n "$GONE" ] && echo "$BODY" | grep -q -- "$GONE" && ok=0
  [ -n "$WANT" ] && ! echo "$BODY" | grep -q -- "$WANT" && ok=0
  [ $ok -eq 1 ] && { echo "deployed after $i check(s)"; exit 0; }
  sleep 20
done
echo "NOT DEPLOYED after 15 checks"; exit 1
