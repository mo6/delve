# Authoring a Training Dungeon

You do not need to know Python, or NetHack, to write a training. You need Markdown.

A training is a folder of Markdown files. Each file is one **room**: a lesson, and the
questions a learner must pass to leave it. Write it top to bottom like a document, because
that's what it is.

---

## 1. The three tiers

```
  PACK        your training        →  a dungeon
   └── CHAPTER   a module          →  one dungeon floor
        └── ROOM    one lesson     →  one room, one keeper, one sealed door
```

A learner walks into a room, meets the keeper, reads the lesson, and is examined. Pass, and
**a door appears in the wall** — beyond it, a corridor to the next room. Pass every room in
a chapter and stairs appear down to the next chapter. The final chapter ends in a chamber
with the scroll on a pedestal.

**Doors move you within a chapter. Stairs move you between chapters.** A one-chapter
training has no stairs at all. Doors, once earned, stay open — learners can walk back and
re-read any lesson as often as they want.

You never place a door, a corridor, or a staircase. You never draw a map. You write lessons
and group them into chapters. That's the whole job.

---

## 2. A pack at a glance

```
packs/security-onboarding/
└── en/                          one subtree per language
    ├── pack.md                  what the dungeon is
    ├── 01-email-threats/        chapter = one dungeon floor
    │   ├── chapter.md             title, intro
    │   ├── 01-phishing.md         room = one lesson
    │   ├── 02-spear-phishing.md
    │   └── 03-attachments.md
    ├── 02-credentials/
    │   ├── chapter.md
    │   ├── 01-passwords.md
    │   └── 02-mfa.md
    └── scroll.md                the award text
```

**Order comes from filenames.** `01-`, `02-`, `03-` — that's it. To reorder a chapter, rename
its files. There is no manifest listing them and no `order:` field to keep in sync.

### More than one language

Add a sibling subtree with **exactly the same file names**:

```
packs/security-onboarding/
├── en/
│   ├── pack.md
│   └── 01-email-threats/
│       ├── chapter.md
│       └── 01-phishing.md
└── nl/                          ← same names, Dutch content
    ├── pack.md
    └── 01-email-threats/
        ├── chapter.md
        └── 01-phishing.md
```

Folder and file names are **slugs, not content** — they never translate. The translated title
goes in the frontmatter (`title: Het sorteerkantoor`), which is where a reader actually sees it.

This buys you three things. `diff <(ls -R en) <(ls -R nl)` tells you if a translation is
complete, and the validator does exactly that and errors on mismatch. Room `id`s stay shared, so
a learner who takes the Dutch dungeon lands in the same trophy case as everyone else. And a
language is complete or it's absent — there's no per-room fallback, because a half-Dutch dungeon
is worse than an English one.

**Language rules and voice live in [STYLE.md](STYLE.md).** Read it before writing Dutch; `u` is
wrong, and `u` → `je` is not a find-and-replace.

---

## 3. How big is a chapter?

