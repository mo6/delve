# 📤 Iedereen met de link — nl candidate answers

Source: `docs/research/free-text/security-onboarding/sharing-nl.md`

## Candidate correct answers

1. **"Verborgen tabbladen in het werkblad"** — why this should ACCEPT: near-direct paraphrase of the canonical accept-list entry ("verborgen tabbladen"); matches letter and spirit of the reference.
2. **"Opmerkingen"** — why this should ACCEPT: bare one-word answer, exact match for the accept-list entry "opmerkingen." Tests whether the grader accepts terse answers, which the lesson invites ("Noem... iets").
3. **"Er kan nog een tabblad in zitten waar je niet meer aan dacht"** — why this should ACCEPT: full-sentence, casual-register paraphrase of "verborgen tabbladen/bladen" that avoids the accept list's exact wording.
4. **"Het spoor van wie wat wanneer heeft aangepast"** — why this should ACCEPT: paraphrase of "versiegeschiedenis" using a more colloquial synonym ("spoor van wijzigingen") a non-native or informal speaker might reach for instead of the formal "versiegeschiedenis."
5. **"Rijen die je hebt weggefilterd maar die technisch nog in het bestand staan"** — why this should ACCEPT: partial restatement of the "weggefilterde regels" reasoning drawn from the lesson's point that hidden data persists even when not displayed, phrased as an explanation rather than a keyword.
6. **"Info over de auteur en organisatie die in de bestandseigenschappen zit"** — why this should ACCEPT: paraphrase of "metadata," describing the concept via "bestandseigenschappen" (file properties) without using the word "metadata."
7. **"Gekoppelde formules die stilletjes data uit andere werkbladen ophalen"** — why this should ACCEPT: the explanation *explicitly* calls this "een werkelijk goed antwoord" ("Gekoppelde formules zijn een werkelijk goed antwoord; ze kunnen structuur lekken en verwarrend stukgaan"). It is absent from the accept list — a real gap (see Quality assessment) — but per the room's own explanation this must be judged correct.
8. **"Bijgehouden wijzigingen die nog aanstaan van de laatste ronde"** — why this should ACCEPT: direct paraphrase of the accept-list entry "bijgehouden wijzigingen," phrased more fully as a careful learner might write it.

## Candidate wrong answers

1. **"Het bestand kan corrupt raken als ze het openen"** — why this should REJECT: an unrelated technical worry (file corruption) that has nothing to do with data traveling silently with the file; misses the question's point entirely.
2. **"De bestandsgrootte kan verraden hoeveel erin zit"** — why this should REJECT: independently arrives at the same idea as the reject-list entry "bestandsgrootte" — file size is visible and knowable, not something that travels silently and invisibly, so it fails the question's actual premise.
3. **"Het kan er raar uitzien als ze niet hetzelfde lettertype hebben"** — why this should REJECT: a plausible guess from someone who skipped the lesson prose and free-associated to "things that go wrong when sharing files," matching the spirit of reject-list "lettertypeproblemen" but phrased independently.
4. **"Ze kunnen het gewoon doorsturen naar iemand anders"** — why this should REJECT: sounds on-topic (a real sharing risk) but answers a different question — about who gets downstream access, not about hidden content silently traveling inside the file. A lenient grader focused on "sharing risk in general" could mistakenly accept this even though it doesn't answer what was asked.
5. **"De deling kan nog jaren openstaan nadat de externe kracht vertrokken is"** — why this should REJECT: a real point from the same lesson ("Vergeten dat gedeelde links niet verlopen... Die staat over tien jaar nog open") but it answers the link-lifetime concern, not the hidden-content-in-the-spreadsheet question being asked. Flag: a lenient LLM grader pattern-matching "risk from this lesson" rather than reading the specific question could wrongly accept this.
6. **"De virusscanner van de ontvanger zou het kunnen blokkeren"** — why this should REJECT: off-topic, an invented risk with no grounding anywhere in the lesson.
7. **"banaan"** — why this should REJECT: nonsensical, tests the floor of the grader rather than any real ambiguity.
8. **"De opmaak klopt niet meer op hun computer"** — why this should REJECT: directly mirrors reject-list "opmaak," independently generated; opmaak mismatches are cosmetic and visible on open — the opposite of "reist geruisloos mee."

## Quality assessment

- **Question clarity:** Clear and unambiguous — "noem, naast wat er op het scherm te zien is, iets dat geruisloos meereist" points a careful reader directly at hidden/non-obvious content.
- **Lesson/question alignment:** Strong. The lesson's "Meer meesturen dan je bedoelde" paragraph (tweede tabblad, bijgehouden wijzigingen, opmerkingen, metadata) maps directly onto the accept list and question.
- **Accept-list coverage:** Same gap as the English sibling room: the explanation explicitly praises "gekoppelde formules" ("een werkelijk goed antwoord") but neither "gekoppelde formules" nor a synonym appears on the accept list. Under the offline keyword floor (substring matching, not meaning), a correct "gekoppelde formules" answer would be wrongly rejected, contradicting the room's own explanation text.
- **Reject-list false-positive risk:** Moderate. "Opmaak" as a reject substring could catch an otherwise-correct metadata-flavored answer that happens to mention formatting in passing (e.g., "verborgen voorwaardelijke opmaak die laat zien welke rijen gemarkeerd waren" contains the substring "opmaak" and would be auto-rejected outright despite otherwise-correct content).
- **Explanation consistency:** Inconsistent in the same specific way as the `en` sibling — the explanation endorses "gekoppelde formules" as correct, but the accept list omits it. Everything else (verborgen bladen, weggefilterde regels, bijgehouden wijzigingen, opmerkingen, versiegeschiedenis) is consistent.

## Suggested refinements

- Add "gekoppelde formules" (and a close synonym like "externe verwijzingen" / "gekoppelde data") to the accept list to match the explanation's own endorsement.
- Consider narrowing the "opmaak" reject entry (e.g., to "opmaak ziet er anders uit") to reduce the risk of false-positive rejection of otherwise-correct metadata-flavored answers that happen to contain the word.
- No change needed to the question wording or lesson prose — both are clear and well-aligned with the intended concept.
