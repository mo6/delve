---
id: DELVE-0033
title: Require a reachable LLM grader; play refuses to start without one
status: implemented
area: [assess, session, delve, docs]
type: feature
epic:
effort: low
milestone:
version: 1.13.0
version_span:
created: 2026-07-26
updated: 2026-07-26
commits: [d54aa19, 4096e8c]
related: [DELVE-0012]
supersedes: []
docs: [docs/PHASE2.md]
changelog: "1.13.0"
reason:
---

# Require a reachable LLM grader; play refuses to start without one

## Summary

Make the local LLM grader a hard requirement to play, instead of an opt-in (`--grader-model`)
layered on top of an always-available `KeywordGrader` floor. `delve` refuses to start a play
session when no LLM grader is reachable, printing the same diagnosis `delve doctor` would and
pointing at `delve setup`, rather than silently sitting a learner's free-text answers through the
keyword floor.

## Motivation / problem

DELVE-0012 built a two-grader stack on purpose: `LLMGrader` trusted above a confidence floor,
falling back to a deterministic `KeywordGrader` whenever the model is absent, unreachable, or
low-confidence, with "making the LLM a required dependency" written down as an explicit
non-goal. That fallback is now judged to cost more than it buys:

- The keyword floor is error-prone as a grading strategy in its own right (substring/keyword
  matching on free text is a poor judge of whether a learner understood the material), so
  treating it as an acceptable steady-state grader, not just an emergency fallback, undersells
  the examinations it grades.
- Carrying it as a fully-supported no-LLM mode adds real complexity: the confidence-floor
  plumbing, the `--grader-model` opt-in branch, dual messaging in `delve doctor`/`setup`, and a
  permanently-offline code path that every grading change has to keep working.
- Delve's premise is partly to be a showcase of a local LLM doing real work inside an offline
  tool. A pack author writing free-text questions, and a learner sitting them, should be able to
  assume the LLM grader is what's judging them, not a keyword match that happens to be silently
  in play whenever Ollama isn't running.

This issue is about making the LLM grader **required to play at all**, not merely the default.

## Stories

### As a learner, I want delve to tell me up front if the grader isn't available, so that I never sit a free-text exam graded by keyword-matching without knowing it.

- Given no LLM grader is reachable (Ollama not installed, not running, or the configured model
  not pulled),
  when I run `./delve.sh` or `python -m delve` to play,
  then delve prints the same diagnosis `delve doctor` would (which check failed, and its remedy)
  and exits non-zero before curses starts, instead of starting the run on the keyword floor.
- Given the LLM grader is reachable,
  when I start a run,
  then play starts exactly as it does today, with no new prompt or flag required beyond what
  `delve.sh` already sets up.

### As a maintainer, I want the keyword grader demoted from a supported no-LLM mode to an internal fallback only, so that the grading path has one steady state instead of two.

- Given the LLM grader is reachable at startup but a single grading call returns garbled JSON, an
  empty answer, or a low-confidence verdict mid-run,
  when that grade resolves,
  then it may still fall to `KeywordGrader` for that one answer (transient-failure resilience is
  kept; the mid-run behaviour of DELVE-0012 is unchanged).
  then `--grader-model` is no longer optional for the play path, since there is no supported way
  to play without one.

### As a pack author, I want `delve validate` to keep working without Ollama installed, so that packs can be authored and CI-checked on a machine with no local model.

- Given a pack with free-text questions and no LLM grader reachable,
  when I run `delve validate ./pack`,
  then validation still runs to completion on structure and policy alone (it never sits an
  examination), unaffected by this change.

### As a maintainer, I want `delve doctor`/`delve setup` to read as the on-ramp for this requirement, not an optional extra, so that a new machine's first run tells you what's missing in one place.

- Given a fresh checkout with nothing installed,
  when I run `delve doctor`,
  then it reports the same four checks it does today (binary, service, model, warm-up), and its
  report is what play now shows automatically when the requirement isn't met.

## Non-goals

- Any cloud model or network dependency; the grader stays local-only (Ollama), unchanged from
  DELVE-0012.
- Removing `KeywordGrader` from the codebase entirely; it stays as the deterministic fallback for
  a single low-confidence/garbled/empty verdict mid-run (`LLMGrader`'s existing `fallback`
  argument), just no longer reachable as a way to play with no model at all.
- Changing the confidence floor, the non-blocking `ThreadedGrader`/`GradeReady` polling, or the
  socket seam in `assess/llm.py`; those mechanics are unaffected.
- Deciding the exact wording of the startup failure message or which model `delve.sh` requires by
  default; that is implementation, not this issue.

## Design notes / links

This reverses one explicit non-goal of DELVE-0012 ("Making the LLM a required dependency; the
keyword grader is always the floor") while keeping the rest of that design (the confidence floor,
the threaded runner, `assess/llm.py` as the one socket-opening module, `Grader` as a protocol).
`docs/PHASE2.md` and `CLAUDE.md`'s "two-grader stack" gotcha need updating alongside the code to
stop describing the keyword floor as an offline default for play. The check itself belongs at the
same edge `delve/__main__.py:_play` already probes Ollama from (`startup_warning`/`delve/doctor.py`),
before curses starts, per rule 1's "content never in frontmatter" sibling principle: startup
failures surface before `ui/` is ever reached.

## Acceptance / verification

- A test drives `delve/__main__.py`'s play entry point with no reachable Ollama and asserts a
  non-zero exit and a doctor-style message, without curses ever starting.
- A test drives the same entry point with a reachable (faked) LLM client and asserts play starts
  normally.
- Existing `assess/grader.py` tests for `LLMGrader`'s mid-run fallback-on-low-confidence /
  fallback-on-garble behaviour keep passing unchanged.
- `delve validate` tests on packs with free-text questions keep passing with no Ollama installed.
- `./run-tests.sh` green, including `tools/issues.py --check`.
