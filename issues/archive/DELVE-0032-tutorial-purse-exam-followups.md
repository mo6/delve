---
id: DELVE-0032
title: Backfill process and content gaps left by the tutorial purse exam
status: implemented
area: [delve, session, docs]
type: bug
epic:
milestone:
version: 1.11.0
version_span:
created: 2026-07-26
updated: 2026-07-26
commits: [pre-reset]
related: [DELVE-0031]
supersedes: []
docs: [docs/PLAN.md]
changelog:
---

# Backfill process and content gaps left by the tutorial purse exam

## Summary

A code review of DELVE-0031 (the tutorial's fourth room, Merryn's free-text purse exam that pays
100 gold) found the feature itself sound but five things the shipping commits left behind: no
version bump or CHANGELOG entry, a design doc that still describes the old two-room tutorial, a
free-text accept list with a false-positive-prone keyword, an exam that requires a perfect score
under keyword-only grading, and a reward-guard/test shape that is more nested than it needs to be.
None of these block play; all of them are worth cleaning up before the next tutorial change trips
over them.

## Motivation / problem

- **No release bookkeeping.** Every prior archived story or bug (DELVE-0016 to 1.10.0, DELVE-0029
  to 1.10.1, DELVE-0030 to 1.10.2) bumped `delve/__init__.py`, `pyproject.toml`, and
  `CHANGELOG.md` as part of shipping, and filled the issue's own `version:` field. Neither
  DELVE-0031's feature commit (`5d99271`) nor its archive commit (`3f4ead7`) does any of this, so
  `delve --version` and CHANGELOG.md do not reflect that the tutorial purse room shipped.
- **`docs/PLAN.md` section 9 "Shape" is stale.** It still reads "Two rooms... 2. Alwin the
  Patient... His question is trivial and unscored," but CLAUDE.md's parallel passage (updated by
  DELVE-0031) now correctly describes four rooms ending with Merryn's paid, perfect-score,
  free-text exam. DELVE-0031's own front matter listed `docs/PLAN.md` as a doc needing alignment;
  the implementation commit only touched CLAUDE.md.
- **A generic keyword risks a false accept.** `delve/tutorial/{en,nl}/00-the-threshold/
  04-the-purse.md`'s accept list for "how do you pick up something that is not a coin" includes
  the bare word "drop" (English) / a similarly short token (Dutch). `KeywordGrader.grade_text`
  (`delve/assess/grader.py`) accepts whenever an accept phrase is a substring of the answer, so an
  unrelated sentence that happens to contain "drop" (e.g. "not sure, let's just drop this one")
  reads as a correct answer. The same short-keyword pattern existed in the old (pre-DELVE-0031)
  free-text version of room 02, where a false positive only nudged a partial score; in the new
  room it can tip a `pass: 1.0` sitting from fail to pass on a lucky word.
- **`pass: 1.0` plus keyword-only grading is a tight combination.** Every other tutorial room
  passes at `0.5`; Merryn's room requires all three free-text answers to hit the fixed accept
  lists, with no LLM grader unless a learner is running `--grader-model`. Retries are free
  (the tutorial pack is `difficulty: relaxed`, so a missed sitting costs no HP), so this is not a
  hard block, but a learner who answers correctly in their own words can still be told they failed
  because their phrasing was not anticipated.
- **The reward guard and its test are more nested than they need to be.** `_pay_reward`
  (`delve/session/run.py`) now nests `if not self.cur.scored: return` inside the `reward is None`
  branch; folding the unscored case into the `reward` value itself would let the existing
  `if coins <= 0: return` guard absorb it. `test_tutorial_purse_pays_one_hundred_on_a_perfect_pass`
  (`tests/test_languages.py`) separately hand-loops over `run.gates.values()` to reproduce
  `_clear_chapter`'s existing room-order guarantee instead of just calling it.

## Stories

### As a maintainer, I want DELVE-0031's release bookkeeping backfilled and PLAN.md brought back in sync, so that the version, changelog, and design docs agree with what shipped.

- Given the tutorial-purse-exam feature (DELVE-0031, commit `5d99271`) is already on `main`,
  when this issue is implemented,
  then `delve/__init__.py`'s `__version__` and `pyproject.toml`'s `version` are bumped past
  `1.10.2`, `issues/archive/DELVE-0031-tutorial-purse-exam.md`'s `version:` field is filled with
  the same number, and `CHANGELOG.md` gains an entry describing the tutorial purse room and its
  100-coin reward.
