# 🔌 Het ding dat je meedraagt — nl candidate answers

Source: `docs/research/free-text/security-onboarding/devices-nl.md`

## Candidate correct answers

1. **"Inleveren bij de beveiliging"** — why this should ACCEPT: near-direct paraphrase of the canonical accept-list entry ("inleveren bij beveiliging").
2. **"Er niet aankomen"** — why this should ACCEPT: terse answer capturing the "hem er nergens in steken" half of the taught response; matches the lesson's rule "als je niet weet waar het vandaan komt, gaat het er niet in."
3. **"Afgeven bij de receptie, of waar gevonden voorwerpen ook heen gaan"** — why this should ACCEPT: functionally equivalent to "inleveren bij beveiliging" in offices where reception routes items onward. Tests whether the accept list is too narrow by requiring the specific word "beveiliging" rather than any legitimate hand-off channel.
4. **"Melden bij de IT-helpdesk zodat zij het kunnen afhandelen"** — why this should ACCEPT: same reasoning — the taught principle is "onderzoek het niet zelf, geef het aan wie hiervoor verantwoordelijk is," and a learner might reasonably name "IT" instead of "beveiliging." Also a full-sentence, formal-register answer versus the accept list's terse phrases.
5. **"Nooit een onbekende USB-stick gebruiken — geef hem af bij de beveiliging"** — why this should ACCEPT: combines both taught behaviors (niet aansluiten + inleveren) in one sentence, a direct paraphrase of two canonical entries at once.
6. **"Laat hem zitten en waarschuw wie hier verantwoordelijk voor is"** — why this should ACCEPT: partial restatement of the lesson's reasoning ("als je niet weet waar het vandaan komt, gaat het er niet in") plus a paraphrase of "inleveren," phrased more roundabout, non-native-speaker style.
7. **"Gewoon niet in je laptop steken, punt"** — why this should ACCEPT: casual register, direct match to "hem er nergens in steken" but with emphatic phrasing a real learner might type.

## Candidate wrong answers

1. **"Eerst testen op een geïsoleerde laptop om te zien wat erop staat"** — why this should REJECT: independently reaches the same trap as reject-list "in een geïsoleerde machine steken," phrased without the word "geïsoleerd." The explanation calls this "de val voor technische mensen: het klinkt grondig, wat de meeste mensen geïsoleerd noemen is dat niet." A lenient grader could easily be fooled by how confident and technical this sounds — flagging this as a real risk.
2. **"Op je eigen computer bekijken van wie hij is, zodat je hem kunt teruggeven"** — why this should REJECT: a common, well-intentioned misconception the lesson explicitly warns against — "Sommige doen zich voor als toetsenbord en typen commando's zodra ze aangesloten worden." Sounds helpful, is actively dangerous.
3. **"Eerst de bestandsnamen checken of het er verdacht uitziet"** — why this should REJECT: sounds like reasonable due diligence but the lesson explicitly rules it out — "er bestaat geen 'even kijken' dat veilig is, en bestandsnamen zijn juist het lokaas." Directly contradicts the taught lesson, not just a paraphrase of the reject wording.
4. **"Wissen en zelf hergebruiken"** — why this should REJECT: an off-topic, resourceful-sounding guess from someone who skipped the lesson prose entirely; doesn't address the actual risk of a compromised device at all.
5. **"Op het interne Slack-kanaal vragen of iemand een USB-stick kwijt is"** — why this should REJECT: sounds helpful and public-spirited but is wrong — it doesn't get the device out of circulation quickly, and if the drop was deliberate (as the lesson implies — "dáárvoor is hij neergelegd"), publicizing it does nothing to neutralize the threat.
6. **"Melden bij je manager"** — why this should REJECT under this room's specific accept list, since "manager" isn't the taught channel ("beveiliging") — but flag this explicitly: a lenient grader might accept it since the underlying principle (niet zelf afhandelen, escaleren naar iemand verantwoordelijk) is correct, even though the specific channel named doesn't match. Worth a human's attention.
7. **"Het is vast een leuk cadeautje, ik hou hem gewoon"** — why this should REJECT: off-topic/nonsensical rationalization, tests the floor of the grader rather than any genuine ambiguity.
8. **"Zorg dat je schijfversleuteling aanstaat voordat je iets aansluit"** — why this should REJECT: this is a *correct* answer to a different concern raised in the very same lesson (volledige schijfversleuteling, discussed two paragraphs earlier — "Versleuteling is degene die een ramp in papierwerk verandert") but it does not answer *this* question, about what to do with the found drive. Tests whether the grader is reading this question or pattern-matching a nearby concept from the same room.

## Quality assessment

- **Question clarity:** Clear and specific — "ongelabelde USB-stick op het parkeerterrein van kantoor" is concrete and matches the lesson's own example verbatim ("USB-sticks op parkeerterreinen zijn ook geen grap"). Unambiguous.
- **Lesson/question alignment:** Strong; the car-park USB scenario is explicitly discussed in the lesson, and the explanation directly addresses both traps in the reject list (isolated machine, filenames).
- **Accept-list coverage:** Reasonably strong on the core behaviors ("niet aansluiten," "inleveren") but narrow on *who* to hand it to — most accept entries specify "beveiliging" by name except the bare "inleveren" and "hem er nergens in steken." A learner whose organisation routes this through IT, reception, or a general helpdesk risks a wrongly-rejected answer under the offline substring floor, though "inleveren" alone should catch some of these cases.
- **Reject-list false-positive risk:** The most concrete finding here. The reject entry "de bestandsnamen bekijken" would, as a raw substring match, incorrectly flag an otherwise fully-correct answer like *"Kijk niet naar de bestandsnamen — geef hem gewoon af bij beveiliging"* — which explicitly warns against the wrong behavior while giving the right one. Because reject matches "fail the answer outright" regardless of accept-list matches, a negated mention of a reject phrase inside a correct answer is a real risk here.
- **Explanation consistency:** Fully consistent — the explanation's reasoning (keyboard-emulatie risico, geïsoleerde-machine val, passiviteit van laten liggen) maps cleanly onto both the accept and reject lists.

## Suggested refinements

- Broaden the accept list slightly to cover other legitimate hand-off channels commonly used in practice (e.g., "geven aan IT," "melden bij de helpdesk," "naar de receptie brengen") so organisations that don't route this specifically through "beveiliging" aren't penalized for teaching the right underlying behavior.
- No change to the question wording or lesson prose — both are clear, concrete, and well-aligned.
- Flag (not necessarily fix): the substring-based reject floor is vulnerable to being tripped by correct answers that explicitly negate a wrong behavior (e.g., "kijk niet naar de bestandsnamen"). This is a structural risk of keyword-substring rejection rather than something fixable by editing this room's specific list, but worth noting for whoever reviews grading behavior across the pack.
