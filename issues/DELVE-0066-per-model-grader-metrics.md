---
id: DELVE-0066
title: Show the grader model and the ambient model as separate rows in Info/Grader and Info/Status
status: proposed
area: [assess, session, ui]
type: feature
epic:
effort: high
milestone:
version:
version_span:
created: 2026-07-31
updated: 2026-07-31
accepted_by:
accepted_at:
commits: []
related: []
supersedes: []
docs: []
changelog:
reason:
---

# Show the grader model and the ambient model as separate rows in Info/Grader and Info/Status

## Summary

Delve actually runs two different local models per session: the configured grader model (default
`qwen2.5:3b`, `assess/llm.py`'s `DEFAULT_MODEL`) that grades free-text answers, and a separate,
more capable ambient/backstory model (`session/run.py`'s `_BACKSTORY_MODEL`, currently
`qwen3.5:9b`) that writes the room-entry toast prose. The Info panel's Grader and Status tabs
currently only ever name and measure the grader model; the ambient model's calls are folded into
the *same* metrics (tokens, latency, call counts) with no way to see it named or measured
separately. This issue splits both tabs so each model's identity and performance are visible on
their own.

## Motivation / problem

`RunState._grader_info`/`_backstory_client` both duck-type the same underlying `OllamaClient`
instance and report `client.model`, which is the grader's model; the ambient runner only ever
*overrides* the model per call (`OllamaClient.chat(..., model=self.model)`), so nothing about
that override is visible anywhere in the UI. Worse, both kinds of calls accumulate into one
shared `GraderMetrics` instance (`RunState._backstory_metrics` reuses `_grader_runner`'s own
metrics), so the Grader tab's `This run` and `Avg latency` rows are already a blend of grading and
ambient traffic with no way to tell which model produced which number. A learner or maintainer
watching Info/Status to sanity-check what's actually running only ever sees one model name, even
though two are doing real work.

## Stories

### As a maintainer, I want the Info/Status tab to name both configured models, so that I can see at a glance what the session is actually running.

- Given a grader is configured (an `LLMGrader` present),
  when the Status tab renders,
  then it shows one row for the grader model (as today) and a second row naming the ambient
  model, each with its own label.
- Given no grader is configured (the default keyword-only floor),
  when the Status tab renders,
  then neither model row appears, exactly as today.

### As a maintainer, I want the Info/Grader tab to report each model's own call counts, tokens, and latency separately, so that I can tell the grading workload apart from the ambient workload.

- Given both a grading verdict and an ambient toast call have happened this run,
  when the Grader tab renders,
  then the grader model's own section shows its verdict counts (`llm`/`keyword`), tokens, and
  latency, and the ambient model's own section shows its call count, tokens, and latency,
  as two distinct blocks rather than one merged total.
- Given only grading calls have happened (no ambient calls yet, e.g. a run with no keeper rooms
  visited),
  when the Grader tab renders,
  then the ambient section reflects zero calls rather than being omitted outright (so its
  presence is predictable, not conditional on traffic).

## Non-goals

- No change to which model is used for which purpose, or to `_BACKSTORY_MODEL`'s value.
- No new configuration surface (e.g. no new `--ambient-model` CLI flag); this issue is about
  *visibility* of the existing two-model setup, not making the ambient model operator-configurable.
- No change to the keyword-fallback confidence floor or grading behaviour itself (DELVE-0033).

## Design notes / links

- `assess/grader.py:GraderMetrics` currently accumulates everything into one instance; the
  natural fix is either two `GraderMetrics` instances (one per model, threaded through
  `RunState._grader_runner`'s metrics and a new ambient-only one) or a metrics class that tracks
  per-model sub-totals internally. Either way, `RoomBackstoryRunner` (`session/backstory.py`) is
  the one call site that should record into the ambient side rather than the shared one.
- `RunState._grader_info`/`_backstory_client`/`_backstory_metrics` (`session/run.py`) are the
  existing duck-typed reads to extend; keep the duck-typing (rule 1: no new `assess` import from
  `ui`, and `session` already reads these opaquely).
- New `Strings` keys will be needed for the ambient model's row/section labels
  (`delve/strings/{en,nl}.toml`), following the existing `item.grader_*`/`item.status_grader`
  naming.

## Acceptance / verification

- A test asserting `_status_body` includes both model rows when a grader is configured.
- A test asserting `_grader_body` reports the grader and ambient sections separately, with
  distinct call counts, after triggering one of each kind of call in a headless run.
- A test asserting the ambient section renders even at zero calls.
- `./run-tests.sh` passes in both locales (new/changed strings need `nl.toml` entries too).
