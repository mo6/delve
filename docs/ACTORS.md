# Living actors: an LLM behind how NPCs and the pet move and speak

Future-reference design note, not scheduled work. The third companion to [TEXTMODE.md](TEXTMODE.md)
(parked) and [VARIATION.md](VARIATION.md), and it inherits from both. Text mode spent the LLM on
*input* ("the model parses, it does not narrate"). Variation spent it on *output text* ("the model
re-voices; it does not author"). This note spends it on a third thing: **behaviour**. Could the local
model drive how an actor in the dungeon *moves* and *talks* — a keeper who paces, a Monty Python
knight who wanders a floor and mutters at you, a pet that reacts to what you just did — rather than
the fixed, hand-tuned rules those actors follow today?

The dungeon already has autonomous actors. The pet moves for itself every turn (`engine/pet.py`: a
pure step over a species registry, drawing from a dedicated RNG). Keepers stand, teach, and block a
tile until passed. Both behave by fixed rules. The question is whether a model can make them feel
*alive* — purposeful in motion, characterful in speech, reactive to the player — and what that costs.

The answer, as in the two sibling notes, turns on one boundary, and the mirror rule to their rules
is:

> **The model animates; it does not adjudicate. It moves and mutters; it never gates, grades, or
> blocks the way.**

An actor's *mechanics* — who blocks a door, who steals a coin, who ends a chapter, when a lesson is
passed — stay deterministic, engine-owned, and untouched. Its *expression* — the flourish of a wander,
the timing and content of a remark — is the only thing a model may reach. As with both siblings, this
is captured with its costs attached, and as with both, [multilingual quality](#7-the-multilingual-and-tone-problem)
is where it is most expensive.

---

## 0. The boundaries that do not move

Three of the five rules bear directly on this idea, harder than on either sibling, because behaviour
lives *inside* the engine today and a model does not:

- **Rule 1: `engine` imports nothing above it.** `engine/pet.py` is pure — it reads the grid and the
  floor's `$` stacks, mutates the pet, and returns a `PetEvent` the session turns into words. It
  cannot call `assess.llm` (the socket seam) without breaking the layering the whole project is built
  on. **So an LLM-driven actor cannot live in `engine`.** Its *legal* moves are still computed there;
  the *choice* among them, if a model makes it, lives in `session`, exactly where grading and the
  proposed intent-parser runners live. This is not negotiable and it shapes everything below.
- **Rule 2: sealed doors are structural.** An actor never opens or seals a way; a door is stone until
  its exam is passed, and there is no path to validate. A wandering NPC that could *unblock* a route
  would reintroduce the problem the design deleted. Behaviour may decorate the dungeon; it may never
  change its topology.
- **Determinism (PLAN §7).** A run is regenerable tile-for-tile from `(seed, ...)`. The pet already
  respects this by drawing from a **dedicated `pet_rng`, never `self.rng`** (which shuffles exam
  options; PETS.md §8). A model choosing moves is non-deterministic by nature, so it collides with
  reproducibility the same way TEXTMODE.md §7 flagged for parsing. Any model-driven motion must be
  seeded-and-cached or logged, or replay breaks.

And the two commitments VARIATION.md leaned on hold verbatim: **the pack is the source of truth**, and
**load-bearing behaviour is fixed; only expressive behaviour may vary** (§1).

---

## 1. The one line: mechanical vs expressive behaviour

Every thing an actor does falls into one of two classes, and the boundary is the safety rail for the
whole idea — the behavioural twin of VARIATION.md's load-bearing/flavour line.

- **Mechanical behaviour** carries consequence the app is accountable for: a keeper blocks the tile in
  front of a sealed door; passing the exam opens it (rule 3, write-once); a cat that carries your coins
  flees and must be cornered; a dog delivers and banks gold; REPELLED pushes you back; HP:0 respawns
  you. If a model changed *these*, a learner could be blocked wrongly, paid wrongly, or let past a
  lesson. **Never model-driven. Deterministic, engine-owned, in every language.**
- **Expressive behaviour** is the dressing: *how* the pet mills when it has nothing to fetch, whether a
  keeper paces or stands, an idle NPC's path around a room, and above all the *ambient remarks* an
  actor makes. If a model varied these, the worst case is the dungeon reads a little differently. **This
  is the only behaviour the model may touch.**

The split maps cleanly onto today's code. In `engine/pet.py`, the fetch-and-flee logic (carrying → dog
heels, cat flees; empty → seek coins in `interest` range, heel past `leash`) is **mechanical** and must
stay pure and deterministic. Only the `p_wander` branch — "nothing better to do, mill to a random
adjacent tile" — is **expressive**, and it is exactly the one place a model could choose more
characterfully without touching a single consequence. That is not a coincidence; it is where to
experiment and nowhere else.

---

## 2. The two things a model could drive

"Behaviour" is really two separable channels, and they have very different risk profiles. Keeping them
apart is the single most useful move in this note.

### 2.1 Motion — the choreographer

The model chooses, among the moves the **engine has already declared legal**, which one an idle actor
makes, to make wandering feel purposeful or in-character rather than random. This is the direct analogue
of TEXTMODE.md's core trick: the engine computes the legal-action menu; the model only *picks from it*.
A Monty Python knight paces a patrol, drifts toward the player when close, retreats when you advance —
all from moves the engine vetted, so no phrasing or "personality" can produce an illegal step, walk
through a wall, or leave the tile it is meant to guard.

The honest verdict up front: **motion is the weaker case for a model.** The pet's fixed rules already
produce believable movement (seek, heel, flee, mill), and a 3B model choosing a wander direction buys
very little a weighted RNG does not, while costing a per-turn model call (§8) and non-determinism (§0).
Believable idle motion is a *solved cheap problem*; the model earns its keep in the other channel.

### 2.2 Speech — the voice

The model generates an actor's **ambient remarks**, reacting to the world and the player: the knight
two rooms over shouting "Ni!", the Bridgekeeper needling you about the gorge you fell in last time, the
shopkeeper commenting on your empty purse. This is VARIATION.md's ladder (rung 1 authored-pool selection
→ rung 2 paraphrase → rung 3 reactive elaboration) pointed at *who is speaking and when*, and it is where
personality and replay value actually live. It is also where every VARIATION.md risk returns: AI-funny
is rarely funny, Dutch degrades, and unreviewed shipped text erodes the pack.

