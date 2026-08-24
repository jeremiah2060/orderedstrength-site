# THE CONTENT PRESSURE TEST

**Site:** orderedstrength.com, branch `redesign-elite`, HEAD `d7be874`
**Date:** 2026-08-23
**Scope:** content only. No design, no code. Seven pages, 4,904 visible words, three app captures.
**Method:** every claim below is measured or cited at `file:line`. Nothing here is an impression.

---

## THE VERDICT IN ONE PARAGRAPH

The writing is genuinely good. It is better than every competitor's site in this category, it has
a real voice, it never once uses a hype adjective, and it contains zero em-dashes across 4,904
words, which means the app's own copy law was carried onto the web without being asked.
**And it is selling the wrong thing to the wrong person.** This is a 4,900-word proof-of-integrity
manifesto written for a skeptical engineer. It is not a strength product page written for a lifter.
Measured across the body copy of all seven pages, with the repeated navigation and footer chrome
stripped out so the count is not inflated by it: the proof apparatus (*receipt, record, verify,
sealed, fingerprint, nonce, anchor*) is named **65 times**. What happens to the athlete's body
(*stronger, gains, muscle, hypertrophy, PR, personal record, results, progress, performance*) is
named **6 times**, and five of the nine words in that list appear **zero** times. That is an
**11:1 ratio**. An athlete finishes this site knowing exactly how honest you are, and
with no idea whether they will squat more. The fix is not a rewrite. The bones are excellent. The
fix is a re-aim: same voice, pointed at a body instead of at a proof.

---

## PART 1 — THE MEASUREMENTS

Every number below was counted from the HTML, not estimated.

### 1.1 What the site talks about

Body copy only, 4,367 words. The site's repeated nav and footer are excluded, because counting
them would inflate this in my favour.

| Vocabulary | Count | |
|---|---|---|
| record / records | 15 | |
| receipt / receipts | 14 | |
| sealed / seal | 10 | |
| fingerprint(ed) | 8 | |
| verify / verified / verifier | 8 | |
| anchor / anchors | 6 | |
| nonce | 4 | |
| **PROOF APPARATUS TOTAL** | **65** | **The thing the site is about** |
| | | |
| muscle / muscles | 4 | |
| results | 1 | |
| progress | 1 | |
| stronger | **0** | |
| gains | **0** | |
| hypertrophy | **0** | |
| performance | **0** | |
| personal record / PR | **0** | |
| **ATHLETE OUTCOME TOTAL** | **6** | **The thing the reader is buying** |

**11 : 1.** The ratio matters less than the five zeros.

### 1.2 Who the site is written for

| Term | Count | Verdict |
|---|---|---|
| test suite | 3 | Engineer |
| `scripts/verify.sh` printed literally on the page | 2 | Engineer (`index.html:315`, `index.html:444`) |
| SHA-256 | 1 | Engineer |
| nonce | 4 | Engineer |
| byte for byte | 1 | Engineer |
| root hash | 1 | Engineer |
| repository / commit dates | 5 | Engineer |
| clean install | 3 | Engineer |
| simulator | 1 | Engineer |
| JSON | 1 | Engineer |

**Answer to "do we sound like we're talking to engineers or potential users": engineers.**
Not as a matter of tone. As a matter of vocabulary. There are 22 engineer-only terms on a
consumer site, and the homepage prints an internal shell command twice.

### 1.3 Who is missing

| | Count |
|---|---|
| Named humans anywhere on the site | **0** |
| The word "founder" | **0** |
| The word "team" | **0** |
| The words "athlete" / "athletes" | **0** |
| "lifter" | 1 |
| Testimonials, quotes, reviews | **0** |
| Competitors named (Hevy, Strong, Whoop, Juggernaut, RP, Fitbod...) | **0** |
| Support address | `tachiwonajeremiah@gmail.com` |

### 1.4 Why it reads as documentation, not marketing

On the homepage body: "you / your" appears **36 times**, and there is **exactly one capital "You"
on the entire page**. It is "You are fading faster than I planned", inside a mock quote from Jerry
in the set-card illustration. The site never once begins a sentence with the reader.

The reader is grammatically present on every line and is **never the subject of a sentence**.
That is the technical reason this page feels like a specification. The app is the subject of
nearly every sentence on the site.

Future-state language, homepage: "imagine" 0. "picture" 0. "you get" 0. "in 12 weeks" 0.
"in 6 months" 0. "by session 20" 0. **The site never once describes the reader's future.**

### 1.5 Page weight

| Page | Words | Read time |
|---|---|---|
| index.html | 1,123 | ~6 min |
| how-it-works | 1,361 | ~7 min |
| app-privacy | 889 | ~5 min |
| join | 438 | ~2 min |
| support | 424 | ~2 min |
| record | 343 | ~2 min |
| verify | 230 | ~2 min |

