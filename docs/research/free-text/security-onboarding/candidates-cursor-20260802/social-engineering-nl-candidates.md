# De aanval die gewoon een gesprek is — nl candidate answers

Source: `docs/research/free-text/security-onboarding/social-engineering-nl.md`

## Candidate correct answers

1. **"om een wachtwoord vragen is het teken"** — why this should ACCEPT: Canonieke idee; het verzoek diskwalificeert zichzelf.
2. **"echte ondersteuning vraagt nooit om je wachtwoord"** — why this should ACCEPT: Directe accept-entry.
3. **"geen legitieme ondersteuning heeft je wachtwoord nodig"** — why this should ACCEPT: Canonieke accept-entry.
4. **"ze hebben nooit je wachtwoord nodig"** — why this should ACCEPT: Korte accept-vorm.
5. **"het wachtwoordverzoek zelf"** — why this should ACCEPT: Parafrase van "het verzoek zelf is het teken".
6. **"ondersteuning heeft eigen toegangspaden"** — why this should ACCEPT: Reden uit de uitleg zonder accept-woorden. Flag: keyword-floor kan missen.
7. **"wachtwoorden deel je nooit met IT"** — why this should ACCEPT: Informele beleidsformulering van dezelfde regel.
8. **"dat verzoek is nooit legitiem"** — why this should ACCEPT: Formele herformulering; zelf-ontkrachtend verzoek.

## Candidate wrong answers

1. **"het gesprek kwam ongevraagd"** — why this should REJECT: Expliciete reject; contextueel signaal.
2. **"ze creëerden haast"** — why this should REJECT: Reject; echt maar contextueel.
3. **"IT zou al toegang moeten hebben"** — why this should REJECT: Reject; naburige intuïtie, niet het geleerde teken.
4. **"nummerweergave klopte niet"** — why this should REJECT: Les: nummerweergave is een suggestie. Flag: soepele grader.
5. **"verifieer via een tweede kanaal"** — why this should REJECT: Juiste algemene verdediging, niet het *ene teken* dat het wachtwoordverzoek onecht maakt. Flag: hoog false-ACCEPT-risico.
6. **"meelopen / badge"** — why this should REJECT: Andere social-engineeringvorm uit deze kamer.
7. **"beter dan niets"** — why this should REJECT: MFA-antwoord; hier fout.
8. **"omdat ze beleefd waren"** — why this should REJECT: Mist het punt; behulpzaamheid is het aanvalsoppervlak.

## Quality assessment

- Question clarity: Iets zwaar geformuleerd, maar stuurt naar het zelf-ontkrachtende verzoek.
- Lesson/question alignment: Voldoende. Voorbeeld IT-wachtwoord; uitleg maakt de regel scherp.
- Accept-list coverage: Sterk rond het wachtwoordverzoek. Mist mogelijk `eigen toegangspaden`.
- Reject-list false-positive risk: Laag op genoemde rejects; groter risico op false ACCEPT van "tweede kanaal".
- Explanation consistency: Consistent en scherper dan het korte lesvoorbeeld.

## Suggested refinements

- Reject toevoegen: `tweede kanaal`, `ophangen en bellen`, `nummerweergave`.
- Accept toevoegen: `ondersteuning heeft eigen toegang`, `deel nooit je wachtwoord`.
- Optioneel één leszin met de regel expliciet.
