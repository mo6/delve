# De tweede factor — nl candidate answers

Source: `docs/research/free-text/security-onboarding/mfa-nl.md`

## Candidate correct answers

1. **"beter dan niets"** — why this should ACCEPT: Canonieke accept; tabel zegt "Beter dan niets".
2. **"het stopt de meeste aanvallen"** — why this should ACCEPT: Directe accept-entry.
3. **"stopt credential stuffing"** — why this should ACCEPT: Accept-lijst en uitleg; aanvallen op schaal.
4. **"houdt massale phishing tegen"** — why this should ACCEPT: Zelfde schaal-idee; gedeeltelijk maar correct.
5. **"zwak is niet waardeloos"** — why this should ACCEPT: Betekenis uit de uitleg zonder accept-woorden.
6. **"goed genoeg als het enige is wat er is"** — why this should ACCEPT: Informele herhaling van de sms-rij.
7. **"houdt opportunistische aanvallers buiten"** — why this should ACCEPT: Formeel synoniem voor schaalaanvallers.
8. **"verhoogt de drempel voor aanvallers"** — why this should ACCEPT: Gedeeltelijke herformulering; zou moeten tellen. Flag: vaag voor keyword-floor.

## Candidate wrong answers

1. **"het is waardeloos / niet de moeite"** — why this should REJECT: Expliciete reject.
2. **"laat het uit"** — why this should REJECT: Reject-lijst.
3. **"sms kan niet gephisht worden"** — why this should REJECT: Onjuist; les behandelt simswap en relay. Flag: klinkt zeker.
4. **"weiger push-meldingen die je niet veroorzaakte"** — why this should REJECT: Juiste MFA-moeheidsregel, verkeerd antwoord op de sms-waaromvraag.
5. **"passkeys zijn sterker"** — why this should REJECT: Waar, maar niet waarom je sms tóch aanzet.
6. **"verifieer via een tweede kanaal"** — why this should REJECT: Targeted-antwoord; hier fout.
7. **"sms is de sterkste factor"** — why this should REJECT: Tegengesteld aan de tabel.
8. **"omdat het gratis is"** — why this should REJECT: Mist het punt van de les.

## Quality assessment

- Question clarity: Duidelijk; "ook al is het de zwakste" stuurt naar beter-dan-niets.
- Lesson/question alignment: Voldoende. Sms-rij + uitleg over stuffing/phishing ondersteunen het.
- Accept-list coverage: Goed. Keyword-floor mist mogelijk `als het enige is`, `opportunistisch`.
- Reject-list false-positive risk: Laag.
- Explanation consistency: Consistent en iets rijker dan de tabel.

## Suggested refinements

- Accept toevoegen: `als het enige is wat er is`, `zwakst is niet waardeloos`.
- Optioneel één leszin dat sms nog steeds schaalaanvallen stopt.
