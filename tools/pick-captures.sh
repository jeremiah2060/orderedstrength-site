#!/usr/bin/env bash
# Audit a capture directory, then build a contact sheet of the frames that PASSED, so the
# choice of what to publish is made from clean frames only. Usage: tools/pick-captures.sh <dir>
set -uo pipefail
D="${1:?capture directory}"
cd "$(dirname "$0")/.."
echo "── audit ──────────────────────────────────────────────"
python3 tools/audit-captures.py "$D" || true
echo
echo "── contact sheet of full-screen English frames ────────"
rm -rf /tmp/pick && mkdir -p /tmp/pick
i=0
for f in "$D"/*.png; do
  case "$f" in *es419*|*AX5*) continue;; esac
  read -r w h < <(sips -g pixelWidth -g pixelHeight "$f" 2>/dev/null | awk '/pixelWidth/{w=$2}/pixelHeight/{h=$2}END{print w, h}')
  [ "${w:-0}" = "1206" ] || continue
  i=$((i+1)); n=$(printf %02d $i)
  sips -Z 700 "$f" --out "/tmp/pick/$n.png" >/dev/null 2>&1
  echo "$n  $(basename "$f" | sed 's/.*__//;s/_0\.png$//')"
done
{ echo '<style>body{margin:0;background:#111;font:11px -apple-system;color:#fff;display:flex;flex-wrap:wrap;gap:6px;padding:6px}figure{margin:0;width:170px}img{width:100%;display:block;border:1px solid #444}figcaption{padding:2px 0;font-size:10px}</style>';
  for p in /tmp/pick/*.png; do b=$(basename "$p" .png); echo "<figure><img src=\"$b.png\"><figcaption>$b</figcaption></figure>"; done; } > /tmp/pick/s.html
echo "contact sheet: /tmp/pick/s.html ($i frames)"
