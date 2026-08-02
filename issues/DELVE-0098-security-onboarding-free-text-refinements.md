---
id: DELVE-0098
title: Investigate the free-text candidate-answer research for security-onboarding and refine the pack's accept/reject lists and lesson prose
status: proposed
area: [content]
type: story
epic:
effort: medium
milestone:
version:
version_span:
created: 2026-08-02
updated: 2026-08-02
accepted_by:
accepted_at:
commits: []
related: [DELVE-0096]
supersedes: []
docs: [docs/AUTHORING.md, docs/research/free-text/security-onboarding/candidate-answers-prompt.md, docs/research/free-text/security-onboarding/candidates-claude-code-20260802/comparison-vs-cursor.md]
changelog:
reason:
---

# Investigate the free-text candidate-answer research for security-onboarding and refine the pack's accept/reject lists and lesson prose

## Summary

DELVE-0096 converted the last question of every room in `packs/security-onboarding` (11 rooms,
`en`+`nl`, phishing excluded) to free text, but never validated whether the resulting accept
lists, reject lists, and lesson prose actually hold up against the range of ways a real learner
might answer. Two independent research runs of `docs/research/free-text/security-onboarding/candidate-answers-prompt.md`
have now done that validation, one by Claude Code, one earlier in Cursor, each generating 5-10
plausible correct and wrong answers per question and a quality assessment against the lesson,
accept list, reject list, and explanation. A synthesis comparing the two runs room by room
(`comparison-vs-cursor.md`) surfaced concrete, specific problems: a lesson that doesn't teach what
its question asks, an accept-list entry missing despite the explanation calling it correct,
several reject-list phrases that would substring-match and wrongly fail a genuinely correct
answer, and a couple of unresolved disagreements between the two runs worth a human call. This
issue is to work through that research and land the resulting fixes in the pack.

## Motivation / problem

The free-text questions DELVE-0096 added are graded two ways: an LLM grader judging meaning, and
(when no model is configured) an offline keyword floor that only does substring matching against
the `?answer:`/`?reject:` lists. Neither path was checked against realistic learner phrasing before
now. The comparison research found real, specific defects that would misgrade a learner in actual
play, not hypothetical edge cases:

- `passphrases-en/nl`: the visible lesson prose (entropy, length vs. cleverness, uniqueness,
  credential stuffing) never actually states *when* to change a passphrase; the accept list's
  answer ("when there's a reason," "after a breach," etc.) is only taught in the post-answer
  explanation. A learner who read the lesson carefully has no textual basis for the expected
  answer.
- `sharing-en/nl`: the explanation calls "linked formulas" a genuinely good answer, but no accept
  entry covers it; both research runs independently caught this.
- `devices-en/nl`: the reject phrase "check the filenames" would substring-match and wrongly fail
  a correct compound answer like "don't check the filenames, hand it to security."
