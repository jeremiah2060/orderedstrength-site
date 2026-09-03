# HANDOFF: the Spanish was English wearing Spanish words

**2026-09-03** · site repo · the three red gates are closed, the six pages are on the domain,
and every one of the thirteen Spanish pages was read line by line against its English twin.

---

## Read this first

**WHAT A USER CAN NOW DO:** open `orderedstrength.com/es/` and read Spanish that a Spanish
speaker wrote rather than Spanish that a translator produced, and reach `/receipt/`, `/spec/`
and `/design/` in both languages, which returned 404 this morning. The CEO's wife read the site
and named the defect exactly: *"El coaching **corre** en tu teléfono"* is what a machine writes;
*"se ejecuta"* or *"funciona"* is what a person writes. She found one instance. Reading all
thirteen pages against their English twins produced **149 string corrections**, hers among them,
in that family and in five others, including two misspellings shipped in the design notes and one
sentence whose Spanish said the opposite of its English. Each of those 149 is a counted, applied
replacement, not an estimate; the largest single defect is one sentence repeated on twelve pages.

The single most consequential one for a reader: on `/es/how-it-works/`, *"Díselo y quita lo que
no es seguro, entrena todo lo demás a esfuerzo completo"* reads in Spanish as an instruction to
**the athlete** to remove the unsafe lift himself. The English says Jerry does it. One missing
pronoun turned the product's injury promise into homework.

---

## The three red gates, closed

**Shadowed declarations, 2 → 0.** Both receipt pages declared a bare `.card`, which
`assets/site.css:688` already owns. Renamed to `.rcard` in the style block and the markup; every
`.card__*` child kept its name, because those are distinct selectors that shadow nothing. The
previous handoff was right that the rename had been reported and never applied.

**Type floor, 12 → 0.** `.swatch__hex`, `.swatch__note` and `.type-label` were `.6875rem`, which
renders at 11px against a 12px floor, on both design pages, measured at both widths. All six
declarations are `.75rem`. No exemption was used: all three carry text a reader is meant to read.

**Parallel text, 2 → 0, and the previous handoff's fix for it was wrong twice.** It proposed
marking `iPhone (iOS 17+)` and `32 bytes CSPRNG` with `translate="no"`. First, that would not have
worked: `lang-gate.py`'s parallel arm strips `<script>`, `<style>` and `<code>` and has no
`translate` logic at all, so the attribute would have changed nothing and the gate would have
stayed red. Second, and more important, **the gate was right and the strings were wrong**. Spanish
is head-initial, so a Spanish spec sheet writes *"CSPRNG de 32 bytes"*, never English's noun-adjunct
order; and *"iOS 17 o posterior"* is what a Spanish spec says where English writes `17+`. Both are
now real translations, so the gate went green because the defect went away.

🔒 **A GATE THAT FINDS ENGLISH-SHAPED SPANISH LOOKS EXACTLY LIKE A GATE WITH A FALSE POSITIVE,
BECAUSE BOTH POINT AT A STRING THAT "IS THE SAME IN BOTH LANGUAGES".** The difference is whether a
native writer would produce that order. Ask that before reaching for a suppression, and check that
the suppression mechanism you are reaching for exists.

---

## The Spanish pass: what was actually wrong

Six families, all of them the same underlying error, which is translating word order and idiom
instead of meaning.

**1. `run` translated as `correr`.** The one the CEO's wife caught, and it was in six places, not
one: the coaching chip, the dial note (*"el ritmo corre con evidencia"*), the seal console twice,
the pressure-test intro, and the privacy policy's account of the old server design. `correr` is a
body moving through space. Computation `se ejecuta`, a pace `lo marca la evidencia`, and arithmetic
is not `la aritmética` at all: Spanish does the sums, so it is `las cuentas se hicieron en tu
máquina`.

**2. Idioms carried across whole.** *"observa cómo aterriza"* (planes land, effects do not),
*"la plomería detrás de"* (Spanish plumbing is pipes, never infrastructure), *"hacerlo ver mejor"*,
*"la página se vería establecida"*, *"un piso duro"*, *"la prueba de presión"* (which in Spanish is
a plumbing test; the acid test is *la prueba de fuego*), and *"la cambia mientras cae"*, which says
the set falls.

