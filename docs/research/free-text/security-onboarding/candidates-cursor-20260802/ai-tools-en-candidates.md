# What You Told The Oracle — en candidate answers

Source: `docs/research/free-text/security-onboarding/ai-tools-en.md`

## Candidate correct answers

1. **"report it"** — why this should ACCEPT: Canonical accept; treat as disclosure.
2. **"rotate the credential and report it"** — why this should ACCEPT: Full accept; lesson says a key in a prompt must be rotated.
3. **"treat it like any other disclosure"** — why this should ACCEPT: Direct accept entry.
4. **"tell security and change the secret"** — why this should ACCEPT: Casual paraphrase of rotate + report.
5. **"assume it left and escalate"** — why this should ACCEPT: Meaning from "assume no delete" + report path without accept words. Flag: keyword floor may miss.
6. **"rotate it now"** — why this should ACCEPT: Partial but correct when the paste was a credential; accept list includes rotate variants. Flag: incomplete if the paste was only personal data (report still needed).
7. **"notify the right people"** — why this should ACCEPT: Informal report; should count.
8. **"report it; deleting the chat is not enough"** — why this should ACCEPT: Correct and explicitly rejects the common wrong fix; meaning-aligned.

## Candidate wrong answers

1. **"delete the conversation"** — why this should REJECT: Explicit reject; lesson "assume no delete".
2. **"delete it and move on"** — why this should REJECT: Reject-list.
3. **"remove the chat"** — why this should REJECT: Reject-list.
4. **"ask the AI to forget it"** — why this should REJECT: Same misconception in new clothes; not on reject list. Flag: LLM should still reject.
5. **"never use AI again"** — why this should REJECT: Oracle says refusing tools is not security; wrong remediation.
6. **"hand it to security" (USB sense only)** — why this should REJECT if meaning physical drive; but "report to security" should ACCEPT. Wording matters. Flag: ambiguous.
7. **"was I expecting this"** — why this should REJECT: Attachments-room answer; wrong here.
8. **"clear browser cache"** — why this should REJECT: Off-point floor / wrong mental model of where the data went.

## Quality assessment

- Question clarity: Clear accidental-paste scenario.
- Lesson/question alignment: Partial. Lesson teaches rotate credentials and assume no delete; "report it" / "treat as disclosure" is strongest in the explanation (and points at the next room).
- Accept-list coverage: Good for report/rotate. May miss `tell someone`, `escalate`, `assume it's gone`.
- Reject-list false-positive risk: Watch `"don't delete the conversation, report it"` containing reject substring `delete the conversation`.
- Explanation consistency: Matches accept list; lesson under-teaches reporting for non-credential sensitive pastes.

## Suggested refinements

- Add lesson sentence: accidental sensitive paste is a disclosure; report it; if a credential, rotate first.
- Add accept: `tell someone`, `escalate`, `assume it cannot be deleted`.
- Tighten reject phrases so negations of "delete the chat" don't false-fail.
