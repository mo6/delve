# Parrot: concept note

**Status: research only.** Not scheduled. Extends the undesigned future species in
[PETS.md](PETS.md) §12 ("Parrot (talking)") and sits beside the cat's free consult and the dog's
fetch ([OBJECTS.md](OBJECTS.md) §8). This note fixes character, suggests mechanical uses, and
samples pirate-voice lines for the pilot pack (`security-onboarding`, *The Caverns of Compliance*).

Nothing here is implemented. Glyph, knobs, and the exact help rule stay open until a later issue.

---

## 1. The pitch

A **parrot** is the talking companion: it mills near you, occasionally squawks, and (when asked, or
rarely on its own) drops a **pirate-flavoured hint** about the lesson or the question in front of
you. Where the cat *strikes an option* and the dog *fetches loot*, the parrot *says something*.

That split keeps the three species readable:

| Species | Edge | Feel |
|---|---|---|
| Cat | First consult free; strikes a wrong option | Clever, quiet help |
| Dog | Fetches any floor item; heels to deliver | Loyal, useful body |
| Parrot | Speaks; hints in pirate speech | Loud, colourful, half-helpful |

The parrot is flavour first and help second. A learner who picks it should feel they brought a
crewmate who overheard every keeper, not a walking answer key.

---

## 2. Character

**Who it is.** An old ship's bird that somehow ended up in a corporate dungeon. It has heard every
scam that ever crossed a quay: forged letters, false captains, "urgent" cargo, strangers with
plausible names. It translates that street sense into Delve's lessons without ever sounding like a
slide deck.

**Voice.** Pirate English, but short. Squawks and one-liners, not speeches. The bird mangls grammar
on purpose (`be`, `ye`, `arr`), loves nautical metaphors for digital threats (hooks, forged seals,
false colours, treasure maps that lead to rocks), and repeats the useful bit twice when excited.

Rules of thumb for any line it says:

- **One idea per squawk.** Never a full explanation; that is the keeper's job.
- **Hint, don't spoil.** Nudge toward the *habit* (slow down, check the domain, don't share the
  link) rather than naming the numbered answer.
- **No em-dashes.** Same house rule as pack prose; pirates use commas, colons, and ellipses.
- **Never grade.** It may be wrong, vague, or theatrical. The gate and the grader stay authoritative
  (same spirit as ACTORS.md: the model, or the bird, animates; it does not adjudicate).
- **Locale later.** Concept samples below are English only. A Dutch pirate voice (`arr` → something
  that still reads as fun, not as a cartoon insult) needs its own pass; do not machine-translate.

**Default name.** Something like "Polly" or "Cap'n" if the learner leaves the name blank; the prompt
asks "What is your parrot's name?" like the dog and cat.

**Glyph (proposed).** `B` (NetHack's bird class), as PETS.md already floats. Avoid `p` (already
crowded in NetHack lore) and anything non-ASCII.

**Movement feel (proposed).** Narrow interest in money (it is not a fetch pet), a loose leash so it
perches around the room, high wander so it flutters. Carrying coins is optional flavour; the dog
already owns fetch. Prefer **no purse** at first so the parrot's identity stays "talks", not
"also competes for `$`".

---

## 3. Suggested uses

Ordered from smallest change to richest. Any one of these is enough for a first ship; stacking them
is a later balance problem.

### A. Idle chatter (pure colour)

On a pet step, with low probability, emit a `spoke` event (PETS.md §6 already reserves this) carrying
a flavour line. No mechanical effect. The session prints something like:

> Polly squawks: "Pieces of eight! Check the seal twice, ye lubber!"

Drawn from a small pool of **ambient** lines (chapter-agnostic) plus optional **room-tagged** lines
once the learner has entered a keeper's room. This alone justifies the species.

### B. Consult (`?`) in pirate speech

Reuse the existing consult key. Instead of (or as well as) striking a wrong MCQ option, the parrot
returns a **spoken hint** for the current question or room. Cost model options:

