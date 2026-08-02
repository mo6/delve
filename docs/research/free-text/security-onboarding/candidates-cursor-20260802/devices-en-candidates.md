# The Thing You Carry — en candidate answers

Source: `docs/research/free-text/security-onboarding/devices-en.md`

## Candidate correct answers

1. **"hand it to security"** — why this should ACCEPT: Canonical accept; explanation's correct disposal path.
2. **"don't plug it in"** — why this should ACCEPT: Direct accept and the lesson's dull rule ("it doesn't go in").
3. **"report it to security"** — why this should ACCEPT: Accept-list; same as handing it in via a channel.
4. **"give it to IT / security team"** — why this should ACCEPT: Casual synonym of hand to security.
5. **"turn it in at reception"** — why this should ACCEPT: Plausible org variant of handing it in; meaning-aligned. Flag: keyword floor may miss without "security".
6. **"leave it alone and tell someone"** — why this should ACCEPT: Combines don't-use with escalation; should count.
7. **"do not connect it to anything"** — why this should ACCEPT: Formal restatement of don't plug it in.
8. **"take it to #security-help"** — why this should ACCEPT: Pack placeholder channel; same as report/hand in.

## Candidate wrong answers

1. **"plug it into an isolated machine"** — why this should REJECT: Explicit reject; explanation's trap for technical people.
2. **"check the filenames"** — why this should REJECT: Reject; filenames are bait.
3. **"leave it there"** — why this should REJECT: Reject; next person is the drop's purpose.
4. **"ignore it"** — why this should REJECT: Reject-list.
5. **"open it on a burner phone"** — why this should REJECT: Same isolated-machine misconception in new clothes. Flag: not on reject list; LLM may still reject.
6. **"format it and reuse it"** — why this should REJECT: Skipped-lesson greed; still plugging/handling as usable media.
7. **"was I expecting this"** — why this should REJECT: Links/attachments answer; wrong here.
8. **"put it in your bag for later"** — why this should REJECT: Passive possession without reporting; close to leave/ignore.

## Quality assessment

- Question clarity: Unambiguous scenario and ask.
- Lesson/question alignment: Partial. Lesson teaches "if you don't know where it came from, it doesn't go in" but not "hand it to security". Handing in / reporting is stronger in the explanation (and reject list).
- Accept-list coverage: "don't plug it in" is lesson-backed; "hand it to security" may be narrow for orgs that say facilities/reception/IT.
- Reject-list false-positive risk: Low. Watch for "don't plug it into an isolated machine" containing reject substring `plug it into an isolated machine`.
- Explanation consistency: Matches accept/reject; ahead of the lesson on escalation.

## Suggested refinements

- Add lesson beat: don't plug it in; hand it to security (or your org's channel).
- Add accept: `give it to IT`, `report it`, `don't connect it`.
- Prefer reject phrases that won't substring-match negations of the trap.