**3. Subjects that changed who acts.** The injury sentence above is the worst. Also *"que el día
uno tiene promedios"* (day one has averages?), and *"Si estás en una versión anterior, sigue en la
que tienes"*, which reads as an instruction to stay put when the English says the code remains.

**4. False friends and register.** `Raro` for *rare* means **strange** in Spanish. `prolijo` is
Rioplatense, not es-419. `pulsa` is Spain; es-419 taps. `gestionando una lesión` and `manejando una
lesión` are both English `manage`. `mesa de soporte` is `mesa de ayuda`. `como mucho` is Spain's;
es-419 says `como máximo`.

**5. One sentence that inverted its meaning.** `/es/support/` said *"Lo que la app envía y lo que
no está detallado por completo en la política de privacidad"*, which parses as **"what is not
detailed"**. It now says *"y lo que no envía está detallado"*.

**6. Two shipped misspellings**, both on `/es/design/`: `leyiéndose` for `leyéndose` and `peldano`
for `peldaño`.

**And the three pages built last session were a different site.** Their footer said *"Un entrenador
de fuerza … luego se evalúa con lo que anotó"* where the other ten say *"Un coach de fuerza … y
después se califica a sí mismo con lo que escribió"*; their footer column said *"La letra pequeña"*
where the site says *"La letra chica"*; they wrote `&#218;nete` where every other page writes
`Únete`; and they were the only three Spanish pages encoded in HTML entities rather than UTF-8,
which is why nobody reading them noticed. All three now match. 177 entities were decoded after
proving that not one of them sits inside a `<script>`, so no CSP hash could move because of it.

---

## What the gates could not have caught, and now would

**The Spanish share card still painted the old headline.** Changing the H1 to *"Te cambia el
entrenamiento en plena sesión"* changed the `og:image:alt` on all twelve Spanish pages, and
`tools/og.html` went on typing *"a la mitad"* into `assets/og-es.jpg`. That is a false claim about
an image, on the site whose argument is that its claims are checkable. The generator was corrected,
both cards were re-rendered, and the new one was **read back with `tools/ocr.swift`**, the same
instrument `shot-gate.py` uses, which returns `Te cambia el entrenamiento en plena sesión.` from
the pixels. `assets/og.jpg` came back byte-identical, which is the generator proving it is
deterministic.

🔒 **NO GATE IN THIS REPO READS THE SHARE CARD.** `shot-gate.py` checks the screenshots against
their captions and stops there; `og:image:alt` is a claim about a picture that nothing compares to
the picture. It is the same class of hole `shot-gate` was written to close, one artefact over.

**`csp-hashes.py --check` caught what would have been three dead pages.** Editing the Spanish
strings inside the inline scripts on `/es/`, `/es/verify/` and `/es/receipt/` moved their hashes,
and the policy still named the old ones, so all three scripts would have silently refused to run:
the seal console dead, the verifier dead, the receipt card blank. Regenerated, re-checked.

**`webkit-gate` had never run on this machine.** It was the only failure in the first full run,
and not for anything in the diff: Playwright's WebKit binary was not installed, so the one gate
that asks what a **non-Chrome** browser gets had been failing open. For a product whose entire
audience is on iPhone, that is the browser that matters most. `npx playwright install webkit`,
and it runs now.

---

## The thing I found while about to make it worse

**Every internal document in this repository is a public URL, and I was one commit from adding
a fourteenth.** Cloudflare Pages deploys the repository as it stands, so the root is the web
root. Measured against production with curl, not assumed:

```
/HANDOFF_the-day-the-site-went-live_2026-09-02.md   200   12558 bytes
/CONTENT_PRESSURE_TEST_2026-08-23.md                200   45807 bytes
/README.md                                          200    4768 bytes
/check.sh                                           200   22474 bytes
/check-site.py                                      200
/tools/es_strings.py                                200
```

The handoff is the one that matters. It quotes the CEO, prints the deploy topology and the
force-push rollback command, lists what is owed including the name of a Fly secret, and records
which defects reached TestFlight users. That is an internal document and it has been on the open
web since the site went live on 2026-09-02.

A new `_redirects` serves 404 for the handoffs, the pressure test, the README, the root gate
programs and all of `tools/`. It deliberately leaves `/record/anchors.json` alone, which is
published data the record page is built from.

