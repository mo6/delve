---
id: DELVE-0097
title: Drop the Status tab's Grader/Ambient rows, now that the Grader tab holds all the detail
status: implemented
area: [session, ui]
type: bug
epic:
effort: low
milestone:
version: 1.35.1
version_span:
created: 2026-08-02
updated: 2026-08-02
accepted_by: George Moses
accepted_at: 2026-08-02
commits: [4b80b76, 2fe7ae9]
related: [DELVE-0066, DELVE-0054]
supersedes: []
docs: [docs/INFOSCREEN.md]
changelog: "1.35.1"
reason:
---

# Drop the Status tab's Grader/Ambient rows, now that the Grader tab holds all the detail

## Summary

The Info panel's Status tab (`i` then Status) shows two rows, `Grader: {model} @ {host}` and
`Ambient: {model} @ {host}` (DELVE-0066), whenever a grader is configured. The Info panel's own
Grader tab already shows both models' full detail, model, host, status, this run's token/verdict
counts, average latency, and a latency sparkline (DELVE-0054/DELVE-0066/DELVE-0077), as two side
by side sections. The Status tab's two rows are now a strict subset of what the Grader tab already
shows, one tab strip cycle away. Remove them from Status; the model/host identity stays visible,
just on the tab built to hold it.

## Motivation / problem

`RunState._status_body` (`delve/session/run.py:1827`) was given its Grader/Ambient rows at
DELVE-0066, at the same time as (and for the same reason as) the Grader tab's own two-section
split: both were "make both models visible, not just one blended reading" fixes landing together.
Since then the Grader tab has grown into the full picture (DELVE-0077's sparkline, DELVE-0078's
label colouring), while the Status tab's rows never grew past `Model: host`. The result is
duplicated information spread across two tabs for no remaining reason: anyone checking Status
"what's configured" already gets a fuller answer one tab over on Grader, so the Status copy is
just an obsolete leftover of before the Grader tab existed in its current form.

## Stories

### As a maintainer, I want the Status tab to show only what isn't already shown elsewhere in the Info panel, so that I'm not reading the same fact twice under two different tabs.

- Given a grader is configured,
  when the Status tab renders,
  then it no longer shows a `Grader:` or `Ambient:` row; it shows only version, pack, locale, and
  terminal size, exactly as it does today when no grader is configured.
- Given no grader is configured,
  when the Status tab renders,
  then it is unchanged from today (it already omits both rows in this case).
- Given a grader is configured,
  when the Grader tab is opened instead,
  then both models' full detail (model, host, status, this run, avg latency, latency) is still
  shown exactly as today; this issue removes nothing from the Grader tab.

## Non-goals

- Not changing anything about the Grader tab itself (DELVE-0087's in-progress two-column layout
  work is a separate, orthogonal change to that tab).
- Not removing `item.status_grader`/`item.status_ambient` from the locale files if some other
  surface still reads them (Design notes below); if nothing else does, delete the now-dead keys
  rather than leaving them unused.
- Not changing what the Status tab shows for version/pack/locale/terminal size, or the tab's
  general shape (DELVE-0044): only the two grader-related rows go.

## Design notes / links

- `delve/session/run.py:1827` `_status_body`: delete the `grader = self._grader_info()` block
  (the `if grader is not None:` branch that appends `item.status_grader` and
  `item.status_ambient`), keeping version/pack/locale first and the terminal-size row last, same
  as today's ordering.
- `item.status_grader`/`item.status_ambient` (`delve/strings/en.toml:113-114`, `nl.toml:94-95`)
  become dead once `_status_body` stops reading them; grep the rest of the tree for other readers
  before deleting the keys (`_grader_info`/`_ambient_info` themselves stay, since the Grader tab's
  own body-building methods, `_grader_metrics_lines`/`_ambient_metrics_lines`, still call them).
- `docs/INFOSCREEN.md`'s §9 table entry for the Status tab currently lists "grader model/host" as
  part of what it shows; update that line to match once removed.
- Existing tests to update or remove, not just leave failing: `tests/test_items.py`'s
  `test_status_body_includes_the_grader_model_and_host_when_one_is_configured` and
  `test_status_body_names_the_ambient_model_as_a_separate_row_from_the_grader` both assert the rows
  this issue removes; `test_status_body_shows_version_pack_and_locale_and_omits_grader_by_default`
  already asserts the no-grader case and should still pass unchanged, since that's the behaviour
  every configuration now has. `tests/test_languages.py`'s `status_grader` locale-mismatch
  assertion (line 64) needs removing too if the key is deleted.

## Acceptance / verification

- A session-level test: with a grader configured, `_status_body()`'s rendered text contains
  neither `"Grader:"`/`"Nakijker:"` nor `"Ambient:"`, in either locale.
- A regression test confirming the Grader tab is unaffected: with the same configured grader,
  the Grader tab's body still names and measures both models exactly as before this change.
- `./run-tests.sh` green, both locales, with the two now-obsolete assertions in
  `tests/test_items.py` removed or rewritten to match the new behaviour rather than deleted
  silently (their DELVE-0066 history is still worth a comment pointing at this issue).

## Peer review

- Auto (implementing agent), 2026-08-02: `_status_body` no longer appends Grader/Ambient rows; dead `item.status_grader`/`item.status_ambient` keys removed from both locales; INFOSCREEN.md §9 updated. The two obsolete Status assertions rewritten as omit-with-grader tests (en + nl) with a DELVE-0097 comment, plus a Grader-tab regression that still names both models. `./run-tests.sh` green (682). Ready to land once you say so.
- Claude Code, 2026-08-02: peer-reviewed the core fix (verified `_status_body`/locale/doc changes, confirmed no other reader of the dropped keys, ran the full suite green) and implemented an addendum, moving the Status tab to the last position in the strip; updated every hardcoded tab-index test/fixture affected by the reorder.
- George Moses (maintainer), 2026-08-02: peer-reviewed; implementation accepted.
