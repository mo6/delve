# 🎭 De aanval die gewoon een gesprek is — nl candidate answers

Source: `docs/research/free-text/security-onboarding/social-engineering-nl.md`

## Candidate correct answers

1. **"Echte IT vraagt nooit om je wachtwoord"** — why this should ACCEPT: near-direct paraphrase of the canonical accept-list entry ("echte ondersteuning vraagt nooit om je wachtwoord").
2. **"Het feit dat ze het vragen is al het bewijs"** — why this should ACCEPT: direct paraphrase of "het verzoek zelf is het teken," swapping "bewijs" for "teken" — the same concept in a synonym.
3. **"Een wachtwoord is gewoon niet iets wat support ooit nodig heeft"** — why this should ACCEPT: paraphrase of "ze hebben nooit je wachtwoord nodig," full-sentence and slightly more casual/roundabout register.
4. **"Support heeft z'n eigen toegang — dus als ze om je wachtwoord vragen, klopt er iets niet"** — why this should ACCEPT: partial restatement of the explanation's own reasoning ("ondersteuners hebben hun eigen toegangspaden en willen je inloggegevens niet"), not just a copy of an accept-list phrase.
5. **"Je zou nooit gevraagd moeten worden je wachtwoord aan iemand van IT te geven"** — why this should ACCEPT: formal-register full sentence, paraphrase of "echte ondersteuning vraagt nooit om je wachtwoord."
6. **"Dat is gewoon niet iets wat ze zouden hoeven weten"** — why this should ACCEPT: casual, roundabout phrasing of "geen legitieme ondersteuning heeft je wachtwoord nodig" — deliberately avoids the accept list's exact words.
7. **"Niemand legitiem heeft het nodig, punt"** — why this should ACCEPT: terse, emphatic paraphrase of the canonical entry.

## Candidate wrong answers

1. **"Ze belden me onverwacht, zonder dat ik het had aangevraagd"** — why this should REJECT: independently arrives at the same idea as reject-list "het gesprek kwam ongevraagd," phrased without reusing that wording. The explanation is explicit that unsolicited contact is "een echt signaal" but "contextueel," not disqualifying on its own — so this misses the point of the question (the tell that holds *regardless of context*).
2. **"Ze joegen me op en deden alsof het heel dringend was"** — why this should REJECT: independently arrives at reject-list "ze creëerden haast." Same reasoning as above — urgency is a real, contextual signal per the explanation, not the context-independent tell asked for.
3. **"IT heeft toch al toegang tot mijn account, dus waarom zouden ze het vragen"** — why this should REJECT: independently arrives at reject-list "IT zou al toegang moeten hebben" — true as a fact, but it's reasoning *about* IT's access rather than the actual tell (that the ask happened at all), so it misses what the question is asking for.
4. **"Het nummerweergave zag er vervalst uit, dus werd ik achterdochtig"** — why this should REJECT: sounds on-topic — vishing and nummerweergave-vervalsing are discussed in this exact lesson ("Nummerweergave is een suggestie, geen feit") — but this answers a different, adjacent question (how to spot a spoofed *call*) rather than what makes this specific request illegitimate regardless of context. Tests whether the grader is reading this question or pattern-matching nearby lesson content.
5. **"Je moet verifiëren via een kanaal dat zij niet gaven, bijvoorbeeld terugbellen op een nummer dat je al had"** — why this should REJECT: this is the lesson's own recommended *defence* ("Verifieer via een kanaal dat zij niet gaven... hang op en bel IT op het nummer dat je al had") but it describes an *action to take*, not the tell that makes the request illegitimate. It answers "wat moet je doen" rather than "wat is het teken" — a subtly different question shape from the same lesson.
6. **"Omdat ze zeiden dat ze van de bank belden, niet van IT"** — why this should REJECT: confuses roles from two different examples in the lesson (the vishing "fraudeafdeling van de bank" example vs. the IT-wachtwoord example in this specific question) and doesn't identify what makes the request itself illegitimate.
7. **"Omdat ik het telefoonnummer niet herkende"** — why this should REJECT: an off-topic guess conflating "een nummer niet herkennen" with the actual disqualifying tell (om een wachtwoord vragen); not grounded in the lesson's reasoning.
8. **"banaan"** — why this should REJECT: nonsensical, tests the floor of the grader rather than any genuine ambiguity.

## Quality assessment

- **Question clarity:** Well worded — "het ene teken... ongeacht de context" is precise and deliberately steers the learner away from the contextual signals (haast, ongevraagd contact) toward the single context-independent one (het wachtwoordverzoek zelf). Clear once read carefully.
- **Lesson/question alignment:** Strong and deliberate. The lesson explicitly sets up the exact accept/reject distinction the question tests: "Ongevraagd contact en gefabriceerde haast zijn allebei echte signalen, en allebei contextueel... Deze maakt je zeker." The question is clearly designed to test whether the learner picked up on that specific distinction, not just general social-engineering awareness.
- **Accept-list coverage:** Good coverage of the core idea (het wachtwoordverzoek zelf is diskwalificerend) phrased several ways. No major gaps found; the five accept entries span from terse ("het verzoek zelf is het teken") to fuller phrasing ("geen legitieme ondersteuning heeft je wachtwoord nodig").
- **Reject-list false-positive risk:** Real but narrow risk in compound answers. An answer like *"Ze creëerden haast door om mijn wachtwoord te vragen, en dát is het probleem"* contains the reject substring "creëerden haast" even though the answer correctly identifies the password ask as the disqualifying tell. Under substring-based rejection, this otherwise-correct compound answer would fail outright.
- **Explanation consistency:** Fully consistent — the explanation explicitly draws the accept/reject line ("Ongevraagd contact en gefabriceerde haast zijn allebei echte signalen... contextueel... Deze maakt je zeker") that the accept and reject lists encode.

## Suggested refinements

- No changes to the accept or reject lists' content — coverage is good and the reject entries correctly encode real-but-contextual signals the lesson explicitly wants learners to distinguish from the actual tell.
- Flag (not necessarily fix): the substring-reject floor risks failing compound answers that correctly name the password ask as the tell while also mentioning haast/ongevraagd contact as secondary context. This is a structural limitation of substring matching, not something specific to this room's word choices — worth noting for whoever reviews grading behavior across the pack, but no change to this file's content is proposed.
- No change needed to the question wording or lesson prose — both are clear and unusually well-aligned with the specific concept being tested.
