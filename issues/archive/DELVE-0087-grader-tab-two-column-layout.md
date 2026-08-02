---
id: DELVE-0087
title: Lay the Grader tab's two model sections out side by side so the latency sparkline fits on one page
status: implemented
area: [ui, session]
type: bug
epic:
effort: medium
milestone:
version: 1.34.3
version_span:
created: 2026-07-31
updated: 2026-08-02
accepted_by: George Moses
accepted_at: 2026-08-02
commits: [4ce5a9b, 45e75e3]
related: [DELVE-0066, DELVE-0075, DELVE-0077, DELVE-0078]
supersedes: []
docs: [docs/INFOSCREEN.md]
changelog: "1.34.3"
reason:
---

# Lay the Grader tab's two model sections out side by side so the latency sparkline fits on one page

## Summary

The Info panel's Grader tab (`i` then the Grader tab) stacks the grading model's section
(`Grading` heading, `Model`/`Status`/`This run`/`Avg latency`/`Latency`) directly above the
ambient toast model's identical section. Once a `Latency` sparkline row (DELVE-0077) is present in
either section, the combined stack no longer fits the panel's single page and spills onto a
second one. Lay the two sections out side by side as two columns instead of stacked, the same way
the Pack tab already splits into a list column and a description column (DELVE-0075), so both
sections plus their sparklines fit on one page.

## Motivation / problem

Everything the Grader tab shows already comes in two parallel, same-shaped sections (grading vs.
ambient, DELVE-0066/DELVE-0078); they only ever differ in their values, not their row shape. Stacking
them is what forces the extra page the instant a sparkline row exists, and a second page here means
an extra keypress just to compare the two models' status, which is exactly the kind of thing a
side-by-side layout removes. `windows.PANEL_W`/`TEXT_W` (69 columns of inner text) already comfortably
fits two roughly-33-column halves.

## MUST / MUST NOT

1. MUST render the `Grading` section and the `Ambient toast` section as two side-by-side columns
   inside the Grader tab's body, not stacked, mirroring the Pack tab's existing
   `PACK_LIST_W`/`PACK_DESC_W` split (`delve/ui/windows.py`).
2. MUST remove the blank line currently separating each section's heading (`Grading` /
   `Ambient toast`) from its own `Model`/`Status`/… data, in both columns, to reclaim the row this
   frees for the sparkline. (Today's blank row is a side effect of the heading and the data being
   two separate `TextBlock`s; the pager inserts a blank row between distinct blocks.)
3. MUST wrap `item.grader_model`/`item.ambient_model` (`"Model: {model} @ {host}"`) onto two lines
   when rendered in a column, so a value like `qwen2.5:3b @ http://localhost:11434` fits the
   narrower column width instead of running past it or wrapping mid-word. Applies to both locales
   (`en.toml`/`nl.toml`).
4. MUST wrap `item.grader_run`/`item.ambient_run` (`"This run: In {tin}   Out {tout}   LLM {llm}
   keyword {keyword}"` / `"…Calls {calls}"`) onto two lines for the same column-width reason.
   Applies to both locales.
5. MUST NOT change the underlying metrics data or what's shown (`Model`/`Status`/`This run`/
   `Avg latency`/`Latency`), only its layout and line-wrapping; this is a presentation fix, not a
   metrics change.
6. MUST NOT regress the "no grader configured" state (`item.grader_offline`), which today renders
   as a single explanatory line instead of either section; that single-line state stays a single,
   full-width line, not squeezed into a half column.
7. MUST NOT regress the ambient section's "always renders, even at zero calls" behaviour
   (DELVE-0066): the right-hand column still shows a zeroed `Ambient toast` section even when no
   toast has fired yet this run.

## Non-goals

- Not changing the Pack tab's own two-column split or its widths; this only reuses the same
   pattern for the Grader tab.
- Not changing the latency sparkline's own rendering (DELVE-0077) or the avg-latency calculation,
   only where the row sits.
