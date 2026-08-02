# Anyone With The Link — en candidate answers

Source: `docs/research/free-text/security-onboarding/sharing-en.md`

## Candidate correct answers

1. **"hidden tabs"** — why this should ACCEPT: Canonical; lesson mentions a second tab; explanation adds hidden sheets.
2. **"comments"** — why this should ACCEPT: Direct accept and lesson ("tracked changes and comments").
3. **"tracked changes"** — why this should ACCEPT: Accept-list and lesson.
4. **"metadata"** — why this should ACCEPT: Accept-list; lesson mentions PDF metadata as parallel.
5. **"revision history"** — why this should ACCEPT: Accept-list; silent travel of past edits.
6. **"filtered rows"** — why this should ACCEPT: Accept-list; data present but not visible in the current view.
7. **"a second sheet you forgot"** — why this should ACCEPT: Casual paraphrase of hidden/extra tabs without exact accept words.
8. **"formulas that pull other data"** — why this should ACCEPT: Explanation calls linked formulas a genuinely good answer; should ACCEPT even though not on the list. Flag: keyword floor will miss it.

## Candidate wrong answers

1. **"file size"** — why this should REJECT: Explicit reject; not a silent content leak.
2. **"formatting / fonts"** — why this should REJECT: Reject-list; cosmetic, not silent sensitive payload.
3. **"the share link itself"** — why this should REJECT: Related lesson theme, but not something that travels *with* the spreadsheet file as hidden content. Flag: lenient grader may accept as "sharing risk".
4. **"anyone with the link"** — why this should REJECT: Correct concept for this room's main thesis, wrong object for this question.
5. **"ask the data owner"** — why this should REJECT: Classification-room answer; wrong here.
6. **"macros"** — why this should REJECT: More malware/attachment territory than silent spreadsheet carry; possible confusion. Flag: some graders may accept as "hidden stuff".
7. **"the visible numbers"** — why this should REJECT: Explicitly on-screen; question asks besides what's visible.
8. **"aardvark"** — why this should REJECT: Off-topic floor test.

## Quality assessment

- Question clarity: Clear; "besides what's visible" and "silently" constrain well.
- Lesson/question alignment: Good. Lesson lists second tab, tracked changes, comments, metadata; explanation adds hidden sheets, filtered rows, revision history.
- Accept-list coverage: Strong. Gap: linked formulas (praised in explanation) not on accept list for keyword floor.
- Reject-list false-positive risk: Low for file size/formatting. Unlikely to catch "hidden sheet formatting" style answers.
- Explanation consistency: Consistent; slightly broader than accept list (linked formulas).

## Suggested refinements

- Add accept: `linked formulas`, `extra sheets`, `desktop in a screenshot` (if screenshots stay in scope; lesson mentions them).
- Or drop the linked-formulas praise from the explanation if they should not count.
- No question reword needed.