🔒 **THIS STOPS THE BLEEDING AND REPAIRS NOTHING.** Anything served at 200 can already be
cached, archived or indexed. Treat all six as permanently public and write the next handoff
knowing a stranger may have read the last one.

`_redirects` is a Cloudflare mechanism, so `check.sh` cannot prove it: the local gate server is
`python3 -m http.server`, which ignores the file entirely. It is verified by curl against the
domain after the push, and the result of that check is at the bottom of this document. If the
rule had not worked, the failure mode is the status quo rather than a broken site.

---

## Verification

`./check.sh` end to end, one run, after every change. **`SITE OK`.** All twenty-six gates:
check-site, screenshots, ring cause, pins, icon, pairs, voice, vocabulary, translation, language,
parallel text, notranslate, minify, CSP hashes, headers, engine, contrast, type floor, alignment,
measure, hero, language redirect, language switch, bar, CSP runtime, CSS equivalence, print,
webkit, and type at both 1440px and 390px. Every one reports zero failures.

`stamp-assets.py` and `tools/csp-hashes.py` were re-run before it, in that order, and
`csp-hashes.py --check` passes after.

Reading, not just gates: all thirteen Spanish pages were extracted to visible text with line
numbers and read against their English twins, including the strings inside inline `<script>`
bodies, which the prose extractor masks and which nothing had audited before. Those held four more
defects, among them an English `'unknown'` rendered into Spanish copy.

Every rewrite went through a replacement tool that **refuses to write a file if any `old` string
does not occur exactly the expected number of times**. It caught four mistakes of mine during this
session, including one string that existed twice when I had assumed once.

`tools/es_strings.py` was carried forward with 28 replacements. It has no driver today, so it could
not have reintroduced anything; the day someone writes the driver, every stale phrase left in it
would arrive looking like a build.

---

## Owed to the CEO

1. **Set a Cloudflare Pages build output directory.** This is the real fix for the section above,
   and it is in your dashboard rather than in this repository, which is the only reason it is
   yours. Recommendation: create a deploy folder holding only what a visitor should reach, and
   point Pages at it, so that a new internal document cannot become a URL by being saved in the
   wrong place. Until then `_redirects` is a list somebody has to remember to extend, and the next
   handoff nobody adds to it is public the day it is written. Reversing it costs one dashboard
   field.

2. **Read `/es/` on your phone with your wife.** This is the only check no gate here can make: a
   native speaker deciding whether it sounds like a person. Everything above is one non-native
   engineer applying rules; she applied an ear, and her ear found the defect first. Specific
   places to look, because they are the judgement calls rather than the corrections: the headline
   *"Te cambia el entrenamiento en plena sesión"*, the section title *"La prueba de fuego"*, the
   chip *"El coaching se ejecuta en tu teléfono"* (she offered `se ejecuta` **or** `funciona`; I
   chose `se ejecuta` because the sentence under it already says `se calcula`, and repeating a
   computation verb reads worse than varying it, but this is hers to overrule), and whether
   `coach` should stay English at all where Spanish has `entrenador`. That last one is the biggest
   open question and it is **product identity**, not engineering: the site says `coach` and
   `coaching` in twenty places, she did not object to it, and changing it is a brand decision.

3. **`fly secrets set GITHUB_ANCHOR_TOKEN=...` then `server/deploy.sh`.** Unchanged from the
   2026-09-02 handoff and still the blocker on the anchor client. There is a standing law against
   writing a client for a route nobody has curled, and `api.orderedstrength.com/api/v1/anchor/health`
   returns 404.

---

## Still owed, and whose it is

**The G1 photograph is engineering and it is not done.** The 2026-09-02 list asks for a real
capture of Jerry cutting a set mid-session. It needs the simulator in the app repo driven to the
point where a cut fires, which is a build plus a scripted session, and today's directive was the
five items plus the Spanish audit. **Next action: engineering**, in the app repo, not here. It is
named here so it is not lost, not to hand it back.

**The twenty-second film** from the same list is unstarted. It is video production, not something
this repository can author.

**The light reading scheme for the document pages** stays where the 2026-09-02 handoff put it:
product identity, the CEO's call, because light is most operating systems' default and shipping it
means most visitors meet four pages in light for the first time.
