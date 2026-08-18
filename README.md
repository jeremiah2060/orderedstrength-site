# OrderedStrength — Public Site

Minimal public website for the OrderedStrength iPhone app: a privacy policy and a support page,
required by Apple App Store Review Guideline 3.1.2 and the App Store Connect Support URL field.

**This repo is deliberately separate from the main app repo.** The app repo is private and
contains competitive strategy, pricing research, and internal engineering docs that must never
become public. This repo contains only the three files meant to be public.

**Source of truth for the wording lives in the main app repo**, not here:
`docs/legal/privacy.html` and `docs/legal/support.html`. If those change, copy the update into
`privacy/index.html` / `support/index.html` here and push.

Custom domain: `app.orderedstrength.com` (see `CNAME`). DNS is managed in Squarespace, under the
`orderedstrength.com` domain settings, as a CNAME record: host `app` -> `jeremiah2060.github.io`.