**You never draw a map.** The engine generates every floor: it places a room per lesson in
file order, carves the corridors, puts each keeper beside their sealed door, and adapts the
whole thing to whatever terminal the learner has (minimum 100×30, bigger if they've got it).

So the only sizing question you face is: *how many lessons belong on one floor?*

| Rooms in a chapter | What happens |
|---|---|
| 1–6 | Comfortable. The target. |
| 7–8 | Validator **warns**. Probably two chapters. |
| 9+ | Validator **errors**. Definitely two chapters. |

These limits are **not technical**. The grid would hold about fifteen rooms at the 100×30 minimum. They're about the
learner: nine lessons without a break isn't a floor, it's a lecture. Descending a staircase
is the punctuation mark that tells someone they've finished a thought.

**The engine will never split a chapter for you.** It could — but it would put the break
wherever the packing ran out of grid, which means nothing to a human. A chapter break should
be a break in the *material*: "you've finished email, now we do credentials." That judgement
is yours, and it's the main design decision you actually make.

Aim for **3–4 rooms per chapter**. If you're at 9, you have two chapters and haven't noticed.

---

## 4. `pack.md`

````markdown
---
id: security-awareness
title: The Caverns of Compliance
difficulty: standard        # relaxed | standard | strict
scroll: The Scroll of Vigilance
reward: 20                  # optional: coins each passed room pays (a room may override); default 0
---

# The Caverns of Compliance

Deep beneath the office, the old policies stir. Two floors down, and a keeper
in every room. Answer them well and you will leave with the Scroll of Vigilance.
````

The body is the dungeon's intro screen — the first thing a learner reads, and your one
chance to signal this won't be the usual slide deck. Chapters are discovered from the
subfolders; you don't list them.

### `reward`

Optional, and 0 by default. When set, passing a room drops that many coins on the newly
opened way onward (the door, the stairs, or the final pedestal); the learner walks onto them
and they bank automatically, so the `$` in the status line finally moves. It is a pack-level
default that any room can override in its own frontmatter (§7); coins are collectible flavour,
they buy nothing and never gate progress. Whole numbers, zero or more.

### How an examination works

This is the loop a learner walks, and it's worth understanding before you set the knobs below.

A room's examination is **sat as a whole**. The keeper asks every question in the room, one after
another, and after each one the explanation appears whether the answer was right or wrong; that is
the teaching moment, and it's why a wrong answer is never wasted. When the questions run out, the
learner's **score is the fraction they got right**, and it's compared to the room's `pass`:

- **Score meets `pass`** → the door appears, and the score is written down **for good**. A passed
  room is never re-sat (see §8). This is the only branch that touches the trophy case.
- **Score falls short** → the **sitting failed**. The learner loses HP **once** (the difficulty's
  penalty, below), and one **attempt** is spent. They're returned to the keeper to re-read the
  lesson (free, as often as they like), ask the pet for a hint (costs score, not HP), and then
  **re-sit the whole room** from the top.

**A wrong answer on its own costs nothing.** HP is spent per *failed sitting*, not per wrong
answer, so the learner who misses one question and passes anyway pays nothing, and exploring a
tempting wrong option to read its explanation is free. The stakes attach to *failing the room*,
not to *being wrong once*.

When the attempts run out, the keeper **repels** the learner: pushed back out of the room, but
nothing earned is lost and every door already opened stays open. They can rest, re-read and try
again. If accumulated HP loss across the floor ever reaches zero, the learner respawns at the
chapter entrance with all their doors intact. **Neither of these is a punishment for learning
slowly** — that is the one thing the design will not do.

### `difficulty`

| Value | HP per **failed attempt** | Attempts before repelled |
|---|---|---|
| `relaxed` | 0 | unlimited |
| `standard` | 3 | 3 |
| `strict` | 5 | 2 |

An **attempt** is one full sitting of the room, and the HP cost is charged once per sitting that
misses `pass` — not once per wrong answer. So `standard` is: three sittings to get there, three HP
each time you don't, and repelled on the third miss (from a starting 12, that's HP 3, still on your
feet). `relaxed` can never repel and never costs HP; the learner simply re-sits until it clicks.

Use `relaxed` when the material is genuinely hard or the audience is nervous. Nothing about
the dungeon changes — only the stakes.

---

## 5. `chapter.md`

````markdown
---
id: email-threats
title: The Sorting Office
---

# The Sorting Office

Dust, and the smell of old paper. Somewhere below, a letter is waiting to lie to you.
````

The body is shown on arrival at the floor. Keep it to a few lines — it's a threshold, not a
lesson.

That's the entire file. There is nothing else to configure: the floor is generated from the
room files sitting next to it.

---

## 6. A room file

````markdown
---
id: phishing
keeper: wizard              # wizard | shopkeeper | gatekeeper
name: Ada the Suspicious
pass: 0.75                  # fraction of questions needed to pass
---

# Recognising a Phish

Ada looks up from a stack of intercepted letters.

A **phishing** message wants one of three things: your credentials, your money, or
your click. It gets them by manufacturing *urgency* — a deadline, a threat, an
authority you don't want to disappoint.

The tell is almost never the spelling. Modern phishing is well written. The tell is
the **mismatch**: a sender domain that isn't quite right, a link whose text and
destination disagree, a request that bypasses a process that exists precisely to
stop it.

> When a message makes you feel hurried, that feeling *is* the attack.

## Questions

### An email from your CEO asks you to buy gift cards, urgently, and to keep it quiet. What is the strongest signal that this is an attack?

- [ ] The request came by email rather than in person
- [x] It manufactures urgency and bypasses the normal purchasing process
- [ ] Gift cards are not a standard company expense
- [ ] The CEO would not normally email you directly

> Urgency plus process-bypass is the signature. The other answers are all *odd*,
> but oddness alone isn't evidence — the combination of pressure and "don't tell
> anyone" is what gives it away.

