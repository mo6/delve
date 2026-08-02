# 📄 Knowing What You're Holding — en candidate answers

Source: `docs/research/free-text/security-onboarding/classification-en.md`

## Candidate correct answers

1. **"Check with the person responsible for the data"** — why this should ACCEPT: paraphrase of "ask the data owner" / "check with whoever owns the data."
2. **"Just ask"** — why this should ACCEPT: terse two-word paraphrase of the canonical "ask someone."
3. **"Reach out to whoever's in charge of that information"** — why this should ACCEPT: casual-register paraphrase of "ask whoever owns it."
4. **"Treat it cautiously in the meantime and check with someone who'd know"** — why this should ACCEPT: partial restatement combining "handle it carefully" with "ask" — matches "handle it carefully and ask" without repeating its wording.
5. **"Escalate the question to the data's owner rather than guessing"** — why this should ACCEPT: formal-register paraphrase of "ask the data owner," explicitly contrasting with guessing.
6. **"Confirm with your manager or the relevant team"** — why this should ACCEPT: a plausible generic-authority answer. It doesn't name "the data owner" specifically, but it's a legitimate instance of the broad canonical answer "ask someone," which doesn't require the asked party to be the formal data owner.
7. **"Don't guess — flag it and get clarification from someone who knows"** — why this should ACCEPT: full-sentence version combining the "don't default" framing with "ask."
8. **"Verify with the responsible party"** — why this should ACCEPT: a slightly formal, non-native-speaker-style synonym for "ask the data owner" — plausible phrasing from someone reaching for a more formal register than the accept list uses.

## Candidate wrong answers

1. **"Mark it as restricted to be safe"** — why this should REJECT: this is the exact misconception the room is built to correct — over-classification "feels responsible. It is not." Matches the reject list closely, just phrased as a first-person action rather than a bare instruction.
2. **"Leave it unclassified until someone tells you"** — why this should REJECT: sounds related (defers the decision) but misses the point — the lesson's actual instruction is to proactively ask, not to passively wait. Flag: a lenient grader might mistake this for "ask someone" because both involve not personally deciding the tier, but this answer contains no active step to actually resolve the uncertainty.
3. **"Use your best judgment based on the four tiers"** — why this should REJECT: a plausible-sounding guess from someone who remembers the classification table but skipped the room's actual point — that the resolving move is to ask, not to self-judge from the table.
4. **"Deny it, then go change your password"** — why this should REJECT: this is the correct answer to the *MFA* room's unsolicited-push-prompt scenario, not to this room's classification-uncertainty question. Tests whether the grader is reading this specific question rather than any nearby "what should you do" advice from the pack.
5. **"Classify it based on what could happen if it leaked"** — why this should REJECT under the current accept list, but flagged below as a genuine ambiguity: this restates the lesson's own closing reasoning — "the question isn't 'what tier is this document,' it's 'what could someone do with this?' Answer that honestly and the tier usually answers itself" — rather than the explanation's literal instruction to ask someone. It is well-grounded in the room's own prose, which is exactly why a careful, lesson-literate grader (or learner) might mistakenly treat it as correct. See quality assessment.
6. **"Put it in the shredder"** — why this should REJECT: nonsensical, off-topic; tests the floor rather than any real ambiguity.
7. **"Escalate it to restricted by default until proven otherwise"** — why this should REJECT: restates the over-classification bias the room explicitly warns against, dressed up as caution.

## Quality assessment

- **Question clarity**: Reasonably clear — the question specifically frames the "unsure" case and contrasts it with "defaulting to the highest label," which narrows the intended answer space.
- **Lesson/question alignment**: This is the substantive finding for this room. There is a real tension between two things the lesson teaches: the post-answer explanation says the actual default when unsure is to "handle it carefully and ask someone," but the lesson prose's own closing line teaches a *different* resolving mechanism — self-assessment via "what could someone do with this? Answer that honestly and the tier usually answers itself." A learner who reads the lesson prose carefully, rather than skipping to the explanation, could reasonably conclude the taught answer is "reason about potential impact yourself," not "ask someone" — and that answer isn't in the accept list. Candidate 5 above is a direct test of this ambiguity.
- **Accept-list coverage**: Decent coverage of "ask" phrasings, but given the tension above, it has a genuine gap: no accept entry captures the "assess what someone could do with it" reasoning that the lesson's own final line presents as the resolving question.
- **Reject-list false-positive risk**: Concrete risk here. The reject entry "default to restricted" is a short, generic phrase that can appear as a literal substring inside an explicitly correct answer that contrasts itself with the wrong behavior — e.g., *"Don't default to restricted, ask the data owner instead"* contains the exact substring "default to restricted" and would fail an offline keyword floor despite being a fully correct answer.
- **Explanation consistency**: The post-answer explanation is internally consistent with the accept list ("the actual default when unsure: handle it carefully and ask someone"), but as noted above, it's in tension with the lesson prose's own closing framing, which points toward self-assessment of impact rather than asking.

## Suggested refinements

- Either add an accept entry bridging the two framings (e.g., "assess the impact and ask" or "figure out what someone could do with it, then check with the owner"), or adjust the lesson's closing line so it doesn't read as a competing, self-sufficient resolution method to "ask someone."
- For the reject list, reword "default to restricted" to a phrase less likely to appear as a substring inside a correct, contrastive answer (e.g., "defaults to restricted without asking"), or flag this reject entry as one that should rely on the LLM grader layer rather than the offline substring floor.
- No other changes needed beyond the two above.