1. **Same as the dog:** consult always costs (never free); the payment is a cryptic squawk, not a
   struck option.
2. **Same as the cat's freebie:** first consult per room free, further ones cost; the freebie is a
   voice line rather than an option strike.
3. **Hybrid:** first consult is a free squawk; further consults either escalate to a clearer hint
   (still pirate) or fall through to the usual option-strike, so the parrot is not strictly worse
   than the cat at hard questions.

Recommendation for a first cut: **(2)**. Distinct from the cat (words vs struck option), still a
reason to pick the bird, easy to explain on the choice screen ("a parrot that hints in pirate talk").

### C. Echo the keeper

After the learner finishes a lesson page (or passes), the parrot occasionally repeats a mangled
version of the keeper's punch line. Reinforces teaching without new authoring if the echo is built
from a short per-room `parrot_echo` string in frontmatter, or from a hand-authored pool keyed by
`room.id`. Prefer an authored pool over scraping lesson prose: scraping will produce bad pirate and
risk spoilers.

### D. Rare unsolicited nudge during an exam

While a question overlay is open, a very rare `spoke` (or a one-shot on entering the exam) drops a
hint. High risk of feeling noisy or unfair (some learners get a free tip). Cap hard: at most once
per room, never on the unscored tutorial, and only if the learner chose the parrot. Probably
**defer** until A and B feel good.

### E. Pack-authored hint tables

Authors ship optional `parrot` lines per room (or per question id) in the pack, the way items carry
`on_pickup`. The engine only picks and emits; content stays out of code (rule 5's spirit: prose in
the document world, not in Python). The pilot samples in §5 are the seed of that table for
`security-onboarding`.

### F. What not to do

- **Do not let the parrot open doors, change scores, or auto-answer.** Help is information, never
  adjudication.
- **Do not put full explanations in squawks.** If the line could replace the keeper, it is too long.
- **Do not compete with the dog on fetch** in v1. Three pets, three jobs.
- **Do not generate pirate live from the LLM grader path** for the first version. Hand-authored
  pools keep voice, both locales, and determinism under control; ACTORS.md can revisit generative
  squawks later as *expressive* behaviour only.

---

## 4. How it would plug in (sketch)

For implementers later; not a spec.

1. Registry entry in `engine/pet.py`: `parrot` → glyph `B`, low `interest`, loose `leash`, high
   `p_wander`.
2. Extend `PetEvent` with `kind="spoke"` and a stable line id (or the session maps id → string).
   Engine stays string-free (rule 1); `delve/strings/{en,nl}.toml` holds ambient lines; pack tables
   hold lesson hints.
3. Selection: `--pet parrot`, prompt grows to `[cdp]` or similar, default name `"your parrot"`.
4. Snapshot: species already stored; no new state if there is no purse. Optional
   `parrot_consult_used` mirrors the cat's freebie flag.
5. UI: paint `B`; message line shows the squawk; hint line can mention `?: ask your parrot`.

---

## 5. Line pool: *The Caverns of Compliance*

Two kinds of line:

- **Ambient chatter:** can fire anywhere; no lesson spoilers.
- **Room hints:** keyed to the pilot pack's twelve rooms; safe to use on consult or as a rare echo
  after the learner has opened that room's lesson. Worded as *nudges*, not answer keys.

Replace `{name}` with the parrot's name at print time.

### 5.1 Ambient chatter

1. `{name} ruffles its feathers. "Arr! Fresh meat on the stair!"`
2. `{name} squawks: "Pieces of eight! Mind yer purse, sailor!"`
3. `{name} mutters: "Pretty bird. Pretty careful bird."`
4. `{name} tilts its head. "Who goes there? Friend or phish?"`
5. `{name} screeches: "Avast! A door that won't open be a lesson, not a wall!"`
6. `{name} whispers: "Slow waters run deep. Hurry be the hook."`
7. `{name} cackles: "I seen captains fooled by a forged seal. Ye ain't special."`
8. `{name} hops closer. "Ask me proper and maybe I'll sing."`
9. `{name} preens. "Crackers is nice. Caution is nicer."`
10. `{name} squawks: "Dead men tell no tales. Live ones report the odd mail."`
11. `{name} eyes a coin pile. "Shiny! But I ain't yer dog."`
12. `{name} flaps once. "The keepers talk true. I just talk louder."`
13. `{name} mutters: "False colours on the mast. Always look twice."`
14. `{name} chirps: "A sealed door means ye still got thinkin' to do. Arr."`
15. `{name} yawns: "Wake me when the exam starts. Or don't."`

