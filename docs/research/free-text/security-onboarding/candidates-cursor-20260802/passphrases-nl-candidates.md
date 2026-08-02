# Lengte verslaat slimheid — nl candidate answers

Source: `docs/research/free-text/security-onboarding/passphrases-nl.md`

## Candidate correct answers

1. **"als daar een reden voor is"** — why this should ACCEPT: Canonieke accept-entry; sluit aan op de uitleg.
2. **"na een lek"** — why this should ACCEPT: Directe accept-entry; concreet voorbeeld van een reden.
3. **"bij vermoeden van compromittering"** — why this should ACCEPT: Parafrase van de accept-lijst.
4. **"als het gedeeld is geweest"** — why this should ACCEPT: Uitleg noemt "een gedeeld geheim"; betekenis-correct ook zonder die exacte frase.
5. **"alleen als er iets misgaat"** — why this should ACCEPT: Informele parafrase van reden-gebonden wijzigen.
6. **"als het mogelijk gelekt is"** — why this should ACCEPT: Synoniem voor lek/vermoeden zonder accept-woorden.
7. **"als je denkt dat iemand anders het kent"** — why this should ACCEPT: Gedeeltelijke herhaling van vermoeden van misbruik.
8. **"bij aanwijzingen van blootstelling"** — why this should ACCEPT: Formele registervariant van hetzelfde idee.

## Candidate wrong answers

1. **"elke 90 dagen"** — why this should REJECT: Expliciete reject; het kalenderbeleid dat NIST/NCSC introk.
2. **"op een vast schema"** — why this should REJECT: Exact reject en wat de vraag uitsluit.
3. **"routinematig / elke drie maanden"** — why this should REJECT: Reject-lijst routinematig verlopen.
4. **"als het er slim genoeg uitziet"** — why this should REJECT: Verwart de entropie-les met de wijzigingsvraag.
5. **"nooit"** — why this should REJECT: Overcorrectie; bij lek moet je wél wijzigen. Flag: soepele grader kan "niet op schema" horen.
6. **"gebruik een wachtwoordzin"** — why this should REJECT: Juiste les-thema, verkeerd antwoord op deze timingvraag.
7. **"melden"** — why this should REJECT: Juist voor reporting/AI-kamers, hier fout.
8. **"dinsdag"** — why this should REJECT: Off-topic floor test.

## Quality assessment

- Question clarity: Als prompt duidelijk, maar veronderstelt kennis die de zichtbare les nauwelijks geeft.
- Lesson/question alignment: Zwak. De les gaat over entropie, lengte vs slimheid, uniciteit; níet wanneer je wijzigt. NIST/NCSC anti-expiry staat alleen in de uitleg.
- Accept-list coverage: Redelijk voor het beoogde antwoord; een zorgvuldige lezer die "bij hergebruik" antwoordt valt mogelijk buiten de keyword-floor.
- Reject-list false-positive risk: Laag.
- Explanation consistency: Uitleg past bij de accept-lijst; de les niet.

## Suggested refinements

- Korte lespassage toevoegen over wijzigen bij reden/lek/vermoeden, niet op kalender.
- Of de free-textvraag herijken op wat de les wél leert (uniciteit, waarom verminking faalt).
- Accept toevoegen: `gedeeld geheim`, `als het gelekt is`.
