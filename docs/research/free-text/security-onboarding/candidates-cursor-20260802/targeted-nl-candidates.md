# Wanneer het voor je geschreven is — nl candidate answers

Source: `docs/research/free-text/security-onboarding/targeted-nl.md`

## Candidate correct answers

1. **"de transactie"** — why this should ACCEPT: Canonieke accept-entry; Grigors "De transactie blijft over".
2. **"wat er gevraagd wordt"** — why this should ACCEPT: Letterlijke lesformulering zonder accept-lijstwoorden te kopiëren; zelfde betekenis als het verzoek.
3. **"via een tweede kanaal"** — why this should ACCEPT: Korte vorm van de verdediging uit de les (telefoon die je al had, naar hun bureau lopen).
4. **"bel ze op een nummer dat je al had"** — why this should ACCEPT: Concreet tweede-kanaalgedrag; methode noemen i.p.v. "transactie" blijft correct.
5. **"het geldverkeer controleren"** — why this should ACCEPT: Informele parafrase van geld dat ergens nieuws heen gaat; zelfde als de transactie verifiëren.
6. **"niet wie vraagt, maar wat er gevraagd wordt"** — why this should ACCEPT: Echo van "Laat maar zitten wie het vraagt"; betekenis-aligned zonder accept-keywords.
7. **"wijzigingen van rekeningnummers"** — why this should ACCEPT: Gedeeltelijke herhaling van de high-stakes verzoeken; bedoeld als "die verifiëren" zou moeten tellen.
8. **"out-of-band bevestigen"** — why this should ACCEPT: Formele/synonieme registervariant van tweede-kanaalverificatie.

## Candidate wrong answers

1. **"je LinkedIn-profiel"** — why this should REJECT: Reject-thema (zichtbaarheid); les zegt dat openbare info niet ongedaan kan. Flag: onwaarschijnlijk geaccepteerd.
2. **"hoeveel ze over je weten"** — why this should REJECT: Expliciete reject-lijst; vooronderzoek is niet de te verdedigen stap.
3. **"het domein van de afzender"** — why this should REJECT: Les zegt dat domein/toon/verzoek bij BEC kloppen kunnen; domein checken mist het punt. Flag: soepele grader kan "iets verifiëren" goedkeuren.
4. **"je online zichtbaarheid verlagen"** — why this should REJECT: Misvatting die de uitleg waarschuwt; niet wat de vraag vraagt.
5. **"verwachtte ik dit"** — why this should REJECT: Juist voor links-en-bijlagen, hier fout; cross-room pattern-match.
6. **"MFA aanzetten"** — why this should REJECT: Aangrenzend vault-onderwerp, niet deze vraag.
7. **"spelfouten in de mail"** — why this should REJECT: Massale-phishing-teken; spear phishing is gebouwd om die te doorstaan.
8. **"paarse olifant"** — why this should REJECT: Off-topic floor test.

## Quality assessment

- Question clarity: Duidelijk; "in plaats daarvan" stuurt weg van openbare info naar verificatie van het verzoek.
- Lesson/question alignment: Sterk. Grigor eindigt op transactie en tweede kanaal; accept-lijst volgt dat.
- Accept-list coverage: Goed (transactie, verzoek, tweede kanaal). Keyword-floor mist mogelijk `terugbellen`, `out-of-band`, `rekeningnummer controleren`.
- Reject-list false-positive risk: Laag. Reject-frases over profiel/zichtbaarheid zitten zelden in een correct antwoord.
- Explanation consistency: Consistent met accept-lijst.

## Suggested refinements

- Accept toevoegen: `tweede kanaal`, `terugbellen`, `wat er gevraagd wordt`.
- Optioneel reject: `het domein`, `de afzender`.
