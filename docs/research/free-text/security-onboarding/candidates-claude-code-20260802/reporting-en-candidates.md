# 🚨 The Last Door — en candidate answers

Source: `docs/research/free-text/security-onboarding/reporting-en.md`

## Candidate correct answers

1. **"Loop in security straight away"** — why this should ACCEPT: full-sentence paraphrase of the canonical "report it," swapping in "loop in" for "report" while keeping the urgency.
2. **"Let the security team know now, even if it turns out to be nothing"** — why this should ACCEPT: directly grounded in "Report before you're sure. 'I think I might have...' is a complete report" from the lesson prose — this candidate restates that permission-to-be-unsure alongside the core action.
3. **"Flag it"** — why this should ACCEPT: a shorter two-word paraphrase of the canonical answer, using the verb "flag" (already validated by the accept list's "flag it to security right away") without the extra urgency qualifier.
4. **"Report it, don't wait to be sure"** — why this should ACCEPT: combines the core accepted action with a partial restatement of the "report before you're sure" reasoning from the lesson.
5. **"Send it to the security desk immediately"** — why this should ACCEPT: uses none of the accept list's exact words ("report," "flag") but clearly conveys prompt escalation to security.
6. **"Yeah, I'd just ping IT about it right now"** — why this should ACCEPT: casual register, correct meaning (report immediately) via the informal synonym "ping."
7. **"One should notify the security department without delay upon observing this"** — why this should ACCEPT: formal/stilted register a non-native speaker might reach for; still means "report it now."
8. **"Better to raise a false alarm than stay quiet about it"** — why this should ACCEPT: a partial restatement of the reasoning ("they would vastly rather examine ten false alarms... than hear about the real one next week") that implies the correct action (report/raise it) without using the literal verb "report." The spirit of the answer is unambiguous even though it's indirect.

## Candidate wrong answers

1. **"Ask them if they sent it before reporting"** — why this should REJECT: a hybrid of the warned-against instinct and the correct action — but the delay and the risk of messaging the attacker directly remain, exactly what the explanation calls out ("if the account is compromised, you may be messaging the attacker, and you've spent an hour").
2. **"Change your own password just to be safe"** — why this should REJECT: sounds related to account security generally, but misses the point — the vulnerable account is the colleague's, not the learner's; this doesn't address the actual risk described.
3. **"Reply and ask what they meant"** — why this should REJECT: a plausible guess from someone reacting to a weird message without having internalized the lesson; directly wrong per the explanation's warning about possibly messaging the attacker.
4. **"Rotate the credential and report it"** — why this should REJECT: this is the canonical combo answer from the ai-tools room (pasting a credential into an AI tool), not this scenario. There's no credential mentioned here — a colleague's account is behaving oddly. This tests whether the grader is reading this specific question rather than pattern-matching a nearby "report + fix" shape from another room.
5. **"Buy them a coffee to smooth things over"** — why this should REJECT: off-topic/nonsensical, tests the floor.
6. **"Mention it to them privately so they're not embarrassed"** — why this should REJECT, and flagged as a lenient-grader risk: this mirrors the question's own framing ("raising it might embarrass them") and sounds considerate, but it's exactly the "ask them first" instinct the explanation warns against, just reworded as tact rather than curiosity. A lenient grader focused on "did they take some action" might wrongly accept it.
7. **"Keep an eye on it for a day or two before deciding"** — why this should REJECT, and flagged as a lenient-grader risk: sounds measured and responsible, but is "wait and see" wearing a more reasonable-sounding coat. It directly contradicts "Speed is the entire game" and the dwell-time argument in the lesson.

## Quality assessment

- Question clarity: Clear. The scenario (odd messages, "probably nothing," embarrassment risk) is specifically engineered to bait the exact wrong instincts the lesson warns about, and the ask ("what should you do?") is unambiguous.
- Lesson/question alignment: Strong — the question is a near-literal instantiation of "Report anything odd, not just your own mistakes. A colleague's strange message" from the lesson prose, and the explanation directly extends the lesson's account-takeover framing.
- Accept-list coverage: The five accept entries are all close variants built from "report"/"flag" plus an urgency word. This covers the most likely phrasings but is narrow in vocabulary — it has no entry using words like "let security know," "escalate it," or "loop in security," which are natural things a learner might type and would fail the offline keyword-substring floor despite being correct in meaning.
- Reject-list false-positive risk: Low for the four listed phrases ("ask them first," "wait and see," "do nothing," "ignore it") — none are likely to appear as a substring inside a genuinely correct answer. However, the reject list has a coverage gap on the other side: it doesn't include the more realistic near-miss phrasings identified above ("mention it privately," "keep an eye on it for a day"), which are the actual failure mode the lesson is written to warn against, and which the offline floor currently has no way to catch since they don't match any reject phrase either.
- Explanation consistency: Consistent — the explanation directly refutes "ask them first" and "wait and see" and reinforces the urgency behind "report it," matching the accept/reject lists well.

## Suggested refinements

- Broaden the accept list with non-"report"/"flag" synonyms learners are likely to type (e.g. "let security know," "escalate it," "loop in security") to reduce offline keyword-floor false negatives.
- Broaden the reject list to include the more realistic "kind but wrong" near-misses this analysis surfaced (discreetly asking/mentioning it to the colleague, observing for a day before acting) — these are closer to what the lesson is actually trying to prevent than the blunter "do nothing"/"ignore it" phrasings already listed.
- No change needed to the question wording or lesson prose itself; they support one clear, well-defended correct answer.
