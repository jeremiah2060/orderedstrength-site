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
  local d="$1" fail=0 v ns at

  # 🔒 ASK THE DOMAIN'S OWN NAMESERVERS, NEVER THE LOCAL RESOLVER. Measured 2026-09-02, live:
  # the SPF record was added at the registrar, was visible within fifteen seconds on 8.8.8.8,
  # and this script reported it MISSING for the next four hours. Nothing was wrong with the
  # record. The apex TXT had been queried earlier the same day, the answer had no SPF in it,
  # and the local resolver was serving that cached answer for the zone's 4-hour TTL.
  #
  # A verification tool that reads a cache is not verifying, it is remembering, and it fails in
  # the WORST direction: it tells you the thing you just did did not work, so you go and do it
  # again, and the second attempt is how a domain ends up with two SPF records, which is a
  # permanent error and the exact failure this script warns about further down.
  ns=$(dig +short NS "$d" 2>/dev/null | head -1)
  at=${ns:+@$ns}

  # ── SPF ────────────────────────────────────────────────────────────────────────────────
  # 🔒 MORE THAN ONE spf1 RECORD IS WORSE THAN NONE. RFC 7208 says a domain publishing two
  # results in PermError, and receivers treat that as no policy at all, so a well-meant second
  # record silently disables the first.
  v=$(dig +short TXT "$d" $at | tr -d '"' | grep -c 'v=spf1' || true)
  if [ "$v" -eq 0 ]; then
    echo "  SPF     MISSING     nothing authorises a server to send as $d"
    echo "          fix   TXT  @   v=spf1 include:_spf.google.com ~all"
    fail=1
  elif [ "$v" -gt 1 ]; then
    echo "  SPF     $v RECORDS   two spf1 records is a permanent error and counts as none"
    fail=1
  else
    v=$(dig +short TXT "$d" $at | tr -d '"' | grep 'v=spf1')
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
  v=$(dig +short TXT "google._domainkey.$d" $at | tr -d '"' | tr -d ' ')
  if [ -z "$v" ]; then
    echo "  DKIM    MISSING     mail is not signed, so a receiver cannot tell a forgery from you"
    echo "          fix   admin.google.com > Apps > Google Workspace > Gmail > Authenticate email"
    echo "                generate the key, publish the TXT it prints at google._domainkey, then START AUTHENTICATION"
    fail=1
  elif ! echo "$v" | grep -q 'p='; then
    echo "  DKIM    BROKEN      a record exists but carries no public key (p=)"
    fail=1
  else
    # 🔒 A DKIM RECORD THAT PARSES IS NOT A DKIM RECORD THAT WORKS. The key is a 400-character
    # base64 blob a human copies out of a WRAPPED box in the Google Admin console, and a record
    # with the right prefix and some p= value satisfies every "is DKIM set up" checker on the
    # web while failing every message silently. So decode it and make OpenSSL agree.
    #
    # 🔒 AND HERE IS WHAT THIS CANNOT SEE, MEASURED RATHER THAN ASSUMED (2026-09-02). Corrupting
    # a real published key one way at a time:
    #     one character DROPPED     REJECTED
    #     one character ADDED       REJECTED
    #     TRUNCATED half way        REJECTED
    #     one character SUBSTITUTED accepted, parses as a valid key of the same size
    # The rejected three are the LENGTH-SHIFTING class, which is exactly what copying out of a
    # wrapped box produces: a missed line or a duplicated one. A substitution keeps the DER
    # structure intact and yields a structurally perfect key that is simply the WRONG key, and
    # no amount of local parsing can know that, because the right key lives in Google's console
    # and nowhere else. THE ONLY COMPLETE PROOF IS AN END-TO-END SIGNED MESSAGE: send one mail
    # to a Gmail address and read Show original. That is not belt and braces, it is the only
    # arm that closes this gap, which is why it is printed as the last step below.
    local key bits
    key=$(echo "$v" | sed -n 's/.*[;[:space:]]p=\([A-Za-z0-9+/=]*\).*/\1/p')
    if [ -z "$key" ]; then
      echo "  DKIM    BROKEN      p= is present but empty or not base64"
      fail=1
    else
      bits=$( { echo "-----BEGIN PUBLIC KEY-----"; echo "$key" | fold -w 64; echo "-----END PUBLIC KEY-----"; } \
              | openssl pkey -pubin -noout -text 2>/dev/null | sed -n 's/.*Public-Key: (\([0-9]*\) bit).*/\1/p')
      if [ -z "$bits" ]; then
        echo "  DKIM    CORRUPT     the p= value is not a valid RSA public key."
        echo "          This is what a copy-paste that lost or gained a character looks like."
        echo "          Re-copy the TXT value from admin.google.com by SELECTING it, never by retyping,"
        echo "          and make sure no line breaks came with it."
        fail=1
      else
        if [ "$bits" -lt 2048 ]; then
          echo "  DKIM    OK          valid RSA public key, $bits bit  (Google offers 2048; prefer it)"
        else
          echo "  DKIM    OK          valid RSA public key, $bits bit"
        fi
        echo "          well-formed, but only a signed message proves it is the RIGHT key: see below"
      fi
    fi
  fi

  # ── DMARC ──────────────────────────────────────────────────────────────────────────────
  v=$(dig +short TXT "_dmarc.$d" $at | tr -d '"')
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
echo "  asked $(dig +short NS "$D" 2>/dev/null | head -1), the domain's own nameserver, not a cache"
check "$D"
rc=$?
echo
if [ $rc -eq 0 ]; then
  echo "ALL THREE PUBLISHED, AND ONE STEP REMAINS, because a well-formed key can still be the"
  echo "wrong key and nothing local can tell. Send one message from this domain to a Gmail"
  echo "address, open it, and choose Show original. SPF, DKIM and DMARC must all read PASS."
  echo "Until you have seen that, DKIM is unproven rather than working."
else
  echo "NOT ALL PUBLISHED. Records live at the registrar: Squarespace Domains,"
  echo "nameservers ns-cloud-d1..d4.googledomains.com."
fi
exit $rc
