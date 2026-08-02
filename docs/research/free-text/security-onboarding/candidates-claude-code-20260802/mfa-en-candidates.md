# 📱 The Second Factor — en candidate answers

Source: `docs/research/free-text/security-onboarding/mfa-en.md`

## Candidate correct answers

1. **"It blocks random attackers, just not someone specifically targeting me"** — why this should ACCEPT: paraphrases "it stops most attacks" / "still stops scale attacks" using the lesson's own distinction between scale attackers and targeted ones.
2. **"Still better than having no second factor at all"** — why this should ACCEPT: a fuller paraphrase of the canonical "better than nothing" that spells out what "nothing" means here.
3. **"It blocks the vast majority of automated attacks"** — why this should ACCEPT: paraphrase of "it blocks most attackers" / "still stops scale attacks."
4. **"Most attackers aren't specifically after you, so SMS is enough to stop them"** — why this should ACCEPT: a full-sentence paraphrase directly grounded in the lesson's own line, "every attacker working at scale who isn't specifically interested in you."
5. **"It's not perfect, but it beats having no MFA at all"** — why this should ACCEPT: casual-register paraphrase of "better than nothing."
6. **"It defends against credential stuffing"** — why this should ACCEPT: a partial restatement of "it stops credential stuffing and bulk phishing" — names only one of the two named attack types, but that partial restatement is still a correct, on-topic reason.
7. **"It's better than relying on a password alone"** — why this should ACCEPT: partial paraphrase; correctly identifies that SMS MFA improves on single-factor auth even if weak as a second factor.
8. **"Although imperfect, SMS verification still thwarts the majority of automated, non-targeted attack attempts."** — why this should ACCEPT: formal-register, full-sentence version of "it stops most attacks" / "still stops scale attacks."

## Candidate wrong answers

1. **"It's worthless against sophisticated attackers"** — why this should REJECT: doesn't answer *why you should enable it*; it only restates the room's own admission that SMS is weak against targeted attacks, without the "but still useful at scale" half. Flag: this is close in spirit to the reject entry "it's worthless" but adds a qualifier ("against sophisticated attackers") that makes it a *true* statement about SMS's limits — the grader has to recognize it still fails to answer the question, not just pattern-match the word "worthless."
2. **"SIM swapping makes it insecure so don't bother"** — why this should REJECT: combines a real fact from the lesson (SIM swapping is a genuine SMS weakness) with the literal reject phrase "don't bother" — demonstrates the exact misconception the room is written to head off (weakest ≠ worthless).
3. **"It's the strongest form of MFA"** — why this should REJECT: directly contradicted by the room's own ranking table, which places SMS as "Weak, but real" beneath authenticator apps and passkeys.
4. **"Because a prompt you didn't request means an attack is happening"** — why this should REJECT: this is the correct answer to a *different* implicit question in this same room (how to respond to an unsolicited MFA push), not to why SMS-based MFA is still worth enabling. Tests whether the grader is reading this specific question rather than any MFA-adjacent fact from the room.
5. **"Passkeys are the best because they're cryptographically bound to the real site"** — why this should REJECT: true and lesson-grounded, but about passkeys, not about why SMS specifically is worth keeping on. Off-topic for this question.
6. **"You should enable it because it uses your phone number to verify who you are"** — why this should REJECT: describes SMS MFA's *mechanism*, not the reasoning the question asks for (why keep the weakest option enabled). Sounds related but misses the point.
7. **"Because carrier pigeons are slower"** — why this should REJECT: nonsensical, off-topic; tests the floor rather than any real ambiguity.
8. **"Enable it because SMS can't be intercepted"** — why this should REJECT: a misconception directly refuted by the lesson, which explicitly says SMS is "Vulnerable to SIM swapping and interception."

## Quality assessment

- **Question clarity**: Clear. "Why should you still enable SMS-based MFA even though it's the weakest option?" unambiguously asks for a justification, not a mechanism or a ranking.
- **Lesson/question alignment**: Strong — unlike the password-managers room, this room's pre-question table and prose already state the answer directly: "Weak, but real... Better than nothing; use it if it's all there is." A learner who reads the table carefully has a clear textual basis for the expected answer.
- **Accept-list coverage**: Good coverage of the "stops most/scale/non-targeted attacks" framing. A minor gap: no accept entry captures the simpler "better than only a password" framing (candidate 7), though this is arguably subsumed by "better than nothing."
- **Reject-list false-positive risk**: Low. The reject phrases ("it's worthless," "don't bother," "it's not worth using," "it should be disabled") are distinctive, multi-word phrases unlikely to appear as accidental substrings inside a genuinely correct answer.
- **Explanation consistency**: Consistent — the post-answer explanation ("SMS MFA still stops credential stuffing, bulk phishing, and every attacker working at scale who isn't specifically interested in you") matches the accept list closely and reinforces rather than contradicts the pre-question table.

## Suggested refinements

- No changes suggested; the question and lesson support one clear answer, and the pre-question prose (unlike some other rooms in this pack) already teaches the fact the question tests, rather than revealing it only afterward.
- Optional, low-priority: add "better than just a password" to the accept list to explicitly cover candidate 7's framing, though it is already reasonably subsumed by "better than nothing."