- A recurring pattern across `ai-tools`, `reporting`, and others: reject lists catch blunt wrong
  instincts but not negated/compound phrasings of the same correct idea (e.g. "don't delete the
  conversation, report it" collides with the reject phrase "delete the conversation").
- A handful of unresolved disagreements between the two runs (`links-and-attachments`'s
  explanation-consistency verdict, `password-managers`'s "nothing" reject-substring risk,
  `classification`'s missing "default to confidential" reject entry) that need a human read of the
  source file to settle, not just another LLM opinion.

Full detail, per room, is in the comparison document linked below; this issue exists to turn that
research into an accepted, tracked change rather than letting it sit unread in `docs/research/`.

## Stories

### As a pack author, I want each security-onboarding free-text question's accept list, reject list, and lesson prose reconciled against the candidate-answer research, so that both the LLM grader and the offline keyword floor grade real learner answers correctly.

- Given the findings in `comparison-vs-cursor.md` for `passphrases-en/nl` (lesson does not teach
  when to change a passphrase),
  when the pack author reviews `packs/security-onboarding/{en,nl}/02-the-vault/01-passphrases.md`,
  then either a short lesson beat teaching reason-based change is added before the question, or the
  question is re-aimed at what the lesson already teaches (entropy/uniqueness/why mangling fails),
  per the two refinement options already recorded in
  `candidates-claude-code-20260802/passphrases-{en,nl}-candidates.md`.
- Given the `sharing-en/nl` accept-list gap ("linked formulas" praised in the explanation, absent
  from the accept list),
  when the pack author reviews `03-the-archive/02-sharing.md`,
  then an equivalent accept entry is added in both locales.
- Given the `devices-en/nl` reject-substring risk ("check the filenames" would false-reject a
  correct compound answer),
  when the pack author reviews `03-the-archive/03-devices.md`,
  then the reject entry is reworded to avoid the collision (or the lesson is strengthened per
  cursor's separately-flagged "hand it to security" alignment gap, if both are judged worth fixing
  together),
  and the fix is checked against the `KeywordGrader` directly, the way DELVE-0096's peer review
  verified its own accept/reject sets didn't collide.
- Given the recurring negated/compound-phrasing reject-list gap flagged in `ai-tools`, `reporting`,
  and others,
  when the pack author reviews each flagged room's reject list,
  then either the reject phrasing is tightened to avoid the substring collision, or the risk is
  explicitly accepted and recorded as a known LLM-grader-only gap (the offline floor is a fallback,
  not the primary grading path, so not every gap needs a list edit, but each one needs a decision,
  not silence).
- Given the unresolved disagreements between the two research runs (`links-and-attachments`
  explanation-consistency, `password-managers` "nothing" reject risk, `classification`'s missing
  "default to confidential" reject entry, `social-engineering`'s "hang up and call" near-miss,
  `mfa-nl`'s reject-list locale-parity gap),
  when the pack author reads the relevant source file directly (not just the two research
  opinions),
  then each is resolved one way or the other, and the resolution (change made, or left as-is with a
  reason) is noted in this issue's Peer review section on completion.

## Non-goals

- Not re-running `candidate-answers-prompt.md` again; the two existing runs are sufficient input.
  A future re-run, if wanted after these fixes land, is a separate ask.
- Not restructuring which question in each room is free text, or reverting any room to checkbox;
  DELVE-0096's scope and its phishing-room exclusion stand.
- Not touching any pack other than `security-onboarding`.
- Not changing `candidate-answers-prompt.md`'s own reusable output-directory convention (currently
  a generic `candidates/`, while the two existing runs used dated, tool-named directories); that's
  a separate, smaller decision the maintainer flagged as open but out of scope here.
- Not attempting to resolve every research finding by editing the pack: some (e.g. genuinely
  low-risk substring overlaps) may be explicitly declined; this issue's bar is that each finding
  gets a recorded decision, not that every one results in a content change.

## Design notes / links

- `docs/research/free-text/security-onboarding/candidate-answers-prompt.md`: the reusable
  prompt/tool that generated both research runs; also documents the pack's authoring convention
  for accept/reject lists (short reference phrases, not full sentences).
- `docs/research/free-text/security-onboarding/candidates-claude-code-20260802/`: this run's 22
  per-room candidate-answer files (`<room>-<locale>-candidates.md`), one per DELVE-0096 free-text
  question, each with candidate correct/wrong answers, a quality assessment, and suggested
  refinements.
- `docs/research/free-text/security-onboarding/candidates-cursor-20260802/`: the earlier,
  independent Cursor run of the same prompt against the same 22 source files, same structure.
- `docs/research/free-text/security-onboarding/candidates-claude-code-20260802/comparison-vs-cursor.md`:
  the synthesis comparing the two runs room by room, the primary document to work from for this
  issue, since it already distills where the runs agree, where they disagree, and which run to
  trust for reject-list false-positive risk specifically (see its "Recommendation" section).
  Includes one already-fixed factual error (`passphrases-en/nl`'s lesson-alignment claim, corrected
  2026-08-02) that does not need re-doing.
- `docs/AUTHORING.md` §10: the free-text authoring format (`?answer:`/`?reject:`, canonical
  answer first, explanation unchanged) that any list edit here must keep following.
- [[DELVE-0096]]: created the free-text questions this issue investigates; read its
  Non-goals (Dutch accept/reject sets are idiomatic, not literal translations) before editing `nl`
  files.

## Acceptance / verification

- `./tools.sh validate` clean on `packs/security-onboarding`, both locales, after any accept/reject
  list or lesson edit.
- For every reworded or added reject/accept entry, a direct `KeywordGrader` check (as DELVE-0096's
  peer review did) confirming the canonical `?answer:[0]` still grades correct and no reject entry
  now collides with a genuinely correct answer.
- `./run-tests.sh` green.
- This issue's own body (Stories section) shows a recorded decision for every finding named above,
  not just the ones acted on.

## Peer review

Left blank until the change is implemented and tested.
