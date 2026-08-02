# 🤖 Wat je het Orakel verteld hebt — nl candidate answers

Source: `docs/research/free-text/security-onboarding/ai-tools-nl.md`

## Candidate correct answers

1. **"Geef het door aan de beveiligingsafdeling"** — waarom dit ACCEPT moet zijn: directe parafrase van het canonieke "het melden," met "doorgeven" als synoniem voor "melden."
2. **"De sleutel vernieuwen en de beveiliging inlichten"** — waarom dit ACCEPT moet zijn: komt inhoudelijk overeen met "de sleutel vervangen en het melden," met "vernieuwen" i.p.v. "vervangen" en "inlichten" i.p.v. "melden" — beide synoniemen die de les zelf ondersteunt ("Inloggegevens en sleutels... een sleutel in een prompt is een sleutel die je nu moet vervangen").
3. **"Behandel het zoals je elk ander datalek zou behandelen"** — waarom dit ACCEPT moet zijn: bijna-directe parafrase van "behandelen als elke andere bekendmaking," met "datalek" i.p.v. "bekendmaking" — sluit direct aan bij de uitleg ("Behandel het zoals je elke andere bekendmaking zou behandelen").
4. **"Wachtwoord wijzigen en er iemand van op de hoogte stellen"** — waarom dit ACCEPT moet zijn: volledige zin, iets losser geformuleerde versie van "vervangen en iemand vertellen," dekt beide onderdelen van dat combinatieantwoord.
5. **"Meld het"** — waarom dit ACCEPT moet zijn: tweewoordige, directe parafrase van het canonieke "het melden," nu als gebiedende wijs in plaats van een naamwoordelijke constructie — ander register, zelfde betekenis.
6. **"Niet zomaar verwijderen, maar melden wat er gebeurd is"** — waarom dit ACCEPT moet zijn: gedeeltelijke herformulering van de redenering uit de uitleg (verwijderen haalt het niet betrouwbaar weg) gecombineerd met de juiste actie (melden); zo'n gedeeltelijke herhaling van de redenering mag hier meetellen als correct.
7. **"Gewoon meteen even zeggen tegen IT"** — waarom dit ACCEPT moet zijn: informeel/casual register, correcte betekenis (direct melden bij IT) via de spreektalige formulering.
8. **"Men dient dit onverwijld te rapporteren aan de verantwoordelijke afdeling"** — waarom dit ACCEPT moet zijn: formeel/stijf register dat een niet-moedertaalspreker zou kunnen kiezen; betekent nog steeds "meld het."

## Candidate wrong answers

1. **"Het gesprek gewoon wissen, het is toch weg"** — waarom dit REJECT moet zijn: precies de denkfout waar de les en de uitleg expliciet voor waarschuwen — verwijderen haalt het niet betrouwbaar weg uit logboeken, back-ups of caches, en trekt geen al gebeurde bekendmaking terug.
2. **"Voortaan alleen de goedgekeurde AI-tool gebruiken"** — waarom dit REJECT moet zijn: klinkt verwant (het echoot de regel "weet welke deur je gebruikt") maar mist het punt van de vraag, die vraagt wat je nú moet doen na de fout, niet hoe je de volgende keer voorkomt dat het gebeurt.
3. **"Vragen of het AI-systeem het kan vergeten"** — waarom dit REJECT moet zijn: een plausibele gok van iemand die de lestekst heeft overgeslagen; wordt direct tegengesproken door "Ga uit van geen verwijderen. Modelgedrag is geen archiefkast waar je één blad uit kunt halen."
4. **"Het account laten controleren op inbraak"** — waarom dit REJECT moet zijn: dit is inhoud die bij een accountovername-scenario hoort (vergelijkbaar met de reporting- of mfa-kamer), niet bij het per ongeluk plakken van gevoelige data in een AI-dienst — test of de grader deze specifieke vraag leest in plaats van aanpalende content te herkennen.
5. **"De computer herstarten"** — waarom dit REJECT moet zijn: off-topic/onzinnig, test de ondergrens.
6. **"Vragen of de AI-dienst de data uit de training verwijdert"** — waarom dit REJECT moet zijn, en gemarkeerd als risico bij een coulante grader: klinkt proactief en veiligheidsbewust, precies waarom een coulante grader dit zou kunnen goedkeuren. Maar het wordt tegengesproken door "Ga uit van geen verwijderen" — een verwijderverzoek is geen vervanging voor het vervangen van een gelekte sleutel of het melden van een bekendmaking.
7. **"Het even aan je manager laten weten, kan later ook nog"** — waarom dit REJECT moet zijn, en gemarkeerd als risico bij een coulante grader: lijkt oppervlakkig op het geaccepteerde "iemand vertellen," maar "kan later ook nog" ondermijnt precies de urgentie die de hele les benadrukt, en een manager is niet het meldkanaal dat "het melden" impliceert.

## Quality assessment

- Question clarity: Grotendeels duidelijk, maar "iets gevoeligs" omvat drie verschillende categorieën uit de les — inloggegevens, gereguleerde persoonsgegevens, en algemene vertrouwelijke bedrijfsinformatie (contract, logboek, notitie) — die elk een andere vereiste actie hebben (vervangen vs. melden vs. beide). De vraag maakt niet duidelijk welk type "gevoelig" is geplakt, terwijl de structuur van de accept-lijst impliciet aanneemt dat de leerling de juiste combinatie kiest voor het juiste geval.
- Lesson/question alignment: Sterk. De uitleg is in feite de vraag herschreven als antwoordsleutel, en de hele les bouwt naar precies dit "wat nu"-moment toe.
- Accept-list coverage: Redelijk voor de aanwezige formuleringen, maar smal op twee manieren: (a) er is geen item voor "de sleutel vervangen" alléén — terwijl de uitleg zegt "was het een inloggegeven, vervang het nu" zonder expliciet te eisen dat er ook gemeld wordt in dat specifieke geval, waardoor een leerling die alleen "vervangen" antwoordt bij een inloggegeven-lezing van de vraag mogelijk onterecht wordt afgewezen; (b) de lijst mist gangbare synoniemen zonder de stam "meld-"/"vervang-" (bijv. "doorgeven," "inlichten," "aangeven bij beveiliging") die door de offline keyword-ondergrens (alleen substring-matching) zouden worden afgewezen, ook al betekenen ze hetzelfde.
- Reject-list false-positive risk: Laag. "het gesprek verwijderen," "verwijderen en verdergaan," "de chat weghalen" zijn allemaal strak gericht op de verwijder-denkfout en onwaarschijnlijk als substring in een oprecht correct antwoord.
- Explanation consistency: Consistent. De uitleg koppelt direct aan de accept-lijst (melden / vervangen+melden) en weerlegt direct de reject-lijst (verwijderen werkt niet).

## Suggested refinements

- Verduidelijk of "de sleutel vervangen" alléén (zonder expliciet melden) geaccepteerd moet worden wanneer de vraag gelezen wordt als specifiek over een gelekte inloggegeven — voeg dit toe aan de accept-lijst, of pas de vraag/les aan zodat expliciet wordt dat melden altijd de ene vereiste actie is, ongeacht wat er geplakt werd, met vervangen als aanvulling in plaats van alternatief.
- Verbreed de accept-lijst met een paar Nederlandse synoniemen zonder de stam "meld-"/"vervang-" die leerlingen realistisch zouden typen (bijv. "doorgeven," "inlichten," "aangeven bij beveiliging"), zodat inhoudelijk correcte antwoorden niet stranden op de offline keyword-substring-ondergrens.