### Poor spelling and grammar are a reliable way to spot a phishing email.

- [ ] True
- [x] False

> This was true fifteen years ago and is now actively dangerous advice. Assume
> phishing is well written.
````

That's the whole format. Note there is **no map in a room file** — a room doesn't have a
map, it *is* a room on the chapter's floor.

---

## 7. Room frontmatter reference

| Key | Required | Default | Meaning |
|---|---|---|---|
| `id` | yes | — | Stable identifier. **Never change it** — progress records point at it. |
| `keeper` | no | `gatekeeper` | Who teaches this room. Affects voice, not mechanics. |
| `name` | no | auto | The keeper's name. Give them one; it costs nothing and helps a lot. |
| `pass` | no | `0.75` | Fraction of questions the learner must get right in one sitting for the door to appear. |
| `attempts` | no | from difficulty | Sittings allowed before the keeper repels the learner. Overrides the pack default for this room. |
| `penalty` | no | from difficulty | HP lost per **failed** sitting (not per wrong answer). Overrides the pack default for this room. |
| `reward` | no | from pack | Coins the keeper drops on a pass, collected on the way onward. Overrides the pack default for this room; whole numbers, zero or more. |
| `place` | no | — | Objects scattered on this room's floor, e.g. `place: coconut-half x2`. See section 14; the kinds are defined in `items/`. |

Metadata only. **Content never goes in frontmatter** — that's what the document is for.

### The three keepers

| Keeper | Voice | Use when |
|---|---|---|
| `wizard` | Scholarly, discursive, fond of a digression | The lesson has depth and you want room to explain |
| `shopkeeper` | Transactional — knowledge has a price | You want gold and hints to matter |
| `gatekeeper` | Terse. Asks. Judges. Moves on. | The material is procedural and you want pace |

---

## 8. What the engine does, so you don't

Everything spatial. You will not find a map syntax in this document because there isn't one.

| The engine handles | You never think about |
|---|---|
| Laying out the floor from your room files, in filename order | Room sizes, positions, corridors |
| Adapting to the learner's terminal (100×30 minimum, larger if available) | Screen dimensions |
| Placing each keeper beside their sealed door | Where anyone stands |
| Opening the door when the learner passes | Doors — see below |
| Stairs down when a chapter is complete; the scroll chamber at the very end | Stairs, the ending |

**You cannot place a door, and this is the point.** A door is something a learner *earns*.
Until they satisfy the keeper, the wall out of that room is solid stone — so there is no path
around your lesson, and no way for you to accidentally create one. The thing that would
otherwise be the whole design's weak spot simply isn't expressible.

### Learners can walk back, and you should write like they will

Every door stays open once earned. A learner can wander back to any room they've cleared and
ask that keeper to teach the lesson again, as often as they like, free. `<` takes them up to
earlier chapters. Re-reading is the behaviour this whole application exists to encourage, so
nothing about it costs anything.

Two things follow for you:

**You may build on earlier rooms.** "Remember what Ada told you about urgency" is a fair thing
to write, because the learner can go and ask her. Later chapters can lean on earlier ones
without re-explaining from scratch.

**But an examination is sat once.** The moment a learner passes, that room's score is final.
Keepers will re-instruct forever and re-examine never — otherwise anyone could grind a room to
100% and the trophy case would mean nothing. So write questions that are fair the *first*
time. A learner cannot come back to fix a lucky guess or an unlucky misread.

---

## 9. The lesson

Everything between the frontmatter and `## Questions` is the lesson. Standard Markdown:
headings, **bold**, *italic*, lists, `code`, blockquotes, fenced code blocks.

Three things that make lessons land in this format specifically:

**Write the keeper, not the slide.** `Ada looks up from a stack of intercepted letters.`
costs one line and turns a policy document into a person talking. The learner walked across
a dungeon to meet this character.

**Put the payload in a blockquote.** It renders highlighted, and it gives the learner one
sentence to carry into the examination.

**Keep it under roughly 60 lines.** Longer and the text window becomes a scrolling chore,
and you've reinvented the thing you're trying to escape. If a lesson won't fit, it's two
rooms — which is good, because two rooms means two examinations.

### Your paragraphs are the page breaks

A lesson opens in a panel beside the room, about 69 columns wide and around 20 lines tall, and
**pages break on paragraph boundaries**. A paragraph is never split across two pages; the engine
fills a page with whole paragraphs and breaks before one that doesn't fit.

