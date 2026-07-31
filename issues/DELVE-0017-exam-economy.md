---
id: DELVE-0017
title: An exam economy - spend gathered money for help in the examination
status: proposed
area: [assess, session, ui]
type: epic
effort: high
milestone:
version:
version_span:
created: 2026-07-25
updated: 2026-07-25
commits: []
related: [DELVE-0010, DELVE-0011]
supersedes: []
docs: [docs/OBJECTS.md, docs/PLAN.md]
changelog:
---

# An exam economy: spend gathered money for help in the examination

## Summary

Gold is currently a trophy: the pet fetches it, the reward drops it, the scroll totals it, but a
learner never spends it on anything. Give money a *use* by letting a learner spend it, during a
sitting, to make a hard question easier, at a price tied to that room's reward. The economy is
deliberately unprofitable to lean on: buying enough help to guarantee a room costs more than the
room pays, so it is a genuine choice under pressure, not a shortcut. This epic is the umbrella; its
child stories are the individual things money can buy in the exam.

## Motivation / problem

The objects-and-money epic (DELVE-0010) built the whole supply side of an economy (a reward on every
pass, scattered coins, the pet retrieving them, the scroll banking them) and the companion epic
(DELVE-0011) added a *free* form of exam help, the pet consult, which crosses out one wrong option but
forfeits that question's contribution to the score. What is missing is a **demand** side: a reason
to have saved money and a decision about when to spend it. Without one, the reward number on the
scroll is the only thing gold ever affects, and the pet consult (help paid for in score) has no paid
counterpart (help paid for in coin). An exam economy closes that loop: the coins the learner worked
to gather buy a measurable edge, and the price is set high enough that relying on it drains the
purse faster than the dungeon fills it.

## Child stories

An epic carries no code of its own; it is done when its children are (AGILE.md). The children:

- **[[DELVE-0018]]** - *Eliminate a wrong answer for gold, priced against the room reward.* The
  concrete, fully specified mechanic: pay to remove one wrong option from the current question, at a
  price of `room_reward / remaining_options`, rising as options are removed, keeping the question's
  score (unlike the pet consult). This is the first and primary child.
- *Buy a textual hint (future, no id yet).* The other framing the request named: spend gold to
  reveal an author-written hint toward the answer, rather than removing an option. It is deferred,
  not scheduled: it needs a pack-authoring surface (a hint per question, in both locales) and a
  price rule of its own, so it is a separate story to be written only if the elimination mechanic
  proves worth extending. Recorded here so the epic's shape is honest, not as committed work.

## Non-goals

- A shop, a merchant, or any spend outside the examination. This epic is only about spending gold
  *during a sitting*.
- Changing how gold is earned (reward amount, scatter, pet retrieval, banking) - all supply-side and
  owned by DELVE-0010/DELVE-0011.
- Changing the pet consult's score-forfeit rule. The paid mechanic sits *beside* it, it does not
  replace it (see DELVE-0018 for how the two interact).
- Any spend that could let a learner buy a *pass* profitably. The pricing rule exists specifically to
  keep full assistance more expensive than the reward.

## Design notes / links

Money is session policy, not a gate mechanic: gold lives on `self.player.gold` and the on-pass
reward is paid by `RunState._pay_reward`, while `gate.py` stays the pure training seam (CLAUDE.md,
the five rules). Every child of this epic must keep that split, the session owns the purse and
decides affordability, the gate owns the exam state and the strike bookkeeping, exactly as the pet
consult already does (`gate.consult` returns which option to cross out, the session decides free vs
paid). The pricing basis throughout is the room's *reward*, `gate.content.reward` or the pack
default, the same value `_pay_reward` scales by the passing score. Design essays: `docs/OBJECTS.md`
(the money economy and the on-pass reward), `docs/PLAN.md` sections 5-6 (examination lifecycle and
the pet's score-priced help).

## Acceptance / verification

This epic is done when every child story is implemented, archived with its own commits, and
`./run-tests.sh` is green. It ships no code of its own. Track completion by the child list above.
