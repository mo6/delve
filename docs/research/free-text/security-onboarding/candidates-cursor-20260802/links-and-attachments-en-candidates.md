# Links, Attachments, and the Space Between — en candidate answers

Source: `docs/research/free-text/security-onboarding/links-and-attachments-en.md`

## Candidate correct answers

1. **"was I expecting this"** — why this should ACCEPT: Canonical accept entry and the Postmaster's exact "better question".
2. **"did I expect this attachment"** — why this should ACCEPT: Full-sentence paraphrase of the same question.
3. **"expected?"** — why this should ACCEPT: Ultra-short form; still the expect-check the lesson teaches.
4. **"was this something I asked for"** — why this should ACCEPT: Meaning-aligned without accept-list words; expectation framed as prior request.
5. **"am I waiting for this file"** — why this should ACCEPT: Casual register of the same expect-check.
6. **"check if it was anticipated"** — why this should ACCEPT: Formal synonym; same judgment the lesson wants.
7. **"if unexpected, ask first"** — why this should ACCEPT: Partial restatement of "Unexpected: ask"; should still count as naming the expect rule.
8. **"was this on my radar"** — why this should ACCEPT: Informal synonym a non-native or casual learner might use for expectation.

## Candidate wrong answers

1. **"is the filename safe"** — why this should REJECT: Exact wrong question the Postmaster rejects; filename is a claim.
2. **"does the extension look right"** — why this should REJECT: Same misconception; extensions/names are sender-written.
3. **"hover the link"** — why this should REJECT: Related lesson content about links, but not the attachment decision rule. Flag: lenient grader might accept as "checking something".
4. **"scan it with antivirus"** — why this should REJECT: Sounds security-aware but the lesson says you cannot know safety that way.
5. **"the transaction"** — why this should REJECT: Correct for the targeted/spear-phishing room, wrong here.
6. **"read the domain from the right"** — why this should REJECT: Correct for link inspection in this same lesson, but not the attachment question asked.
7. **"open it if it looks official"** — why this should REJECT: Skipped-lesson guess; appearance is what attackers forge.
8. **"banana"** — why this should REJECT: Off-topic floor test.

## Quality assessment

- Question clarity: Slightly awkward: it already says "unexpected attachment", then asks for the question that decides whether to open it; a careful reader may say "ask the sender" instead of "was I expecting this".
- Lesson/question alignment: The lesson's better question is clearly "Was I expecting this?"; alignment is good if the learner quotes that. The explanation, however, talks about filename tricks and barely restates the expect-check.
- Accept-list coverage: Narrow around "expect*" forms. Keyword floor may miss `ask first`, `was I waiting for this`, `did I request this`.
- Reject-list false-positive risk: Empty reject list; no false-positive risk, but also no keyword floor for common wrong answers like "filename" / "safe to open".
- Explanation consistency: Weak. Explanation focuses on filename-as-claim, which supports the "regardless of filename" clause, not the expect-question itself.

## Suggested refinements

- Reword the prompt to avoid embedding "unexpected": e.g. "what's the one question that tells you whether to open an attachment, regardless of what its filename claims?"
- Add accept: `ask first`, `did I request this`, `was I waiting for this`.
- Add reject: `is it safe`, `check the filename`, `trust the extension`.
- Align explanation to restate "Was I expecting this?" before the filename aside.
