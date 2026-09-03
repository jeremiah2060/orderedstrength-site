#!/usr/bin/env bash
# WHAT ONLY THE DEPLOYED SITE CAN ANSWER.
#
# 🔒 check.sh RUNS AGAINST `python3 -m http.server`, WHICH DOES NOT SEND `_headers`. Everything
# in that file, twenty-seven programs, is therefore blind to the response headers: the
# Content-Security-Policy, the cache rules, the redirects Pages performs. On 2026-09-03 the
# local suite was fully green while production refused to run the language diagnostic's inline
# script, because its hash had been left out of script-src. A live run found it in one line.
#
# 🔒 SO A DEPLOY IS NOT FINISHED WHEN THE PUSH SUCCEEDS. Run this after every one.
#
#     tools/verify-live.sh [https://www.orderedstrength.com]
set -uo pipefail
cd "$(dirname "$0")/.."
B="${1:-https://www.orderedstrength.com}"
fail=0
say(){ printf '  %-58s %s\n' "$1" "$2"; }
ok(){ say "$1" "OK  $2"; }
no(){ say "$1" "FAIL  $2"; fail=1; }

echo "VERIFYING $B"

# 1. the policy names exactly the hashes this tree generates, and no longer trusts inline script
want=$(python3 - <<'PY'
import sys; sys.path.insert(0,'tools')
import importlib.util as u
s=u.spec_from_file_location('c','tools/csp-hashes.py'); m=u.module_from_spec(s); s.loader.exec_module(m)
print(len(m.hashes()))
PY
)
got=$(curl -sSI --max-time 25 "$B/" | grep -io "script-src[^;]*" | grep -o "sha256" | wc -l | tr -d ' ')
[ "$got" = "$want" ] && ok "script-src names every inline script" "$got hashes" \
                     || no "script-src names every inline script" "live has $got, the tree generates $want"
curl -sSI --max-time 25 "$B/" | grep -io "script-src[^;]*" | grep -q "unsafe-inline" \
  && no "script-src no longer trusts inline script" "'unsafe-inline' is still there" \
  || ok "script-src no longer trusts inline script" ""

# 2. one Cache-Control per file, and immutable only where a stamp backs it
for u in /assets/site.min.css /assets/site.js /assets/fonts/public-sans-400-latin.woff2; do
  cc=$(curl -sSI --max-time 25 "$B$u" | grep -i "^cache-control" | tr -d '\r' | sed 's/^[Cc]ache-[Cc]ontrol: //')
  case "$cc" in
    *max-age*max-age*) no "$u" "two rules appended into one header: $cc" ;;
    *immutable*)       ok "$u" "$cc" ;;
    *)                 no "$u" "expected immutable, got: $cc" ;;
  esac
done
cc=$(curl -sSI --max-time 25 "$B/assets/lang-check" | grep -i "^cache-control" | tr -d '\r')
case "$cc" in *immutable*) no "/assets/lang-check" "must not be immutable: $cc";;
              *) ok "/assets/lang-check" "revalidates";; esac

# 3. the diagnostic's own script runs, which is what a missing hash silently kills
v=$(curl -sS --max-time 25 "$B/assets/lang-check" | grep -c 'id="verdict"')
[ "$v" = "1" ] && ok "/assets/lang-check is served" "" || no "/assets/lang-check is served" "not found"

# 4. real 404s, and the Spanish one under /es/
for p in /nonexistent-xyz /es/nonexistent-xyz; do
  code=$(curl -sS --max-time 25 -o /tmp/vl.html -w '%{http_code}' "$B$p")
  lang=$(grep -o '<html lang="[^"]*"' /tmp/vl.html | head -1)
  want_lang=en; case "$p" in /es/*) want_lang=es;; esac
  case "$code:$lang" in
    404:*\"$want_lang*) ok "$p" "$code, $lang" ;;
    *) no "$p" "got $code $lang, wanted 404 in $want_lang" ;;
  esac
done

# 5. and the whole language contract, driven by a browser with a real Spanish locale
echo "  running lang-redirect-gate against the deployed site..."
if BASE="$B" node tools/lang-redirect-gate.mjs > /tmp/verify-live-lang.log 2>&1; then
  ok "the language contract" "$(grep -c '^PASS' /tmp/verify-live-lang.log) checks"
else
  no "the language contract" "$(grep -c '^FAIL' /tmp/verify-live-lang.log) failed, see /tmp/verify-live-lang.log"
  grep '^FAIL' /tmp/verify-live-lang.log | head -4 | sed 's/^/      /'
fi

echo
[ $fail -eq 0 ] && echo "LIVE OK" || echo "LIVE NOT OK"
exit $fail
