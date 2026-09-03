# HANDOFF: the day the site went live
**2026-09-02** · `main` at `a7d52f2` · tree clean · **www.orderedstrength.com is serving this repo**

---

## Read this first

The redesign had never been on the domain. `origin/main` sat at `9f7a5a3` from 23 August, six
files, and the live site was a 2,555-byte placeholder that answered **every** URL with itself at
HTTP 200: the share image, the sitemap, the robots file, the legal pages the app links to. Local
`main` was 72 commits ahead and unpushed. That is fixed. Twenty pages in two languages are live,
seventeen gate programs are green, and the domain returns real 404s.

The single most consequential thing that changed for a real person: the app ships
`https://www.orderedstrength.com/app-privacy` in `LegalLinks.swift:88`, and that URL was serving
the August text saying *"Three things can leave your device ... none of them is your training
log."* The true answer is five (now six), and one of them **was** the training log. Every
TestFlight user who tapped Privacy Policy read a legal document that undercounted what leaves
their phone. Publishing corrected it. `scripts/check_legal_links.sh` in the app repo passes
against the live URLs.

---

## Deploy topology, measured

| | |
|---|---|
| Production | Cloudflare Pages, building `main` **as it exists on GitHub** |
| Publish | `git push origin main`. Nothing else. |
| Preview | any other branch → `https://<branch>.orderedstrength-site.pages.dev`, sent `x-robots-tag: noindex` |
| Roll back | Cloudflare Pages → Deployments → *Rollback to this deployment* (seconds), or `git push --force-with-lease origin 9f7a5a3:main` |
| Apex | `orderedstrength.com` is still **GitHub Pages** (four A records, 185.199.108-111.153) 301-ing to www. Moving it to Cloudflare would give both hosts the same headers and the same 404. **Do not touch the MX rows** (Google Workspace). |
| Registrar / DNS | Squarespace Domains; nameservers `ns-cloud-d1..d4.googledomains.com` |

🔒 **Pushing any branch other than `main` is not shipping.** The README says so and it is true.

---

## The gate suite: what actually protects this site

`./check.sh` runs **sixteen programs** and prints `SITE OK` or `SITE NOT OK`. Run
`python3 stamp-assets.py` **before** it, always: every page's `?v=` must equal the stylesheet's
real hash or the stamp check fails.

| Gate | The failure it exists to catch |
|---|---|
| `check-site.py` | Eight checks in one: a page `<style>` silently shadowing the shared sheet; tag **nesting** by stack, not count; hygiene (duplicate ids, dead anchors, unversioned or missing assets, banned symbols, missing alt); the build stamp; **cross-page counts**; **input font size**; **third-party hosts**; **every inline script parses** |
| `shot-gate.py` | The pixels, read with the OS Vision framework, against every phrase a caption quotes about them |
| `ring-cause-gate.py` | A caption explaining one ring with a different ring's input |
| `pin-gate.py` | The three callout pins against the pixels they point at |
| `icon-gate.py` | The favicon being a drawing of the mark rather than the mark |
| `pair-gate.py` | The two languages photographing different athletes, or one photo published twice |
| `voice-gate.py` | A selling page talking about itself; **and the app's banned coaching vocabulary, both languages** |
| `translate-gate.py` | What a browser-translate reader gets: unguarded quoted app strings |
| `lang-gate.py` | A page not actually written in the language it declares; and Spanish identical to English |
| `contrast-gate.py` | WCAG 2.1 on every ink-on-surface pair, read from the stylesheet's own tokens |
| `type-floor-gate.mjs` | Any rendered text below 12px |
| `align-gate.mjs` | The one left edge; and any page scrolling sideways |
| `measure-gate.mjs` | A block of running text wrapping absurdly short because a grid or flex placement broke |
| `type-gate.mjs` | The optical size of an inline literal against the sentence holding it |
| `hero-gate.mjs` | **The hero composition at six viewport HEIGHTS** |
| `lang-redirect-gate.mjs` | A Spanish browser reaching the Spanish site, and the two language links not looping |