The only contextual buy-CTA on the homepage sits at **68% scroll depth**, after the reader has
been walked through a cryptographic commitment demo.

---

## PART 2 — DEFECTS, RANKED BY WHAT THEY COST

### D0 — THE PRIVACY POLICY STATES A FALSE FACT ABOUT THE APP. THIS OUTRANKS EVERYTHING ELSE IN THIS DOCUMENT.

A source-verification pass against the app repo (`OrderedStrength22`, branch `The-Tax-Sunday`)
was run against every factual claim on the site. It found one that is not a wording problem.

**The published policy says, verbatim** (`app-privacy/index.html:48-51`):

> "All of this is stored on your iPhone and is **never sent to us**: ...
> **Every set you log: exercise, weight, reps, and the reps you had left in reserve.**"

**The app sends exactly that list, on every freestyle workout completion, ungated.**

- `OrderedStrength2/FreestyleWorkoutView.swift:4466` calls `submitSetsToSovereignEngine()`
  unconditionally in the success path of `completeWorkout()`, after the Core Data save.
- `OrderedStrength2/FreestyleWorkoutView.swift:4691-4697` is the whole gate: `guard let userId =
  user.uuid`. There is no consent check, no toggle, and no `ProxyGateway.isEnabled` check. The
  proxy master switch gates voice and chat; **the set-ingest path never consults it.**
- `OrderedStrength2/FreestyleWorkoutView.swift:4725-4735` builds
  `SetIngestRequest(setId, userId, exerciseId, weight, weightUnit, reps, reportedRIR)`. That is
  the policy's enumerated list, plus a stable per-install `userId`.
- `OrderedStrength2/Core/Services/SetIngestionService.swift:57` validates and, when `isOnline`
  (which defaults to `true`), calls `apiClient.ingestSet`.
- `OrderedStrength2/Core/Networking/APIEndpoint.swift:138` and `:179` point at
  `https://ordered-strength-proxy.fly.dev`. That is the production host and it is live.

It is the **only** production construction of `SetIngestRequest` in the app; the other two are in
`Phase3MacrocycleTests`. So one call site is the whole exposure, and one call site is the whole fix.

**The server may reject the request today.** That does not help: privacy is about what leaves the
device, not about what the far end accepts. The body is on the wire either way.

**Two adjacent defaults are also ON**, and both carry stale comments in source claiming otherwise:
`Info.plist:35-36` sets `OSProxyDefaultEnabled` to `true` (while `ProxyGateway.swift:24-32`
still describes the default as off), and `RetentionAnalytics.isEnabled` returns
`... as? Bool ?? true` under a comment reading "sends NOTHING until the proxy ships". The proxy
has shipped.

**RECOMMENDATION, and this one is genuinely the CEO's because it is what the product IS.**
Gate `FreestyleWorkoutView.swift:4466` behind explicit consent, defaulting OFF. The pattern
already exists in the codebase at `JerryCloudBrain.swift:130`, which is how Cloud Answers is
correctly handled. That makes the strongest sentence on the whole website true, costs roughly five
lines, and reverts by deleting the guard. The alternative, amending the privacy policy to disclose
set ingestion, is worse: it trades the product's central promise for a paragraph, and the promise
is the moat.

**Not fixed in this mission, and why.** The directive was explicitly content-only, the app's
working tree currently holds twenty-two uncommitted Swift files belonging to another session, and
a networking change on a build that is on TestFlight needs `scripts/verify.sh fast` plus the
gauntlet on a tree I can own. This is not an engineering deferral: the next action is a
product-identity decision about whether OrderedStrength ingests training data server-side at all,
and that decision is the CEO's. The engineering behind it is five lines and one commit.

### D0b — THE SEAL DEMO ON THE HOMEPAGE IS NOT A REAL RECEIPT

The homepage says of the seal widget: "**A real sealed prediction, made before the set.**"
It is not. No app-produced receipt could ever hash to the object on screen.

- **The `kind` does not exist.** The site's console shows `field kind = topSetBand`.
  `topSetBand` appears **nowhere** in the app. The only three kinds the engine ever emits are
  `session-forecast` (`JerryTrackRecordEngine.swift:105`, `:236`), `sealed-envelope`
  (`SealedEnvelopeEngine.swift:76`), and `trial-prereg` (`SilentTrialEngine.swift:215`).
- **The field name is borrowed from a different payload.** The site shows `sealedOn`. The real
  session-forecast payload's sixth field is `sealedFor` (`JerryTrackRecordEngine.swift:109`).
