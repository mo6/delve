# The Last Door — en candidate answers

Source: `docs/research/free-text/security-onboarding/reporting-en.md`

## Candidate correct answers

1. **"report it"** — why this should ACCEPT: Canonical; Wren's whole lesson.
2. **"report it immediately"** — why this should ACCEPT: Direct accept; speed is the game.
3. **"flag it to security right away"** — why this should ACCEPT: Accept-list phrasing.
4. **"tell security now"** — why this should ACCEPT: Casual synonym of report immediately.
5. **"raise it even if you're unsure"** — why this should ACCEPT: Lesson: report before you're sure; "I think I might have…" is enough. Flag: keyword floor may miss without "report".
6. **"don't wait, report the odd messages"** — why this should ACCEPT: Explicitly rejects wait-and-see; meaning-aligned.
7. **"send it to #security-help"** — why this should ACCEPT: Pack placeholder channel; same as report.
8. **"report it; the colleague is the victim"** — why this should ACCEPT: Full-sentence with explanation's framing; still the right action.

## Candidate wrong answers

1. **"ask them first"** — why this should REJECT: Explicit reject; explanation says you may be messaging the attacker.
2. **"wait and see"** — why this should REJECT: Reject; donates dwell time.
3. **"do nothing / ignore it"** — why this should REJECT: Reject-list.
4. **"investigate whether it's really malicious"** — why this should REJECT: Lesson: do not investigate first. Flag: not on reject list; high false-ACCEPT risk if grader hears diligence.
5. **"mention it casually next time you see them"** — why this should REJECT: Soft form of ask-them-first / delay.
6. **"delete the conversation"** — why this should REJECT: AI-tools wrong answer; wrong here too.
7. **"rotate your own password"** — why this should REJECT: Adjacent remediation, not what to do about *their* odd messages.
8. **"assume it's fine"** — why this should REJECT: Off-point / the silence Wren warns against.

## Quality assessment

- Question clarity: Excellent; builds the embarrassment temptation into the stem.
- Lesson/question alignment: Strong. Lesson teaches report odd things (including a colleague's strange message), report before sure, no blame, speed.
- Accept-list coverage: Narrow around "report*". May miss `tell security`, `flag it`, `raise it` under keyword floor.
- Reject-list false-positive risk: Low for ask/wait/ignore. Possible FP if someone writes "don't ask them first, report it" and `ask them first` substring-matches.
- Explanation consistency: Consistent; account-takeover framing matches accept.

## Suggested refinements

- Add accept: `tell security`, `raise it`, `report even if unsure`.
- Add reject: `investigate first`, `confirm with them`, `mention it later`.
- Minor: reject phrases that only match affirmative delay/ask behaviour, not negations.
- Overall: one of the stronger question/lesson pairs; no major rewrite needed.