**Recommendation, stated early:** keep motion deterministic and engine-owned; spend the LLM, if at all,
on *occasional* speech, drawn mostly from authored pools. The rest of the note is why.

---

## 3. Where a model-driven actor lives (the five rules still bind)

Because `engine` cannot import the socket seam (§0), a model-driven actor threads through `session`
exactly like grading and the proposed parser:

```
  ui ──▶ session ──▶ actor runner ──▶ assess.llm     [the socket seam, reused]
   │          │
   │          ├──▶ engine.pet.step / engine.layout    [legal moves, mechanics — unchanged, pure]
   │          └──▶ gate ──▶ assess / content / progress   [unchanged]
   └──▶ paints a Frame; a remark is a Frame message field   [rule 2]
```

- **The engine still owns motion mechanics.** `step()` stays pure: it computes what an actor *may* do
  and does the consequential parts (grab, flee, deliver). If a model influences the *idle* choice, the
  session hands `step` a chosen direction (or a pre-selected wander target), the way it already hands the
  pet its RNG; the engine never learns a model exists. Rule 1 holds untouched.
- **Speech is output text, and it rides the Frame.** A remark reaches `ui` as a message field, the same
  channel keeper voices and carry-flavour already use; `ui` imports no model and no strings (rule 2). The
  session composes the line — from an authored pool, or from a model runner shaped like `session/grading.py`
  (`InlineActor` picks from authored variants for the headless tests; a `ThreadedActor` runs the blocking
  model off-thread and folds a remark in on a poll, so the loop never blocks on an NPC).