### 5.2 Room hints (pilot pack)

Keyed by room `id`. One primary hint plus a spare; rotate with the pet RNG so repeats stay fresh.

#### Chapter 1 — The Sorting Office

**`phishing` (Recognising a Phish)**

- `"When the letter shouts NOW, that be the attack talkin'. Slow down and check one thing. Arr!"`
- `"Urgency be the bait, mismatch be the hook. Look where they hoped ye wouldn't."`
- `"A CEO wantin' gift cards in secret? That ain't business. That be plunder by post."`
- `"Spellin' mistakes ain't the tell no more. Clever thieves can spell. Check the seam that don't fit."`

**`targeted` (When It Is Written For You)**

- `"Spear-fishin' uses yer own name on the hook. Personal don't mean honest."`
- `"Bank details 'changed' from a long-time supplier? Call them on a number ye already trust. Not the one in the mail."`
- `"Fancy writin' don't make an attack expensive. The expensive ones just know yer name."`
- `"Hidn' from the internet helps a little. Verifying strange requests helps a lot more. Arr."`

**`links-and-attachments` (Links, Attachments, and the Space Between)**

- `"The treasure map's last island be the real destination. Read the domain at the end, not the pretty words."`
- `"`google.com.evil.net` still ends at evil. Hoverin's a look, not a blessing."`
- `"A PDF from a stranger with no hurry and no ask still ain't automatically safe. Strange cargo is strange cargo."`
- `"A file named report.pdf can be a wolf in sheep's clothing. Names lie. Arr!"`

#### Chapter 2 — The Vault

**`passphrases` (Length Beats Cleverness)**

- `"Short and clever sinks ships. Long and plain sails farther."`
- `"One great passphrase for every chest? One breach and they got the whole hold."`
- `"Hard for you to read ain't the same as hard for a machine to crack. Length, ye swab."`
- `"Changin' passwords every ninety days for sport? Only change when ye got a reason. Arr."`

**`managers` (One Lock Worth Picking)**

- `"One strong vault beats a dozen rotten locks. The basket talk is fear, not wisdom."`
- `"Encrypted chests stolen from a manager still need the master key. Stolen vault ≠ open vault."`
- `"Memorise the one that opens the manager. Let the manager remember the rest."`
- `"Yer browser rememberin' passwords ain't the same crew as a proper manager. Different ship."`

**`mfa` (The Second Factor)**

- `"Phone buzzin' and ye ain't loggin' in? Someone's knockin' with yer password. Deny it and change course!"`
- `"Password plus a secret question be two of the same kind o' thing. That ain't real multi-factor."`
- `"A key ye hold beats a code that can be phished. Passkeys and hardware keys be stout timber."`
- `"SMS MFA be leaky, aye, but leaky still beats a naked password. Take what ye can get."`

#### Chapter 3 — The Archive

