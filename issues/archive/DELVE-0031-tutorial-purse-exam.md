---
id: DELVE-0031
title: Tutorial ends with a free-text exam room that pays 100 gold
status: implemented
area: [delve, session, docs]
type: story
epic:
milestone:
version: 1.11.0
version_span:
created: 2026-07-26
updated: 2026-07-26
commits: [pre-reset]
related: [DELVE-0008, DELVE-0017, DELVE-0018]
supersedes: []
docs: [docs/PLAN.md, docs/AUTHORING.md, docs/STYLE.md]
changelog:
---

# Tutorial ends with a free-text exam room that pays 100 gold

## Summary

Add a fourth room to the tutorial floor: a short lesson about gold and a paid helpline that
removes wrong answers downstairs, followed by three open (free-text) questions that check what
the Porter, the Peddler, and Alwin just taught. Earlier tutorial rooms stay multiple-choice;
only this last room asks free text. Passing drops an explicit `reward: 100` on the unscored
floor, so learners leave orientation with a purse they can spend later.

## Motivation / problem

The tutorial currently ends on Alwin's door-and-stakes lesson. Gold has no tutorial framing, and
the planned paid removal (DELVE-0018) is unexplained until a learner meets it cold on a scored
floor. A final exam room closes the orientation loop (screen, objects, keepers) and seeds the
purse with a concrete use.

## Stories

### As a learner, I want a last tutorial room that examines what I just learned in my own words, so that I leave orientation having practised free-text answers.

- Given the tutorial floor in either locale,
  when the learner reaches the fourth room,
  then that room asks three free-text questions whose keyword answers match the Porter's message
  line, the Peddler's pick-up / drop keys, and Alwin's "earned doors stay open" rule.
- Given the tutorial pack trees,
  when `delve validate` runs on the tutorial,
  then both `en/` and `nl/` carry matching `04-*.md` files and the room validates clean.

### As a learner, I want the last tutorial keeper to pay 100 gold and say what it is for, so that the purse has a purpose before I descend.

- Given the last tutorial room sets `reward: 100`,
  when the learner passes it,
  then 100 coins (scaled by the sitting score; a perfect pass yields 100) drop on a walkable
  interior tile of that room, even though the floor is unscored.
- Given other tutorial rooms leave `reward` unset,
  when those rooms are passed,
  then they still pay nothing (the main pack's default is never inherited on an unscored floor).
- Given the lesson prose in both locales,
  when the learner reads it,
  then it explains that gold can later buy a helpline that removes a wrong answer on an
  examination (the DELVE-0018 lifeline), without claiming the mechanic already works on Dlvl 0.

### As a maintainer, I want clearing the tutorial still leave the pack score at zero, so that orientation never contaminates the scroll.

- Given a fresh run with the tutorial prepended,
  when every tutorial gate is passed,
  then `pack_score()` remains `0.0`, no `room_results` are written for tutorial rooms, and only
  the last room's gate is `rewarded`.

## Non-goals

- Implementing the paid wrong-answer removal itself (DELVE-0018); this issue only teaches and
  funds it.
- Scoring the tutorial floor, writing `room_results`, or changing skip-tutorial behaviour.
- Changing the scattered tutorial coins seeded at floor generation.

## Design notes / links

`_pay_reward` today returns early on `not self.cur.scored`, which correctly blocks inheriting the
*main* pack's reward default onto Dlvl 0, but also blocks an explicit room `reward:`. Narrow that
guard so an unscored floor pays only when `gate.content.reward` is set. The last keeper still
seals nothing and stands beside already-open stairs (CLAUDE.md tutorial shape); Alwin moves to
room 3 of 4 and should no longer speak as if the stairs are next. Update the Porter's status-line
example (`Rooms:1/3` → `1/4`) and pack intro ("three people" → "four"). Voice and no-em-dash
rules: [docs/STYLE.md](../docs/STYLE.md). Free-text authoring: [docs/AUTHORING.md](../docs/AUTHORING.md).

## Acceptance / verification

- Tutorial validates in both locales; trees match.
- A headless pass of the fourth room with a perfect sitting asserts `gate.rewarded` and a MONEY
  pile of 100 on an interior tile; other tutorial gates remain unrewarded.
- `test_clearing_the_tutorial_adds_nothing_to_the_pack_score` still asserts `pack_score() == 0.0`,
  updated to allow the last room's reward.
- `./run-tests.sh` passes (or the focused tutorial / reward / languages subset during edit).
