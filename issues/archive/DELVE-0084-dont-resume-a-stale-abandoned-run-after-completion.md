---
id: DELVE-0084
title: Don't offer to resume a stale abandoned run once the pack has since been completed
status: implemented
area: [progress, session]
type: bug
epic:
effort: low
milestone:
version: 1.36.1
version_span:
created: 2026-07-31
updated: 2026-08-03
accepted_by: George Moses
accepted_at: 2026-08-03T18:14:56Z
commits: [515004c, 7da6364]
related: []
supersedes: []
docs: []
changelog: "1.36.1"
reason:
---

# Don't offer to resume a stale abandoned run once the pack has since been completed

## Summary

A learner who finished The Caverns of Compliance, claimed the scroll, and quit still gets asked
"…left it unfinished. Descend again where you stood?" the next time they launch the same pack,
and answering yes drops them back on some earlier floor instead of the trophy case they just
earned. The prompt should not appear once the learner has a completed run of this pack more
recent than any abandoned one.

## Motivation / problem

`SQLiteStore.unfinished_run` picks the most recent run row with `finished_at IS NULL` for a given
`(user_id, pack_id)`. A learner who starts a run, quits before finishing (declining a later resume
offer, or simply walking away), and then starts a *fresh* run that they do carry through to
completion, ends up with two rows: the old abandoned one (`finished_at` still `NULL`, never
touched again) and the new completed one. `unfinished_run`'s `WHERE finished_at IS NULL` excludes
the completed row entirely, so it keeps surfacing the old abandoned run indefinitely, on every
future launch, even though the learner has since completed the pack. The resume prompt is meant
to offer picking up where you stood (PLAN.md section 10), not to resurface a run the learner
already walked away from and superseded.

## Stories

### As a learner, I want the resume prompt to reflect my most recent outcome for a pack, so that finishing a pack stops old, abandoned attempts from being offered back to me.

- Given a learner started a run of a pack and quit without finishing it,
  when they later start a fresh run of the same pack and complete it (claim the scroll),
  then the next launch of that pack does not offer to resume anything, and starts a fresh run
  flow as if no unfinished run existed.
- Given a learner has one abandoned run and one completed run of the same pack, in that order,
  when `unfinished_run` (or whatever replaces its query) is asked for a resume candidate,
  then it must not return the abandoned run, because a later completion supersedes it.
- Given a learner has an abandoned run of a pack and has never completed that pack,
  when they launch it again,
  then the resume prompt still offers that abandoned run as before (unchanged, existing
  behaviour).

## Non-goals

- Not changing what happens for a learner who has never completed the pack; the resume prompt for
  a genuinely unfinished, never-superseded run is correct today and stays as is.
- Not deciding whether an old abandoned run should be deleted, marked with some new `outcome`, or
  simply excluded from the resume query; that's an implementation choice, not a behaviour change
  visible to the learner (see Design notes).
- Not changing "keep both" for completed scrolls (a fresh, later completion of the same pack still
  gets its own trophy-case row, CLAUDE.md's "Re-taking a pack" section); this issue is only about
  which row (if any) the resume prompt offers.

## Design notes / links

- `delve/progress/store.py:118` `SQLiteStore.unfinished_run` is the query in question:
  `SELECT * FROM runs WHERE user_id = ? AND pack_id = ? AND finished_at IS NULL ORDER BY id DESC
  LIMIT 1`. It needs to stop returning a run older than the learner's most recent finished run of
  the same pack (or otherwise recognise that run as superseded).
- `delve/session/launch.py:111` `pending_run` and `delve/ui/app.py:253` `_begin` are the only
  callers; neither needs to change if the store-level query is fixed to exclude superseded runs.
- CLAUDE.md's "Resume (M5)" section describes the intended `[yn]` prompt; this issue narrows it
  ("an unfinished run of the same pack" implicitly assumed there was no later completed one).

## Acceptance / verification

- A new store-level test alongside `tests/test_progress.py::test_unfinished_run_is_the_resume_candidate`:
  create an abandoned run, then a second run for the same user/pack that is finished, and assert
  `unfinished_run` returns `None`.
- A launch-level test alongside `test_completing_a_run_writes_results_and_a_scroll`: start a run,
  quit without finishing (no `finish_run`), start and complete a second run of the same pack, then
  assert `launch.pending_run` returns `None`.
- `./run-tests.sh` green.

## Peer review

- Auto (implementing agent), 2026-08-03: store-only query change as the design notes preferred (`id` greater than the latest finished run of the same pack); `pending_run` / `_begin` untouched; abandoned-only path still returns the unfinished row; abandoned row is left in the table (not deleted). New store and launch tests match the acceptance criteria. `./run-tests.sh` green (688). Ready to land once you say so.
- Claude (peer review), 2026-08-03: confirmed the `COALESCE(..., 0)` fallback keeps the no-completed-run case identical to the old query (any `id > 0` passes), so the "never completed" non-goal holds; the id-ordering assumption is the same one `ORDER BY id DESC` already relied on, not a new one. Verified all three acceptance-criteria scenarios (superseded-abandoned, still-resumable-abandoned, never-completed) are covered by name in `tests/test_progress.py`, and that the abandoned row is left in place (`store._run(abandoned.id).finished_at is None`), matching the issue's non-goal against deleting/marking it. `./run-tests.sh` green locally. No changes requested.
- George Moses (maintainer), 2026-08-03: peer-reviewed; implementation accepted.