- Not adding a Grader sub-tab strip (unlike Scoring's `Now`/`Rooms`, DELVE-0055); the two columns
  are both always visible together, not toggled.

## Design notes / links

- `delve/session/run.py:1650` `_grader_body` currently returns one flat `list[TextBlock]`: a
  `plain` heading, a `kv`-condensed data block, then the same pair again for ambient. Producing two
  independent columns instead needs either a new `InfoView` field (two body lists, mirroring how
  `pack_rows`/`body` already carry the Pack tab's two panes, `delve/session/views.py`) or a
  session-side pre-formatted two-column block `ui` just prints; whichever keeps `ui` painting only
  (rule 2) and `session` owning the content.
- `delve/ui/windows.py:53` `PACK_LIST_W = 26` / `PACK_DESC_W = TEXT_W - PACK_LIST_W - 3` is the
  existing two-column precedent to follow; the Grader tab likely wants a closer-to-even split
  (both columns carry the same row shapes) rather than Pack's list/description asymmetry. A new
  `GRADER_COL_W` (or two, if a divider gap is kept) belongs beside `PACK_LIST_W` with the same kind
  of comment explaining the arithmetic.
- `item.grader_model`/`item.ambient_model`/`item.grader_run`/`item.ambient_run` are today single
  interpolated strings (`delve/strings/en.toml:118,122,129,133` and the `nl.toml` equivalents); the
  two-line wrap needs either splitting each into two string keys (a label line, then a value line)
  or a `ui`-side wrap that still treats the whole thing as one opaque localised string (rule 2:
  `ui` must never assemble words itself, only fit an already-localised string to a column, the same
  distinction the Status-line `Rooms`/`$` fix drew, CLAUDE.md's locale section).
- `docs/SCREENS.md` and `./tools.sh screens` are gone (DELVE-0092, retired 2026-08-02); the current
  on-demand tool is `./tools.sh screenshot <scenario>` (`tools/screenshot.py`), driven against the
  real `RunState`/`delve/ui/windows.py` rather than a checked-in mock-up. It has no `grader` scenario
  yet (`tools/screenshot.py:332`'s `SCENARIOS` dict); this issue needs to add one (reaching the
  Grader tab with both sections populated, one of them holding a `Latency` sparkline) alongside the
  layout fix, so the new columns can actually be inspected on demand.

## Acceptance / verification

- A new `grader` scenario in `tools/screenshot.py`'s `SCENARIOS`, reaching the Grader tab with both
  sections populated and at least one holding a `Latency` sparkline row; `./tools.sh screenshot
  grader` shows both sections side by side on a single page at 100x30.
- A session-level test asserting the Grader tab's rendered body no longer requires a second page
  once both sections include a latency sparkline (today's regression case).
- A rendering test (or screen mock-up assertion) confirming the wrapped `Model:` and `This run:`
  rows fit within the new column width in both locales, including the long example from this issue
  (`qwen2.5:3b @ http://localhost:11434`).
- `./run-tests.sh` green, both locales.

## Peer review

- Auto (implementing agent), 2026-08-02: `InfoView` gains `grader_left`/`grader_right`; `_grader_columns` builds one condensed `kv` block per section (heading included, so no blank between heading and data); `Model`/`This run` split onto two string keys each in en/nl; `windows._draw_grader_columns` mirrors Pack's even-split divider (`GRADER_COL_W` = 33). Offline stays a full-width `body` line. Column titles (`Grading` / `Ambient toast`) are bold bright-yellow via `_kv_spans` treating a leading colon-less line as a section heading. New `grader` screenshot scenario; session tests cover one-page with sparklines, wrap width in both locales, and offline; render test asserts side-by-side highlighted headings. `./tools.sh screenshot grader` shows both columns on one page. `./run-tests.sh` green.
- George Moses (maintainer), 2026-08-02: peer-reviewed; implementation accepted.
