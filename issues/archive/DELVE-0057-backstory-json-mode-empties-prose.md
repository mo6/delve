---
id: DELVE-0057
title: Objectives' LLM passage comes back empty because the grader client forces JSON mode
status: implemented
area: [assess, session]
type: bug
epic:
effort: low
milestone:
version: 1.22.1
version_span:
created: 2026-07-30
updated: 2026-07-30
accepted_by: George Moses
accepted_at: 2026-07-30
commits: [9e80678]
related: [DELVE-0028]
supersedes: []
docs: [docs/PHASE2.md]
changelog: "1.22.1"
---

# Objectives' LLM passage comes back empty because the grader client forces JSON mode

## Summary

The Help panel's Objectives tab (DELVE-0028) shows `{ }` instead of a scene-setting passage. The
cause is that `session/backstory.py` reuses the free-text grader's `OllamaClient`
(`RunState._backstory_client`), but `OllamaClient.chat` (`assess/llm.py`) unconditionally sends
`"format": "json"` and `"temperature": 0` to Ollama. Those settings are correct for
`LLMGrader`, which needs a strict, deterministic `{"verdict": ..., "confidence": ...}` reply, but
wrong for prose: told its output must be JSON, the model complies with the smallest valid document
it can, `{}`, regardless of what the prompt asked for.

## Motivation / problem

Verified directly against a local Ollama (`qwen2.5:3b`): the exact prompt `backstory.build_prompt`
constructs ("Write a brief, atmospheric passage...") gets back the literal reply text `'{ }'`. This
is not a model-quality problem (a bigger or different model would show the same behaviour, since
`format: json` is a structural constraint Ollama enforces on the output, not a suggestion); it is a
wiring bug in how DELVE-0028 reused the grading-tuned client for a different kind of call.

## Stories

### As a learner, I want the Objectives tab's optional passage to actually contain prose, so that it adds atmosphere instead of showing `{ }`.

- Given a grader model is configured and reachable,
  when the Objectives tab's background call completes,
  then the cached text is the model's prose reply, not an empty or near-empty JSON document.
- Given the same model and prompt,
  when compared to today's behaviour,
  then the reply is no longer constrained to JSON at the transport level (Ollama's `format` option
  is omitted or set to plain text for this call), so the model is free to write sentences.

### As a maintainer, I want the grader's call and the backstory call to ask for different things without duplicating the client, so that a future caller with its own needs (JSON vs. prose, deterministic vs. varied) doesn't hit the same bug.

- Given `OllamaClient.chat`,
  when a caller needs plain prose rather than a strict verdict,
  then the client exposes a way to ask for that (no forced JSON format, and a non-zero temperature
  so repeated calls are not each other's identical clone), without changing `LLMGrader`'s existing
  behaviour or its tests.
- Given `LLMGrader`,
  when it calls `chat` exactly as it does today,
  then it is unaffected: still JSON-formatted, still temperature 0, no behaviour change and no test
  changes required there.

## Non-goals

- Choosing or configuring a *different model* for the backstory call; that is DELVE-0058's concern
  (a separate, more capable model for prose, configurable). This issue only fixes today's call to
  produce prose at all with whatever model is already configured.
- Retrying or falling back to a keyword-style default passage on a bad reply; an empty reply after
  the fix is treated exactly as `LLMUnavailable` already is (no passage shown, no error), not a new
  failure mode to design for.
- Any change to `LLMGrader`'s prompt, floor, or fallback behaviour.

## Design notes / links

`OllamaClient.chat` (`assess/llm.py`) currently hardcodes the request payload:
```python
payload = {
    "model": self.model,
    "messages": [{"role": "user", "content": prompt}],
    "stream": False,
    "format": "json",
    "think": False,
    "options": {"temperature": 0},
}
```
Add optional parameters (e.g. `json_mode: bool = True, temperature: float = 0`) defaulting to
today's exact behaviour, so `LLMGrader._PROMPT`'s call site (`grader.py`) needs no change and no
new test. `session/backstory.py`'s call then passes `json_mode=False` and a non-zero temperature
(a value that gives some variety without becoming incoherent; the spike range used for grading
doesn't apply here since this is generation, not judgement, so a small trial against the local
model is warranted before picking one, documented in this file's implementation commit). `think:
false` stays unconditional either way (DELVE-0052's reasoning-trace-is-overhead finding applies to
both calls).

## Acceptance / verification

- A test on `OllamaClient` (or a thin wrapper) asserts that a call requesting prose mode sends no
  `"format": "json"` field (or sends a non-JSON format) and a non-zero temperature, while a default
  call (existing `LLMGrader` usage) is unchanged.
- A `backstory.py` test with a fake client asserts the payload/params passed to `chat` differ from
  the grader's own call (this can be asserted via a fake that records kwargs, mirroring
  `test_llm_grader.py`'s `FakeClient`).
- A regression test reproducing this bug's exact symptom: build the real backstory prompt, send it
  through a fake client configured to only accept non-JSON-mode calls (raising if `json_mode` is
  left at its old default), and assert `BackstoryRunner` gets prose back, not `{}`.
- `./run-tests.sh` passes.
