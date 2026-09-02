#!/usr/bin/env bash
# CAN THIS DOMAIN PROVE ITS OWN MAIL IS ITS OWN?
#
# WHY THIS EXISTS (2026-09-02). The site's only call to action is an email address. The domain
# published no sender records at all, which costs two things at once: replies to testers are
# scored as unauthenticated and can land in spam, and anybody can send mail that claims to be
# from this domain and nothing contradicts them. Publishing the three records is DNS work at the
# registrar, which is the CEO's, and this file is what turns "I pasted them" into "they work".
#
# 🔒 A CHECK THAT CAN ONLY EVER SAY NO IS NOT A CHECK. Today all three of these are absent, so a
# gate that just reports failure looks identical to a gate whose parser is broken. `--selftest`
# runs the same three tests against a domain that HAS all three, so the answer YES is proven
# reachable before the answer NO is trusted. Run it whenever you doubt the result.
#
#     tools/check-mail-dns.sh                 check orderedstrength.com
#     tools/check-mail-dns.sh <domain>        check any domain
#     tools/check-mail-dns.sh --selftest      prove the three tests can pass
set -uo pipefail

check() {
  local d="$1" fail=0 v

  # ── SPF ────────────────────────────────────────────────────────────────────────────────
  # 🔒 MORE THAN ONE spf1 RECORD IS WORSE THAN NONE. RFC 7208 says a domain publishing two
  # results in PermError, and receivers treat that as no policy at all, so a well-meant second
  # record silently disables the first.
  v=$(dig +short TXT "$d" | tr -d '"' | grep -c 'v=spf1' || true)
  if [ "$v" -eq 0 ]; then
    echo "  SPF     MISSING     nothing authorises a server to send as $d"
    echo "          fix   TXT  @   v=spf1 include:_spf.google.com ~all"
    fail=1
  elif [ "$v" -gt 1 ]; then
    echo "  SPF     $v RECORDS   two spf1 records is a permanent error and counts as none"
    fail=1
  else
    v=$(dig +short TXT "$d" | tr -d '"' | grep 'v=spf1')
    if echo "$v" | grep -q '_spf.google.com'; then
      echo "  SPF     OK          $v"
    else
      echo "  SPF     PRESENT     but it does not include _spf.google.com, and the MX is Google"
      echo "          found $v"
      fail=1
    fi
  fi

  # ── DKIM ───────────────────────────────────────────────────────────────────────────────
  # The selector is Google Workspace's default. It cannot be typed by hand: the key is
  # GENERATED in the Admin console and the TXT value is what that screen gives you.
  v=$(dig +short TXT "google._domainkey.$d" | tr -d '"' | tr -d ' ')
  if [ -z "$v" ]; then
    echo "  DKIM    MISSING     mail is not signed, so a receiver cannot tell a forgery from you"
    echo "          fix   admin.google.com > Apps > Google Workspace > Gmail > Authenticate email"
    echo "                generate the key, publish the TXT it prints at google._domainkey, then START AUTHENTICATION"
    fail=1
  elif ! echo "$v" | grep -q 'p='; then
    echo "  DKIM    BROKEN      a record exists but carries no public key (p=)"
    fail=1
  else
    echo "  DKIM    OK          $(echo "$v" | cut -c1-58)..."
  fi

  # ── DMARC ──────────────────────────────────────────────────────────────────────────────
  v=$(dig +short TXT "_dmarc.$d" | tr -d '"')
  if [ -z "$v" ]; then
    echo "  DMARC   MISSING     nothing tells a receiver what to do with a forgery"
    echo "          fix   TXT  _dmarc   v=DMARC1; p=quarantine; rua=mailto:jeremiah@$d"
    fail=1
  elif ! echo "$v" | grep -q 'v=DMARC1'; then
    echo "  DMARC   BROKEN      a record exists at _dmarc but is not a DMARC policy"
    fail=1
  else
    echo "  DMARC   OK          $v"
  fi
  return $fail
}

if [ "${1:-}" = "--selftest" ]; then
  # 🔒 ONE SELFTEST DOMAIN IS NOT ENOUGH, AND THE FIRST DRAFT USED ONE AND FAILED ITSELF.
  # It ran all three arms against google.com, which publishes SPF and DMARC but does NOT sign
  # with the `google` DKIM selector: that selector belongs to Google Workspace CUSTOMERS, and
  # Google's own mail uses its own. So the selftest reported DKIM MISSING on a domain chosen to
  # prove DKIM works, which would have been read as a broken parser. Each arm is proved against
  # a domain that actually publishes the record that arm reads. Stripe is a Workspace customer
  # on the default selector, which is exactly the shape this domain will have.
  echo "SELFTEST: each test proved against a domain that really publishes that record"
  rc=0
  echo "  -- SPF and DMARC, against google.com --"
  a=$(check google.com); echo "$a" | grep -E "SPF|DMARC" | grep -v "^ *fix"
  echo "$a" | grep -q "SPF     OK"   || { echo "  SELFTEST: the SPF test cannot see a real SPF record";   rc=1; }
  echo "$a" | grep -q "DMARC   OK"   || { echo "  SELFTEST: the DMARC test cannot see a real DMARC record"; rc=1; }
  echo "  -- DKIM at the google selector, against stripe.com --"
  b=$(check stripe.com); echo "$b" | grep "DKIM"
  echo "$b" | grep -q "DKIM    OK"   || { echo "  SELFTEST: the DKIM test cannot see a real DKIM record";  rc=1; }
  echo
  [ $rc -eq 0 ] && echo "SELFTEST PASSED: all three tests can report OK, so a NO below is real." \
                || echo "SELFTEST FAILED: a test cannot see a record that exists. Fix this file first."
  exit $rc
fi

D="${1:-orderedstrength.com}"
echo "MAIL AUTHENTICATION for $D  ($(date '+%Y-%m-%d %H:%M'))"
check "$D"
rc=$?
echo
if [ $rc -eq 0 ]; then
  echo "ALL THREE PUBLISHED. Send one message to a Gmail address and open"
  echo "'Show original': SPF, DKIM and DMARC should all read PASS."
else
  echo "NOT ALL PUBLISHED. Records live at the registrar: Squarespace Domains,"
  echo "nameservers ns-cloud-d1..d4.googledomains.com."
fi
exit $rc
