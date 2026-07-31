---
id: DELVE-0080
title: Instruct the ambient toast model with an explicit character budget, so the sentence-boundary cap rarely fires
status: in-progress
area: [session]
type: bug
epic:
effort: low
milestone:
version:
version_span:
created: 2026-07-31
updated: 2026-07-31
accepted_by: George Moses
accepted_at: 2026-07-31
commits: []
related: []
supersedes: []
docs: []
changelog:
reason:
---

# Instruct the ambient toast model with an explicit character budget, so the sentence-boundary cap rarely fires

## Summary

The ambient room-entry toast (`session/backstory.py`) asks the model for "a very short (2-3
sentence) scene-setting passage", but DELVE-0070 already found the model doesn't reliably comply,
so `RunState._cap_toast_text` trims an overlong reply to the last complete sentence under a firm
480-character cap (`_TOAST_TEXT_CAP`), falling back to a mid-word `textwrap.shorten` ellipsis only
when even the first sentence overruns the cap. A screenshot from actual play shows exactly that
fallback firing: a passage ending `"...a…"`, cut off mid-clause with no punctuation in sight. This
story adds an explicit numeric character budget to the prompt itself (`backstory.PROMPT`), so the
model is told a hard number rather than a vague "very short", which should make the cap's
sentence-boundary trim (and especially its mid-word ellipsis fallback) fire far less often.

## Motivation / problem

"2-3 sentences" is not a number a small local model reliably holds itself to, especially once the
prompt gives it real material to describe (DELVE-0064's items-first restructuring gave it more to
say, not less). The 480-character cap is a good safety backstop (DELVE-0070's own docstring calls
it exactly that, "a rendering backstop, not a style choice"), but relying on it as the *common*
path means learners routinely see a passage cut off mid-thought, which reads as broken rather than
deliberately concise. Telling the model a concrete character count, something models generally
hold to far better than a sentence count, should make the cap the rare exception again rather than
something a learner runs into regularly.

## Stories

### As a learner reading an ambient toast, I want to see the model's complete passage far more often, so a cut-off mid-sentence stops being a regular thing I notice.

- Given `backstory.PROMPT`, when it is sent to the model, then it states an explicit maximum
  character count for the whole reply (e.g. "Keep your entire reply under 400 characters,
  including spaces and punctuation."), in addition to (not replacing) the existing "very short
  (2-3 sentence)" framing, so the instruction reads as a hard number, not just a vague qualifier.
- Given the chosen budget, when picked, then it sits comfortably under `_TOAST_TEXT_CAP` (480), so
  a reply that lands close to, but a little over, its instructed budget still lands under the cap
  and is shown whole rather than trimmed.
- Given `backstory.NUDGE_PROMPT` (the shorter 1-2 sentence idle nudge), when reviewed, then it gets
  the same treatment for consistency, with its own, smaller number appropriate to a one-line
  nudge, even though it is less prone to overrunning in practice.
- Given the model still does not comply (an LLM instruction is never a guarantee, the same lesson
  DELVE-0070 already learned from "2-3 sentences" not holding), when a reply exceeds
  `_TOAST_TEXT_CAP` anyway, then `_cap_toast_text` keeps trimming it exactly as it does today
  (sentence boundary preferred, word-boundary ellipsis as the last resort); this story does not
  remove or weaken that backstop, only makes it fire less often.

## Non-goals

- No change to `_cap_toast_text`'s trimming logic or to `_TOAST_TEXT_CAP`'s value; the backstop
  stays exactly as DELVE-0070 built it.
- No guarantee that truncation can never happen again; an LLM cannot be forced to obey an
  instruction, only asked more precisely. This story reduces frequency, not eliminates the
  possibility, and the acceptance criteria below are written accordingly (no live-model
  determinism test, since none of this repo's tests talk to a real model per PHASE2.md section 6).
- No change to `draw_toast`'s own line-count truncation (`max_lines`, tied to terminal rows) or to
  `_TOAST_TTL`'s read-time budget; both are separate, already-tuned concerns this story doesn't
  touch.
- No change to `_TEMPERATURE` or any other generation parameter.

## Design notes / links

- `delve/session/backstory.py:PROMPT` is the one string to change: append the character-budget
  sentence near the existing "very short (2-3 sentence)" framing at the top.
- `delve/session/backstory.py:NUDGE_PROMPT` gets the same treatment, its own smaller number.
- `delve/session/run.py:_TOAST_TEXT_CAP`/`_cap_toast_text` (DELVE-0070) are untouched; this story
  is upstream of them, in the prompt only.
- `tests/test_room_toast.py`'s existing cap tests (`test_an_overlong_ambient_reply_is_trimmed_...`,
  `test_a_reply_within_the_cap_is_shown_unchanged`, `test_cap_helper_falls_back_...`) all construct
  a canned model reply directly via `FakeClient`, bypassing the prompt text entirely, so none of
  them need to change; they keep proving the backstop still works.

## Acceptance / verification

- A new test asserts `backstory.build_prompt(...)`'s returned string contains a concrete number
  (the chosen character budget), so the instruction is present and the number is pinned (a
  message-drift tripwire the same way `en.toml`'s exact English wording already is elsewhere).
- A new test asserts `backstory.build_nudge_prompt(...)`'s returned string contains its own
  (smaller) character budget.
- The existing DELVE-0070 cap tests in `tests/test_room_toast.py` stay green unchanged, confirming
  the backstop itself is untouched.
- `./run-tests.sh` is green.