- **The numeric scale is wrong by a factor of 1000.** `PredictionCommitment.swift:117` is
  `add(_ key: String, _ value: Double, places: Int = 4)` and no call site overrides it, so a real
  receipt encodes 102.5 kg as `1025000`. The site encodes it as `1025`.

The *protocol* is faithful: the page's JavaScript matches `server/verify.js` byte for byte, the
seal genuinely is minted before the first repetition (`LivePredictionEngine.swift:317-339`), and
the naive baseline it races is real. So the mechanism survives scrutiny and the **specimen does
not.** On the one page that says "not a mockup", that is the worst possible place to have a prop.

Fix: generate the demo receipt from a real `session-forecast` payload with the real field names
and the real 4-decimal scale, or relabel it "a receipt in the same format" and stop calling it real.

### D0c — "THE MISSES STAY ON THE RECORD" IS NOT TRUE INDEFINITELY

`index.html` hero fact: "Hits and misses both. **The misses stay on the record.**"
`JerryTrackRecordEngine.swift:457-459` trims to `record.events.prefix(100)`, newest first, so the
oldest events are evicted at one hundred. Honest version: "The misses stay on the record" →
"**Nothing is deleted to make him look better**", which is what is actually true.

### D1 — BLOCKING: THE PRIVACY PAGE CONTRADICTS THE MARKETING PAGES ON THE ONE SUBJECT THIS SITE IS ABOUT

Two pages say **one thing** leaves your phone. The privacy policy says **three**.

- `how-it-works/index.html:220-221` — "Exactly what does and does not leave your phone, including
  **the one thing that does**, is set out in the privacy policy."
- `join/index.html:79` — "including **the one thing that does**, is set out in the privacy policy."
- `app-privacy/index.html:45` — "**Three things can leave your device**, two of them only if you
  switch them on, and none of them is your training log."
- `app-privacy/index.html:8` (meta description) — "**the three things** that can leave it"
- `app-privacy/index.html:61` (heading) — "**The three things** that can leave your device"

**Why this is the worst thing on the site.** The reader who follows that link is, by construction,
the skeptic this entire site was built to convert. He clicks a sentence that says *one*, lands on a
page that says *three* in the heading, the first paragraph, and the meta description, and one of
the three (the daily usage summary, `app-privacy:70`) is **on by default**. Everything upstream of
that click is now discounted. The site's whole thesis is "we are the ones who do not overclaim,"
and its single measurable overclaim is about privacy.

The privacy policy itself is excellent and completely honest. The marketing pages are what is
wrong. **Fix the two marketing sentences, never the policy.**

### D2 — THE SITE ARGUES WITH ITS OWN EVIDENCE, IN THREE PLACES

This is the class of defect a sharp reader catches and never forgets, because in each case the
copy is refuted by the thing sitting directly under it.

**(a) "Three different surfaces" is two surfaces, and the site says so 30 lines later.**
- `index.html:398` — "Not three angles on one screen. **Three different surfaces**."
- `index.html:427` — the caption on the second one: "**The same session, further down.**"

It is the dashboard scrolled, the dashboard scrolled further, and one sheet. The headline is
refuted by its own figcaption. The one place on the site that promises it is not doing the
brochure move is doing the brochure move.

**(b) "The gate is evidence, never a countdown" is proven with two screens full of counters.**
- `index.html` annotation 03: "**The gate is evidence, never a countdown.** No feature unlocks
  because a week passed."
- The screenshot chosen to prove it (`evidence.png`) reads: "**Build toward 15 sessions'** worth of
  evidence" and "**Return after 3 more** unexpected or extended gaps."
- The interactive proof of the same claim (`index.html:257-263`) is a slider whose **only input is
  a session count** (`<input type="range" id="sessions" min="1" max="60">`), with a disclaimer
  underneath: "The tier is not a countdown."

An athlete drags a slider labelled *sessions you have logged*, watches the tier change as a pure
function of that number, and then reads a line telling him not to believe what he just saw. The
parenthetical that rescues it in the app ("dense days of quality working sets count fastest") is
true and is invisible to a skimming reader.

**(c) "No feature unlocks because a week passed" sits beside a button called "Unlock Map".**
In `intelligence.png`, on the site's own hero and again in the gallery: **Unlock Map — What opens
next, and what unlocks it.** The word *unlock* is gacha vocabulary. It is the exact word the copy
is arguing against, and it is on screen twice.

### D3 — EVERY CAPTURE ON THE SITE IS FROM A CLEAN INSTALL WITH ONE SESSION LOGGED

