---
id: DELVE-0054
title: Grader tab, take 1, model/status/token rows from GraderMetrics
status: implemented
area: [session, delve, docs]
type: story
epic: DELVE-0035
effort: medium
milestone:
version: 1.19.0
version_span:
created: 2026-07-29
updated: 2026-07-29
accepted_by: George Moses
accepted_at: 2026-07-29
commits: [pre-reset]
related: [DELVE-0040, DELVE-0044, DELVE-0053]
supersedes: []
docs: [docs/INFOSCREEN.md]
changelog: "1.19.0"
reason:
---

# Grader tab, take 1, model/status/token rows from GraderMetrics

## Summary

The `i` panel's Grader tab has shown only `item.tab_soon` since DELVE-0040 built the tab strip; the Status tab (DELVE-0044) prints the configured model and host, but nothing about whether the grader is actually alive or what it has cost this run. DELVE-0053 gave `LLMGrader` a `GraderMetrics` accumulator (tokens in/out, last/max latency, warm/cold, LLM-vs-keyword-fallback counts); this story is the first to read it, filling the Grader tab with the plain key/value rows INFOSCREEN.md §7's "Live" mock-up sketches: `Model`, `Status`, `This run`. No sub-tab split (`Live` / `Run`) and no latency sparkline yet, the same "ship the whole body directly, split later if a second slice needs it" scoping DELVE-0042 used for Scoring's first cut.

## Motivation / problem

A learner running with the local LLM grader configured has no way, mid-run, to tell whether it is actually answering or silently falling back to the keyword floor on every question; `delve doctor` answers that only before play starts, from outside curses. `GraderMetrics` already collects the numbers that would answer it (DELVE-0053); nobody has read them into a `Frame` yet.

## Stories

### As a learner playing with the local grader configured, I want the Grader tab to show whether it is reachable and how it has performed this run, so that I can tell a real grade from a silent fallback without leaving the dungeon.

