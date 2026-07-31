---
id: DELVE-0051
title: Evaluate qwen3.5:9b as an alternative to qwen2.5:3b for the LLM grader
status: proposed
area: [assess, docs]
type: story
epic:
effort: low
milestone:
version:
version_span:
created: 2026-07-29
updated: 2026-07-29
accepted_by:
accepted_at:
commits: []
related: [DELVE-0047]
supersedes: []
docs: []
changelog:
reason:
---

# Evaluate qwen3.5:9b as an alternative to qwen2.5:3b for the LLM grader

## Summary

Decide, with evidence rather than a hunch, whether `qwen3.5:9b` should replace `qwen2.5:3b` as
`assess/llm.py`'s `DEFAULT_MODEL`, the model `LLMGrader` uses to judge free-text answers during
play. This issue is about producing that evidence and a recommendation; it does not itself change
the default.

## Motivation / problem

An ad hoc side-by-side of the two models was run in `poc/ambient-flavour/` (a throwaway spike, not
wired into the shipping engine) comparing their **ambient flavour text**: `qwen3.5:9b` produced
noticeably less repetitive prose than `qwen2.5:3b`. That comparison does not transfer to grading.
Grading is a different task with different constraints:

- `LLMGrader` asks for a structured `ACCEPT`/`REJECT` verdict plus a confidence score at
  `temperature=0` (deterministic judgement), not free-form prose at `temperature=0.9`
  (`assess/llm.py`'s existing comment on why generation and grading pin different temperatures).
- The `0.65` confidence floor (DELVE-0033, rule 5 area) that decides when `LLMGrader` is trusted
  over the `KeywordGrader` fallback was calibrated against `qwen2.5:3b`'s behaviour. A different
  model may produce systematically different confidence values, which would silently shift how
  often the fallback fires without anyone deciding that on purpose.
- `qwen3.5:9b` is a thinking model. Its reasoning trace, unless suppressed, blew past both the
  120s timeout used in the `poc/ambient-flavour/` spike and `assess/llm.py`'s tighter
  `DEFAULT_TIMEOUT = 60` (grading happens synchronously while a learner waits mid-sitting, not on
  a spike script's own clock). [[DELVE-0052]] makes `think: false` unconditional for every
  `OllamaClient` call, which removes that specific failure mode, but the model is also simply
  larger, so its per-grade latency under `think: false` still needs measuring, not assumed away.

Nothing here says `qwen3.5:9b` is better or worse for grading; that is exactly the open question.

## Stories

### As a maintainer, I want a same-shape grading benchmark comparing qwen2.5:3b and qwen3.5:9b, so that a model swap is a decision backed by evidence, not the ambient-text side-by-side.

- Given a fixed set of real free-text prompts already used for grading (e.g. the tutorial floor's
  `04-the-purse.md` question set, in the same style DELVE-0047 uses for its cross-machine
  benchmark),
  when each prompt is sent through the exact `LLMGrader._PROMPT`/`OllamaClient` seam once per
  model, with `think: false` set,
  then the run records, per model: verdict correctness against a known-good answer key, confidence
  distribution, and wall-clock latency per grade.
- Given the recorded results,
  when they are written up,
  then the write-up states a recommendation (keep `qwen2.5:3b`, switch to `qwen3.5:9b`, or neither
  without further data) and the reasoning, so a future reader does not have to re-run the
  comparison to know what was concluded.

## Non-goals

- Changing `assess/llm.py:DEFAULT_MODEL` or any shipped grading behaviour. That is a separate,
  later issue if this one recommends a switch.
- Re-litigating the `0.65` confidence floor's value; only whether it still makes sense under a
  different model is in scope to flag, not to re-tune here.
- Ambient/flavour text generation quality; already informally compared in `poc/ambient-flavour/`
  and out of scope for this grading-focused story.

## Design notes / links

- [[DELVE-0033]] (the confidence floor and the required-grader rule), [[DELVE-0047]] (the sibling
  cross-machine benchmark methodology this reuses), [[DELVE-0052]] (`think: false` made
  unconditional, a prerequisite for `qwen3.5:9b` to even respond within `DEFAULT_TIMEOUT`).
- `delve/assess/grader.py:LLMGrader._PROMPT` is the exact prompt shape to benchmark, not a
  hand-written approximation.

## Acceptance / verification

A short written comparison (where DELVE-0047's benchmark script lives, or a new one beside it) with
per-model verdict accuracy, confidence distribution, and latency numbers, plus an explicit
recommendation. No change to `run-tests.sh` behaviour is expected from this issue alone.