All three images: `dashboard.png` reads "Session 1", `intelligence.png` reads "1 session ·
building your model" on both cards, `evidence.png` is badged "Population" with every investigation
still open. The homepage shows two of them twice (hero at `index.html:172,186`, gallery at
`index.html:407,420`), so the reader sees "One session logged" **four times on one page**.

There is a section titled **"Day one against day one hundred"** and there is not one pixel of day
one hundred anywhere on this site. You are asking for $199 a year and showing only the free trial's
first evening. **The product you are selling is the app after 40 sessions and it has never been
photographed.** This is the largest missing asset, not a copy problem.

### D4 — THE BEST LIFT ON THE MARKETING SCREENSHOT IS A 56.3 kg SQUAT

- `index.html:414` — "The strongest thing on record is a `Barbell Back Squat` at
  `Estimated 1RM 56.3 kg`, **which is what a first block actually weighs**."
- Meanwhile `index.html` set-card mock: "Back Squat · set 3 of 4 — **100 kg · 6 reps · RIR 2**",
  "**102.5 kg**", "**102.5 kg**".

56.3 kg is ~124 lb. To the intermediate lifter who is your actual buyer, that is a beginner
number, and it is the number the site labels *best on record*. The caption's defence
("what a first block actually weighs") is a rationalisation the reader will not perform on your
behalf. Worse: your own illustration on the same page shows a 102.5 kg working set. Read together,
the reader concludes the illustration is aspirational and the capture is the truth.