Not in `check.sh`, run by hand:
`tools/check-mail-dns.sh` (+ `--selftest`) · `tools/perf.mjs` · `tools/mirror-anchors.py` ·
`tools/quotable.py <image>` · `tools/audit-captures.py <dir>` · `tools/await-deploy.sh`

---

## What shipped today

**Truth.** Fourteen sentences plus a hand-drawn card, both languages, each checked against the
Swift at the line. The dial claimed a measured accuracy rate that does not exist (it is the
coverage *target* at `ConformalBandCalibrator.swift:87`). The privacy count said four on five
pages and five on the policy. The injury example quoted pain at 4/10 when
`InjuryHistoryTracker.swift:157-171` holds the ramp above 5. The evidence floor was described
backwards. `/es/stronger/` was selling *"una racha de meses"* — **racha is streak**, the one word
this product refuses to use about a body. The price comparison quoted one competitor's two tiers
as the market. The share card promised a different headline from the page it opened.

**The phone.** At 390px the header showed the wordmark and the word "Verify": three rules hid the
links and a fourth hid the call to action, and nothing replaced any of them, so four of five
destinations were unreachable from every phone. Now a Join pill that shortens instead of
vanishing, and a `<details>` menu that needs no script. The margin scale was gated at 1520px and
therefore rendered on no laptop and no phone; it now lies on its side in the bar below that width,
built from the same section list. The callout pins were hover-only, which is the one thing a phone
cannot do, so they are buttons. The seal console's inputs were 14px, which makes iOS zoom the page
on every tap, and two one-tap presets now break the seal without typing.

**What the page no longer asks of strangers.** `/record/` read its listing from `api.github.com`
in the visitor's browser, rate-limited to 60 an hour per IP behind carrier NAT, and it answered
403 and rendered *"Could not read the repository"* to someone who had come to check our honesty.
`tools/mirror-anchors.py` takes that listing at build time; the CSP no longer permits the call.

**The record is now an instrument at zero:** three counters and an empty coverage plot with the
target line drawn, every figure read out of `record/anchors.json` rather than typed.

**Mail.** SPF, DKIM (2048-bit, Google Workspace default selector) and DMARC (`p=quarantine`) are
published and verified end to end: a real message reads PASS three times.

**Language.** A Spanish browser now lands on the Spanish site before a pixel is painted.

---

## The laws this day produced

🔒 **A GATE SCOPED TIGHTLY ENOUGH TO AVOID A FALSE POSITIVE CAN BE SCOPED TIGHTLY ENOUGH TO MISS
THE REAL THING.** The cross-page count gate was narrowed in the morning after it flagged a
headline about four screenshots; by evening it called every page clean while the Spanish policy's
own opening sentence still read *"Cinco cosas pueden salir"*. Nothing tells you which side you are
on except writing the sentence out and checking the pattern against it.

🔒 **A REMEMBERED PREFERENCE THAT IS NEVER ACTED ON IS WORSE THAN NONE.** Clicking "Español"
stored `es`, and the stored value was read *only* to suppress the automatic redirect. The bare
domain then served English. The reader believes they chose and the site quietly disagrees.

🔒 **EVERY GATE IN THIS REPO VARIED WIDTH AND FIXED HEIGHT.** align, type, type-floor and measure
sweep 320 to 2560 across and all run at 900 or 950 down, taller than most laptops sold. The hero
device is sized by *height*. A whole axis went untested, and that is why the site looked right on
every machine here and broken on a Windows laptop. `hero-gate.mjs` closes it.

🔒 **A LAYOUT THAT CHANGES SHAPE WHEN YOU RESIZE IS WORSE THAN ONE THAT IS MERELY SMALL.** The
first fix for the above made the card drop below the phones under 55rem of height. That removed
the symptom and produced two designs that swapped as you dragged the corner. The real cause was
one number, `--device-h`'s floor, and above it nothing changed at all.