That means a long lesson runs to several pages, and **that's fine** — it's the deliberate trade.
A page that ends mid-sentence makes the reader carry a clause across a keypress, and this whole
application exists to buy their attention, not spend it. More pages, always, over a broken
sentence.

Two things follow for you:

**Write ordinary paragraphs and the pagination takes care of itself.** Three to six lines each is
the sweet spot. The pilot's `01-phishing.md` is 3 pages and no page ends mid-thought.

**One enormous paragraph is the only way to break this.** A block bigger than a whole page has to
be split somewhere, and the engine will split it at a line, which is exactly the mid-sentence
break the rule exists to avoid. If a paragraph runs past ~15 lines, it's two paragraphs and you
already knew that.

URLs, domains and `code spans` are never broken across lines, so `yourcompany-hr.net` stays in one
piece — which matters, because in a lesson about domains the domain is the whole point.

---

## 10. Questions

Everything after `## Questions`. Each `###` heading is one question. The type is **inferred from
how many options you write** — you never declare it, and the engine has no opinion about what
language you're writing in.

| Options | Type |
|---|---|
| Exactly 2 | Assertion — a two-way prompt |
| 3 or more | Multiple choice — a lettered menu, **shuffled** |

### Multiple choice

Three or more options; mark exactly one `[x]`.

```markdown
### Which of these is the strongest password?

- [ ] P@ssw0rd!2024
- [x] correct horse battery staple
- [ ] Tr0ub4dor&3
- [ ] Your child's name plus a number

> Length beats complexity. A long passphrase has more entropy than a short
> string of tortured substitutions, and you can actually remember it.
```

Options are shuffled at runtime, so don't write "all of the above."

### Two-option assertion

**Exactly two options** — that's the whole rule. The labels are yours: `True`/`False`,
`Waar`/`Niet waar`, `Safe`/`Unsafe`, whatever the question needs. Renders as a two-way prompt
using your labels.

```markdown
### A password manager is riskier than reusing one strong password everywhere.

- [ ] True
- [x] False

> Reuse means one breach is every breach. A manager concentrates risk in one
> place that is actually designed to hold it.
```

```markdown
### Een wachtwoordmanager is riskanter dan één sterk wachtwoord overal hergebruiken.

- [ ] Waar
- [x] Niet waar

> Hergebruik betekent dat één lek elk lek is. Een manager concentreert het
> risico op één plek die daar daadwerkelijk voor ontworpen is.
```

Both are assertions, because both have two options. Nothing in the engine knows the word
"True" — an earlier version of this spec required it, and the Dutch pack broke on the first
question.

Assertions are the sharpest tool for compliance material: state the misconception as if it were
fact, and make the learner reject it.

### Explanations

The `>` blockquote after a question is shown **after answering, whether right or wrong**.

Always write one. It is the highest-value text in the pack — it lands at the exact moment
the learner is most receptive, having just committed to an answer. Explain why the wrong
answers were tempting, not just why the right one is right.

### Free text (Phase 2)

For a question the learner answers **in their own words**, write a `- ?answer:` line and **no
checkboxes**. The option-count rule that separates assertion from multiple choice does not apply;
the `?answer:` marker is what makes a question free text.

```markdown
### In one word, name the feeling a phishing email manufactures to stop you thinking.

- ?answer: urgency, time pressure, being rushed, panic
- ?reject: fear of the boss, curiosity

> Urgency is the lever. The message wants you moving before you think.
```

- **`- ?answer:`** is a comma-separated **accept set**: reference answers, any of which is fully
  correct. The first is the canonical one; the rest are accepted phrasings. Write several, because
  this set is also what the offline fallback matches against.
- **`- ?reject:`** (optional) lists common wrong answers to fail outright. Omit it when the accept
  set is enough.
- The `>` explanation is required and unchanged: shown after answering, right or wrong.

**Grading.** Run `delve setup` once to pull and warm up the local model (it needs Ollama installed;
`delve doctor` reports what is missing), then play with `delve play --grader-model qwen2.5:3b` and
answers are graded on **meaning**, so a paraphrase the accept set doesn't list is still accepted. **Without a model it still plays**: it falls back to deterministic keyword matching against
your accept/reject sets, which is stricter, so `validate` warns you a free-text pack wants the model
for full quality. Because that fallback is literal (especially in Dutch, where compounding defeats
substring matching), don't make free text the *only* gate on a room; mix it with a checkbox question
or two. The full architecture, the local model, and the one-step install are in
[PHASE2.md](PHASE2.md).

