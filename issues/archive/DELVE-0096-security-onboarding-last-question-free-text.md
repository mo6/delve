---
id: DELVE-0096
title: Convert the last question of every room in security-onboarding to free text, so the pack exercises the grader
status: implemented
area: [content]
type: story
epic:
effort: medium
milestone:
version: 1.36.0
version_span:
created: 2026-08-02
updated: 2026-08-02
accepted_by: George Moses
accepted_at: 2026-08-02
commits: [fcaa527, d47076f]
related: []
supersedes: []
docs: [docs/AUTHORING.md, docs/PHASE2.md]
changelog: "1.36.0"
reason:
---

# Convert the last question of every room in security-onboarding to free text, so the pack exercises the grader

## Summary

Every question in every room of `packs/security-onboarding` is today a checkbox question
(multiple-choice or a True/False assertion); the pack has no `- ?answer:` free-text question
anywhere, in either locale. That means the pack never exercises the local LLM grader
(`assess/llm.py`, `delve setup`/`delve doctor`, DELVE-0066's per-model metrics, the Grader tab)
at all: the grader has nothing to grade. Change the last question of each of the pack's 12 rooms,
in both `en` and `nl`, from its current checkbox form into a free-text question, so a real playthrough
of this pack actually calls the grader.

**Amended during implementation, agreed with the maintainer:** `01-phishing.md` ("phishing", chapter
1's first room) is excluded and stays all-checkbox. It is also the hardcoded M2 "golden slice"
(`delve.content.pilot.PHISHING_ROOM`), kept byte-equal to this file by `test_parser.py`'s golden
test and reused as the default single-room fixture across a wide swath of engine-mechanics tests
(stakes, pets, elimination, screenshots) that answer every question by index and know nothing about
free text. Converting it broke ~25 tests unrelated to content; rather than rewrite that much
engine-test infrastructure for one room, the scope narrowed to the other 11 rooms. Everything below
that says "every room" or "12 rooms" means "every room except phishing" / "11 rooms" as of this
amendment.

## Motivation / problem

`security-onboarding` is the pack most likely to be used to demonstrate or exercise Delve's Phase 2
grading (docs/PHASE2.md), since it's the shipped, non-pilot, real-content pack (`packs/holy-grail`
and `packs/ethics-of-ai` are the others; `packs/friends-nap-partners` is a demo pack). Right now
running it, even with a model configured and warmed up (`delve setup`), never actually invokes the
grader, because there is no free-text question in the pack for it to grade; `LLMGrader.metrics`
stays at zero calls all run, and the Grader tab (DELVE-0054) only ever shows the "no grade yet this
run" status. A pack that is supposed to show off the grading feature currently can't.

## Stories

### As a pack author, I want at least one free-text question per room in security-onboarding, so that a playthrough of this pack actually calls the LLM grader.

- Given any room in `packs/security-onboarding` (either locale),
  when its content file is read,
  then its last `###` question (the final one in `## Questions`, in source order) is a free-text
  question: an H3 prompt followed by a `- ?answer:` line and no `- [ ]`/`- [x]` checkboxes.
- Given a room's converted free-text question,
  when `tools/validate.py` (or `./tools.sh validate`) checks the pack,
  then it has a non-empty `?answer:` accept set (the first phrase is the canonical answer),
  an explanatory `>` blockquote (unchanged rule, docs/AUTHORING.md §10), and validates cleanly
  (only the existing "uses free-text questions; the LLM grader is required..." advisory warning
  is expected to newly appear, not an error).
- Given the pack is played end to end with no model configured (the deterministic keyword
  fallback, docs/PHASE2.md §"Grading"),
  when a learner answers each converted question with one of its accept-set phrasings verbatim,
  then the room still passes exactly as before the conversion (the fallback must not make an
  achievable room newly unpassable).

## Non-goals

- Not converting any question other than each room's *last* one; the remaining questions in every
  room stay checkbox (MCQ or assertion), per docs/AUTHORING.md's own advice not to make free text
  the only gate on a room.
- Not changing `pass` thresholds, `reward`, room prose above `## Questions`, or any room's `place`/
  `keeper`/`name` frontmatter; this only changes the *type* of one question per room.
- Not touching any other pack (`holy-grail`, `ethics-of-ai`, `friends-nap-partners`) or the
  tutorial, which already has its own free-text room (DELVE-0009's purse).
- Not writing the Dutch accept/reject sets as literal translations of the English ones: Dutch
  compounding defeats the offline substring fallback (docs/AUTHORING.md §10), so the `nl` accept
  set needs its own idiomatic phrasings, not a mechanical translation pass.

## Design notes / links

- 12 rooms total, 4 chapters of 3 rooms each: `01-the-sorting-office/{01-phishing,02-targeted,
  03-links-and-attachments}.md`, `02-the-vault/{01-passphrases,02-managers,03-mfa}.md`,
  `03-the-archive/{01-classification,02-sharing,03-devices}.md`, `04-the-watchpost/
  {01-social-engineering,02-ai-tools,03-reporting}.md`, each present under both `en/` and `nl/`.
- Today's last question in each room is a mix of True/False assertions (e.g.
  `01-phishing.md`: "A message that survives your check of the sender domain and the link
  destination has been proven legitimate.") and multiple-choice (e.g. `03-devices.md`: "You find
  an unlabelled USB drive in the office car park. What's the correct action?"). Converting an
  assertion is usually the more natural fit for a short free-text answer (the misconception it
  states can become "in your own words, why is X not actually true/safe"); converting an MCQ
  question may need rephrasing from "which of these" into an open prompt the accept set can
  meaningfully cover, per the worked example in docs/AUTHORING.md §10.
- `docs/AUTHORING.md`'s "Free text (Phase 2)" section is the exact format to follow: `- ?answer:`
  comma-separated accept set (several phrasings, since it's also what the offline fallback
  matches against), optional `- ?reject:` for common wrong answers, the `>` explanation unchanged.
- `delve/content/schema.py:127` (`_free_text_needs_grader` or similar) is the validator that emits
  the advisory warning; `delve/content/parser.py:240-248` is where `?answer:`/`?reject:` become a
  question with no options. Neither needs code changes; this is a content-only issue.
- Scoring does not weight by question type (`delve/assess/examination.py`), so converting one
  question per room does not change a room's `pass` threshold's meaning; a room with `pass: 0.75`
  and 4 questions still needs 3 of 4 right, one of which is now graded on meaning (or matched
  against the accept/reject sets offline) instead of picked from a checkbox list.

## Acceptance / verification

- `./tools.sh validate` (or the pack-specific validator) shows exactly 12 new free-text advisory
  warnings (one per room, `en` and `nl` each validated separately, so 24 rooms' worth of files but
  the same 12 logical rooms), no new errors.
- A pack-level test (alongside existing `tests/test_torch.py`/content tests that load
  `security-onboarding`) asserting every room's last question is free text (`accept` is non-None)
  and every other question in the pack is not.
- A playthrough test (offline fallback, no model configured) answering every converted question
  with its canonical (`?answer:`'s first) phrase, confirming every room still reaches its existing
  `pass` bar.
- `./run-tests.sh` green, both locales.

## Peer review

- Claude Code (implementing agent), 2026-08-02: converted 11 rooms' last question to free text
  (en/nl, idiomatic Dutch accept/reject sets); excluded "phishing" (see amendment above) after
  converting it broke ~25 unrelated engine-mechanics tests reusing the hardcoded M2 golden-slice
  fixture. Verified every canonical `?answer:[0]` grades correct against its own `?reject:` list
  with `KeywordGrader` directly (no accidental collisions), not just via the playthrough test.
  `_pass_room` (test_dungeon.py) extended to settle a threaded/LLM grading pause via `GradeReady`.
  `./run-tests.sh` green: 685 tests, ruff, pip-audit, issues index, validate on all four packs.
- George Moses (maintainer), 2026-08-02: peer-reviewed; implementation accepted, including the
  phishing-room amendment.
