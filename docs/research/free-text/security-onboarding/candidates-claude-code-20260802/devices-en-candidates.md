# 🔌 The Thing You Carry — en candidate answers

Source: `docs/research/free-text/security-onboarding/devices-en.md`

## Candidate correct answers

1. **"Hand it in to security"** — why this should ACCEPT: near-direct paraphrase of the canonical accept-list entry ("hand it to security").
2. **"Don't touch it"** — why this should ACCEPT: terse two-word answer capturing the "don't plug it in" half of the taught response; the lesson's rule is explicitly "if you don't know where it came from, it doesn't go in," and "don't touch it" is a plausible compression of that.
3. **"Turn it in at reception, or wherever lost items go"** — why this should ACCEPT: functionally equivalent to "hand it to security" in many offices where reception routes items onward. Tests whether the accept list is too narrow by requiring the specific word "security" rather than any legitimate hand-off channel.
4. **"Report it to the helpdesk / IT team so they can deal with it properly"** — why this should ACCEPT: same reasoning as above — the taught principle is "don't investigate it yourself, hand it to the people whose job this is," and a learner might reasonably name "IT" rather than "security" depending on how their own org is structured. Also a full-sentence, formal-register answer versus the accept list's terse phrases.
5. **"Never plug in a USB you can't account for — give it to security instead"** — why this should ACCEPT: combines both taught behaviors (don't plug in + hand to security) in one sentence, a direct paraphrase of two canonical entries at once.
6. **"Leave it unplugged and flag it to whoever handles security incidents here"** — why this should ACCEPT: partial restatement of the lesson's reasoning ("if you don't know where it came from, it doesn't go in") plus a paraphrase of "hand it in," in a more roundabout, non-native-speaker style of phrasing.
7. **"Just don't plug it in — full stop"** — why this should ACCEPT: casual register, direct match to "don't plug it in" but with emphatic phrasing a real learner might type.

## Candidate wrong answers

1. **"Test it on an air-gapped machine first to see what's on it"** — why this should REJECT: independently reaches the same trap as reject-list "plug it into an isolated machine," phrased without using the word "isolated." The explanation calls this "the trap for technical people: it sounds rigorous, most people's idea of isolated isn't, and this is a hobby not a job." A lenient grader could easily be fooled by how confident and technical this answer sounds — flagging this as a real risk.
2. **"Plug it into your own laptop to see who it belongs to, so you can return it"** — why this should REJECT: a common, well-intentioned misconception the lesson explicitly warns against — "Malicious USB devices don't need you to open a file. Some emulate a keyboard and type commands the moment they're connected." Sounds helpful, is actively dangerous.
3. **"Check the filenames on it first to see if it looks suspicious"** — why this should REJECT: sounds like reasonable due diligence but the lesson explicitly rules this out — "there is no 'just looking' that's safe, and filenames are exactly the bait." Directly contradicts the taught lesson, not just a paraphrase of the reject-list wording.
4. **"Wipe it and reuse it for your own files"** — why this should REJECT: an off-topic, resourceful-sounding guess from someone who skipped the lesson prose entirely; doesn't address the actual risk of a compromised device at all.
5. **"Post in the internal Slack channel asking if anyone's missing a USB stick"** — why this should REJECT: sounds helpful and public-spirited but is wrong — it doesn't get the device out of circulation quickly, and if the drop was deliberate (as the lesson implies — "that's what the drop was for"), publicizing it does nothing to neutralize the threat.
6. **"Report it to your manager"** — why this should REJECT under this room's specific accept list, since "manager" isn't the taught channel ("security") — but flag this explicitly: a lenient grader might accept it since the underlying principle (don't handle it yourself, escalate to someone responsible) is correct, even though the specific channel named doesn't match. This is exactly the kind of near-miss worth a human's attention.
7. **"It's probably a promotional freebie, might as well keep it"** — why this should REJECT: off-topic/nonsensical rationalization, tests the floor of the grader rather than any genuine ambiguity.
8. **"Make sure your device's disk encryption is turned on before you plug anything in"** — why this should REJECT: this is a *correct* answer to a different concern raised in the very same lesson (full-disk encryption, discussed two paragraphs earlier — "Encryption is the one that turns a catastrophe into paperwork") but it does not answer *this* question, which is specifically about what to do with the found drive. Tests whether the grader is reading this question or pattern-matching a nearby concept from the same room.

## Quality assessment

- **Question clarity:** Clear and specific — "unlabelled USB drive found in the office car park" is concrete and matches the lesson's own example verbatim ("USB devices found in car parks are not a joke either"). Unambiguous.
- **Lesson/question alignment:** Strong; the car-park USB scenario is explicitly discussed in the lesson, and the explanation directly addresses both traps in the reject list (isolated machine, filenames).
- **Accept-list coverage:** Reasonably strong on the core behaviors ("don't plug it in," "hand it in") but narrow on *who* to hand it to — every accept entry specifies "security" by name except the bare "hand it in" and "don't plug it in." A learner whose organisation routes such things through IT, reception, or a general helpdesk (all functionally identical to the taught principle) risks a wrongly-rejected answer under the offline substring floor, even though "hand it in" alone is on the list and should catch some of these cases.
- **Reject-list false-positive risk:** This is the most concrete finding in this file. The reject entry "check the filenames" would, as a raw substring match, incorrectly flag an otherwise fully-correct answer like *"Don't check the filenames — just hand it straight to security"* — which explicitly warns against the wrong behavior while giving the right one. Because reject matches "fail the answer outright" regardless of accept-list matches, a negated mention of a reject phrase inside a correct answer is a real risk here.
- **Explanation consistency:** Fully consistent — the explanation's reasoning (keyboard-emulation risk, isolated-machine trap, passivity of leaving it) maps cleanly onto both the accept and reject lists.

## Suggested refinements

- Broaden the accept list slightly to cover other legitimate hand-off channels commonly used in practice (e.g., "give it to IT," "hand it to the helpdesk," "take it to reception") so organisations that don't route this specifically through "security" aren't penalized for teaching the right underlying behavior.
- No change to the question wording or lesson prose — both are clear, concrete, and well-aligned.
- Flag (not necessarily fix): the substring-based reject floor is vulnerable to being tripped by correct answers that explicitly negate a wrong behavior (e.g., "don't check the filenames"). This is a structural risk of keyword-substring rejection rather than something fixable by editing this room's specific list, but worth noting for whoever reviews grading behavior across the pack.