---

## 11. The scroll

`scroll.md` is the award, picked up from a pedestal in the final chamber. It supports
`{name}`, `{score}`, `{date}`, and `{pack}`.

**`{score}` and `{date}` render themselves in the reader's language, and you must not
second-guess them.** Write `{date}`, never `17 July 2026`; write `{score}`, never `91.7%`. The
engine formats both from the locale's `[format]` table, so the same scroll reads
`91.7%` / `17 July 2026` in English and `91,7%` / `17 juli 2026` in Dutch — comma for the decimal,
lower-case month. Getting that right is the engine's job; typing a literal takes it away.

```markdown
# The Scroll of Vigilance

Be it known that **{name}** descended the Caverns of Compliance,
faced every keeper, and answered with a score of **{score}**.

Sealed this {date}.
```

Write it as a reward, not a receipt. It's the thing that persists after the dungeon is gone,
and the thing that accumulates in the trophy case.

---

## 12. Validating your pack

```bash
python -m delve validate packs/security-awareness
```

Checks frontmatter, chapter capacity, question well-formedness, and that every question has an
explanation. Errors point at `file:line`.

```bash
python -m delve play packs/security-awareness --seed 42
```

`--seed` makes generated layouts reproducible, so a bug you hit is a bug you can show
someone.

---

## 13. A checklist before you ship

- [ ] Every chapter is a real break in the material, not a place you ran out of room.
- [ ] No chapter has more than 6 rooms; 3–4 is the target.
- [ ] Every keeper has a name.
- [ ] Every question has an explanation that teaches, not just confirms.
- [ ] Every question is fair on a *first* read — nobody gets to re-sit it.
- [ ] No lesson runs past ~60 lines.
- [ ] No "all of the above" (options shuffle).
- [ ] Assertions state misconceptions, not truisms.
- [ ] `pass` is set deliberately, not left at default by accident.
- [ ] Objects, if any, are seasoning: one or two, none needed to progress.
- [ ] You played it start to finish yourself, and it took the time you expected.

---

## 14. Objects on the floor (optional)

Objects are **seasoning**: a coconut half to bang together, a found USB stick that teaches you
not to pick it up, a warm coffee. They are never needed to progress; a keeper still holds the only
door. Use them for flavour, a teaching moment, or a small bonus, and use them sparingly.

An object is defined once, in an `items/` folder beside your chapters, and placed in a room's
frontmatter. Definitions live **per locale**, exactly like rooms, so a Dutch player reads Dutch:

```
packs/holy-grail/en/items/coconut-half.md
---
id: coconut-half
glyph: (
colour: yellow
name: coconut half
on_pickup: You pick up an empty half-coconut. Suspiciously horse-like.
on_move: You bang the coconuts together. Clip-clop, clip-clop.
---
Half of a tropical coconut, hollow and dry. One of a pair, by the look of it.
```

The body is the item's "look", shown when the learner opens their inventory (`i`).

| Key | Required | Meaning |
|---|---|---|
| `id` | yes | Stable identifier, shared across locales. `money` is reserved. |
| `glyph` | yes | One map character from the object classes: `$ ( % ! ? [ * ) = "`. ASCII only. |
| `colour` | yes | One of the sixteen, e.g. `yellow`, `bright_cyan`. |
| `name` | yes | Singular; a stack of several shows as `coconut half (2)`. |
| `on_pickup` | no | Printed **once**, the first time the kind enters the learner's hands. |
| `on_move` | no | Printed **each step** while the learner carries it (deduped, so a pair prints once). |
| `value` | no | Makes it a currency: it banks to gold when walked over, like coins, instead of being carried. |

**Placement** is a room's `place:` line. A count places a stack; several kinds are comma-separated:

```
place: coconut-half x2, usb-stick      # a stack of two coconut halves, and one USB stick
```

The engine scatters them on free floor tiles of that room, the same way for every learner on a
given dungeon, so a saved game restores exactly what you left. `validate` checks that every glyph
and colour is legal, every `place:` names a kind you actually defined, and that both locales carry
the same items. That is the whole vocabulary: effects are **data, not code**, so a pack is always
safe to download. If you want an effect that isn't here (a lantern, a key), it is a change to the
engine, not something a pack can smuggle in.
