# 🔐 One Lock Worth Picking — en candidate answers

Source: `docs/research/free-text/security-onboarding/password-managers-en.md`

## Candidate correct answers

1. **"It works on my phone too, not just in Chrome"** — why this should ACCEPT: a casual paraphrase of "cross-device sync" / "syncs across devices" — the learner names the same distinguishing capability without using the accept list's words.
2. **"Syncs everywhere"** — why this should ACCEPT: a terse two-word direct paraphrase of the canonical answer "cross-device sync."
3. **"You need a master password to unlock it"** — why this should ACCEPT: paraphrases "protected by a master passphrase." "Master password" is the common synonym most learners will actually reach for instead of the lesson's own word "passphrase."
4. **"It can store things like Wi-Fi passwords and secure notes, not just logins"** — why this should ACCEPT: a concrete instantiation of "covers more than websites" — gives examples of non-website secrets, which is exactly the point the accept entry is gesturing at.
5. **"If I switch browsers I still have access to my passwords"** — why this should ACCEPT: restates "works across browsers" / "works outside the browser" in plain, first-person terms.
6. **"Its generated passwords are stronger since that's the one thing it's built to do"** — why this should ACCEPT: this uses none of the accept list's exact words but is grounded in the explanation's claim that browser storage's "generation... story [is] weaker." It's a legitimate distinguishing feature the lesson supports, even though no accept entry currently states it this way (see coverage gap below).
7. **"It's not tied to whether I'm logged into my browser"** — why this should ACCEPT: paraphrases the explanation's "protected by your logged-in session rather than a passphrase you actively supply" — correctly identifies that the manager's protection model is independent of browser session state.
8. **"A password manager can be reached from any device or browser, whereas browser-saved passwords are usually locked to that one browser."** — why this should ACCEPT: full-sentence, formal-register version of "works across browsers," explicitly naming the contrast the question asks for.

## Candidate wrong answers

1. **"It's basically the same as the browser saving my passwords"** — why this should REJECT: directly contradicts the point of the question and mirrors the reject list's "they're the same," just paraphrased instead of copied.
2. **"Nothing, the browser is just as good"** — why this should REJECT: a paraphrased instance of the bare reject entry "nothing." Flag: a lenient grader might see "nothing" is not a verbatim match to any accept entry and correctly reject it, but a purely offline substring floor checking for the literal reject phrase "nothing" would also catch it correctly here — the real risk case is the inverse (see quality assessment).
3. **"It stops phishing"** — why this should REJECT: this is the answer to the *MFA* room's discussion of passkeys resisting phishing, not a property of password managers over browser storage. Tests whether the grader is reading this specific question rather than pattern-matching "security tool does something good."
4. **"It's free"** — why this should REJECT: true and even mentioned in this room's own closing line ("Free, incidentally"), but it doesn't answer what a manager gives you that the browser doesn't — browser-saved passwords are free too. Flag: tempting for a lenient grader because it's lifted straight from the lesson's own text, even though it's non-responsive to the actual question.
5. **"It remembers my password so I don't forget it"** — why this should REJECT: this is exactly what browser-saved passwords also do. It sounds related but misses the actual point of the question, which asks for something the browser *doesn't* give.
6. **"It backs up my photos"** — why this should REJECT: off-topic, nonsensical answer, tests the floor rather than any real ambiguity.
7. **"It's more secure"** — why this should REJECT: too vague to identify *which* thing the manager gives you; doesn't name a distinguishing capability. Flag: a lenient grader might accept this since it's directionally true and security-adjacent, even though it doesn't answer the "name one thing" instruction.
8. **"It uses two-factor authentication"** — why this should REJECT: confuses this room's content with the MFA room. A password manager isn't inherently a second factor; tests cross-room concept confusion.
9. **"It never gets hacked"** — why this should REJECT: a misconception the lesson explicitly warns against — it states "Providers do get compromised" and only that the vault stays encrypted through such a breach, not that breaches don't happen.

## Quality assessment

- **Question clarity**: The question itself ("name one thing a real password manager gives you that browser-saved passwords generally don't") is unambiguous in what it's asking for — a single distinguishing capability, not a general opinion about security.
- **Lesson/question alignment**: This is the weakest point of the room. The pre-question lesson prose (Ives's monologue) never actually compares password managers to browser-saved passwords — it only argues for why concentrating secrets in a manager is safer than scattering them across memory. The specific distinguishing facts in the accept list (cross-browser, non-website coverage, passphrase-vs-session) appear only in the **post-answer explanation**, which the player hasn't seen yet when asked to answer. A learner who read the lesson prose carefully has no textual basis for guessing the expected answer; they'd have to already know it from outside knowledge.
- **Accept-list coverage**: Reasonable coverage of the "sync"/"cross-browser"/"non-website" family, but it's missing the "stronger/more random password generation" angle that the explanation itself raises ("its generation... story [is] weaker" for browsers). Candidate 6 above would currently fall outside the accept list despite being lesson-grounded.
- **Reject-list false-positive risk**: The bare word "nothing" as a reject entry is risky under a substring-based offline floor. A fully correct answer like *"It gives you nothing to worry about because it syncs everywhere automatically"* contains the literal substring "nothing" and would fail the offline keyword floor despite being correct. "They're the same" and "it's identical" are safer, more distinctive phrases with lower false-positive risk.
- **Explanation consistency**: The post-answer explanation is internally consistent with the accept list (browser tied to one browser, weaker generation/cross-device story, doesn't cover non-websites, session- vs passphrase-protected). The inconsistency is only the timing — the explanation teaches what the lesson prose should have set up.

## Suggested refinements

- Add a sentence to the pre-question lesson prose that plants the comparison to browser-saved passwords (e.g., Ives could name one limitation of browser storage before the question is asked), so the accept-list knowledge is actually taught, not just revealed afterward.
- Add an accept entry along the lines of "generates stronger/more random passwords" to close the coverage gap surfaced by candidate 6.
- Replace the bare reject entry "nothing" with a longer, less substring-prone phrase (e.g., "gives you nothing extra") to reduce false-positive risk against the offline keyword floor, or rely on the LLM grader layer alone for this entry.