The fixture, not the copy, is the defect. A capture whose athlete squats 140 kg costs nothing to
generate and removes the whole problem. (The commit `4b5eba0` "The athlete on the front page trains
a week a human would recognise" already started this work; it has not reached the captures.)

### D5 — NOBODY MADE THIS

Zero founders, zero names, zero faces, zero athletes, zero testimonials, zero "who we are".
The support and contact address on a $199/year product is **`tachiwonajeremiah@gmail.com`**
(`support/index.html`, `app-privacy` contact, and the homepage `mailto:` at `index.html:468`).

The site says "**Write to us. A person writes back**" (`join/index.html`) and then declines to say
who the person is. For a product whose entire pitch is *trust me, I will tell you when I am wrong*,
the total absence of a human being is the credibility hole. Elite teams put a name on the work.
The anonymity reads as either a shell or a generator, and it is the single strongest argument that
this site was produced by a machine, far stronger than any sentence in it.

The gmail address is a separate, smaller unforced error: you own the domain, the site sells
epistemic rigour, and the contact address is a free consumer mailbox.

### D6 — "JERRY" IS NEVER INTRODUCED

`index.html:157`, the third line of the page: "**Jerry** plans every session..." First and only
context. The reader does not know whether Jerry is the founder, the app, or a person who will read
their data. The name is the product's warmest asset and it is deployed cold. `how-it-works` has the
same problem at `:75`.

### D7 — $199 APPEARS ONCE, AT 68% DEPTH, AGAINST NOTHING

`index.html:458`. No anchor, no comparison, no justification. The most persuasive sentence
available to this product is absent from the site: **a human strength coach costs $200 to $400 per
month.** $199 a year is 4% of that. You are 16 dollars a month against a category where Whoop is
$30, Juggernaut is $35, and a real coach is ten times either. That comparison is free, true, and
not written anywhere.

### D8 — "READ THE RECORD" IS A PRIMARY CTA POINTING AT AN EMPTY PAGE

`index.html:463` — the ghost button beside "Join the test" sends the reader to `/record/`, which
says "**Not started yet.**" The decision to start empty is correct and is the bravest thing on the
site. Making it one of the two buttons in your conversion block is not. The reader's last
impression before deciding is a blank page.

### D9 — THE SITE BREAKS ITS OWN RULE EXACTLY FOUR TIMES, AND ALWAYS IN A COMPETITIVE SUPERLATIVE

A site built on not overclaiming makes four claims it cannot substantiate:

- `index.html:8` (meta description) — "...and **is the only one that can be checked**."
- `index.html:440` — "**The line that no competitor ships**: ..."
- `how-it-works/index.html:60` — "Then **the promise no other app makes**."
- `record/index.html:44` — "**Nobody in this market publishes** how often they were right."

Each requires having audited every competitor. None is defensible in a dispute, and the last one
is the kind of statement a competitor's lawyer enjoys. They are also unnecessary: the honest
version is stronger. "I have not found another one that does" is more credible than "nobody does,"
because it is the sentence of someone who actually looked.

### D10 — THE ONE PIECE OF COPY DOING THE MOST WORK IS BURIED

The single most persuasive object on the entire site is the set-card mock in section 2:

> Set 4 — **withdrawn / cut**
> *"You are fading faster than I planned. I am cutting the last set. That protects tomorrow more
> than one more hard set helps today."*

That is the product. It is concrete, it is emotionally legible, no competitor does it, and an
athlete understands it instantly with no explanation. It is at roughly 25% scroll depth under the
heading "He decides, then he reacts", and the hero says nothing about it.

---

## PART 3 — DOES IT SOUND LIKE AI?

Asked directly, so answered directly, with the evidence in both directions.

### What CLEARS it (I tried to convict and could not)

- **Zero em-dashes** in 4,904 words. Zero en-dashes. Zero curly apostrophes. The single most
  reliable machine tell in English prose is absent, and deliberately so.
- **No hype adjectives.** No "seamless", "powerful", "revolutionary", "cutting-edge", "elevate",
  "unlock your potential", "journey". Not one.
- **No emoji, no rocket, no checkmark bullets, no "In today's world".**
- **Sentence length is human-shaped.** Homepage median 10 words; 30 sentences under 8 words, 14
  over 20. Generated marketing prose clusters tightly at 15-22. This does not.
- **Real specificity.** "RIR 2", "102.5 kg", "Pop. Est.", "4 out of 10 on Tuesday", "17 days until
  full load". Machines write round numbers. These are not round.
- **The aphorism rate is lower than I expected.** I predicted an epigram per paragraph; measured,
  it is 9 of 87 homepage sentences (10%). My own hypothesis was wrong and I am recording that.

### What CONVICTS it

1. **The homepage sections share one scaffold almost perfectly.** Counted from source: 8 sections,
   **8 of 8** carry an eyebrow label, **8 of 8** carry a heading that is a complete declarative
   sentence ending in a period, **7 of 8** carry a one-sentence `sub` (section 2, "He decides, then
   he reacts", is the single exception). A human writer varies structure out of boredom; here the
   variance across eight consecutive sections is one missing paragraph.
   *This is the strongest tell on the site and it is structural, not verbal.*
2. **The negation frame runs at 1 per 170 words**: "rather than" ×11, ", not X" ×10, "instead of"
   ×4, "it is not" ×4 = 29 occurrences. Define-by-what-it-is-not is the house style of a language
   model asked to sound principled.
3. **Nobody is in it.** No name, no face, no biography, no grudge, no anecdote, no gym, no failure
   story, no date that mattered to a person. Every fact on the site is about a *system*. This is
   what an elite team's site never looks like, because elite people are vain about the right things
   and they sign their work.
4. **Perfect internal consistency of voice across seven pages including the legal one.** The
   privacy policy is written in the same cadence as the hero. Humans get tired; legal pages come
   from a template and read like it. This one does not, which is admirable and is also a tell.
5. **The footer tagline is byte-identical on all seven pages** and "Your training is computed on
   your device" appears three times per page.

**Verdict on the AI question:** a careful reader will not be able to point at a *sentence* and say
"a machine wrote that." They will feel it from the *architecture*: eight near-identical section
shapes, no human being anywhere, and a page that never wants anything from you. The remedy is not
to write worse. It is to **break the template three times and put a person in it.**

### And the harder question: does it sound like an elite team?

It sounds like **one very good writer with no colleagues.** That is a different thing, and the
difference is legible.

What elite reads like on this site, genuinely: the empty record page and the paragraph explaining
why backfilling it would destroy the only thing it is for. The privacy policy written from the
app's own source. The decision to display "Pop. Est." on a marketing screenshot instead of cropping
it out. The seal widget that invites you to break it. Those are not the moves of someone
assembling a landing page. They are the moves of someone who has thought about this for a long
time and is not afraid of a skeptic. No competitor in this category has anything like them.

What is missing is everything that makes a *team* visible: a second opinion, an argument that got
settled, a section someone fought to keep, a name, a face, a job title, a photograph of a gym.
Elite teams are legible because their work carries fingerprints, and fingerprints are exactly what
this site has none of. Every page is the same temperature. Nothing is uneven, and unevenness is
what a group of strong people produces.

The commercial version of this problem: the reader cannot tell whether they are buying from a
company or from a project. At $199 a year, on a product that stores everything locally and will be
gone with the phone if the developer disappears, "is anyone actually there" is a live question and
the site does not answer it once.

**So: elite craft, invisible team, and the invisibility is the thing costing you.**

---

## PART 4 — WHAT ATHLETES ACTUALLY SAY WHEN THEY READ THIS

Three real readers, in the order they will arrive.

**The 8-month lifter (arrives from a link, is not your buyer at $199).**
Reads "A coach who writes it down before you lift." Does not know what that means; his notes app
writes it down. Scrolls, finds a slider about population estimates, then a SHA-256 fingerprint.
Leaves at about 40%. **What he says: "I couldn't tell what it actually does."**

**The intermediate, three years in, currently on a spreadsheet or 5/3/1 (this is your buyer).**
Reads "He never adds weight on a calendar. He holds the load, asks for one more repetition, and
adds the plate once you have earned it." and thinks: *that is double progression, I already run
that for free.* He is right, and the site never tells him what it does that his spreadsheet cannot:
cut set 4 while he is standing there, refuse a muscle he asked for and show the receipt, hold an
injury ramp on his reported pain, remember him across months. Those are on page two, in prose.
**What he says: "Nice principles. What does it do that my program doesn't?"** He does not reach
the price.

**The skeptic, ex-Whoop, reads Hacker News (this is who the site is actually written for).**
Loves it. Reads all 4,900 words. Breaks the seal widget. Then clicks "the one thing that leaves
your phone," lands on "**three things can leave your device**," one of them on by default.
**What he says: "So which is it?"** And that is your best-fit reader, lost at the last inch by a
sentence that was easier to fix than to write.

Nobody in these three says "this app will make me stronger," because the site never claims it.

---

## PART 5 — WHAT IS THE POINT OF THIS SITE, AND IS IT SERVING IT?

Stated honestly, the site currently has three jobs and does them at three different levels:

1. **Prove the product is honest.** Grade: A. Nothing in this category comes close. The seal
   widget, the empty record page, the "Pop. Est." captures, the privacy policy written from source.
2. **Explain what the product does.** Grade: C. The differentiators exist, in the right words, on
   the second page. The homepage leads with record-keeping, which sounds like administration.
3. **Make an athlete want it.** Grade: F. Measured: 5 outcome words, 0 sentences where the reader
   is the subject, 0 future-state language, 0 humans, 0 social proof, price at 68% depth with no
   anchor.

**Does it market itself? No. It documents itself.** Those are different acts. A marketing page
makes the reader *want* something. This page makes the reader *respect* something. Respect is
necessary here and it does not convert on its own. You have built the most trustworthy page in
your category and forgotten to ask anyone to train.

The point of this site should be one sentence: **make a serious lifter believe that a coach who
changes the session while he is in it will get him stronger than the program he is running now, and
that this one can be checked.** Right now the site delivers the second clause at world class and
the first clause not at all.

---

## PART 6 — SUBTRACTIONS (what to cut, and why)

Cutting is the highest-leverage work here. The homepage is 1,123 words for a product nobody can
buy yet.

| Cut | Where | Why |
|---|---|---|
| `scripts/verify.sh screens` printed literally, ×2 | `index.html:315`, `index.html:444` | An athlete does not know what a test suite is. Replace with "captured automatically by our own test run, on a phone with nothing on it". Same claim, no shell command. |
| "nonce", "root hash", "byte for byte", "scheme os-commit-v1-sha256" | seal widget + `/verify/` | Keep the widget. Move the crypto vocabulary behind a "what is actually sealed" disclosure that is closed by default. The skeptic opens it; the athlete never sees it. |
| The full field dump (`field kind = topSetBand`, `bandLowKg = 1025`...) | `index.html` seal panel | This is a debug console on a marketing page. Collapse it. |
| One of the two hero devices | `index.html:172-186` | Both are the same session. Two phones showing one session logged reads as one screenshot photographed twice. |
| "The status bar is the simulator's own" | `index.html:316` | Honest and unnecessary. It draws attention to the fact that this is not a real phone. Fix the status bar instead. |
| Duplicated privacy assurance ×3 per page | footer + facts + body | Say it once, well. |
| "Read the record" as a primary CTA | `index.html:463` | Empty page as the last impression. Demote to a text link until the first anchor lands. |
| The four superlatives | D9 above | Replace with the falsifiable version. |

**Do not cut:** the empty record page, the seal widget itself, "Pop. Est." captions, the
declines/refuses section, the privacy policy. Those are the moat.

---

## PART 7 — THE SCREENSHOTS, ONE BY ONE: DO THEY SURVIVE SCRUTINY?

### `dashboard.png` — SURVIVES WITH TWO WOUNDS
Strong: "One session logged. Your individual model starts from it." is a better headline than
anything on the website. "Fatigue (Pop. Est.)" / "Calibration (Building)" with an empty ring is the
proof, and it is real.
Wounds: **(1)** "Best on record: Barbell Back Squat · Estimated 1RM **56.3 kg**" — see D4.
**(2)** the "Fatigue Forecast" slider is clipped at the bottom edge with the axis labels
half-cut ("Now / 24H / 48H / 72H" sliced through). A capture that ends mid-component reads as an
accident, on a page whose caption says "nothing staged".
Minor: the banner says "You were away for 3 days" while the badge says "Session 1" — coherent
(one session, then a gap) but it takes the reader a beat, and a beat is expensive above the fold.

### `intelligence.png` — DOES NOT SURVIVE UNCHANGED
**(1) "Unlock Map · What opens next, and what unlocks it"** directly contradicts the site's
annotation 03 (D2c). **(2) "Full Intelligence — 40 Surfaces"** is a feature-count brag, which is
precisely the move this site's voice rejects everywhere else; "40 Surfaces" means nothing to a
lifter and reads as filler inflation to a skeptic. **(3)** Both cards carry the identical footer
"1 session · building your model", so the capture's dominant visual message is *this app has been
used once.*
This is the weakest of the three and it is used **twice** on the homepage, including in the hero.

### `evidence.png` — THE BEST IDEA, THE WORST EXECUTION FOR THIS ARGUMENT
The concept is unmatched: an app listing what it does not yet know, by name, with what would close
each. "Each one names the evidence I still need" is the best line in the product.
But the site deploys it as proof that **"the gate is evidence, never a countdown"**, and the visible
text is "**Build toward 15 sessions'** worth of evidence" and "**Return after 3 more** ... gaps".
The site chose, as its evidence against countdowns, the one screen that displays two counters
(D2b). Also undecodable to any reader: the tab-bar dot rows with trailing "+"
(`Coach ●●●● / Body ●●●●●●+`).

### The one they all share
All three are session 1 (D3). There is no capture of the product anyone would pay $199 for.

---

## PART 8 — THE ACTION PLAN, ORDERED FOR EXECUTION

No design work. Every item is copy or fixture. Each is independently shippable.

### TIER 1 — SHIP TODAY (trust defects; each is one sentence)

**A1. Fix the privacy contradiction.** `how-it-works/index.html:220-221` and `join/index.html:79`.
Replace "including the one thing that does" with:
> "including **the three things that can**, one of which is on by default"

Reason: it must be *more* candid than the policy, never less, or the click-through kills you.
This is the highest-value four-word edit on the site.

**A2. Fix "Three different surfaces."** `index.html:398`. It is two surfaces. Replace:
> "Not three angles on one screen. **Two surfaces and a sheet**, each one admitting something..."

Or re-shoot so it genuinely is three. The current line is refuted by `index.html:427`.

**A3. Retire the four superlatives.** `index.html:8`, `index.html:440`,
`how-it-works/index.html:60`, `record/index.html:44`. Pattern:
"Nobody in this market publishes how often they were right" → "**We have not found another app in
this market that publishes how often it was right. If one exists, tell us and we will link it.**"
The offer to be corrected is worth more than the superlative and cannot be disputed.

**A4. Put a name on the site.** One line in the footer or on `/join/`:
> "Built in [city] by Jeremiah Tachiwona. If you write to us, you are writing to me."

This single line does more against the "made by AI" charge than any rewrite. **CEO decision: this
is product identity and yours alone. My recommendation is to sign it.**

**A5. Move support off gmail.** `support@orderedstrength.com` → forwards to the same inbox.
Sites at `orderedstrength-site` already own DNS. Costs nothing, removes a credibility tax on
three pages.

### TIER 2 — SHIP THIS WEEK (the re-aim)

**A6. Rewrite the hero to lead with the set he cuts, not the record he keeps.**
Current, `index.html:155-159`:
> Strength coaching for iPhone
> **A coach who writes it down before you lift.**
> Jerry plans every session, changes it as each set lands, and records what he expected from you
> before you touch the bar. Then he grades himself on it and keeps the misses.

Recommended:
> Strength coaching for iPhone
> **He changes your workout in the middle of it.**
> Most apps hand you a program and stop listening. Jerry writes the next set while you are still
> breathing hard from the last one: he cuts the session when you are fading, adds the plate the day
> you earn it, and writes down what he expected from you before you touch the bar, so you can check
> him on it later.

What changed and why: the differentiator moves from *record-keeping* (sounds like admin, a logbook
also does it) to *mid-session reaction* (nothing in the category does it, and an athlete
understands it in three seconds). The honesty claim survives as the closing clause, which is where
it belongs: it is the *reason to believe*, not the *reason to buy*. Runner-up considered and
rejected: "A coach who is still watching after the first set" — better rhythm, less concrete.

**A7. Change the hero CTA target.** `index.html:161`, "See what that changes" currently jumps to
`#dial`, the population-estimate slider: the first thing the athlete is invited to see is the app
admitting it does not know him. Point it at `#coach`, the withdrawn-set card. Make the seal and the
dial the *second* thing, for the skeptic who scrolls.

**A8. Add the price anchor.** In the commitment block, `index.html:458-460`:
> "A strength coach costs $200 to $400 a month. This is $199 a year, and the accuracy record goes
> up before anyone is charged."

**A9. Introduce Jerry.** `index.html:157` and `how-it-works/index.html:75`, first mention:
> "**Jerry, the coach inside the app,** plans every session..."

**A10. Demote "Read the record."** `index.html:463`. Make the second button "How it works" and
leave `/record/` as a text link beneath. Restore it to a primary CTA the day the first anchor lands.

**A11. Cut the engineer vocabulary from the homepage.** Per Part 6. Keep every claim; collapse the
crypto detail behind a disclosure. The skeptic still gets it in one click; the athlete never trips
over it.

### TIER 3 — THE MISSING ASSET (this is the real work)

**A12. Photograph day one hundred.** Every capture on the site is a clean install with one session
logged (D3). Generate a fixture with 40+ sessions and capture: the dashboard with a *real*
calibration number in the middle ring; the accuracy card with a run of hits and at least one honest
miss; a strength curve that has moved. Then the section titled "Day one against day one hundred"
can show day one hundred, and the $199 has something to point at.

**A13. Fix the fixture athlete's numbers.** The capture's "best on record" must not be 56.3 kg
(D4). An intermediate's numbers, matching the 102.5 kg already in the site's own illustration.

**A14. Re-shoot `intelligence.png` or replace it.** It contains "Unlock Map" and "40 Surfaces",
both of which fight the copy (D2c, Part 7). If those strings are staying in the app, this screen
should not be the site's hero image.

**A15. Break the template three times.** Eight of eight homepage sections share one scaffold
(Part 3, tell #1). Pick three and vary them: one with no eyebrow, one whose headline is a fragment
rather than a sentence, one that opens on the quote from Jerry instead of a heading. Structural
variance is what stops a careful reader feeling the machine.

### TIER 4 — WHEN THE TEST GROUP HAS RUN A BLOCK

**A16. One athlete, named, with numbers.** Not a testimonial card. One paragraph: who he is, what
he ran before, what the app cut and why, what moved in twelve weeks, and one thing it got wrong.
The last clause is the one no competitor can copy, and it is the version of social proof that this
site's voice can carry without breaking character.

---

## PART 9 — WHAT I CHALLENGED, INCLUDING MY OWN ASSUMPTIONS

Per Rule 13, the refutations are reported as a first-class number. I set out to convict this site
on six charges and **three of them collapsed on measurement**:

1. **REFUTED — "it will be full of em-dashes."** Zero, across 4,904 words. Also zero en-dashes and
   zero curly apostrophes. The app's copy law was carried onto the web unprompted.
2. **REFUTED — "the aphorism rate will be superhuman."** I predicted one epigram per paragraph.
   Measured: 9 of 87 homepage sentences, 10%. Within human range. My hypothesis was wrong.
3. **REFUTED — "the writing is generic."** It is not. It is better than anything else in this
   category, it never reaches for a hype adjective, and it contains genuinely good lines
   ("He would rather refuse than guess", "It cannot be wrong, which is why it cannot be evidence").
   The problem is aim, not quality.
4. **CONFIRMED — the audience is wrong** (Part 1.2, 22 engineer-only terms, two printed shell
   commands).
5. **CONFIRMED — the outcome is missing** (Part 1.1, 18:1).
6. **CONFIRMED — the site contradicts itself** (D1, D2, three separate instances, all cited).
7. **REFUTED — "the site will be misquoting its own app."** I checked every string the site puts
   in quote marks against `OrderedStrength2/Localizable.xcstrings`. They are verbatim:
   "Each one names the evidence I still need", "intelligence surfaces open on evidence, not time",
   "Unlock Map", "%lld Surfaces". The site quotes the app accurately. The problem in D2 is that two
   of those accurate quotes argue against the copy surrounding them.
8. **CORRECTED IN MY OWN AUDIT.** My first draft of Part 3 claimed all eight homepage sections
   share an identical three-part scaffold. Counted at source, it is 8/8 on two elements and 7/8 on
   the third. Fixed above rather than left standing.

---

## FINAL

You asked whether it survives scrutiny. **The prose does. The strategy does not, and three factual
contradictions do not.** Nothing here requires you to write worse or sound less like yourself. The
voice is an asset and it should be kept exactly as it is. What has to change is who the sentences
are aimed at, that a human being appears somewhere on the page, and that the site stops
contradicting itself in the two places a skeptic is guaranteed to look.

The cheapest item on this list is A1: four words on two pages, and it closes the worst trust hole
on the site. The most valuable is A12: photograph the product you are actually selling.
