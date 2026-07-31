---
id: DELVE-0012
title: "Phase 2: free-text and LLM grader"
status: implemented
area: [assess, session, content, delve]
milestone:
version: 1.4.0
version_span: 1.4.0-1.6.1
created: 2026-07-21
updated: 2026-07-22
commits: [pre-reset]
related: [DELVE-0003]
supersedes: []
docs: [docs/PHASE2.md]
changelog: "1.4.0"
---

# Phase 2: free-text and LLM grader

## Summary

Add free-text questions and a two-grader stack to mark them: a local LLM (Ollama) trusted above
a confidence floor, falling back to a deterministic keyword grader offline or on low confidence.
Grading is non-blocking (a pending-grade state folded in off a daemon thread), and
`delve setup`/`delve doctor` bootstrap the grader. Delivered across `1.4.0` (free text + keyword
grader), `1.5.0` (LLM grader + non-blocking state), and `1.6.0` (setup/doctor).

## Motivation / problem

Multiple choice and assertions cannot ask a learner to explain in their own words. A local LLM
can grade free text, but it must never block the loop, must degrade gracefully when absent, and
must not become a hard dependency.

## Requirements

1. The parser MUST accept free-text questions (`- ?answer:` syntax) that were previously
   reserved and validation-failed.
2. `LLMGrader` (local Ollama over the `assess/llm.py` socket seam) MUST be trusted only above a
   `0.65` confidence floor.
3. Below the floor, on an unreachable model, on garble, or on an empty answer, grading MUST
   fall to the deterministic `KeywordGrader` (also the offline default and the CI seam).
4. The LLM grader MUST be opt-in via `--grader-model`; no flag MUST mean the keyword floor.
5. Grading MUST NOT block `apply`: the LLM runs off a daemon thread and its verdict is folded
   in on a `GradeReady` poll (`InlineGrader` for keyword, `ThreadedGrader` for the LLM).
6. `assess/llm.py` MUST be the one core module that opens a socket; `Grader` stays a protocol
   so `LLMGrader` slots in without touching the engine or the format.
7. `delve setup` MUST perform only safe remedies and `delve doctor` MUST diagnose read-only;
   every side effect MUST be injected so both test with nothing installed.
8. A ready verdict MUST hold briefly (~2s) so the hand-over line can be read.

## Non-goals

- Any cloud model or network dependency; the grader is local only.
- Making the LLM a required dependency; the keyword grader is always the floor.

## Design notes / links

The two-grader stack, the confidence floor, the socket seam, and the non-blocking pending-grade
runners are all in `CLAUDE.md`; the design and PoC findings are in `docs/PHASE2.md`. `delve.sh`
defaults to the LLM grader, auto-managing Ollama for the run (3b644b5).

## Acceptance / verification

- Free-text questions parse and grade; a low-confidence or empty answer falls to the keyword
  grader.
- The loop stays responsive while a grade is pending (threaded grader test).
- `delve doctor` runs read-only with nothing installed; `delve setup` applies only safe fixes.
