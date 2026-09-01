#!/usr/bin/env bash
# Audit a capture directory, then build a contact sheet of the frames that PASSED, so the
# choice of what to publish is made from clean frames only. Usage: tools/pick-captures.sh <dir>
set -uo pipefail
D="${1:?capture directory}"
cd "$(dirname "$0")/.."
echo "── audit ──────────────────────────────────────────────"
python3 tools/audit-captures.py "$D" || true
echo
# 🔒 THIS TOOL SKIPPED EVERY SPANISH FRAME BY DESIGN, AND THAT IS HOW THE SPANISH SITE ENDED UP
# PUBLISHING ENGLISH PHOTOGRAPHS. The filter below read `*es419*|*AX5*) continue`, and its own
# header said "full-screen ENGLISH frames". So when the Spanish captures started working, the
# frames existed, were approved, were native resolution and were correct, and the one tool a
# human uses to CHOOSE what to publish could not show them a single one. Nothing was broken and
# nothing was reported: the candidates were simply never offered.
# Usage: tools/pick-captures.sh <dir> [en|es]   (default en, as before)
LANG_ARM="${2:-en}"
case "$LANG_ARM" in
  en) SKIP='*es419*' ; LABEL="English" ;;
  es) SKIP='!es419'  ; LABEL="Spanish" ;;
  *)  echo "unknown language arm: $LANG_ARM (expected en or es)"; exit 2 ;;
esac
echo "── contact sheet of full-screen $LABEL frames ────────"
rm -rf /tmp/pick && mkdir -p /tmp/pick
i=0
for f in "$D"/*.png; do
  case "$f" in *AX5*) continue;; esac
  if [ "$LANG_ARM" = en ]; then
    case "$f" in *es419*) continue;; esac
  else
    case "$f" in *es419*) ;; *) continue;; esac
  fi
  read -r w h < <(sips -g pixelWidth -g pixelHeight "$f" 2>/dev/null | awk '/pixelWidth/{w=$2}/pixelHeight/{h=$2}END{print w, h}')
  [ "${w:-0}" = "1206" ] || continue
  i=$((i+1)); n=$(printf %02d $i)
  sips -Z 700 "$f" --out "/tmp/pick/$n.png" >/dev/null 2>&1
  echo "$n  $(basename "$f" | sed 's/.*__//;s/_0\.png$//')"
done
{ echo '<style>body{margin:0;background:#111;font:11px -apple-system;color:#fff;display:flex;flex-wrap:wrap;gap:6px;padding:6px}figure{margin:0;width:170px}img{width:100%;display:block;border:1px solid #444}figcaption{padding:2px 0;font-size:10px}</style>';
  for p in /tmp/pick/*.png; do b=$(basename "$p" .png); echo "<figure><img src=\"$b.png\"><figcaption>$b</figcaption></figure>"; done; } > /tmp/pick/s.html
echo "contact sheet: /tmp/pick/s.html ($i frames)"
