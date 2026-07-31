---
id: DELVE-0077
title: Grader tab grows a latency sparkline
status: in-progress
area: [assess, session, docs]
type: story
epic: DELVE-0035
effort: medium
milestone:
version:
version_span:
created: 2026-07-31
updated: 2026-07-31
accepted_by: George Moses
accepted_at: 2026-07-31
commits: []
related: [DELVE-0053, DELVE-0054]
supersedes: []
docs: [docs/INFOSCREEN.md]
changelog:
reason:
---

# Grader tab grows a latency sparkline

## Summary

`GraderMetrics` (DELVE-0053) currently keeps only `last_latency_ms`, `max_latency_ms`, and an
average; DELVE-0054's Grader tab body (`_grader_body`) shows those three as plain rows and
explicitly deferred the sparkline INFOSCREEN.md §7's mock-up sketches (`Latency
▁▁▂▃▂▁▄█▂▁`), because a sparkline needs a *history* of latencies, not just last/max/avg. This
story adds that history and renders it as one more line in the existing Grader tab body: a
`GraderMetrics.latency_history` bounded deque, appended in `record_call` alongside the existing
last/max/avg bookkeeping, and a pure quantiser that turns it into eight-level Unicode block
glyphs (`▁▂▃▄▅▆▇█`).

## Motivation / problem

Last/max/avg answer "how slow was the worst call" and "what's typical", but not "is it getting
slower" or "was that one call a fluke or a trend", the shape a sparkline is for. INFOSCREEN.md §7
names this as the Grader tab's one remaining sketched-but-unbuilt piece; DELVE-0053's own
non-goals list ("adding that history is its own future story if a sparkline is wanted") points
straight at this story.

## Scope decision: no Live/Run sub-tab split

INFOSCREEN.md §7's mock-up shows the sparkline under a `Live` sub-tab, implying a `Live`/`Run`
split. This story does **not** add that split; it ships the sparkline as one more line in the
Grader tab's current single body, the same "ship the whole thing directly, split later if a second
slice needs it" scoping DELVE-0042 and DELVE-0054 already used. A sub-tab split is still
unfiled future work if a later story wants it.

## Scope decision: the x-axis is calls, not sittings

INFOSCREEN.md §7 labels the sparkline's axis "(sittings)". `GraderMetrics.record_call` fires once
per model call, and a single sitting can drive more than one call (a multi-question free-text
room), plus the ambient backstory toast also calls `record_call` and isn't tied to any sitting at
all (`_grader_body`'s own docstring: `This run` already folds ambient calls in for the same
reason). Grouping by sitting would need call boundaries the accumulator doesn't track today and
would either exclude ambient calls (undercounting what `This run`'s other rows already include) or
invent a sitting for a toast that has none. This story tracks and labels the axis as calls, the
unit `GraderMetrics` actually has: `item.grader_latency`'s tail reads `(calls)`, not `(sittings)`.
A per-sitting grouping is separate future work if wanted, and would need its own accumulator
change, not just a new label on this one.

## Stories

### As a learner playing with the local grader configured, I want the Grader tab to show a shape of recent latency, not just last/max, so that I can tell a slow model from one that had a single slow call.

- Given at least two model calls have been recorded this run (via `record_call`, whether a
  grading verdict or an ambient toast call), when the Grader tab is active, then the body shows
  one additional line below `Avg latency`: a `Latency` label followed by one Unicode block glyph
  per recorded call (`▁` lowest through `█` highest, quantised across the visible history's own
  min/max) and the `(calls)` tail.
- Given fewer than two calls have been recorded (zero, per DELVE-0054's existing `grader_status_none`
  case, or exactly one), when the Grader tab is active, then the sparkline line is omitted
  entirely; a single point has no shape to show and a lone glyph would look like a bug, not a
  feature.
- Given more calls have been recorded than fit the sparkline's fixed width, when the tab renders,
  then only the most recent calls are shown (oldest points drop off, matching how `deque(maxlen=…)`
  already behaves elsewhere in this codebase's rolling-window state), so a long run's tab never
  grows a wider row than the panel's fixed column budget.
- Given every recorded latency this run is identical (a suspiciously stable local model, or exactly
  one distinct value repeated), when quantising, then every glyph renders at the same level
  (typically the lowest, `▁`) rather than raising a divide-by-zero on a zero-width min/max range.

### As a maintainer, I want the history capped and the quantiser pure, so that a long run's Grader tab stays cheap to render and the glyph logic is unit-testable without a fake model.

- Given `GraderMetrics` already stores `last_latency_ms`/`max_latency_ms`/`_latency_sum_ms`/
  `_latency_count` as scalars updated in `record_call`, when this story lands, then a
  `latency_ms_history: deque[int]` field is added alongside them, bounded to the sparkline's own
  fixed width (`maxlen` equal to the number of glyphs rendered, so the deque never holds more than
  the tab can show and no separate truncation step is needed at render time), and appended
  whenever `total_duration_ms is not None`, the same guard `record_call` already uses for
  `last_latency_ms`.
- Given the quantiser (call it `_sparkline(values: Sequence[int]) -> str`), when reviewed, then it
  is a pure function taking a plain sequence of ints and returning a string of block glyphs, with
  no dependency on `GraderMetrics`, `RunState`, or any session/UI type, so it is testable directly
  against literal lists of latencies.
- Given the implementation, when reviewed, then `ui/windows.py` needs no new drawing branch; the
  sparkline line is plain text within the existing `_condensed` block `_grader_body` already
  returns (no new `TextBlock.kind`), the same "no new drawing code" property DELVE-0054 kept.

## Non-goals

- No `Live`/`Run` sub-tab split (see scope decision above); still separately unfiled future work.
- No per-sitting grouping; the axis is calls, matching what `GraderMetrics` actually tracks (see
  scope decision above).
- No persistence of latency history beyond the run; it lives on the in-memory `GraderMetrics`
  instance exactly like every other field DELVE-0053 added, reset when the process exits.
- No colour on the sparkline glyphs; plain text, matching every other Grader tab row (DELVE-0054's
  own non-goal, carried forward).
- No change to `record_call`'s existing scalar bookkeeping (`last_latency_ms`, `max_latency_ms`,
  `avg_latency_ms`); this story only adds the bounded history alongside it.
- No refresh/poll cost: the history is a side effect of calls already made, not a new request.

## Design notes / links

- [docs/INFOSCREEN.md](../docs/INFOSCREEN.md) §7 is the design note; its `Latency
  ▁▁▂▃▂▁▄█▂▁  (sittings)` mock-up line is what this story ships, with the two scope deviations
  (no sub-tab split, `(calls)` not `(sittings)`) called out above and worth a follow-up edit to
  the doc once this lands.
- `delve/assess/grader.py:GraderMetrics.record_call` is the only accumulation point to extend; the
  same file is the natural home for the new `_sparkline` helper, kept private and pure.
- `delve/session/run.py:_grader_body` is the only render-side change: one appended line, reading
  `metrics.latency_ms_history` and calling the quantiser, guarded by the "fewer than two points"
  non-goal above.
- New `Strings` key `item.grader_latency` (e.g. `"Latency     {spark}  (calls)"`) goes in both
  `delve/strings/en.toml` and `delve/strings/nl.toml`, aligned with the existing `grader_*` rows'
  column style.

## Acceptance / verification

- A new test in `tests/test_llm_grader.py` (or beside `GraderMetrics`'s existing tests) asserts
  `record_call` appends to `latency_ms_history`, that it is bounded (feeding more calls than the
  cap in still leaves only the most recent ones), and that a call with `total_duration_ms is None`
  does not append.
- A new unit test asserts `_sparkline` against literal input lists: an ascending sequence produces
  monotonically non-decreasing glyph levels, a flat sequence produces one repeated glyph with no
  exception, and an empty or single-element input is handled (even though `_grader_body` itself
  never calls it below two points, the helper should not crash if it were).
- A `tests/test_items.py` Grader-tab test (beside DELVE-0054's existing ones) asserts: with two or
  more recorded calls, `_grader_body`'s condensed text includes the `Latency` line with `(calls)`;
  with zero or one recorded call, the line is absent while the existing `Model`/`Status`/`This
  run`/`Avg latency` rows are unaffected.
- `tests/test_languages.py` gets the new `item.grader_latency` key in both `en.toml` and `nl.toml`;
  the English wording pinned in the acceptance test doubles as the message-drift tripwire
  CLAUDE.md describes.
- `./tools.sh infoscreen_mockups --check` regenerated if `tools/infoscreen_mockups.py`'s Grader >
  Live mock-up is updated to show the shipped sparkline line.
- `./run-tests.sh` is green.