**`classification` (Knowing What You're Holding)**

- `"Stamp every scrap 'Restricted' and soon nobody reads the stamp. Over-classifying be fog."`
- `"Public facts glued to a private deal can still be cargo worth guarding."`
- `"When ye don't know the mark, ask; don't invent the highest stamp out o' panic."`
- `"What's in the document sets the class, not how nervous ye feel. Arr."`

**`sharing` (Anyone With The Link)**

- `"'Anyone with the link' means anyone who finds the link. That's the whole seven seas."`
- `"Ye shared one file wide open? Fine today. Tomorrow the link still sails without ye."`
- `"Access that was right last year may be wrong this year. Revoke what ye don't need."`
- `"Before ye send the sheet outside, check the other tabs. Hidden cargo sinks reputations."`

**`devices` (The Thing You Carry)**

- `"Stolen laptop, screen unlocked: encryption saves the disk, not the session ye left open."`
- `"Public Wi-Fi ain't automatic doom if ye use the proper channels. Panic less, patch more."`
- `"Old holes everybody knows beat fancy new ones. Patch the known leaks first. Arr!"`
- `"Mystery USB in the car park? That be bait. Don't plug it. Hand it to the watch."`

#### Chapter 4 — The Watchpost

**`social-engineering` (The Attack That Is Just A Conversation)**

- `"The sharpest cutlass here be a friendly chat. They want yer trust, not yer firewall."`
- `"Hold the door for a stranger with full arms and ye may be holdin' it for a thief. Badge yer own self."`
- `"Knowin' yer name and yer boss don't make a caller honest. Public facts ain't a passport."`
- `"IT never needs yer password over the horn. The ask itself be the red flag. Arr!"`

**`ai-tools` (What You Told The Oracle)**

- `"What ye whisper to a foreign oracle may not stay in the cave. Don't feed it the crown jewels."`
- `"Free consumer chat and the company tool ain't the same ship, even if the sails look alike."`
- `"Stack traces carry secrets. Read twice before ye paste. Arr."`
- `"Deletin' the chat don't unsay what the oracle already heard. Prevention beats scrubbin'."`

**`reporting` (The Last Door)**

- `"Clicked a shady link and nothin' happened? Still tell the watch. Quiet trouble grows."`
- `"Fast and rough beats slow and perfect. The clock matters more than pretty words."`
- `"Punish the reporter and ye teach the crew to hide the hole. Then the ship sinks silent."`
- `"Odd mail from a mate's account? Raise it kind, raise it quick. Embarrassment is cheaper than a breach."`

### 5.3 Exam-time nudges (optional, sharper)

Use only on consult during a question, and keep even vaguer than the room hints so they do not
point at a single option:

- `"Which answer keeps ye slow and checkin'? That be the trade wind."`
- `"If it sounds like hurry, pick the option that buys time."`
- `"Trust processes ye already know over strangers with urgent tales."`
- `"When two answers feel clever, pick the boring safe one. Arr."`

---

## 6. Open questions

1. **Consult vs chatter only.** Is pirate speech enough without any score interaction, or does the
   parrot need a freebie to compete with the cat on the choice screen?
2. **Authoring burden.** Per-room lines in the pack (localised) vs a global strings table keyed by
   `room.id`. Pack-local is better for third-party packs; strings-local is faster for the pilot.
3. **Dutch pirate.** Needs a native voice pass, not a glossary swap. Who writes it?
4. **Tutorial floor.** Should Dlvl 0 get a couple of interface squawks ("Space waits. I flutter.") or
   stay silent so the Porter and Alwin own the teaching?
5. **Wrong on purpose?** A rare misleading squawk would be on-brand for a chaotic bird and terrible
   for training trust. Default recommendation: **never intentionally wrong** on consult; ambient can
   be pure nonsense.

---

## 7. Relation to existing docs

- [PETS.md](PETS.md) §12 — owns the registry hook and the `spoke` event sketch; this note fills
  character and content.
- [OBJECTS.md](OBJECTS.md) §8 — owns the companion split on question help; parrot would add a third
  flavour (spoken hint) beside cat freebie and dog paid strike.
- [ACTORS.md](ACTORS.md) — generative speech later, expressive only; first parrot should be
  hand-authored pools.
- [STYLE.md](STYLE.md) — learner-facing lines follow the no-em-dash rule and the pack's plain voice,
  even when dressed as pirate.

When this moves from research to build, cut an issue (`DELVE-NNNN`) with Given/When/Then around
selection, `spoke` messaging, and one consult path; keep the line pool in the issue or in pack
files, not in `engine/`.
`)