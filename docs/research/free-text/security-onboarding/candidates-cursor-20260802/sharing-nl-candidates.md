# Iedereen met de link — nl candidate answers

Source: `docs/research/free-text/security-onboarding/sharing-nl.md`

## Candidate correct answers

1. **"verborgen tabbladen"** — why this should ACCEPT: Canonieke accept; les noemt een tweede tabblad.
2. **"opmerkingen"** — why this should ACCEPT: Directe accept en les.
3. **"bijgehouden wijzigingen"** — why this should ACCEPT: Accept-lijst en les.
4. **"metadata"** — why this should ACCEPT: Accept-lijst; les noemt PDF-metadata parallel.
5. **"versiegeschiedenis"** — why this should ACCEPT: Accept-lijst; stille meereizende geschiedenis.
6. **"weggefilterde regels"** — why this should ACCEPT: Accept-lijst; data aanwezig maar niet zichtbaar.
7. **"een tweede blad dat je vergat"** — why this should ACCEPT: Informele parafrase van extra/verborgen bladen.
8. **"formules die andere data ophalen"** — why this should ACCEPT: Uitleg noemt gekoppelde formules als goed antwoord; zou ACCEPT moeten zijn. Flag: keyword-floor mist dit.

## Candidate wrong answers

1. **"bestandsgrootte"** — why this should REJECT: Expliciete reject.
2. **"opmaak / lettertype"** — why this should REJECT: Reject-lijst; cosmetisch.
3. **"de deellink zelf"** — why this should REJECT: Gerelateerd les-thema, niet stille inhoud in het bestand. Flag: soepele grader.
4. **"iedereen met de link"** — why this should REJECT: Juiste kamerstelling, verkeerd object voor deze vraag.
5. **"de eigenaar van de gegevens vragen"** — why this should REJECT: Classification-antwoord; hier fout.
6. **"macro's"** — why this should REJECT: Meer malware/bijlage-terrein. Flag: sommige graders kunnen "verborgen spul" goedkeuren.
7. **"de zichtbare cijfers"** — why this should REJECT: Staat juist op het scherm.
8. **"aardvarken"** — why this should REJECT: Off-topic floor test.

## Quality assessment

- Question clarity: Duidelijk; "naast wat er op het scherm" en "geruisloos" beperken goed.
- Lesson/question alignment: Goed. Les noemt tweede tab, wijzigingen, opmerkingen, metadata; uitleg vult aan.
- Accept-list coverage: Sterk. Gat: gekoppelde formules geprezen in uitleg maar niet op accept-lijst.
- Reject-list false-positive risk: Laag.
- Explanation consistency: Consistent; iets breder dan de accept-lijst.

## Suggested refinements

- Accept toevoegen: `gekoppelde formules`, `extra bladen`.
- Of gekoppelde formules uit de uitleg halen als ze niet mogen tellen.
- Geen herformulering van de vraag nodig.
