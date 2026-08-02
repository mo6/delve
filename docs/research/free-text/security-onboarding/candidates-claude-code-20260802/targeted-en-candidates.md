# When It Is Written For You — en candidate answers

Source: `docs/research/free-text/security-onboarding/targeted-en.md`

## Candidate correct answers

1. **"The money movement"** — why this should ACCEPT: paraphrases the canonical accept entry "the transaction" using none of its exact words. Directly grounded in Grigor's line "Money moving somewhere new. Bank details changing." — the transaction *is* the money movement.
2. **"What's actually being asked for"** — why this should ACCEPT: a full-sentence paraphrase that maps onto the accept entry "the request," lifted almost verbatim in meaning from Grigor's own phrasing: "Look at what is being asked."
3. **"Verify it through another channel, like calling them"** — why this should ACCEPT: matches accept entry "verify through a second channel" with a concrete example, consistent with the lesson's "pick up the phone... walk to their desk."
4. **"Double-check via a different channel"** — why this should ACCEPT: casual-register synonym pair ("double-check" for "verify," "different channel" for "second channel"), same meaning as the accept entries.
5. **"The ask"** — why this should ACCEPT: one-word business-casual synonym for "the request" (canonical-adjacent accept entry); a non-native or informal speaker plausibly reaches for this term.
6. **"Confirm the bank details are correct by calling them directly"** — why this should ACCEPT: partial restatement of the lesson's concrete example ("Bank details changing... these are the things worth a second channel"), still correct because it names both the object (transaction detail) and the second-channel method.
7. **"Call them on a number you already have to check the transaction"** — why this should ACCEPT: full-sentence answer directly operationalizing "verify the transaction through a second channel," echoing the lesson's own instruction: "Not the number in the message, the number you already had."

## Candidate wrong answers

1. **"Their LinkedIn profile"** — why this should REJECT: a variant of the rejected concept ("your online profile," "your visibility") applied to the attacker instead of the player, but the lesson's point is that reconnaissance is not the defensible step regardless of whose profile is discussed.
2. **"How much information is available about me online"** — why this should REJECT: a paraphrase of the reject entry "how much they know about you." Flag: the offline keyword floor only does substring matching and this answer contains none of the literal reject strings, so a lenient offline check could wrongly let it through; an LLM grader should still catch it semantically.
3. **"The sender's email domain"** — why this should REJECT: a plausible-sounding guess from someone who skipped the lesson prose, but the lesson explicitly says the domain "is right, because he has the account" — checking the domain is exactly the tell that no longer works in spear phishing.
4. **"Whether the tone of the message sounds right"** — why this should REJECT: sounds related (tone is mentioned in the text) but misses the point — Grigor explicitly says "The tone is right, because he studied," meaning tone is no longer a usable signal. Flag: a lenient grader might mistake "checking tone" for a form of vigilance and accept it.
5. **"The password strength of my email account"** — why this should REJECT: this would be a plausible answer to the passphrases-room question, not this one — tests whether the grader is reading this specific question rather than pattern-matching "security" in general.
6. **"Whether the attachment is safe to open"** — why this should REJECT: correct-shaped answer for the links-and-attachments room, wrong here — cross-room contamination test; this scenario has no attachment at all.
7. **"Nothing, you can't stop spear phishing"** — why this should REJECT: off-topic/defeatist non-answer, tests the floor rather than any real ambiguity.
8. **"My privacy settings on social media"** — why this should REJECT: a common misconception the lesson explicitly warns against: "You cannot un-publish your own existence, and a job that requires you to be contactable requires you to be findable."

## Quality assessment

- Question clarity: Mostly clear, but the accept list itself blends two different kinds of valid answers — the *object* to verify ("the transaction," "the request") and the *method* of verifying it ("verify through a second channel"). The question asks "what should you actually verify," which grammatically wants an object, yet one canonical-adjacent accept entry answers with a method instead. A learner could reasonably answer either way, and the question doesn't disambiguate which is wanted.
- Lesson/question alignment: Strong. Grigor's monologue builds directly to the answer ("The transaction is left... these are the things worth a second channel"), so the lesson clearly supports the accept list's content.
- Accept-list coverage: Reasonable range, but narrow on vocabulary — it never includes "the money," "the payment," or "a phone call," even though the lesson's own concrete examples ("Money moving somewhere new," "pick up the phone") point straight at those phrasings. Under the offline keyword floor (substring matching only), an answer like "verify the money transfer" wouldn't match any accept substring despite being correct in meaning.
- Reject-list false-positive risk: Low for the three listed phrases as written; they're distinctive enough not to appear as accidental substrings inside a correct answer.
- Explanation consistency: Consistent. The explanation restates "Verify the transaction through a second channel" and explicitly dismisses reconnaissance-based answers, matching the accept/reject split exactly.

## Suggested refinements

- Add "the money," "the payment," and "a phone call" to the accept list to widen offline keyword-floor coverage, since the lesson's own concrete language points at these terms.
- Consider tightening the question to ask unambiguously for the object of verification (e.g., "what part of the message should you verify instead, in a few words?"), or explicitly keep both object- and method-style answers valid and say so in the explanation, since the current accept list already mixes both.
- Consider adding a paraphrase of the reject concept, e.g., "their online presence" or "their digital footprint," to the reject list to close the keyword-floor gap flagged in wrong-answer candidate 2.
