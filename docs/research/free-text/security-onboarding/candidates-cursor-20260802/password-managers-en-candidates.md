# One Lock Worth Picking — en candidate answers

Source: `docs/research/free-text/security-onboarding/password-managers-en.md`

## Candidate correct answers

1. **"cross-device sync"** — why this should ACCEPT: Canonical accept entry; matches the explanation's browser gap.
2. **"a master passphrase"** — why this should ACCEPT: Short form of "protected by a master passphrase"; lesson emphasises one memorable vault key.
3. **"works outside the browser"** — why this should ACCEPT: Direct accept entry; apps/non-web accounts.
4. **"covers apps too"** — why this should ACCEPT: Casual paraphrase of "covers more than websites".
5. **"encrypted vault"** — why this should ACCEPT: Lesson teaches the encrypted vault vs memory; meaning-aligned even if not listed. Flag for keyword floor: may fail offline unless substring matches.
6. **"random unique passwords for every site"** — why this should ACCEPT: Core thing Ives sells; a real manager generates them. Flag: browser managers can too; grader may still accept as "manager benefit".
7. **"syncs across browsers"** — why this should ACCEPT: Accept-list idea (works across browsers / syncs across devices).
8. **"one passphrase unlocks everything else"** — why this should ACCEPT: Formal restatement of the lesson's single-secret model vs session-tied browser storage in the explanation.

## Candidate wrong answers

1. **"nothing / they're the same"** — why this should REJECT: Explicit reject; explanation says better than nothing, not identical.
2. **"it puts all eggs in one basket"** — why this should REJECT: The objection Ives rebuts; not a benefit over browsers.
3. **"you can reuse passwords safely"** — why this should REJECT: Opposite of the lesson; managers exist so you never reuse.
4. **"shorter passwords"** — why this should REJECT: Skipped-lesson guess; managers enable longer random secrets.
5. **"better than nothing"** — why this should REJECT: That phrase is the MFA/SMS lesson's accept idea, not a manager-vs-browser difference. Flag: lenient grader might accept as vaguely positive.
6. **"the transaction"** — why this should REJECT: Correct for targeted room, wrong here.
7. **"browser autofill"** — why this should REJECT: That's what browsers already give; not a differentiator.
8. **"spaghetti"** — why this should REJECT: Off-topic floor test.

## Quality assessment

- Question clarity: Clear comparison prompt, but the lesson never mentions browser-saved passwords.
- Lesson/question alignment: Poor. Lesson teaches concentrating risk into an encrypted vault and one master passphrase. Browser gaps (sync, non-web, passphrase vs session) appear only in the explanation.
- Accept-list coverage: Several plausible correct answers (encrypted vault, generates unique passwords, never type passwords) are outside the list and may fail keyword floor.
- Reject-list false-positive risk: "nothing" / "same" / "identical" are safe; low FP risk on correct answers.
- Explanation consistency: Explanation matches the accept list; lesson does not teach the comparison.

## Suggested refinements

- Add a short lesson contrast with browser-saved passwords (one browser, weaker sync, websites-only, session vs master passphrase).
- Or retarget the free-text question to what the lesson taught (e.g. why concentrating in a vault is safer than memory/reuse).
- Add accept: `encrypted vault`, `unique random passwords`, `never type them`.
