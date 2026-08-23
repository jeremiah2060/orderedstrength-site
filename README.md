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

## Where the wording comes from

The source of truth for the privacy and support wording lives in the main app repo at
`docs/legal/privacy.html` and `docs/legal/support.html`, and the verifier at `docs/verify/index.html`.
When those change, copy the update here and push. Never edit the wording here first: the app repo
runs `scripts/check_legal_links.sh` against these URLs.

## Domain

Custom domain is **`www.orderedstrength.com`** (see `CNAME`).

DNS is managed in Squarespace, under the `orderedstrength.com` domain settings:

| Type | Host | Value |
|---|---|---|
| CNAME | `www` | `jeremiah2060.github.io` |
| A x4 | `@` | GitHub Pages addresses |

**Do not touch the `MX` rows in that screen.** They carry Google Workspace email for the domain
and have nothing to do with this site.

`pt.orderedstrength.com` is a different site entirely (Squarespace) and is not managed here.
