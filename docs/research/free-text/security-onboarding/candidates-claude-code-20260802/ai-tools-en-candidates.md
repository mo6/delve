# 🤖 What You Told The Oracle — en candidate answers

Source: `docs/research/free-text/security-onboarding/ai-tools-en.md`

## Candidate correct answers

1. **"Flag it to security"** — why this should ACCEPT: direct paraphrase of the canonical "report it," swapping the verb. The lesson's overall message ("report it... this is exactly what the next room is about") is agnostic about which verb the learner uses.
2. **"Rotate the key and let security know"** — why this should ACCEPT: matches the "rotate the credential and report it" accept entry in meaning. It uses "key" rather than "credential," but the lesson itself treats these as interchangeable ("Credentials and keys, never... A key in a prompt is a key you must now rotate").
3. **"Treat it like you'd treat any other data leak"** — why this should ACCEPT: near-direct paraphrase of "treat it like any other disclosure," substituting "data leak" for "disclosure." The explanation uses almost these exact words ("Treat it as you'd treat any other disclosure").
4. **"Change the password immediately, then tell someone about it"** — why this should ACCEPT: full-sentence, more explicit/casual version of "rotate it and tell someone," covering both halves of the combo answer.
5. **"Own up to it and let the security team handle it"** — why this should ACCEPT: uses none of the accept list's exact words but conveys reporting/disclosure to security, consistent with the explanation's reassurance that reporting "is not a room you should be afraid of."
6. **"Don't just delete it — report what happened"** — why this should ACCEPT: a partial restatement of the explanation's own reasoning (deleting the conversation isn't enough) combined with the correct action (report). This restatement of the "why" alongside the "what" should still count as correct.
7. **"Yeah, gonna ping security about that right now"** — why this should ACCEPT: casual register, correct meaning (report immediately to security) via the informal synonym "ping."
8. **"One must notify the responsible security officer without delay"** — why this should ACCEPT: formal/stilted register a non-native speaker might reach for; still means "report it."

## Candidate wrong answers

1. **"Just delete the chat history, it's fine"** — why this should REJECT: the exact misconception the lesson and explanation warn against — deletion doesn't remove the data from logs, backups, or caches, and doesn't retract a disclosure that already happened.
2. **"Only use the approved AI tool for anything sensitive next time"** — why this should REJECT: sounds related (it echoes the lesson's "know which door you're using" rule) but misses the point of the question, which asks what to do *after* the mistake, not how to prevent it next time.
3. **"Tell the AI to forget what you told it"** — why this should REJECT: a plausible guess from someone who skipped the lesson prose; directly contradicted by "Assume no delete. Model behaviour is not a filing cabinet you can open and remove one page from."
4. **"Enable two-factor authentication on the account"** — why this should REJECT: this is the correct move for the mfa room's account-takeover scenario, not this one. It doesn't address a data/credential disclosure into an AI tool at all — tests whether the grader is reading this question rather than pattern-matching nearby "account security" content.
5. **"Restart the computer"** — why this should REJECT: off-topic/nonsensical, tests the floor.
6. **"Ask the AI tool to delete your data from its training set"** — why this should REJECT, and flagged as a lenient-grader risk: sounds proactive and security-conscious, which is exactly why a lenient grader might accept it. But it's contradicted by "Assume no delete" — requesting deletion isn't a substitute for rotating a leaked credential or reporting a disclosure.
7. **"Just mention it to your manager next time you see them"** — why this should REJECT, and flagged as a lenient-grader risk: superficially resembles the accepted "tell someone," but "next time you see them" drops the urgency the whole lesson is built around, and a manager isn't the disclosure-handling channel implied by "report it."

## Quality assessment

- Question clarity: Mostly clear, but "something sensitive" spans three different lesson categories — credentials, regulated personal data, and generic confidential business content (contract, log, memo) — that the lesson treats with different required actions (rotate vs. report vs. both). The question doesn't disambiguate which kind of "sensitive" thing was pasted, yet the accept list's structure implicitly assumes the learner picks the right combo for the right case.
- Lesson/question alignment: Strong. The explanation is essentially the question restated as an answer key, and the whole lesson builds to this exact "what next" moment.
- Accept-list coverage: Reasonable for the phrasings it has, but narrow in two ways: (a) it has no entry for "rotate the credential" *alone* — reasonable if the pasted item was specifically a credential, since the explanation says "if it was a credential, rotate it now" without insisting reporting is also mandatory in that specific case — so a learner who answers only "rotate it" for a credential-focused reading of the question may be unfairly rejected; (b) it lacks common non-"report"/"rotate" synonyms (e.g. "flag it," "let security know") that a real learner might type, which would fail the offline keyword floor's substring matching even though they mean the same thing.
- Reject-list false-positive risk: Low. "delete the conversation," "delete it and move on," "remove the chat" are all tightly scoped to the deletion misconception and unlikely to appear as a substring inside a genuinely correct answer.
- Explanation consistency: Consistent. The explanation directly maps to the accept list (report / rotate+report) and directly refutes the reject list (deletion doesn't work).

## Suggested refinements

- Clarify whether "rotate the credential" alone (no explicit report) should be accepted when the question is read as being about a leaked credential specifically — either add it to the accept list, or adjust the question/lesson to make explicit that reporting is the one universal required action regardless of what was pasted, with rotation being an addition rather than a substitute.
- Broaden the accept list with a few non-"report"/"rotate" synonyms learners are likely to type (e.g. "flag it," "let security know," "loop in security") so correct-in-meaning answers don't fail the offline keyword-substring floor.
