---
id: DELVE-0071
title: The drop menu's lit-torch label matches the lowercase, unpunctuated style of every other row
status: implemented
area: [session, delve]
type: bug
epic:
effort: low
milestone:
version: 1.26.2
version_span:
created: 2026-07-31
updated: 2026-07-31
accepted_by: George Moses
accepted_at: 2026-07-31
commits: [581d825]
related: [DELVE-0068]
supersedes: []
docs: []
changelog: "1.26.2"
reason:
---

# The drop menu's lit-torch label matches the lowercase, unpunctuated style of every other row

## Summary

DELVE-0068 fixed the drop menu's lit-torch entry to show its remaining steps by reusing
`item.torch_lit` verbatim ("A torch, lit (33 steps left)."), Info/Pack's own sentence-style line.
Every other drop-menu row is a bare, lowercase noun phrase with no leading article and no
trailing punctuation ("urgent memo", "spear letter", "15 coins"), so the lit-torch row now stands
out as capitalized and ending in a period where nothing else does. This issue gives the drop menu
its own lowercase, unpunctuated wording for the lit torch, leaving Info/Pack's sentence unchanged.

## Motivation / problem

A playtesting screenshot of the drop menu showed the mismatch directly: four lowercase,
article-free rows followed by "A torch, lit (33 steps left)." as the fifth. `item.torch_lit` is
correct as a standalone Info/Pack panel line (a full sentence is right there), but it was never
meant to double as a menu label, and doing so broke the menu's own established style.

## MUST / SHOULD

- MUST add a locale key for the drop-menu wording (both `en.toml` and `nl.toml`), styled like the
  menu's other rows: lowercase, no leading article, no trailing period, e.g.
  `"torch, lit ({n} steps left)"`.
- MUST use that new key for the lit-torch entry in `RunState._droppable_list`
  (`session/run.py`), not `item.torch_lit`.
- MUST NOT change `item.torch_lit` itself or its use in Info/Pack (`_pack_body`); that remains a
  full sentence there.

## Acceptance / verification

- A test asserting the drop menu's lit-torch label is lowercase, has no leading article, and has
  no trailing period.
- A test asserting Info/Pack's own torch row is unchanged (still the full `item.torch_lit`
  sentence).
- `./run-tests.sh` passes in both locales.
