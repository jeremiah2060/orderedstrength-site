# OrderedStrength, public site

The public website for the OrderedStrength iPhone app.

**This repo is deliberately separate from the main app repo.** The app repo is private and
contains competitive strategy, pricing research and internal engineering docs that must never
become public. Only files meant to be public belong here. Nothing else is ever copied in.

## Pages

| Path | File | What it is |
|---|---|---|
| `/` | `index.html` | Homepage |
| `/app-privacy/` | `app-privacy/index.html` | Privacy policy. Required by App Store Review Guideline 3.1.2 |
| `/support/` | `support/index.html` | Support page. This exact URL is typed into the App Store Connect Support URL field, so **it must never move** |
| `/verify/` | `verify/index.html` | Receipt verifier. Paste a receipt the app copied, get VERIFIED or NOT VERIFIED. Posts to `api.orderedstrength.com/api/v1/verify` |
| `/terms/` | `terms/index.html` | Terms of use. Required by App Store Review Guideline 3.1.2 alongside the privacy policy for an auto-renewing subscription |
| `/how-it-works/`, `/stronger/`, `/record/`, `/join/`, `404.html` | | The marketing pages |
| `/es/...` | `es/**` | The Spanish site: every page above, built by substitution from the English skeleton (`tools/build-locale.py` + `tools/es_strings.py`) |

⚠️ **THIS TABLE LISTED FOUR PAGES WHILE THE REPO HELD TWENTY.** It described the site as it was in
August and was never updated as pages landed, which is how a reader concludes the Spanish site does
not exist.

⚠️ **THE SPANISH BUILD HAS NO DRIVER.** `tools/build-locale.py` is a library and its `__main__`
only prints the docstring; the string maps live in `tools/es_strings.py`; and the script that once
wired them together is not in this repo. The `/es/` pages are therefore hand-maintained artefacts
today, not reproducible output. Gates hold them honest (`lang-gate.py`, `shot-gate.py`), but a
rebuild from the English skeleton is not currently a command anyone can run.

## Where the wording comes from

**THE APP LINKS TO THIS SITE, SO THIS SITE IS THE PUBLISHED POLICY.** `LegalLinks.swift` ships
`https://www.orderedstrength.com/app-privacy`, which means what is served here is what a user and
an App Store reviewer actually read. The app repo's `docs/legal/privacy.html` and
`docs/legal/support.html` are a COPY kept for reference, and the direction is: change it here,
publish, then copy it back there.

⚠️ **THIS PARAGRAPH USED TO SAY THE OPPOSITE**, that the app repo was the source of truth and that
the wording must never be edited here first. Nobody was copying in either direction, and on
2026-09-02 the two had been apart for weeks: the app repo said "Three things can leave your device
... none of them is your training log" while the truth, checked against the Swift, is five, and one
of them WAS the training log. The rule pointed at the stale copy, which is worse than having no
rule, because it makes the wrong file look authoritative. Both were brought into agreement that day.

The verifier page at `docs/verify/index.html` in the app repo is unchanged by this: it is a tool,
not published wording.

## Domain, and which host actually serves it

Custom domain is **`www.orderedstrength.com`** (see `CNAME`).

⚠️ **THIS SECTION DESCRIBED A DEPLOY PATH THAT NO LONGER EXISTS.** It said `www` was a CNAME to
`jeremiah2060.github.io`, so the obvious conclusion was that pushing to GitHub Pages publishes the
site. Measured 2026-09-01, the actual records are:

| Host | Record | Points at | Serves |
|---|---|---|---|
| `www.orderedstrength.com` | CNAME | `orderedstrength-site.pages.dev` | **Cloudflare Pages** |
| `orderedstrength.com` (apex) | A x4 | `185.199.108-111.153` | GitHub Pages, which redirects to `www` |

Nameservers are Google Domains, not Squarespace. So **`www` is served by Cloudflare Pages**, and it
is Cloudflare's production branch, not GitHub Pages, that decides what a visitor sees. `_headers`
(CSP, X-Frame-Options, cache rules) is a Cloudflare Pages file and is ignored by GitHub Pages;
verified applying on the Pages deployment and absent from the live domain, because the file has
never been on the branch Cloudflare builds.

Branch previews exist and are NOT the site: `redesign-elite.orderedstrength-site.pages.dev` serves
the full redesign today while the domain serves a 2,555-byte placeholder from an August commit.
🔒 **PUSHING `redesign-elite` IS NOT SHIPPING.** Confirm the Pages production branch in the
Cloudflare dashboard before assuming any push publishes anything.

**Do not touch the `MX` rows in that screen.** They carry Google Workspace email for the domain
and have nothing to do with this site.

`pt.orderedstrength.com` is a different site entirely (Squarespace) and is not managed here.