🔒 **A BROKEN INLINE SCRIPT IS INVISIBLE TO EVERY SOURCE GATE.** A duplicated `catch` killed the
language script on all ten English pages; nesting, hygiene, stamp, contrast, type, align and
measure all passed. A page can be perfectly valid HTML and completely dead. `check-site.py` now
runs `node --check` over every inline script.

🔒 **A VERIFICATION TOOL THAT READS A CACHE IS NOT VERIFYING, IT IS REMEMBERING.** The mail checker
called a live SPF record missing for four hours because the local resolver held a stale answer,
and the natural response to that is to add the record a second time, which is a permanent error
that disables both. It asks the domain's own nameserver now.

🔒 **A CHECK THAT CAN ONLY EVER SAY NO IS NOT A CHECK.** `check-mail-dns.sh --selftest` proves each
arm can report OK against a domain that really publishes that record. Its first draft failed its
own selftest, because google.com does not sign with the `google` DKIM selector.

🔒 **AN EDGE THAT LINES UP WITH NOTHING READS AS AN ACCIDENT, EVEN WHEN SOMEONE CHOSE IT.**

🔒 **A COMMENT WITH NO RULE UNDER IT IS WORSE THAN NO COMMENT: IT READS AS DONE.** Six lines above
`.hero-grid` described the widen-to-the-right fix for a day after its implementation was reverted.
The CEO asked for it three times.

---

## Not started, with nothing done toward them

The shareable receipt card · the printable spec sheet · the design-notes page · the twenty-second
film · hashing the inline scripts so the CSP can drop `'unsafe-inline'` · minifying assets with
immutable caching · the light reading scheme for the document pages (**product identity, the
CEO's call**: light is the default on most operating systems, so shipping it means most visitors
see four pages in light for the first time).

**Blocked on Apple, not on engineering.** App Store id **6780735471** exists, but
`apps.apple.com/us/app/id6780735471` returns **404** and Apple's lookup API returns zero results,
so the listing is not public. A Smart App Banner, a download badge or `SoftwareApplication`
structured data would all point at a dead page today. They unblock the moment pre-order opens.
The universal-links file (`/.well-known/apple-app-site-association`) needs
`89WLCGT66D.com.jerry.OrderedStrength2` **and** an `associated-domains` entitlement the app does
not declare.

**Blocked on the build lock.** The real photograph of Jerry cutting a set (`G1`), which needs the
simulator, and the Swift half of the anchor client.

---

## Owed to the CEO

1. **`fly secrets set GITHUB_ANCHOR_TOKEN=...`** — a fine-grained token scoped to *contents: write
   on the receipts repo only*. Until then `/health` reports `anchor: false`, deliberately, because
   a relay that accepts digests and never publishes looks exactly like success from outside.
2. **`server/deploy.sh`** — the anchor relay is written, tested (48 assertions) and committed, and
   is **not** on the running machine. `api.orderedstrength.com/api/v1/anchor/health` returns 404.
3. **Open pre-order** in App Store Connect to unblock every App Store item above.
4. **Move the apex to Cloudflare** so both hosts share the headers and the real 404. MX untouched.
5. Decide the light reading scheme (product identity).

---

## Traps, so nobody pays for these twice

- **`stamp-assets.py` before `check.sh`**, every time.
- The Spanish pages are **hand-maintained**. `build-locale.py` is a library with no driver
  (README says so). Edit `es/*.html` directly, **and** update `tools/es_strings.py` so a future
  driver cannot reintroduce what you just fixed.
- **The site is the published policy; the app repo's `docs/legal/*.html` is a copy.** The app
  links to the website. Change it here, publish, copy it back. The README used to say the
  opposite and the two drifted for weeks.
- `_headers` does **not** apply to Cloudflare Function responses. That is why the language
  redirect is an inline script and not an edge function.
- `--lang` does not change `navigator.language` in headless Chrome. `--accept-lang` does.
- macOS `sips` reads WebP but **cannot write it**. Use PIL.
- Never add a second `v=spf1` record. Two is a permanent error and counts as none.
- When another session holds the app repo's tree, commit with **explicit paths**
  (`git commit -- <paths>`), never a bare `git commit`.
