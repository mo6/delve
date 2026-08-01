---
id: DELVE-0018
title: Eliminate a wrong answer for gold, priced against the room reward
status: in-progress
area: [assess, session, ui]
type: story
epic: DELVE-0017
effort: high
milestone:
version:
version_span:
created: 2026-07-25
updated: 2026-08-01
accepted_by: George Moses
accepted_at: 2026-08-01
commits: []
related: [DELVE-0011, DELVE-0010]
supersedes: []
docs: [docs/OBJECTS.md, docs/PLAN.md]
changelog:
---

# Eliminate a wrong answer for gold, priced against the room reward

## Summary

During a multiple-choice question with three or more options still showing, let the learner spend gold to remove one wrong option, a paid lifeline. The price of each removal is the room's reward divided by one less than the number of options still standing (`round(R / (n - 1))`), so it climbs as the question narrows: for a four-option question in a room that rewards 100, the first removal costs `100 / 3 = 33`, the next `100 / 2 = 50`, after which only two options remain and no further removal is offered. Buying both costs `33 + 50 = 83`; the lifeline never collapses the menu to a single answer, and an assertion (exactly two options) never offers it. Unlike the pet consult, paying gold does **not** forfeit the question's score, the coin is the price, not the marks.

## Motivation / problem

Gold has no sink (DELVE-0017). This story is the first and primary one that gives it a use. It is modelled on the existing pet consult (DELVE-0011), which crosses out one wrong option but makes that question stop counting toward the score, help paid for in score. The paid removal is its economic twin: help paid for in coin, with the score kept. The rising price, pinned to the room's own reward, makes the decision interesting: cheap when you only need to shave the odds, dear if you keep narrowing toward a coin toss (and never offered once only two options remain). That asymmetry is the intended game dynamic, not a rough edge to file off.

## Stories

### As a learner, I want to spend gold to remove a wrong option, so that a hard question becomes easier when I can afford it.

- Given a multiple-choice question with `n` options still shown (`n ≥ 3`) and a room whose reward basis is `R`, when the learner buys a removal, then the price charged is `round(R / (n - 1))`, one wrong option is removed from the shown set, and the learner's gold falls by exactly that price.
- Given the learner has already removed one or more options from the current question, when they buy another removal, then the price uses the *current* remaining count (so the sequence for a four-option question is `round(R/3)`, then `round(R/2)`), and it is always a *wrong* option that is removed, never the correct one.
- Given a question narrowed until only two options remain (or an assertion that started with two), when the learner asks to buy a removal, then the action is refused and no gold is spent: a helpline is never offered at `n ≤ 2`.
- Given the learner's gold is less than the current removal price, when they try to buy, then the purchase is refused with a message, no option is removed, and no gold is spent (no debt, no partial buy).

### As a learner, I want a removed option to be plainly gone, so that I do not waste an answer on something I paid to rule out.

- Given the learner has paid to remove an option, when the question is shown, then that option is presented as eliminated (struck through or dropped from the list) and cannot be selected as an answer, distinct from the pet's advisory strike, which stays selectable.
- Given one or more removed options, when the learner answers, then only a still-standing option can be chosen, and grading maps the choice to the right option regardless of how many were removed.

### As a learner, I want paying gold to keep my marks, so that money is a real alternative to the pet's score cost.

- Given the learner pays to remove an option on a question, when the sitting is scored, then that question still counts toward the score exactly as if untouched (a paid removal never marks the question `assisted`), in contrast to the pet consult, which does forfeit the score.
- Given the learner both consults the pet and pays for a removal on the same question, when the sitting is scored, then the pet consult's score forfeit still applies (the pet was used); the paid removal adds no further score effect, it only removes an option and charges gold.

### As a learner on a floor that pays nothing, I want the lifeline simply absent, so that it never offers a free or nonsensical purchase.

- Given the unscored tutorial floor (no reward is ever paid there), when a question is posed, then the buy-a-removal action is unavailable.
- Given a free-text (Phase 2) question, which has no options, or an assertion (exactly two options), when the learner tries to buy a removal, then the action is unavailable, the same shrug the pet gives on free text.
- Given a room whose reward basis is `0`, when a question is posed, then the buy-a-removal action is unavailable (there is no price to charge and a free lifeline would break the dynamic).

### As a maintainer, I want the mechanic deterministic and rule-abiding, so that a run stays regenerable and the layers stay clean.

