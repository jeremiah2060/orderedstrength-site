# HANDOFF: the browser was translating it back

**2026-09-03** · site repo · the defect the CEO reported was not in this repository, and four that
were, were found while proving that.

---

## Read this first

He said the site was stuck: "if you switch to spanish it only appears for a split second then goes
back to english again, but all the screenshots are in spanish, only the content is bouncing." All
seventeen gates were green while he said it, and his own first instinct was to revert the language
work from 2026-09-02.

**That last clause is the whole diagnosis.** Text changing while the images do not is not a
navigation: the English home page carries English screenshots, so a bounce would have moved both.
The only thing that rewrites text and leaves images alone is a machine translator. It was Chrome,
replaying the "always translate Spanish" he turned on for `/es/` on 2026-08-31, which this repo's
own comments already record. He confirmed it: "you are right it was my chrome translating back to
english, i just saw that now."

🔒 **THE REVERT WOULD HAVE MOVED NOTHING HE COULD SEE, AND MEASURING THAT TOOK ONE COMMAND.** All
ten Spanish pages are byte-for-byte identical to their state before the auto-detect work, apart
from the `?v=` cache stamp. Commits `6abb556`, `4d9c9b0` and `a7d52f2` only ever edited the English
pages. Before arguing about a plan, hash the files the plan is about.

---

## The four real defects, all found while proving the first one was not ours

**1. A live loop on both 404 pages, proven against the domain.** Neither 404 page loaded
`site.js`, and `site.js` holds the *only* writer of `os-lang`. So on the Spanish 404 the English
link went to `/404.html`, which stored nothing, detected Spanish and replaced straight back.
Measured on the live domain: `stored=null`, no `site.js`, and following that link returned to
`/es/404` in Spanish every time. That link could never work for any browser listing Spanish.
🔒 **THE LOOP TEST THAT EXISTS TO CATCH THIS WALKED ONE PAIR OUT OF TEN.** The rule it proves is a
property of a *page*, because it depends on that page loading the script that records the choice,
and it was asserted about the home page and generalised by hope. It walks all ten now, and it
clicks rather than navigating: a `goto` walks past the click handler that was broken.

**2. The only language control on the site was 17 screens down.** Driven over CDP at 390px:
13,566px down the English home page, 14,512px down the Spanish one. 16.1 and 17.2 screens. In the
same week the site gained the power to move a reader into a language they never chose, silently.
🔒 **EVERY GATE REACHED IT WITH `querySelector` AND CLICKED IT**, which proves the link WORKS and
asks nothing about whether a person could find it. There is a control in the header of all twenty
pages now: zero taps above the collapse breakpoints, one tap below, and `lang-switch-gate.mjs`
measures that rather than assuming it.

**3. The call to action sat on top of the brand name at 320px.** Pre-existing and live: gap 1px in
English, 0px in Spanish, the pill overlapping the last letters of the wordmark on every page. The
narrow rules drop the last plain *link* at 23rem and stop, so the three things actually left in the
bar, wordmark, pill and disclosure, had never been measured against each other. Now 17px and 16px.

**4. The diagnostic told the opposite of the truth.** `/assets/lang-check` read
`navigator.languages[0]`, and the site stopped using that rule one commit after the page was
written. On the exact browser the shipped rule was written *for*, the Spanish macOS reporting
"en-US, en, es", it printed "it is not asking for Spanish" while the site redirected.

---

## What changed, and why each one is not the other

- **The Spanish pages decline machine translation** (`<meta name="google" content="notranslate">`
  and `translate="no"` on `<html>`). `translate-gate.py` guards the *elements* a translator must
  not rewrite and is right about all of them; nobody had said the *page* should not be translated
  at all, and on a page where a real translation already exists a machine pass can only subtract.
  The English pages stay translatable **on purpose**: for a reader whose language this site does
  not publish, the machine is the only way in. `notranslate-gate.py` is therefore two-sided.
- **And the page says so when it happens anyway,** because Safari does not read that declaration.
  It reads its own headline once and reveals one line, in Spanish and itself untranslatable, when
  something rewrites it. 🔒 Keying off Chrome's `translated-ltr` class would see one of the two
  browsers this has to work in; watching its own words has no browser in it.
- **An automatic redirect is no longer recorded as a choice.** It wrote `os-lang` on the way out,
  which made a guess about a browser indistinguishable on disk from a person's click, and it wrote
  it *before* `location.replace` inside one `try`, so a browser that could not write never
  redirected. The comment above it read EVERY BRANCH FAILS OPEN, and that was true of every branch
  except the one that existed to serve a Spanish reader.
- **Breakpoints re-measured to 63rem and 69rem.** Adding the header link put the wordmark and nav
  at 0px from 900 to 980px in English and 1000 to 1072px in Spanish. English: 1px@984, 9px@992,
  16px@1000, 24px@1008. Spanish: 0 through 1072, 14px@1088, 29px@1104.

