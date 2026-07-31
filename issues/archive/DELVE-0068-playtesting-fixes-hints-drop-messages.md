---
id: DELVE-0068
title: Three playtesting fixes: stale hint-line key, torch drop label, and a longer Messages tab
status: implemented
area: [session, delve]
type: bug
epic:
effort: low
milestone:
version: 1.26.1
version_span:
created: 2026-07-31
updated: 2026-07-31
accepted_by: George Moses
accepted_at: 2026-07-31
commits: [fbde393]
related: [DELVE-0063]
supersedes: []
docs: []
changelog: "1.26.1"
reason:
---

# Three playtesting fixes: stale hint-line key, torch drop label, and a longer Messages tab

## Summary

Three small, unrelated rough edges found while playing the Sorting Office, bundled together since
each is a small, self-contained fix: the walking hint line still advertises a retired `p` key and
never mentions `i` (Info); the drop menu's lit-torch entry shows a bare "a torch" instead of its
remaining steps, unlike Info/Pack's own torch row; and the Messages tab caps history at 5 lines,
tighter than is useful during a session with much back-and-forth.

## Motivation / problem

- **Stale hint line.** DELVE-0063 folded the standalone message log (`p`) into the Info panel and
  gave Info its own key (`i`), but `hint.walk` in both locale files was never updated: it still
  reads `"Move: arrows    Wait: space    Talk: t    Messages: p    Help: ?    Quit: q"`, naming a
  key that no longer does anything and omitting the one that now matters.
- **Uninformative drop label.** `RunState._droppable_list` appends the currently-lit torch as
  `(_LIT_TORCH_ID, self._torch_noun(1), 1)`, i.e. just "a torch"/"1 fakkel", while Info/Pack shows
  the same torch as `item.torch_lit` ("A torch, lit (133 steps left)."). The drop menu is the one
  place a learner is actively choosing what to drop and has the least information to go on.
- **Short Messages tab.** `_HISTORY_MAX = 5` (`session/run.py`) was fine for the standalone log's
  original size but reads as cramped now that Messages is a full Info tab of its own.

## Stories

### As a learner, I want the walking hint line to name the keys that actually work, so that it never points me at a dead key or leaves out a live one.

- Given the learner is walking (no overlay open),
  when the hint line renders,
  then it reads `Info: i` in place of `Messages: p` (both `en.toml` and `nl.toml`).

### As a learner, I want the drop menu's lit-torch entry to show its remaining steps, so that I can tell it apart from a fresh spare before I drop it.

- Given the learner has a working torch lit with `N` steps remaining and opens the drop menu,
  when the lit-torch entry is built,
  then its label includes the same remaining-steps figure Info/Pack already shows for it
  (reusing `item.torch_lit`'s wording, or an equivalent), instead of the bare torch noun.

### As a learner, I want the Messages tab to hold more history, so that I don't lose track of what just happened after a couple of turns.

- Given at least 10 distinct non-blank messages have accumulated this run,
  when the Messages tab renders,
  then it shows the 10 most recent distinct lines, newest first (raising `_HISTORY_MAX` from 5
  to 10); deduplication-by-line behaviour is unchanged.

## Non-goals

- No other hint-line wording changes beyond the one stale `Messages: p` reference.
- No change to the drop menu's *ordering* (the lit torch still appends last, per DELVE-0063).
- No change to how spare (unlit) torches are labelled in the drop menu; this is scoped to the
  single lit-torch entry.

## Design notes / links

- `session/run.py:_droppable_list`, `_hint`, `_messages_body`, `_HISTORY_MAX`.
- `delve/strings/{en,nl}.toml`: `hint.walk`.
- Related to, but independent of, DELVE-0067 (torch charge across drop/pickup): this issue only
  changes the *label* shown for the torch that is already tracked as `player.torch_charge`; it
  does not touch how charge is stored or preserved.

## Acceptance / verification

- A test asserting `hint.walk` (both locales) no longer contains `Messages: p` and does contain
  an `Info: i` reference.
- A test asserting the drop menu's lit-torch label includes its remaining-steps figure.
- A test asserting the Messages tab shows up to 10 distinct recent lines.
- `./run-tests.sh` passes.