- Given the same run driven by the same command stream, when a removal is bought on a question, then the *same* wrong option is removed every time: the choice of which wrong option to drop is deterministic and never drawn from `self.rng` (which shuffles exam options).
- Given the mechanic is implemented, when the money is charged, then it is charged by the session from `self.player.gold` (session policy, like `_pay_reward`), while `gate.py` records only which options are eliminated; the exam format and the door mechanic are untouched, so the five rules hold (`ui` gains a view-model field, not an import).
- Given a sitting that fails and is re-sat, or a sitting abandoned with Esc, when the question is shown again, then removals do not carry over (a fresh sitting shows all options) and gold already spent is not refunded (abandoning must not be a way to dodge the cost).

## Non-goals

- The textual-hint variant (reveal an author-written hint for gold). That is a separate future story under DELVE-0017, needing a pack-authoring surface; not in scope here.
- Changing the pet consult, the reward amount, the score-scaling of the paid reward, or how gold is earned.
- Carrying a purchased removal across sittings, or refunding on abandon or failure.
- Any spend outside the examination.

## Design notes / links

The mechanic mirrors the pet consult almost exactly, and should reuse its shape. Today `_consult` (session) calls `gate.consult(...)`, which marks the question and returns the display index of one wrong option to cross out, and `_question_overlay(struck=...)` renders that single crossed-off item; the session decides free vs paid. For a paid removal:

- **Session** adds a command (a natural key is `$`, the spend key, during `EXAMINATION`), refuses when fewer than three options remain, otherwise checks the current price against `self.player.gold`, and on success debits gold and asks the gate to eliminate one option. The price basis `R` is `gate.content.reward`, or the pack default when the room's is None, the same value `_pay_reward` scales; `round(R / (remaining - 1))` mirrors that method's `round`.
- **Gate/exam** grows from a single `struck` index to a *set* of eliminated display indices (it can hold several), tracked per current question and cleared when the sitting re-shuffles (`_shuffle`) or the exam is discarded. It picks a wrong option to remove deterministically (reuse the pattern behind `pet.hint_for`, extended to skip already-eliminated ones), never from `self.rng`. Crucially it must **not** call `Examination.assist`, so the question keeps counting toward the score.
- **View model** (`ui`, rule 2): `MenuItem.struck` / `PromptView.struck` today mean "advisory strike, still selectable". A paid removal needs "eliminated, not selectable", so `MenuView`/`PromptView` need to distinguish the two (a second flag, or an `eliminated` set), and `_question_overlay` must render a set of eliminations rather than one `struck` int. Selection and the answer-key mapping must skip eliminated options. This is the main non-trivial code change; keep it on the `ui` side of the boundary (add a field, not an import).

Locale impact: new strings in `delve/strings/{en,nl}.toml`, both locales, for the buy prompt/label, the price surfaced before purchase (so the choice is informed, e.g. on the hint line or the question footer), the "you removed an option for $N" confirmation, and the "not enough gold" refusal. No `[format]` change beyond the existing money formatting. Screen impact: the examination mock-ups in `docs/SCREENS.md` gain an eliminated option and the new hint-line key and price; regenerate them with `tools/screens.py` (never hand-edit). Tutorial coupling: the tutorial floor is unscored so the lifeline is absent there, but if the exam hint line changes shape, grep `delve/tutorial/` in both locales per CLAUDE.md. Design essays: `docs/OBJECTS.md` (money, reward), `docs/PLAN.md` sections 5-6.

One decision is called out rather than guessed: whether buying is **immediate on the keypress** (price shown first on the hint line, like the pet consult is immediate) or gated behind a **confirm prompt** (safer against a mis-press that overspends). The acceptance criteria assume immediate with the price shown beforehand; a confirm step is a `ui` refinement that does not change the model.

## Addendum: helpline cost vs answering straight (2026-07-26)

**Invariant.** Using a helpline must be strictly more costly than answering correctly without one. The reward is unchanged by a paid removal (marks are kept; `_pay_reward` still scales only by sitting score), so every coin spent on a removal is a pure loss against the unaided baseline. A learner who would have got the question right unaided always ends the room with *less* net gold if they bought any helpline. That is the intended trade: narrower odds are paid for in the purse, never subsidised by the reward.

**Floor.** A helpline is only possible while **more than two** options remain (`n ≥ 3`). At `n = 2` the action is refused: the lifeline never buys a lone remaining answer, and an assertion (which starts at two) never offers it.

