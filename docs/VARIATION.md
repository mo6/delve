# Variation and genre: an LLM voice over fixed pack text

Future-reference design note, not scheduled work. A companion to [TEXTMODE.md](TEXTMODE.md) (parked),
looked at from the other end. Text mode spends the LLM on *input*: it parses what the player typed
into a discrete command, and the golden rule there is **the model parses, it does not narrate**. This
note asks the mirror question on *output*: can the LLM take the **fixed, authored text a pack already
ships** and *vary* it, so the same room, keeper or question reads a little differently each time, or
even differently depending on what the player did earlier?

The answer turns almost entirely on one distinction the brief draws, and it is the spine of this
document:

> **A serious game** (instruction, compliance, the security-onboarding pilot Delve is today) and **an
> entertainment game** (a Monty Python romp, a Friends trivia night) can run on the *same engine*, but
> they have opposite tolerances for letting a model touch the words. The value of LLM text variation is
> roughly **inversely proportional to how accountable the content is.**

So the mirror rule to text mode's is:

> **The model re-voices; it does not author. It dresses the text; it never decides the facts or the
> grade.**

As with text mode, this is captured with its costs attached, not proposed for the roadmap. And as with
text mode, [multilingual quality](#6-the-multilingual-problem-the-sharp-edge) is where the idea is most
expensive, which the brief rightly flags.

---

## 0. The boundary that does not move

PLAN §13.5 and both display docs say the durable asset is the **pack format**, not the Python. This
note leans on that harder than any other, because letting a model rewrite pack text is the fastest way
to dissolve the pack as a reviewable, portable, correct source of truth. Two commitments hold
throughout, in *both* genres:

- **The pack is the source of truth.** Every fact a learner is graded on, every trivia answer, every
  correct/incorrect verdict, is authored and reviewed. The LLM may paraphrase around it; it may never
  originate it. A pack whose facts live in a prompt is not a Delve pack.
- **Load-bearing text is fixed; only flavour may vary.** This line (defined in §2) survives the genre
  split. What changes between serious and entertainment is *how much flavour there is* and *how freely
  the model may touch it*, never whether the load-bearing text is safe.

---

## 1. Why the genre changes everything

The same feature ("an LLM varies the flavour text") is reckless in one genre and delightful in the
other, for reasons that are worth naming precisely rather than hand-waving as "one is fun."

| | Serious game (today) | Entertainment game |
|---|---|---|
| **Cost of a model error** | A wrong fact is a *liability*. Compliance content must be right and consistent. | A flat riff is at worst *not funny*. Nobody's audit depends on the phrasing of a killer rabbit. |
| **Plays** | Once ("most run this once", CLAUDE.md). Fixed text is never worn out. | Many times (trivia night, again and again). Repetition is the enemy; freshness is the point. |
| **What the text is for** | To *teach* accurately. Voice is a nicety. | To *entertain*. Voice and timing are the whole product. |
| **Where variation helps** | Barely. A phishing lesson does not need to be surprising; it needs to be correct twice. | Enormously. Surprise, personality and replay value are exactly what an LLM can add. |
| **Acceptable infra** | Local model only; confidential context must not leave the device (Phase 2's whole premise). | A comedy quiz has no confidential data; a cloud model becomes thinkable (§6). |

Read down the columns and the asymmetry is stark: for serious content the risk of LLM variation is
high and the reward is near zero, so the answer is *don't*. For entertainment the risk is low and the
reward is high, so the answer is *maybe, carefully*. **The genre is not a flavour of the same decision;
it inverts the decision.** That is the single most important thing this note has to say, and everything
below is consequences of it.

There is a catch worth stating early, because it tempers the enthusiasm: **AI-funny is usually not
funny.** A small local model's humour is generic, over-explained, and off-rhythm; Monty Python lives on
timing and specificity that a 3B model flattens. So even in the genre where generation is *allowed*, the
best jokes are still the human ones. This pushes the design toward the model *recombining and reacting*
to authored humour rather than *inventing* it (the ladder, §3, and the further ideas, §7).

---

## 2. The one line that survives both genres: load-bearing vs flavour

Every string a pack ships falls into one of two classes, and the boundary between them is the safety
rail for the whole idea:

- **Load-bearing text** carries meaning the app is accountable for: the question, the options, the
  correct answer, the explanation that teaches *why*, a trivia fact. If the model changed it, a learner
  could be graded wrong or taught something false. **Never varied. Verbatim, always, in every language.**
- **Flavour text** is the dressing: the room description, the keeper's greeting, the transition between
  rooms, the ambient colour, the *tone* of a wrong-answer nudge. If the model varied it, the worst case
  is that it reads slightly differently. **This is the only text the LLM may touch.**

Crucially, **this line holds even in a trivia pack.** A Friends question still has a right answer, and
that fact is load-bearing and fixed. What an entertainment pack has *more* of is flavour around the
fact: how the question is introduced, how a wrong guess is teased, how the room is described. The model
dresses the fact; it never chooses it. Concretely:

```
  LOAD-BEARING (fixed, authored, both languages)
    Q: "What ... is the airspeed velocity of an unladen swallow?"
    correct answer:  asking "African or European?"

  FLAVOUR (the model may re-voice this, entertainment only)
    the Bridgekeeper's menace, the chasm's description, the taunt on a wrong answer:
      "The Bridgekeeper bars the way. Answer, or be cast into the Gorge of Eternal Peril."
```

The engine already has this split latent in its content model: the question/answer/explanation are the
graded core; the room prose is atmosphere. Making the split *explicit and author-declared* (§7.6) is
what lets the engine guarantee "a serious pack's lesson is never touched by a model" mechanically,
rather than by good intentions.

---

## 3. The ladder: how much the model changes the text

Variation is not one thing. It is a ladder, and each rung trades correctness and localisation quality
for freshness. The rung a pack may climb to is governed by its genre (§1) and by the load-bearing line
(§2, which caps every rung at flavour-only).

**Rung 0. Verbatim.** Today. Fixed authored text, shown as written. Deterministic, reviewed, correct in
both languages. The serious default, and never wrong.

**Rung 1. Selection from an authored pool.** The pack ships *several* authored variants of a flavour
line; something picks one. The picker can be plain seeded RNG, or an LLM *router* that chooses the
variant best fitting the player's recent actions (§5). **This is the sweet spot for keeping quality**:
every string is still human-written and human-reviewed in both languages, so there is *zero* hallucination
risk and *zero* localisation degradation. The cost is authoring (a pool is 3-5× the words) and it buys
real variation and even reactivity with none of the danger. If you take one idea from this note, it is
that **variation without generation is largely a solved, safe problem**, and much of the perceived value
of "an LLM varies the text" is actually deliverable at this rung.

**Rung 2. Paraphrase / re-voice.** The model rewrites one authored flavour line into a different
register (terser, more florid, in a named keeper's voice), preserving meaning. Now correctness depends
on the model faithfully *not* changing the meaning, and localisation quality depends on its fluency in
the target language. English: passable on a 3B model. Dutch: risky (§6). Entertainment-only, and even
then, English-first.

**Rung 3. Reactive elaboration.** The model generates *new* connective flavour conditioned on player
history ("you fell in the gorge last time; the Bridgekeeper remembers"). Highest freshness, highest
risk, and the rung the brief's "dependent on earlier actions" points at. Only ever over flavour, only
in entertainment, and it needs a notion of history to condition on (§5).

**Rung 4. Free generation.** The model authors whole encounters from a premise. This is "AI Dungeon",
and it is **off the ladder for Delve**: it discards the pack as the source of truth (§0). Named so no one
climbs to it by accident. A pure toy might want it; a Delve pack, by definition, does not.

The genre map onto the ladder is simple: **serious packs live at rung 0-1 (and only rung 1's flavour,
never the lesson). Entertainment packs may reach rung 2-3 for flavour, English-first. Nobody ships rung
4 and still calls it Delve.**

---

## 4. The second axis: when the model runs

Orthogonal to *how much* the model changes the text is *when* it runs, and this axis is the most
underrated lever for defusing the whole risk profile.

- **Runtime generation** (rungs 2-3, live): the model runs while the learner plays. Fresh, reactive,
  but unreviewed, non-deterministic, latency-bearing, and language-quality-variable. Everything the
  costs section of TEXTMODE.md warned about, now for output text.
- **Authoring-time generation** (the quiet winner): the model runs *for the author*, offline, proposing
  a pool of flavour variants; a human reviews, edits, and the approved variants **ship as fixed authored
  text** (rung 1). The LLM becomes an *authoring accelerator*, not a runtime component.

Authoring-time generation collapses almost every risk at once:

- **Correctness:** a human reviewed every shipped word, so no live hallucination reaches a player.
- **Localisation:** a human reviewed (or wrote) the Dutch, so Dutch quality equals English quality, and
  "both first-class" survives.
- **Determinism & latency:** runtime is plain rung-1 selection, so runs stay regenerable and instant,
  and there is **no runtime model dependency at all**.
- **What you keep:** the variation and replayability the model was wanted for.

The trade is that reactivity to *this run's* history (§5) is weaker, because the variants were frozen
before the run existed. But a surprising amount of "reactive" flavour is really *state-conditioned*
(first visit vs revisit, passed vs blocked, rich vs broke), and those states are enumerable at authoring
time, so their variants can be pre-written and selected live. Genuinely open-ended reactivity ("the
model weaves a callback to that specific thing you did") is the only part that truly needs runtime
generation, and it is the smallest, riskiest slice.

**Recommendation in one line:** treat the LLM first as an *authoring tool that fills a variant pool you
review and freeze*, and only reach for runtime generation for the narrow reactive slice a pool cannot
pre-express, in entertainment packs, in English.

---

## 5. Reactivity to earlier actions (and why it is separable from generation)

The brief's most interesting ask is variation "dependent on earlier actions". The key insight is that
**reactivity and generation are two different things**, and you can have the first without the second.

- **State-conditioned variation (cheap, safe, both languages).** The engine already tracks a lot of
  history: which rooms are passed, HP, gold, pet, items carried, first-visit vs revisit, the passing
  score, a failed sitting. Flavour keyed off *that* is reactive and needs no model and no new store; it
  is exactly TEXTMODE.md §3's "state overlays", and it localises cleanly because each variant is
  authored. "You are back where the rabbit nearly had you" is reactive and 100% safe if "nearly had
  you" was recorded as a flag and the line was authored.
- **Narrative-memory variation (rich, risky, snapshot cost).** True open-ended callbacks need a running
  memory of *notable events* ("you tipped the shopkeeper", "you fled twice"), which is a new narrative
  state the snapshot must carry (TEXTMODE.md §9.3 flags this exact hazard: descriptions stop being a
  pure function of the Frame). The model then conditions a rung-3 generation on a short summary of that
  memory. This is where the magic lives and also where correctness, determinism and Dutch quality all
  get harder at once.

An illustration of the payoff, and the cost, of the second kind:

```
  first encounter (authored, rung 0/1):
    The Bridgekeeper rises from behind a mossy stone. "Who would cross must answer me
    these questions three."

  after you got one wrong and were cast into the gorge (rung 3, reactive):
    "Ah. You again. Still dripping, I see. Three questions. Try to concentrate this time."
```

The second line is delightful and is *precisely* what the brief is reaching for. It also cannot be
pre-written for every path, is non-deterministic, and would need a careful Dutch twin. The honest
position: get 80% of the felt reactivity from state-conditioned authored variants (safe, both
languages), and reserve model-generated callbacks for entertainment packs where the 20% is worth the
risk.

---

## 6. The multilingual problem: the sharp edge

The brief names this, and it is the constraint that most limits the whole idea. Delve is en + nl, both
first-class, and "a locale is complete or absent" (CLAUDE.md): a half-Dutch experience is worse than an
English one. LLM variation collides with this head-on.

**Why it degrades Dutch more than English.** A small local model's target-language fluency falls off
faster than its comprehension. It can *understand* a Dutch line and still *produce* a flawed Dutch
paraphrase: the inversion bug that drops the verb's `-t`, `je`/`u` register slips, anglicisms, calqued
idiom. CLAUDE.md already documents that even a *scripted* transform of the Dutch packs produced comma
splices and broken inversions "because no practical verb-detector is good enough"; a 3B model is a
fancier version of the same unreliable transform. And humour is worse still: a joke rarely survives
paraphrase, and almost never survives it into another language. Monty Python's register is
English-specific; "answer me these questions three" is archaic English word-order that has no clean
Dutch paraphrase a small model will find.

So runtime LLM variation **disproportionately damages the non-English experience**, which is exactly
the failure the locale-complete rule exists to prevent. The mitigations, and their honest verdicts:

- **Vary English only; keep Dutch authored.** Keeps Dutch quality high, but creates an *asymmetry*:
  English players get fresh variation, Dutch players get fixed text. That breaks "both first-class" and
  is unacceptable for a serious pack. For an *opt-in entertainment* pack it may be a tolerable, declared
  compromise ("variation is an English-only feature of this toy"), but it should be a conscious label,
  not a silent gap.
- **Use a bigger (cloud) model for Dutch.** Frontier models do Dutch variation well. But that
  reintroduces the network, privacy and cost that Phase 2's local-only design deliberately avoided.
  Here the genre split pays off again: a **comedy quiz has no confidential data**, so a cloud call is
  defensible for an entertainment pack in a way it never is for compliance content. *Genre changes the
  acceptable infrastructure*, not just the acceptable risk.
- **Author-time generation with human review (the real answer).** Per §4: the model drafts Dutch
  variants offline, a Dutch-fluent human fixes the inversions and register, and the reviewed variants
  ship frozen. This is the *only* mitigation that keeps Dutch genuinely first-class while still gaining
  variation, because a human, not the model, is accountable for the shipped Dutch. It costs review time
  and buys back every quality guarantee.

The through-line: **the more the model touches the live Dutch text, the further Dutch drifts from the
reviewed quality bar English quietly keeps.** Push the model to authoring time, and the problem
dissolves; keep it at runtime, and Dutch is the language that pays.

---

## 7. Further ideas, building on "LLM + the fixed pack texts"

Each of these keeps the pack as source of truth and the load-bearing line intact; they differ in how
they spend the model.

1. **The LLM as authoring assistant (strongest).** Ship a tool that reads a pack's authored flavour and
   proposes a pool of variants (both languages), for the author to review, edit, and freeze into rung-1
   selection. Turns the risky runtime feature into a safe authoring accelerator, and makes *richer packs
   cheaper to write* without putting a model on the runtime critical path. This is probably the most
   valuable single idea here.
2. **The LLM as router, not writer.** Given several *authored* variants and a summary of player state,
   the model *chooses* which variant fits best (context-sensitive selection, §5). Variation and
   reactivity with zero generation risk and zero localisation loss, because it only ever picks
   human-written text. A weak model is fine at picking; it is the *writing* that a weak model does
   badly.
3. **Wrong-answer riffs.** The place humour and personality pay off most is the *reaction to a wrong
   guess*, which is low-stakes and benefits from character. In a serious pack the explanation is
   load-bearing teaching and stays fixed; in a trivia pack the wrong-answer line is a *punchline* and is
   pure flavour the model may dress. A natural, contained first target for entertainment variation.
4. **Sustained keeper voice.** Per-keeper voices already exist (M8, `Strings.teach(kind)`). A pack could
   define a keeper's voice as a short style card the model conditions on, so all of that keeper's flavour
   reads consistently in character. Reward: coherence and personality. Risk: voice drift and
   accidental tone (a comedy character generating something off-brand), which authoring-time review
   neutralises.
5. **Tone adaptation to the player.** The model (or plain state rules) tightens flavour for a player
   speeding through and elaborates for one who lingers. Mostly achievable at rung 1 from pacing state;
   the model only helps at the margins.
6. **A per-field variability budget in frontmatter.** Let a pack declare, as *metadata* (rule 5: this is
   policy, not content), how far up the ladder each text field may go: the lesson `fixed`, the room
   description `select`, the wrong-answer riff `revoice`. This makes the load-bearing/flavour line
   (§2) explicit and machine-enforced, lets `validate` guarantee a serious pack never varies its
   lesson, and lets a single pack be "serious with a smile" (§9) by budgeting only the narrator's asides.
7. **Seeded and cached variation.** Even runtime generation can respect Delve's regenerability: seed the
   prompt from `(run seed, room id, visit count)` at temperature 0 so a given moment yields the same
   text, and/or cache the chosen/generated variant into the snapshot so a resumed or replayed run reads
   identically. Recovers most of the reproducibility TEXTMODE.md §7 put an asterisk on.
8. **"Serious with a smile" mixed packs.** A dry compliance pack with a wry narrator whose *asides* the
   model varies, while the lesson, question and explanation stay fixed and reviewed. This lets serious
   training borrow entertainment's freshness *without* risking correctness, and is plausibly the most
   commercially interesting point on the whole spectrum: make mandatory training pleasant to sit through
   without making one graded word of it uncertain.

---

## 8. Risks, consolidated

- **Correctness / liability.** Any model reach into load-bearing text is a non-starter for serious
  content. The load-bearing line (§2) is the rail; do not file it down.
- **AI-funny is not funny.** Generated humour is often worse than the authored joke or than silence.
  Prefer recombination and reaction over invention (§1, §7.1-7.3).
- **Multilingual degradation.** Runtime variation damages Dutch more than English and threatens "both
  first-class" (§6). Authoring-time review is the only clean fix.
- **Source-of-truth erosion.** The pack is the durable, portable, reviewable asset (PLAN §13.5). Let the
  model author, and the pack dissolves into prompts. Rung 4 is off the ladder for this reason.
- **Determinism / reproducibility.** Runtime generation breaks tile-for-tile replay unless seeded and
  cached (§7.7).
- **Runtime dependency and latency.** A model on the play path adds the same dependency and lag TEXTMODE
  documented; authoring-time generation avoids it entirely.
- **Content safety and tone.** A generator can produce not just unfunny but *inappropriate* text in a
  shipped product; human review, or staying at rung 1, contains it.
- **Privacy/cost if cloud.** Acceptable for a data-free toy, never for confidential compliance context
  (§6). The genre decides.

---

## 9. Possibilities, consolidated

- **Replayability** for entertainment packs, the thing fixed flavour cannot give and repeat-play needs.
- **Personality, voice and mood** a fixed line or a colour grid cannot carry.
- **Reactivity** to what the player did, most of it deliverable safely from engine state (§5).
- **Delve as a platform, not one product.** The same engine (rooms, keepers, gated progress, a pet,
  scrolls) hosts a comedy trivia pack as readily as a compliance pack; the genre lives in the content
  and the variability budget, not the code. That is a real widening of what Delve *is*.
- **The LLM as a force multiplier for authors** (§7.1), making richer packs cheaper to write, which
  helps *every* genre, serious included, without touching the runtime.
- **"Serious with a smile"** (§7.8): the pragmatic middle where most real value probably sits.

---

## 10. Recommendation

1. **Never vary load-bearing text.** In any genre, the lesson, question, answer, explanation and trivia
   fact are authored, reviewed, fixed, and equal in both languages.
2. **Get variation from authored pools (rung 1), selected by engine state or an LLM router.** This is
   safe, localises cleanly, and delivers most of the felt benefit, including most reactivity.
3. **Use the LLM at authoring time to fill those pools, human-reviewed, then frozen.** Best profile for
   correctness, Dutch quality, latency and reproducibility all at once, and it keeps the runtime free of
   a model dependency.
4. **Reserve runtime generation (rungs 2-3) for pure flavour, in explicitly-entertainment, opt-in packs,
   English-first**, with Dutch either authored or accepting a clearly-labelled, genre-specific
   compromise (or a cloud model, which the data-free genre permits).
5. **Make genre and variability author-declared and engine-enforced** (§7.6), so "serious never varies
   its lesson" is a guarantee, not a hope, and one pack can be serious in its teaching and playful in its
   asides.

The unifying idea: the serious/entertainment axis is really an axis of **how much unreviewed text the
content can tolerate**, and that maps directly onto how far up the LLM ladder a pack may climb.
Everything else is bookkeeping around that one honest measurement.

---

## 11. Open questions

1. **Is the variability budget per-field, per-pack, or a genre preset?** Per-field is the most precise
   and the most authoring burden; a genre preset ("serious" locks everything but ambient asides) is the
   most usable. Probably a preset with per-field overrides.
2. **Does an entertainment pack accept an English-only or cloud-model compromise for Dutch, on the
   record?** This is the one place "both first-class" might bend, and only for a declared toy. Where
   exactly is the line, and who signs off on bending it?
3. **How much narrative memory is worth a snapshot field?** §5's rich reactivity needs stored events.
   Which events, and does their value beat the cost of a parallel narrative state the resume path must
   carry?
4. **Is authoring-time generation a Delve feature or an external tool?** It could ship as a `delve`
   subcommand (like `validate`/`doctor`) or stay a separate authoring script outside the runtime. The
   latter keeps the model entirely off the shipped product.
5. **Would an entertainment pack even reuse the dungeon, or want a different shape?** Trivia may not want
   sealed doors and HP; the genre split might eventually pull on the engine, not just the text. Worth
   watching before assuming one engine fits both.