---

## Three new gates, and the one hole that stays open

`./check.sh` runs **21 programs**. Derive that number from the file, never from this line.

| Gate | The failure it exists to catch | Selftest |
|---|---|---|
| `notranslate-gate.py` | A real translation accepting a machine one; and the English side closing itself off | `--selftest`, both arms |
| `lang-switch-gate.mjs` | A language control that works and cannot be found | `--selftest`, prints the 16.1 screens |
| `bar-gate.mjs` | The one component on every screen colliding with itself, at 30 widths | `--selftest` |
| `engine-gate.py` | A Chrome-first CSS feature shipping without an `@supports` that tests it, a guard with no fallback, a prefixed property that lost its pair | `--selftest`, 6 cases |

🔒 **THE OPEN HOLE: EVERY BROWSER-DRIVEN CHECK HERE LAUNCHES THE SAME BINARY.** `measure.mjs` opens
Google Chrome, and align, measure, type, type-floor, hero, lang-redirect, lang-switch and bar are
all built on it. They sweep width, and since 2026-09-02 height, and have never varied the engine.
That is the same shape as the height hole `hero-gate` closed, and the repo already wrote the law
for it. Closing it needs one of two things, and **both are the CEO's**: `safaridriver --enable`,
which asks for an administrator password, or a decision to vendor a WebKit build and give up this
harness's one real virtue, that it depends on nothing but a browser already on the machine.
Until then `engine-gate.py` checks the discipline instead of the render, and the stylesheet is
clean: masks carry their `-webkit-` twins, `backdrop-filter` is gone, `text-wrap:balance` degrades
to normal wrapping, and the scroll-driven animations are `@supports`-guarded with a JS fallback.

---

## Traps

- **A layout box is not a painted pixel.** A closed `<details>` still answers
  `getBoundingClientRect` with a real 200x242 box that paints nothing, so the first draft of
  `lang-switch-gate` reported "0 taps" on every phone. Use `checkVisibility`, and name a closed
  disclosure explicitly. Caught by taking a screenshot instead of trusting the number.
- **`checkVisibility` answers from the last style pass**, so opening a `<details>` and asking in
  the same breath gets the old answer. `void document.body.offsetHeight` is the flush.
- **A measurement written into a comment protects the width it was taken at and nothing else.**
  The wordmark-to-nav gap had been measured by hand twice and written down twice, and one added
  link invalidated both. If it is worth a comment it is worth a gate.
- Everything in the 2026-09-02 handoff still applies: `stamp-assets.py` before `check.sh`, the
  Spanish pages are hand-maintained, publish is `git push origin main` and nothing else.

---

# SECOND BATCH, the same night: the backlog from the 2026-09-02 handoff

The CEO, asleep: "when the machine is free build everything remaining from the last Handoff about
the website". Its *Not started* list held seven items. Three were infrastructure and are done.
The rest are named at the bottom with the specific reason each is not, and none of the reasons is
"later".

## Done

**The CSP stopped trusting inline script.** `script-src` said `'self' 'unsafe-inline'`, which
tells a browser to run any `<script>` that appears in the markup, which is the payload an
injection delivers. It now names the eight SHA-256 hashes of the blocks this site actually ships.
`tools/csp-hashes.py` generates them and `--check` fails a tree whose policy is out of date.
🔒 **style-src KEEPS `'unsafe-inline'`, AND THAT IS A MEASUREMENT.** There are 83 inline
`style="..."` attributes here, mostly the callout pins positioning themselves by percentage. A CSP
hash cannot name an attribute; CSP 3 would need `'unsafe-hashes'`, which re-allows every inline
handler as a side effect and is worse than what it replaces. Scripts are where injection executes.
🔒 **AND A STALE HASH KILLS A SCRIPT SILENTLY**, which is the failure this repo has already
shipped once: *"A BROKEN INLINE SCRIPT IS INVISIBLE TO EVERY SOURCE GATE."* `node --check` will
happily parse a script the browser was told not to run. So `tools/csp-gate.mjs` serves the repo
under the real `/*` block, which `python3 -m http.server` never sends, and asserts what each
script PRODUCES. 24 of 24 go red on a corrupted policy.
🔒 **ITS OWN SELFTEST CAUGHT TWO OF ITS FIRST CHECKS BEING DECORATIVE.** `#hash` and `#verdict`
ship as static no-script markup, so reading them reported on the HTML rather than the script. It
counts the 64 per-character elements only the script can render, and presses a preset to make the
fingerprint recompute.