Price reminder: each removal costs `round(R / (n - 1))` with `n` = options still showing (`n ≥ 3`); `R` is the **room** reward basis (not a per-question share). Worked examples below use `R = 100` and a perfect sitting that pays the full 100.

### Yes / no (assertion, 2 options)

| Path | Spend | Earn | Player gain |
|---|---:|---:|---:|
| Answer right | 0 | 100 | 100 |

No helpline: `n = 2` from the start, so the buy action is unavailable.

### MCQ, 3 options

| Path | Spend sequence | Total spend | Earn | Player gain |
|---|---|---:|---:|---:|
| Answer right | - | 0 | 100 | 100 |
| One removal, then answer right | `round(100/2)=50` | 50 | 100 | 50 |

One removal leaves two options; a second buy is refused. The only helpline path costs half the room reward.

### MCQ, 4 options (summary's worked example)

| Path | Spend sequence | Total spend | Earn | Player gain |
|---|---|---:|---:|---:|
| Answer right | - | 0 | 100 | 100 |
| One removal, then answer right | `round(100/3)=33` | 33 | 100 | 67 |
| Two removals, then answer right | 33 + `round(100/2)=50` | 83 | 100 | 17 |

Two removals leave a 50/50; a third buy is refused. Narrowing a four-option question as far as the helpline allows costs 83.

### MCQ, 5 options

| Path | Spend sequence | Total spend | Earn | Player gain |
|---|---|---:|---:|---:|
| Answer right | - | 0 | 100 | 100 |
| One removal, then answer right | `round(100/4)=25` | 25 | 100 | 75 |
| Two removals, then answer right | 25 + `round(100/3)=33` | 58 | 100 | 42 |
| Three removals, then answer right | 25 + 33 + `round(100/2)=50` | 108 | 100 | −8 |

Three removals leave a 50/50 and cost **more than the room pays** (108 > 100): maxing the helpline on a five-option question leaves a negative player gain.

### Reading across the table

- **Any** available helpline path has a lower player gain than answering right unaided: spend is positive, earn is identical, so `earn − spend` falls.
- A single nudge is cheapest on wider menus (player gain 75 / 67 / 50 for 5 / 4 / 3) and impossible on yes/no.
- The lifeline never grants certainty: every paid path stops at two options. Max spend rises with the starting width: 50 (3) → 83 (4) → 108 (5). From five options up, emptying the menu down to two costs more than `R` itself.
- Because `R` is room-scoped, one helpline in a multi-question room still costs a share of the *whole room's* reward, not a fraction of one question. That keeps the "more costly than answering straight" invariant even when the helpline only touches one prompt.

Implementation must preserve this invariant under the `round(R / (n - 1))` formula (with the `n ≥ 3` floor): for every correct sitting, player gain (`earn − spend`) with one or more paid removals is strictly less than player gain with none. Do not offset helpline spend by shrinking or boosting the reward.

## Acceptance / verification

- A pricing test drives a four-option MCQ in a room with reward 100 and asserts the removal sequence charges 33, then 50, that gold falls by exactly those amounts, that a third removal is refused (two options left), and that the correct option is never the one removed. Covers the first learner story and the worked example.
- A cost-invariant check (see addendum) asserts that for `R = 100`, a perfect sitting that bought any removal sequence on a 3-, 4-, or 5-option question has a strictly lower player gain (`earn − spend`) than the same sitting with no removals; that two removals on four options cost 83 (player gain 17); that three removals on five options cost 108 (player gain −8); and that a buy is refused on a 2-option assertion and whenever only two options remain.
- An affordability test asserts a buy with insufficient gold is refused with the message and spends nothing. Covers the affordability criterion.
- A presentation test asserts an eliminated option is marked eliminated and cannot be selected, and that answering still maps to the correct option with several removed. Covers the second story.
- A scoring test asserts a paid removal leaves the question counting toward the score (score unchanged versus an untouched run), while a pet consult on the same question still forfeits it. Covers the third story.
- Availability tests assert the lifeline is absent on the unscored tutorial floor, on free-text questions, on assertion (2-option) questions, and when the reward basis is 0. Covers the fourth story.
- A determinism test drives the same command stream twice and asserts the identical option is removed and the same gold spent; a re-sit shows all options again and no refund is given on abandon. Covers the maintainer story.
- `./run-tests.sh` passes (pytest, ruff, `tools/screens.py --check`, `tools/issues.py --check`, `delve validate`), with the examination mock-ups regenerated and both locales carrying the new strings.
