# 🎭 The Attack That Is Just A Conversation — en candidate answers

Source: `docs/research/free-text/security-onboarding/social-engineering-en.md`

## Candidate correct answers

1. **"Real IT never asks for your password"** — why this should ACCEPT: near-direct paraphrase of the canonical accept-list entry ("real support never asks for your password").
2. **"The ask itself is the giveaway"** — why this should ACCEPT: direct paraphrase of "the request itself is the tell," swapping "giveaway" for "tell" — the same concept in a synonym a native speaker might reach for.
3. **"Passwords just aren't something support ever needs from you"** — why this should ACCEPT: paraphrase of "they never need your password," full-sentence and slightly more casual/roundabout register.
4. **"Support has its own way in — so wanting your password is the red flag"** — why this should ACCEPT: partial restatement of the explanation's own reasoning ("support staff have their own access paths and don't want your credentials"), not just a copy of an accept-list phrase.
5. **"You should never be asked to hand your password to anyone claiming to be IT"** — why this should ACCEPT: formal-register full sentence, paraphrase of "real support never asks for your password."
6. **"It's just not a thing they'd ever need to know"** — why this should ACCEPT: very casual, slightly non-native-speaker-style phrasing of "no legitimate support needs your password" — deliberately avoids all of the accept list's exact words.
7. **"Nobody legitimate needs to know it, full stop"** — why this should ACCEPT: terse, emphatic paraphrase of the canonical entry.

## Candidate wrong answers

1. **"They called me out of the blue, without me expecting it"** — why this should REJECT: independently arrives at the same idea as reject-list "it was unsolicited," phrased without reusing that wording. The explanation is explicit that unsolicited contact is "a real signal" but "contextual," not disqualifying on its own — so this misses the actual point of the question (which asks for the one tell that holds *regardless of context*).
2. **"They were rushing me and made it sound urgent"** — why this should REJECT: independently arrives at reject-list "they created urgency." Same reasoning as above — urgency is a real, contextual signal per the explanation, not the context-independent tell being asked for.
3. **"IT already has access to my account, so there's no reason for them to ask"** — why this should REJECT: independently arrives at reject-list "IT should have access already" — true as a fact, but it's reasoning *about* IT's access, not the actual tell (the fact that the ask happened at all), so it misses what the question is asking for.
4. **"The caller ID looked spoofed, so I got suspicious"** — why this should REJECT: sounds on-topic — vishing and caller-ID spoofing are discussed in this exact lesson ("Caller ID is a suggestion, not a fact") — but this answers a different, adjacent question (how to spot a spoofed *call*) rather than what makes the specific request illegitimate regardless of context. Tests whether the grader is reading this question or pattern-matching nearby lesson content.
5. **"You should verify through a channel they didn't give you, like calling IT back on a number you already had"** — why this should REJECT: this is the lesson's own recommended *defence* ("Verify through a channel they didn't give you... hang up and call IT on the number you already had") but it describes an *action to take*, not the tell that makes the request illegitimate. It answers "what should you do" rather than "what's the giveaway" — a subtly different question shape from the same lesson.
6. **"Because they said they were calling from the bank, not IT"** — why this should REJECT: confuses roles from two different examples in the lesson (the vishing "bank's fraud team" example vs. the IT-password example in this specific question) and doesn't identify anything that makes the request itself illegitimate.
7. **"Because I didn't recognize the phone number"** — why this should REJECT: an off-topic guess conflating "not recognizing a number" with the actual disqualifying tell (asking for a password); not grounded in the lesson's reasoning.
8. **"banana"** — why this should REJECT: nonsensical, tests the floor of the grader rather than any genuine ambiguity.

## Quality assessment

- **Question clarity:** Well worded — "the one tell... regardless of the surrounding context" is precise and deliberately steers the learner away from the contextual signals (urgency, unsolicited contact) toward the single context-independent one (the password request itself). Clear once read carefully, though "tell" (meaning "giveaway sign") is a slightly idiomatic word choice that a non-native English speaker might not immediately parse — worth noting, though not a true ambiguity.
- **Lesson/question alignment:** Strong and deliberate. The lesson explicitly sets up the exact accept/reject distinction the question tests: "Unsolicited contact and manufactured urgency are both real signals, and they're both contextual... This one makes you certain." The question is clearly designed to test whether the learner picked up on that specific distinction, not just "social engineering awareness" in general.
- **Accept-list coverage:** Good coverage of the core idea (password-ask-itself-is-disqualifying) phrased several ways. No major gaps found; the five accept entries already span from terse ("the request itself is the tell") to fuller phrasing ("no legitimate support needs your password").
- **Reject-list false-positive risk:** Real but narrow risk in compound answers. An answer like *"They created urgency by asking for my password, and that's the actual problem"* contains the reject substring "created urgency" even though the answer correctly identifies the password ask as the disqualifying tell. Under substring-based rejection, this otherwise-correct compound answer would fail outright.
- **Explanation consistency:** Fully consistent — the explanation explicitly draws the accept/reject line ("Unsolicited contact and manufactured urgency are both real signals... contextual... This one makes you certain") that the accept and reject lists encode.

## Suggested refinements

- No changes to the accept or reject lists' content — coverage is good and the reject entries correctly encode real-but-contextual signals the lesson explicitly wants learners to distinguish from the actual tell.
- Flag (not necessarily fix): the substring-reject floor risks failing compound answers that correctly name the password ask as the tell while also mentioning urgency/unsolicited-contact as secondary context (e.g., "...and that's the actual problem" style answers). This is a structural limitation of substring matching, not something specific to this room's word choices — worth noting for whoever reviews grading behavior across the pack, but no change to this file's content is proposed.
- No change needed to the question wording or lesson prose — both are clear and unusually well-aligned with the specific concept being tested.
