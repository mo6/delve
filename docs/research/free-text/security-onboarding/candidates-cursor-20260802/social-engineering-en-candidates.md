# The Attack That Is Just A Conversation — en candidate answers

Source: `docs/research/free-text/security-onboarding/social-engineering-en.md`

## Candidate correct answers

1. **"asking for a password is the tell"** — why this should ACCEPT: Canonical idea; the request itself disqualifies.
2. **"real support never asks for your password"** — why this should ACCEPT: Direct accept entry.
3. **"no legitimate support needs your password"** — why this should ACCEPT: Canonical accept entry.
4. **"they never need your password"** — why this should ACCEPT: Short accept form.
5. **"the password request itself"** — why this should ACCEPT: Paraphrase of "the request itself is the tell".
6. **"support has its own access paths"** — why this should ACCEPT: Explanation reason without accept-list words; meaning-correct. Flag: keyword floor may miss.
7. **"passwords are never shared with IT"** — why this should ACCEPT: Casual policy phrasing of the same rule.
8. **"that ask is never legitimate"** — why this should ACCEPT: Formal restatement; self-invalidating request.

## Candidate wrong answers

1. **"it was unsolicited"** — why this should REJECT: Explicit reject; contextual signal, not the one certain tell.
2. **"they created urgency"** — why this should REJECT: Reject; real but contextual.
3. **"IT should have access already"** — why this should REJECT: Reject; adjacent intuition, not the taught tell.
4. **"caller ID looked wrong"** — why this should REJECT: Lesson says caller ID is a suggestion; not the disqualifying tell. Flag: lenient grader may accept as "a tell".
5. **"verify through a second channel"** — why this should REJECT: Correct general defence from this lesson, but not the *one tell* that the password ask is illegitimate regardless of context. Flag: high false-ACCEPT risk.
6. **"they held a door / tailgating"** — why this should REJECT: Other social-engineering shape from this room, wrong object.
7. **"better than nothing"** — why this should REJECT: MFA answer; wrong here.
8. **"because they were polite"** — why this should REJECT: Off-point; helpfulness is the attack surface, not the tell.

## Quality assessment

- Question clarity: Slightly heavy ("one tell… regardless of surrounding context") but points at the self-invalidating request.
- Lesson/question alignment: Good enough. Pretexting example includes IT asking to confirm a password; explanation crystallises "nobody legitimate needs your password".
- Accept-list coverage: Strong around the password-ask. May miss `own access paths`, `never share passwords with support`.
- Reject-list false-positive risk: Low for the listed rejects. Bigger issue is false ACCEPT of "second channel" / "hang up and call IT".
- Explanation consistency: Consistent and sharper than the lesson's brief example.

## Suggested refinements

- Add reject: `second channel`, `hang up and call`, `caller ID` (correct nearby answers that miss "the request itself").
- Add accept: `support has its own access`, `never share your password`.
- Optional lesson sentence stating the rule in one line before the defence paragraph.