- Given a grader runner backed by `LLMGrader` (a model was configured) and at least one free-text question has been graded, when the Grader tab is active, then the body shows a `Model` row (`{model} @ {host}`, the same values `_status_body`'s `status_grader` row already reads), a `Status` row stating warm or cold from `GraderMetrics.last_warm` and the last latency in ms from `.last_latency_ms`, and a `This run` row with `In {prompt_tokens}`, `Out {completion_tokens}`, `LLM {llm_verdicts}`, `keyword {keyword_verdicts}`.
- Given the same configured grader but no free-text question has been graded yet this run (a fresh `GraderMetrics`), when the Grader tab is active, then the `Model` row still shows (model/host are launch-time facts, not a grade result), the `Status` row reads "no grade yet this run" rather than a stale or fabricated latency, and the `This run` row shows all-zero counts, never a crash on `None` latency.
- Given no model is configured (the default `InlineGrader`/`KeywordGrader` floor, the same condition `_status_body` already detects via `_grader_info() is None`), when the Grader tab is active, then the body shows a single explanatory line, "keyword floor, no model configured" or equivalent, and no `Model`/`Status`/`This run` rows (there is nothing to report), matching INFOSCREEN.md §7's "offline is a first-class state, not an error banner".

### As a maintainer, I want the Grader tab's body built the same way the Scoring and Status tabs are, so that a later story can add the `Live`/`Run` sub-tab split or a sparkline without restructuring this one.

- Given the implementation, when reviewed, then a `_grader_body` method returns `list[TextBlock]` the same way `_scoring_body`/`_status_body` do, reads `GraderMetrics` via the same duck-typed attribute access `_grader_info` already uses (`getattr(getattr(self._grader_runner, "grader", None), "metrics", None)`), and adds no new import of `assess.grader`/`assess.llm` types into `session/run.py` (rule 1's "duck-typing the runner" convention, not a new cross-layer dependency).
- Given the implementation, when reviewed, then `ui/windows.py` needs no new branch beyond what already renders an `InfoView`'s `TextBlock` body (`kind="plain"`); this story adds no new `TextBlock.kind` and no new drawing code, unlike the Scoring tab's `kind="bar"`.

## Non-goals

- No `Live`/`Run` sub-tab split; this story's rows are the Grader tab's whole body, the same "no sub-tab row yet" scoping DELVE-0042 used for Scoring.
- No latency sparkline (INFOSCREEN.md §7's `▁▁▂▃▂▁▄█▂▁`); `GraderMetrics` keeps only last/max latency, not a per-sitting history, and adding that history is its own future story if a sparkline is wanted.
- No rolling average latency; only last and max are read, matching what `GraderMetrics` actually stores.
- No SI-suffixed token counts (`2.1k`); INFOSCREEN.md §7 itself calls tokens "engineering honesty", not a dashboard, and DELVE-0035's non-goals rule out treating this like a token market. Plain integers.
- No coloured border or coloured pill beyond what DELVE-0041 already ships for the tab strip; INFOSCREEN.md §8's per-tab border tint is still separately unfiled future work.
- No change to `GraderMetrics`, `LLMGrader`, or `OllamaClient`; this story only reads what DELVE-0053 already accumulates.
- No new `delve doctor` behaviour; the in-game tab stays the "during play" glance, `doctor` the deep diagnostic, per INFOSCREEN.md §7's own line.

## Design notes / links

- [docs/INFOSCREEN.md](../docs/INFOSCREEN.md) §7 is the Grader tab's design note; its "Live" mock-up (`Model`/`Status`/`This run` rows) is the exact body this story ships, minus the sparkline it separately flags as needing per-sitting history this story does not add.
- `delve/assess/grader.py:GraderMetrics` (DELVE-0053) is the only new data source; its fields (`llm_verdicts`, `keyword_verdicts`, `prompt_tokens`, `completion_tokens`, `last_latency_ms`, `max_latency_ms`, `last_warm`) map directly onto this story's three rows.
- `RunState._grader_info` and `_status_body` (`delve/session/run.py`) are the existing pattern for reaching the configured client without a new import; extend that pattern for metrics rather than inventing a second way to reach the runner.
- `_scoring_body`/`_status_body` and `_info_overlay`'s dispatch (`delve/session/run.py`) are the two places this story's `_grader_body` plugs in, replacing the `item.tab_soon` fallback for the `"grader"` tab key only.
- New `Strings` keys go in both `delve/strings/en.toml` and `delve/strings/nl.toml`, in the same aligned key/value style as the existing `status_*` rows (`en.toml`'s exact English wording is a test fixture per CLAUDE.md, so pick final English wording before writing the acceptance test that pins it).

## Acceptance / verification

- A new `tests/test_items.py` section (beside the Status tab tests) asserts: with a fake LLM-backed runner and metrics recorded via calls to `grade_text`, `_grader_body` includes the model/host, a warm-or-cold status line with the last latency, and the token/fallback counts; with a fresh grader (no calls yet), the same rows show the "no grade yet" status and all-zero counts; with the default inline/no-model runner, the body is the single offline explanatory line and nothing else.
- A `tests/test_render.py` (or existing `InfoView` render test) case confirms the Grader tab paints as plain `TextBlock` rows within `windows.TEXT_W` (69 columns), no new drawing branch required.
- `tests/test_languages.py` gets the new `Strings` keys in both `en.toml` and `nl.toml`; the English wording pinned in the acceptance test doubles as the message-drift tripwire CLAUDE.md describes.
- `./tools.sh screens --check` unaffected (the Grader tab is not in `all_screens()`); `./tools.sh infoscreen_mockups --check` regenerated if `tools/infoscreen_mockups.py`'s Grader > Live mock-up is updated to match the shipped body (dropping the sparkline this story does not ship).
- `./run-tests.sh` is green.