- **The headless harness still runs model-free.** Tests drive actors as they drive everything: the
  deterministic floor (authored-pool selection, seeded) resolves inline, so a whole run stays a flat,
  model-free command list on the CI gate. The model is opt-in for humans, absent in tests — the grader
  pattern, again.
- **`gate.py` gains nothing.** It remains the one module touching both dungeon and training. An actor's
  banter is not a gate concern, and its mechanics are already the engine's.

Nothing here is a new *kind* of thing. It is the grader-runner shape a third time, pointed at behaviour.

---

## 4. Determinism, and the RNG discipline the pet already teaches

The pet is the worked example of getting this right, and it should be copied, not relaxed. It draws
motion from a **dedicated `pet_rng = Rng(seed*100+...)`**, never the exam-shuffle RNG, so movement is
reproducible *and* leaves examination order untouched (PETS.md §8). Two consequences for a model:

- **A model choice is not on a seedable stream.** Ollama at `temperature 0` is more stable than not, but
  not reproducible across model versions, so a model-chosen move breaks tile-for-tile replay the moment
  the model changes. The fix mirrors TEXTMODE.md §1.1: **the reproducible record becomes the resolved
  behaviour**, not the prompt. Log each chosen move/remark (or seed the prompt from `(run seed, actor
  id, turn)` and cache the result into the snapshot), and a resumed or replayed run reads identically.
  Without that, an actor is a fresh source of non-determinism on the hot path.
- **Never let an actor's model call perturb another stream.** The whole reason the pet has its own RNG
  is that borrowing `self.rng` would silently reshuffle a later exam. A model call has no RNG footprint,
  but a *cached* choice still must be stored per-actor and replayed in order, or a resumed run desyncs
  the same way. Treat behaviour state like the pet's carried purse: snapshot it, or it is not real.

The cleanest position: **movement stays on the seedable `pet_rng` (deterministic, free), and only
speech — which is cosmetic and already lowest-priority (the carry-flavour precedent, 1.3.2) — is allowed
to be model-sourced and is cached when it is.**

---

## 5. Reactivity to the player (the interesting part, and the separable part)

The brief's spark is an NPC that reacts "to the behaviour of the player" — the knight who mocks you for
fleeing, the keeper who remembers the gorge. As in VARIATION.md §5, the key insight is that **reactivity
and generation are different**, and most of the felt reactivity is the cheap, safe kind.

- **State-conditioned reaction (cheap, safe, both languages).** The engine already tracks a rich present:
  HP, gold, pet species and whether it is carrying *your* coins, items held, rooms passed, first-visit vs
  revisit, a failed sitting, the passing score, REPELLED. An actor keyed off *that* is reactive with no
  model and no new store: "the shopkeeper eyes your empty purse" fires off `gold == 0`; "the knight jeers
  as you back away" fires off a retreat the engine can see this turn. Every such line is authored, so it
  localises cleanly and can never be wrong. This is where most of the magic actually is.
