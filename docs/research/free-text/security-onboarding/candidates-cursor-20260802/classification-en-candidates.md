# Knowing What You're Holding — en candidate answers

Source: `docs/research/free-text/security-onboarding/classification-en.md`

## Candidate correct answers

1. **"ask someone"** — why this should ACCEPT: Canonical accept entry; matches the explanation's default.
2. **"ask the data owner"** — why this should ACCEPT: Direct accept entry.
3. **"handle it carefully and ask"** — why this should ACCEPT: Full accept phrase from list and explanation.
4. **"check with whoever owns the data"** — why this should ACCEPT: Accept-list paraphrase.
5. **"ask a colleague who knows"** — why this should ACCEPT: Casual form of asking someone; meaning-aligned.
6. **"get a second opinion on the tier"** — why this should ACCEPT: Informal synonym for asking rather than defaulting high.
7. **"ask what someone could do with it"** — why this should ACCEPT: Lesson's real diagnostic question; partial but defensible as the unsure-path. Flag: may not match keyword accept list.
8. **"consult the information owner"** — why this should ACCEPT: Formal register of data-owner ask.

## Candidate wrong answers

1. **"mark it restricted"** — why this should REJECT: Explicit reject; over-classification the lesson warns against.
2. **"use the highest label"** — why this should REJECT: Exact reject and what the question says "instead of".
3. **"default to confidential"** — why this should REJECT: Same over-classification habit with a different tier name. Flag: not on reject list; keyword floor may miss it.
4. **"what could someone do with this"** — why this should REJECT as a *complete* answer to *this* prompt? Actually borderline: it's the lesson's classification question, not the "when unsure" procedure. Flag: lenient grader may ACCEPT; intended path is ask, not only self-diagnose.
5. **"make everything public"** — why this should REJECT: Opposite under-classification error.
6. **"better than nothing"** — why this should REJECT: MFA room answer; wrong here.
7. **"hand it to security"** — why this should REJECT: Devices-room USB answer; wrong here.
8. **"classify as banana"** — why this should REJECT: Off-topic floor test.

## Quality assessment

- Question clarity: Clear anti-overclassification prompt.
- Lesson/question alignment: Partial. Lesson strongly teaches why over-classification fails and "what could someone do with this?", but never says "ask the data owner when unsure". That procedure lives in the explanation.
- Accept-list coverage: Narrow around "ask". A careful reader answering only with Marisol's diagnostic question may fail keyword floor.
- Reject-list false-positive risk: "restricted" / "highest label" are safe. Risk: an answer like "ask before marking restricted" contains reject substrings; keyword reject could false-positive. Flag that.
- Explanation consistency: Matches accept list; ahead of the lesson.

## Suggested refinements

- Add one lesson sentence: when unsure, handle carefully and ask the data owner (don't default to the top tier).
- Add accept: `ask a colleague`, `don't guess the label`.
- Soften or remove bare `restricted` reject if substring matching can catch "don't mark it restricted" style corrects; prefer phrases that only match affirmative over-classification.