- Given `docs/PLAN.md` section 9 "Shape" still describes a two-room tutorial ending with Alwin,
  when this issue is implemented,
  then that section is rewritten to describe the four rooms ending with Merryn's exam, matching
  CLAUDE.md's already-updated passage (room count, ending keeper, and that the last room is a
  paid, perfect-score, free-text sitting rather than a trivial unscored one).

### As a learner, I want the purse exam's free-text grading to only accept meaningful answers, so that a lucky keyword match doesn't substitute for actually knowing the mechanic, and a correct answer in my own words isn't routinely rejected.

- Given the purse room's accept list for "how do you pick up something that is not a coin, and how
  do you put it down again?" includes the standalone word "drop" (`en/`) and its Dutch equivalent,
  when the accept list is revised,
  then it requires a more specific phrase (e.g. "drop it", "press d") rather than a bare common
  word that can appear in an unrelated sentence, in both locales.
- Given `pass: 1.0` on a free-text-only room graded by the default (non-LLM) `KeywordGrader`,
  when this issue is resolved,
  then the three questions' accept lists are broadened to cover reasonable equivalent phrasings a
  learner might use for each answer, so a correctly-worded-but-unanticipated answer is not the
  common case for failing the room. (If the pass mark is lowered instead of broadening the lists,
  record that choice and the reasoning here.)

### As a maintainer, I want `_pay_reward` and its new test to read as simply as the rest of the reward path, so that the next person extending the unscored-floor reward rule isn't tripped by nested special cases.

- Given `_pay_reward`'s current shape (`delve/session/run.py`, the `reward is None` branch nesting
  a second `if not self.cur.scored: return`),
  when this issue is implemented,
  then the unscored-floor case is folded into the `reward` value itself (e.g.
  `reward = self.pack.reward if (self.cur.scored and self.pack is not None) else 0`) so the
  existing `if coins <= 0: return` guard absorbs it, with no behaviour change verified by the
  existing reward tests (`tests/test_languages.py`, `tests/test_dungeon.py`).
- Given `test_tutorial_purse_pays_one_hundred_on_a_perfect_pass` hand-loops over
  `run.gates.values()` to reproduce `_clear_chapter`'s room-order guarantee,
  when this issue is implemented,
  then the test calls `_clear_chapter(run)` directly instead, and the duplicated loop is removed.

## Non-goals

- Rewording DELVE-0031's own archived Summary text (it inaccurately implies rooms 01-03 were
  already multiple-choice before that change, when room 02 was converted from free-text to MCQ in
  the same commit); the archived issue is a historical record and is left as-is.
- Implementing the paid wrong-answer helpline itself (DELVE-0018); this issue only touches the
  purse room that teaches and funds it.
- Adding an LLM grader fallback specifically for the tutorial; the two-grader stack's existing
  `--grader-model` opt-in is unchanged.

## Design notes / links

Versioning: CLAUDE.md's "Versioning" section (two hand-synced files, `CHANGELOG.md` kept
out of `CLAUDE.md` on purpose). Tutorial shape: `docs/PLAN.md` section 9, and CLAUDE.md's "The
tutorial floor" section (already correct, the source to copy from). Grading: `delve/assess/
grader.py`'s `KeywordGrader` (substring match both ways, reject checked before accept) and
CLAUDE.md's "two-grader stack" note. Free-text authoring: `docs/AUTHORING.md`.

## Acceptance / verification

- `delve --version` and `CHANGELOG.md` reflect the tutorial purse room; `issues/archive/
  DELVE-0031-tutorial-purse-exam.md`'s `version:` is filled.
- `docs/PLAN.md` section 9 matches CLAUDE.md's tutorial-shape description (four rooms, Merryn
  last).
- A headless test asserts an unrelated free-text answer containing "drop" (or its Dutch
  equivalent) is graded incorrect for the purse room's second question.
- `test_clearing_the_tutorial_adds_nothing_to_the_pack_score` and
  `test_tutorial_purse_pays_one_hundred_on_a_perfect_pass` still pass after the `_pay_reward` and
  test simplifications, with no `_pass_room`/`run.gates` hand-loop left in the latter.
- `./run-tests.sh` passes; `python tools/issues.py --check` passes for this issue's own file.
