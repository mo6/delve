# Length Beats Cleverness — en candidate answers

Source: `docs/research/free-text/security-onboarding/passphrases-en.md`

## Candidate correct answers

1. **"when there's a reason"** — why this should ACCEPT: Canonical accept entry; matches the explanation's closing line.
2. **"after a breach"** — why this should ACCEPT: Direct accept entry; concrete instance of "a reason".
3. **"if you suspect it's compromised"** — why this should ACCEPT: Full-sentence form of "on suspicion of compromise".
4. **"when it's been shared"** — why this should ACCEPT: Explanation lists "a shared secret" as a reason; meaning-correct even if not on the accept list.
5. **"only when something goes wrong"** — why this should ACCEPT: Casual paraphrase of reason-based change, not calendar-based.
6. **"if it might have leaked"** — why this should ACCEPT: Informal synonym for breach/suspicion without accept-list words.
7. **"when you think someone else knows it"** — why this should ACCEPT: Partial restatement of compromise suspicion; should still count.
8. **"upon evidence of exposure"** — why this should ACCEPT: Formal register of the same idea.

## Candidate wrong answers

1. **"every 90 days"** — why this should REJECT: Explicit reject; the calendar policy NIST/NCSC withdrew.
2. **"on a fixed schedule"** — why this should REJECT: Exact reject and the thing the question says "if not".
3. **"routinely / every three months"** — why this should REJECT: Reject-list routine expiry.
4. **"when it looks clever enough"** — why this should REJECT: Confuses the lesson's entropy theme with the change-timing question.
5. **"never"** — why this should REJECT: Overcorrects against scheduled rotation; breaches still require change. Flag: lenient grader might accept if it hears "not on a schedule".
6. **"use a passphrase"** — why this should REJECT: Correct theme of this lesson's prose, wrong answer to this question (timing of change).
7. **"report it"** — why this should REJECT: Correct for reporting/AI rooms, wrong here.
8. **"Tuesday"** — why this should REJECT: Off-topic floor test.

## Quality assessment

- Question clarity: Clear as a prompt, but it assumes knowledge the visible lesson barely teaches.
- Lesson/question alignment: Poor. The lesson is about entropy, length vs cleverness, uniqueness, and password managers next; it never states when to change a password. The NIST/NCSC anti-expiry advice appears only in the explanation.
- Accept-list coverage: Reasonable for the intended answer, but a careful lesson-reader who answers "when it's reused" or "when you can remember a better one" has nowhere to land.
- Reject-list false-positive risk: "routinely" / "every" are fairly safe. Low risk of catching a correct reason-based answer.
- Explanation consistency: Explanation matches the accept list well; the gap is that the lesson does not.

## Suggested refinements

- Add a short lesson beat (or exam stem earlier in the room) that teaches: change on reason/breach/suspicion, not on a calendar.
- Or re-aim the free-text question at what the lesson actually taught (e.g. uniqueness vs length, or why mangling fails).
- Add accept: `shared secret`, `if it leaked`, `when reused somewhere` (if that remains in scope).
