# De laatste deur — nl candidate answers

Source: `docs/research/free-text/security-onboarding/reporting-nl.md`

## Candidate correct answers

1. **"het melden"** — why this should ACCEPT: Canonieke accept; Winterkonings hele les.
2. **"het meteen melden"** — why this should ACCEPT: Directe accept; snelheid is het spel.
3. **"direct melden bij beveiliging"** — why this should ACCEPT: Accept-lijstformulering.
4. **"nu beveiliging vertellen"** — why this should ACCEPT: Informeel synoniem van meteen melden.
5. **"aankaarten ook als je twijfelt"** — why this should ACCEPT: Les: meld vóór je het zeker weet. Flag: keyword-floor zonder "melden".
6. **"niet afwachten, de rare berichten melden"** — why this should ACCEPT: Wijst afwachten af; betekenis-aligned.
7. **"naar #security-help sturen"** — why this should ACCEPT: Pack-plaatshouderkanaal; zelfde als melden.
8. **"melden; de collega is het slachtoffer"** — why this should ACCEPT: Volzin met framing uit de uitleg; nog steeds de juiste actie.

## Candidate wrong answers

1. **"hen eerst vragen"** — why this should REJECT: Expliciete reject; je mailt mogelijk de aanvaller.
2. **"afwachten"** — why this should REJECT: Reject; schenkt verblijfstijd.
3. **"niets doen / negeren"** — why this should REJECT: Reject-lijst.
4. **"eerst onderzoeken of het echt kwaadaardig is"** — why this should REJECT: Les: niet eerst onderzoeken. Flag: niet op reject-lijst; false-ACCEPT-risico.
5. **"het terloops noemen als je ze ziet"** — why this should REJECT: Zachte vorm van eerst vragen / vertragen.
6. **"het gesprek verwijderen"** — why this should REJECT: AI-tools-foutantwoord; hier ook fout.
7. **"je eigen wachtwoord wijzigen"** — why this should REJECT: Naburige remedie, niet wat te doen met *hun* rare berichten.
8. **"aannemen dat het meevalt"** — why this should REJECT: De stilte waar Winterkoning voor waarschuwt.

## Quality assessment

- Question clarity: Uitstekend; schaamte/verlegenheid zit in de stam.
- Lesson/question alignment: Sterk. Les leert vreemde dingen melden (inclusief collega), vóór je zeker weet, geen schuld, snelheid.
- Accept-list coverage: Smalle cluster rond "melden*". Mist mogelijk `beveiliging vertellen`, `aankaarten`.
- Reject-list false-positive risk: Laag op vragen/afwachten/negeren; let op ontkenningen met reject-substrings.
- Explanation consistency: Consistent; accountovername-framing past bij accept.

## Suggested refinements

- Accept toevoegen: `beveiliging vertellen`, `aankaarten`, `melden ook bij twijfel`.
- Reject toevoegen: `eerst onderzoeken`, `eerst bij hen checken`, `later noemen`.
- Overall: een van de sterkere vraag/les-paren; geen grote herschrijving nodig.
