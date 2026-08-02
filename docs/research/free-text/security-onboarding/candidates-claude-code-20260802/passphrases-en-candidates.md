# Length Beats Cleverness — en candidate answers

Source: `docs/research/free-text/security-onboarding/passphrases-en.md`

## Candidate correct answers

1. **"Only if it's been compromised"** — why this should ACCEPT: paraphrases the canonical accept entries "when there's a reason"/"when compromised" together; a compact restatement of the same idea.
2. **"If I think someone else knows it"** — why this should ACCEPT: full-sentence answer using none of the accept list's exact words, but conveys "if there's a suspicion" / "on suspicion of compromise," grounded in the explanation's mention of "a shared secret."
3. **"After my company got breached"** — why this should ACCEPT: casual-register paraphrase of "after a breach," directly grounded in the lesson's "When one of those sites is breached... the attacker takes your magnificent passphrase and tries it everywhere else you exist."
4. **"When there's an actual reason to, like a leak"** — why this should ACCEPT: partial restatement combining the canonical accept phrase "when there's a reason" with the explanation's specific example "a breach"/"a leak."
5. **"As needed"** — why this should ACCEPT: two-word idiomatic English answer meaning "when there's a reason," in a more casual/business-idiom register than the accept list's phrasing.
6. **"If I accidentally shared it with someone"** — why this should ACCEPT: grounded in the explanation's own list of triggers, which names "a shared secret" as a valid reason to change a password — this is a concrete instance of that trigger.
7. **"Not routinely, only when something's actually wrong"** — why this should ACCEPT: a full sentence that explicitly negates the fixed-schedule misconception while affirming the correct concept ("when there's a reason"), a partial restatement of the lesson's own contrast between routine expiry and reason-based change.

## Candidate wrong answers

1. **"Once every quarter"** — why this should REJECT: the same fixed-schedule misconception as reject entries "every 90 days"/"every three months," phrased differently; a common misconception the lesson explicitly warns against.
2. **"Every month, to be safe"** — why this should REJECT: a routine/fixed-schedule misconception with a cadence not literally present in the reject list. Flag: the offline keyword floor (substring matching only) would not catch this, since it contains none of the listed reject strings — a genuine keyword-floor gap.
3. **"Whenever the system forces me to"** — why this should REJECT: a plausible-sounding guess from someone who skipped the lesson prose; describes reactive-to-policy behavior rather than a real trigger, and the lesson explicitly criticizes being "forced to change constantly," calling out the weaker passwords this produces.
4. **"Never, passphrases don't need to change"** — why this should REJECT: sounds related but overcorrects into a different wrong extreme; the lesson does list valid reasons to change (breach, suspicion, shared secret), so "never" misses that nuance entirely.
5. **"When it's long enough"** — why this should REJECT: this would be a plausible answer to a *different* question about this same passphrase — its length/entropy — but this question is about timing/trigger for change, not passphrase strength. Tests whether the grader is reading this specific question rather than pattern-matching "passphrase quality" in general.
6. **"Use a password manager"** — why this should REJECT: a correct-shaped answer for the password-managers room elsewhere in this pack, wrong here — cross-room contamination test.
7. **"Whenever I feel like it"** — why this should REJECT: off-topic/flippant non-answer, tests the floor rather than any genuine ambiguity.

## Quality assessment

- Question clarity: Clear and well-scoped — "if not on a fixed schedule" preempts the single most common wrong answer (routine expiry) right in the question itself.
- Lesson/question alignment: Weak. The "a reason, a breach, a suspicion, a shared secret" phrasing that maps onto the accept list is not in the lesson — it's in the post-answer Explanation. The "What the player sees" prose (entropy, complexity vs. cleverness, uniqueness, credential stuffing) never once states *when* to change a passphrase; it only argues that long+unique beats clever mangling. A learner who read only the lesson has no textual basis in it for the accept list's answer and would be relying on prior knowledge, not what this room taught.
- Accept-list coverage: Reasonable but incomplete: the explanation names "a shared secret" as an explicit trigger, yet no accept entry captures it (e.g., "I told someone else the password" would currently have nothing to match against under the keyword floor). Idiomatic phrasings like "as needed" or "if something's wrong" also use none of the accept list's substrings and would fail the offline keyword floor despite being correct.
- Reject-list false-positive risk: Low for the phrases as written, but there's a coverage gap in the other direction — the reject list only anchors on "90 days"/"three months"/"routinely"/"fixed schedule." A wrong answer using a different cadence ("every month," "once a quarter," "annually") slips past the offline floor entirely and relies solely on the LLM grader, as shown in wrong-answer candidates 1 and 2.
- Explanation consistency: Consistent, and actually richer than the accept list — it names "a shared secret" as a trigger that has no corresponding accept-list entry.

## Suggested refinements

- Add "a shared secret" / "if I shared it with someone" to the accept list, since the explanation explicitly names this trigger but no accept entry currently captures it.
- Add a few more cadence variants to the reject list (e.g., "every month," "once a year," "annually") to close the keyword-floor gap identified in wrong-answer candidates 1 and 2.
- Add a short lesson beat, before the question, that actually teaches reason-based change (breach, suspicion, shared secret) — right now that content only exists in the post-answer explanation, so the lesson never supports the accept list it's paired with. Alternatively, re-aim the question at what the lesson does teach (e.g. why mangling fails, or length vs. uniqueness), since the wording itself is fine — it's the lesson/question pairing that's the gap, not the phrasing.