**The stylesheet on the wire is a third of the one in the repo.** `assets/site.css` is 96,745
bytes and 58% of it is comment, because the comments here carry the laws and the CDP
measurements. Right for the source, wrong for a render-blocking file. Measured with brotli at
quality 11, which is what Cloudflare serves: **26,918 bytes published, 7,813 with comments
removed. 19,105 bytes, 71%, off the critical path of every first visit.** The pages link
`assets/site.min.css`; every source gate still reads the source.
🔒 **THE STRIPPER IS STRING-AWARE**, because `--grain` holds an SVG data URI and a naive
`/\*.*?\*/` would eat a comment opener living inside a string and truncate a declaration into
something that still parses. It removes comments and blank lines and **nothing else**: no
shorthand collapsing, no selector merging, no newline stripping, each of which can change
rendering for a saving brotli mostly recovers anyway.
🔒 **AND `minify-css.py --check` IS NOT SUFFICIENT ON ITS OWN.** It proves the artifact is what
the *current* stripper produces, which is the generator agreeing with itself: edit one line of
that function and it stays green on a sheet that renders differently. `tools/css-equiv.mjs` links
both files from a bare page and compares the browser's own serialized CSSOM. **260 rules and
41,923 characters on both sides, identical.** One deleted declaration turns it red and it prints
the character where they diverge.

**Immutable caching.** `/assets/*` was `max-age=3600, must-revalidate`, so a returning reader
paid a revalidation round trip for the stylesheet and the script on every navigation while
`stamp-assets.py` had already made a changed file a changed URL. The content-stamped files are
now `max-age=31536000, immutable`. `/assets/lang-check.html` deliberately keeps the hour: its URL
never changes and it is the diagnostic a person is sent to when the language redirect misbehaves.
The precondition is enforced, not assumed: `check-site.py` already fails a page that references
an asset with no `?v=`, which under these headers would be a file cached for a year at one URL.

**And the site can be printed.** There was no `@media print` block at all, and that is not
cosmetic: a browser does not print background colours unless the page asks, so near-white ink on
a ground the printer drops came out **white on white**. The two pages most likely to be printed
are the two the app itself links to, `/terms/` and `/app-privacy/`.
🔒 **EVERY GATE HERE MEASURES THE SCREEN, SO A WHOLE OUTPUT MEDIUM WAS UNTESTED**: the same
shape as the viewport-height axis `hero-gate` closed and the engine axis `engine-gate` covers.
`measure.mjs` gained one additive method, `setMedia`, because `Emulation.setEmulatedMedia` is the
only way to lay a page out for paper without printing it, and without it a print stylesheet is
the one thing on this site nothing would ever look at.
🔒 **THE PRINT GATE'S SELFTEST IS THE ORIGINAL DEFECT, NOT A MUTATION OF THE CHECK**: the same
assertions in `screen` media are exactly what a printer was handed before. 60 of 80 go red there.

## Two mistakes made and caught tonight, both by these gates

🔒 **A GATE THAT WRITES INTO THE TREE IT CHECKS CAN BREAK A GATE THAT READS IT.** The first
`css-equiv.mjs` wrote two probe pages into the repository root and removed them in a `finally`.
They lived about four seconds, and `icon-gate` walked the tree inside that window in the same
`check.sh`, counted twenty-two pages instead of twenty, and failed the suite on *"2 page(s) carry
no icon link"*. It was right. The collision is timing-dependent, which is the kind that passes
locally and fails in the run that matters. It serves from memory now and writes nothing.

🔒 **A CHECK THAT INVENTS A GROUND REPORTS A DEFECT THAT IS NOT THERE.** The print gate's first
ground detection stopped at the first background that was not fully transparent, so the seal
console's `rgba(0,0,0,.32)` well read as opaque black and it reported the home pages printing at
2.58:1 and 1.38:1 on black. No printer would produce that: 32% black over white paper is light
grey. The chain is collected inward-to-outward and composited outward-to-inward now, as a
renderer does. **The next person would have spent the night fixing the page instead of the
instrument.**

🔒 **AND THE NUMBERS IN A COMMENT MUST BE COMPUTED.** The print palette's comment first asserted
five contrast ratios from memory and every one was wrong by about a point. Measured against
`#ffffff`: ink 21.00, ink2 15.20, ink3 8.14, teal 7.54, stone 8.51, azure 8.94, amber 7.48, red
8.10. The hairline was 1.87:1, which is a hairline nobody sees, and is now `#8b9099` at 3.21:1.

## Not built, each with its own reason

- **The shareable receipt card** and **the design-notes page** are new user-facing pages, which
  means new copy in two languages, a Spanish twin, and a voice this site is careful about. That
  is product writing, and it is the CEO's, not something to invent unsupervised overnight.
- **The twenty-second film** needs footage. There is none to edit and none can be generated here.
- **The light reading scheme** is marked in the 2026-09-02 handoff as *product identity, the CEO's
  call*, and it still is.
- **The App Store items** are still blocked on a listing that returns 404, exactly as recorded.
- **`G1`, the photograph of Jerry cutting a set**, needs the app repo's simulator, and that tree
  currently holds sixteen uncommitted Swift files from another session. Photographing unreviewed
  code and publishing it as evidence is the one thing this site must never do.