- **Behavioural-memory reaction (rich, risky, snapshot cost).** True open-ended callbacks ("still
  dripping from the gorge, I see") need a running memory of *notable events* — the same parallel
  narrative state TEXTMODE.md §9.3 and VARIATION.md §5 both warned about. The model conditions a remark
  on a short summary of that memory. This is the delightful 20%, and it is where correctness,
  determinism, Dutch quality, and snapshot cost all get harder at once.

```
  the Bridgekeeper, first meeting (authored, state-conditioned):
    "Stop! Who would cross must answer me these questions three."

  the Bridgekeeper, after you were cast into the gorge and climbed back (behavioural memory):
    "Ah. You again. Still dripping. Concentrate this time."
```

The honest split is VARIATION.md's: get 80% of the felt life from state-conditioned authored lines
(safe, both languages, no snapshot growth), and reserve model-generated callbacks for entertainment
packs where the last 20% is worth the risk and the extra narrative state.

---

## 6. The keeper is not the pet: a load-bearing actor vs a flavour actor

Not all actors are equal, and this is the sharpest practical point in the note. Delve has two kinds of
autonomous actor, and they sit on opposite sides of the mechanical/expressive line:

- **The pet is almost pure flavour.** Its consequence is small and self-contained (it ferries coins;
  worst case you chase a cat). It already has an idle branch (`p_wander`), a dedicated RNG, and a
  cosmetic message channel. **It is the correct and only place to prototype model-driven behaviour**, in
  both channels, because a mistake there costs a weird wander or a flat joke, never a blocked lesson.
- **The keeper is load-bearing.** It teaches, it blocks the tile in front of a sealed door, and passing
  it is final and write-once (rule 3). Its *mechanics* must never be model-driven: a keeper that could
  wander off its tile could unblock a lesson (rule 2 violation), and a keeper whose behaviour decided
  passing would break rule 3 and rule 4 at once. What a keeper *may* borrow from a model is strictly its
  *voice* — banter while it teaches and re-instructs (re-instruction is free and unlimited, rule 3) — and
  that is VARIATION.md territory (rung 1-2 over the keeper's flavour lines, the M8 per-keeper voice made
  reactive), not a behaviour question at all.

So the map is: **prototype motion and reactive speech on the pet; give keepers at most a varied voice,
never varied mechanics; wandering ambient NPCs (below) are a new, deliberately-flavour-only actor class
so they can be lively without ever being load-bearing.**

A wandering NPC — the Ni-knight, a strolling minstrel, a killer rabbit that is all bark — would be a new
actor with **no gate, no exam, no blocking role**: pure atmosphere by construction, which is exactly what
makes it safe to animate. It moves on the `pet_rng`-style stream and speaks on the cosmetic channel, and
because it gates nothing, rules 2, 3 and 4 have nothing to catch. That is the actor type this idea most
wants, and it does not exist yet.

---

## 7. The multilingual and tone problem

VARIATION.md §6 applies unchanged and is the constraint that most limits the speech channel: runtime
model text damages Dutch more than English (the inversion `-t` bug, `je`/`u` register, calqued idiom
that "no practical verb-detector is good enough" to fix), and humour almost never survives paraphrase
into another language. An ambient remark is exactly the kind of short, idiomatic, tone-critical line a
small model does worst in Dutch, and Delve is en + nl, both first-class ("a locale is complete or
absent"). Runtime banter therefore threatens the locale-complete rule the same way, and the same three
mitigations apply with the same verdict: English-only banter breaks "both first-class" (tolerable only as
a labelled, opt-in entertainment compromise); a cloud model is defensible *only* for a data-free
entertainment pack (§ genre); and **authoring-time generation with human review is the clean fix** — the
model drafts a pool of remarks offline, a Dutch-fluent human fixes them, and the frozen pool is selected
live (rung 1).

Behaviour adds one tone hazard beyond text variation: an actor speaks *unprompted and repeatedly*, so a
bad line is not read once in a lesson but barks across the floor. This raises the bar on review and argues
even harder for authored pools over live generation. It also inherits the carry-flavour lesson (1.3.2):
ambient speech must be **low-priority and rare** — never override a keeper or an answer verdict, speak on
a coin-flip not every turn, and abbreviate after a few utterances — or a chatty NPC drowns the teaching
the app exists for.

---

## 8. Latency and the turn budget (the cost unique to behaviour)

This idea has a cost the two siblings do not, and it is decisive. Grading calls the model **once per
answer**; parsing would call it **once per instruction**. Behaviour is per **actor** per **turn**: every
keypress that advances time could, naively, wake every wandering actor for a model call. Two NPCs and a
pet on a floor is three model calls per step, at roughly half a second to two seconds each, turning a
game into a stutter. A grid dungeon cannot afford a model in its movement loop.

The mitigations are the design, not an afterthought:

- **Motion never calls the model** (§2.1, §4): idle movement stays on the deterministic `pet_rng` stream,
  instant and reproducible. This removes the per-turn-per-actor cost entirely from the common path.
- **Speech is occasional and gated cheaply.** A single cheap check ("should *anyone* speak this turn?",
  a coin-flip on a dedicated stream) decides whether to spend a call at all, so most turns cost nothing;
  the carry-flavour cadence (about half of steps, then abbreviate) is the proven shape.
- **Speech from authored pools costs no call at all** (VARIATION.md rung 1). A selected remark is instant
  and reproducible; only rung 2-3 live generation pays the latency, and only in entertainment packs.
- **Off-thread, non-blocking, like the grader** (§3): a `ThreadedActor` never freezes the turn on a
  remark; a slow line simply lands a turn or two later, or not at all.

Net: keep the model off the movement loop, and behaviour costs about what banter-on-a-coin-flip costs,
which the engine already tolerates.

---

## 9. The visible UI mockup

A grid session, English, a Monty Python entertainment pack, mid-floor. The dungeon looks exactly as it
does today (the map is ASCII, rule-of-the-repo); what is new is that `K` (a wandering knight) roams on
its own and the **message line carries its unprompted, player-reactive banter**. `@` is the player, `f`
the cat, `G` the Bridgekeeper who guards the sealed door `+`.

```
+------------------------------------------------------------------------------+
|  The knight two rooms north bellows: "Ni!  We are the Knights who say Ni!"   |
+------------------------------------------------------------------------------+
|                                                                              |
|    +----------+            +-------------+          +------------------+     |
|    | ........ |            | ..... K ... |          | ...........      |     |
|    | ...@..f. +############+ ........... +##########+ .... G + ....... |     |
|    | ........ |            | ........... |          | ...........      |     |
|    +----------+            +------+------+          +------------------+     |
|                                   #                                          |
|                            +------+------+                                   |
|                            | ........... |                                   |
|                            | ..... > ... |                                   |
|                            +-------------+                                   |
|                                                                              |
|                                                                              |
+------------------------------------------------------------------------------+
|  Sir Robin, Dlvl 2      HP 20/20   $15   T:63   .   your cat is here         |
|  move arrows . talk t . the knight is wandering the floor . descend >       |
+------------------------------------------------------------------------------+
```

**What the mockup is deliberately showing.**

*The remark is reactive, and reacts to state the engine already has.* The `K` moved toward the player's
room this turn (motion: deterministic, engine-chosen from legal tiles); the line fired because an NPC is
now within earshot (state-conditioned, §5) and was *selected from an authored pool* (rung 1) or, in an
entertainment pack that opted in, generated. Either way the knight gates nothing — `@` can ignore it and
walk to `G` and the sealed door as always.

*The load-bearing dungeon is untouched.* `G` still blocks `+` until its exam is passed (rule 2); `>`
still appears only when the floor is done. The banter is skin. Turn the model off and the knight still
wanders and still speaks — from the authored pool, in plainer, fixed lines:

```
  [ no model, or a serious pack ]
  |  The knight paces the northern room.                                         |
```

A serious pack would simply not ship a wandering jester, or would keep its one line fixed; the same
engine, a different content decision (VARIATION.md's genre axis, §ahead).

---

## 10. Genre decides this too

The serious/entertainment asymmetry from VARIATION.md §1 governs behaviour even more sharply than text,
because a moving, talking actor is *more* intrusive than a varied paragraph:

- **Serious pack (today).** A wandering NPC muttering during a phishing lesson is not atmosphere, it is
  **distraction** from the one thing the room exists to teach. The slide-deck risk PLAN names is *worse*,
  not better, if the screen is busy with banter. Here the answer is plainly: actors stay minimal and
  fixed — the keeper teaches, the pet fetches, nothing improvises. Behaviour variation earns nothing and
  costs focus.
- **Entertainment pack.** A Ni-knight who roams and heckles *is the product*. Movement and banter are the
  entertainment, replay wants them fresh, and there is no compliance liability if a joke lands flat. This
  is the genre where an animated actor is worth the latency, the snapshot cost, and the review burden —
  and, per §7, the only genre where a cloud model for Dutch banter is even discussable, because there is
  no confidential context to protect.

So behaviour, like text, is a **content and genre decision expressed through the pack**, not an engine
mode. The same engine hosts a silent, fixed-behaviour compliance floor and a rowdy, model-animated comedy
floor; the difference is the pack and a variability budget (VARIATION.md §7.6), extended to cover
behaviour: a pack declares, as metadata, whether an actor may be animated and how far up the ladder its
speech may climb.

---

## 11. Possibilities

- **Actors that feel alive**, the thing a fixed rule and a colour grid cannot give: purpose in motion,
  personality in speech, a floor that reacts to you instead of waiting on you.
- **Reactivity to the player**, most of it deliverable safely from engine state (§5) with no model on the
  hot path.
- **A new, safe-by-construction actor class** — the wandering, gate-less ambient NPC (§6) — that lets a
  pack be lively without ever touching a lesson.
- **Delve as a platform, widened again.** The pet already proved autonomous actors fit the engine; making
  their *expression* pack-driven lets one engine host a dead-serious floor and a Python-esque romp, the
  genre living in content, not code (VARIATION.md's platform point, now for behaviour).
- **The LLM as an authoring tool for behaviour**, drafting banter pools and patrol flavour a human freezes
  — the safe, runtime-free way to get most of the benefit (VARIATION.md §7.1, applied to actors).
- **Mood the grid can't hold**, carried by an actor's timing and voice rather than by tiles.

---

## 12. Risks

- **Rule 1 pressure.** The strongest temptation is to reach the model from inside `engine/pet.step`; that
  is the layering violation the whole architecture forbids. Behaviour choice belongs in `session`. If it
  feels like it must go in `engine`, the design is wrong — stop and say so (rule 1).
- **Determinism erosion.** A model on the movement loop breaks tile-for-tile replay unless motion stays
  on the seedable RNG and any model choice is cached/logged (§4). Easy to lose by accident.
- **Latency on the hot path.** Per-actor per-turn calls are untenable (§8); only a design that keeps the
  model off motion and gates speech cheaply is playable.
- **Distraction and the slide-deck risk.** A chatty floor can bury the lesson; ambient speech must be
  rare, low-priority, and abbreviating (the carry-flavour discipline), and absent entirely from serious
  packs (§10).
- **Multilingual and tone degradation.** Unprompted, repeated Dutch banter is a worse case than one-off
  text variation (§7); authoring-time review is the only clean fix, and "both first-class" bends only for
  a labelled entertainment toy.
- **Source-of-truth erosion and rule 2/3/4.** An actor that could open a way, block wrongly, or influence
  passing would break the structural guarantees the design is built on. Mechanics stay engine-owned and
  fixed; only expression varies (§1, §6).
- **AI-funny is not funny** (VARIATION.md §8). A wandering NPC's whole job is charm; a flat generated line
  is more exposed than a flat paragraph. Prefer authored pools and recombination over invention.
- **Snapshot growth.** Behavioural memory (§5) and cached remarks are new state the resume path must
  carry; weigh each field against the reactivity it buys.

---

## 13. Alternatives

Ordered from least to most divergent.

**A. State-conditioned authored actors, no model (smallest step).** Give NPCs and the pet richer *fixed*
behaviour and authored, state-keyed remarks (VARIATION.md rung 1 over behaviour). Livelier actors, zero
model, zero non-determinism, both languages clean. This captures most of the felt benefit and is the
honest first thing to build; the model only ever adds the last increment.

**B. Model-selected remarks over authored pools (the sweet spot).** The model is a *router* (VARIATION.md
§7.2): given several authored lines and a summary of player state, it picks the fitting one. Reactive and
characterful, but every shipped word is human-written and reviewed, so no hallucination and no Dutch
degradation. A weak local model is good at picking and bad at writing; this spends it on what it does
well. Probably the right ceiling for a shipped feature.

**C. Model-generated banter, entertainment-only, English-first (the real bet).** Live rung 2-3 generation
for a wandering NPC's speech, in an opt-in entertainment pack, with Dutch authored or cloud-assisted and
labelled. Highest charm, all the VARIATION.md/§7 costs, and only defensible where there is no confidential
context and replay wants freshness.

**D. Model-driven motion (least worth it).** Let the model choose idle moves from the legal set. Listed
to be **set aside on the record**: it costs a per-turn call and non-determinism to beat a weighted RNG at
a problem the RNG already solves well (§2.1). If motion ever wants more life, a better *heuristic* (patrol
routes, curiosity toward the player, authored behaviour trees) buys it without a model.

**E. Fully autonomous agent-NPCs (the far end).** Actors with goals and memory improvising freely, an "AI
Dungeon" cast. **Rejected on the record**, the behavioural twin of VARIATION.md's rung 4 and TEXTMODE.md's
alternative E: it dissolves the pack as the source of truth and the dungeon as a designed place. A pure
toy might want it; a Delve pack, by definition, does not.

---

## 14. Recommendation

1. **Never model-drive mechanics.** Blocking, gating, passing, stealing, delivering, respawn — all stay
   deterministic and engine-owned, in both languages (§1, §6). This is rules 1-4, not a preference.
2. **Keep motion off the model.** Idle movement stays on the seedable `pet_rng` stream; if it ever wants
   more life, use a better heuristic, not a model call on the hot path (§2.1, §8, alt D).
3. **Spend the LLM only on occasional speech, mostly by selection from authored pools** (alt A/B). This
   is reactive, characterful, safe, both-languages-clean, and free of runtime latency and hallucination.
4. **Prototype on the pet, add a gate-less wandering NPC, never animate a keeper's mechanics** (§6). The
   safe surfaces are the ones with no consequence to get wrong.
5. **Reserve live generation for explicitly-entertainment, opt-in packs, English-first** (§7, §10), with
   Dutch authored or a labelled cloud compromise, and behaviour declared in a per-pack variability budget.
6. **Make every model-sourced remark cached/logged** so runs stay replayable and resumes stay in sync
   (§4).

The unifying idea across all three sibling notes: the model is trusted with *surface* — input phrasing,
output wording, now the flourish and voice of an actor — and never with the *spine*: the facts, the grade,
the topology, the mechanics. Text mode kept the model off the world; variation kept it off the meaning;
behaviour keeps it off the consequence. Same discipline, third face.

---

## 15. Open questions

1. **Is a wandering NPC a new actor class or a re-tasked keeper?** A gate-less ambient NPC (§6) is the
   clean answer, but it is genuinely new engine state (another autonomous mover in `step`). Does its value
   clear that bar outside an entertainment pack?
2. **How much behavioural memory earns a snapshot field?** §5's rich reactivity needs stored events, the
   same hazard TEXTMODE.md and VARIATION.md both flag. Which events, and does the payoff beat the resume-
   path cost?
3. **Does behaviour want its own variability budget, or share text variation's?** An actor both moves and
   speaks; the budget (VARIATION.md §7.6) may need a behaviour axis distinct from the text axis.
4. **Where is the earshot/relevance line for a remark?** Too eager and NPCs chatter constantly (the
   distraction risk); too shy and they feel dead. This is the tuning that decides whether an animated floor
   feels alive or exhausting — the behavioural twin of TEXTMODE.md's confidence-floor question.
5. **Would an entertainment pack even keep the pet as-is?** A comedy floor might want its animals to be
   bits, not fetch-helpers; the genre split could eventually pull on `engine/pet.py`, not just the message
   channel. Worth watching before assuming one pet fits both genres.
