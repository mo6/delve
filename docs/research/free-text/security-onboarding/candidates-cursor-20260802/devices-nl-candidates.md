# Het ding dat je meedraagt — nl candidate answers

Source: `docs/research/free-text/security-onboarding/devices-nl.md`

## Candidate correct answers

1. **"inleveren bij beveiliging"** — why this should ACCEPT: Canonieke accept.
2. **"hem er nergens in steken"** — why this should ACCEPT: Directe accept en de saaie lesregel.
3. **"melden bij beveiliging"** — why this should ACCEPT: Accept-lijst.
4. **"aan IT of beveiliging geven"** — why this should ACCEPT: Informeel synoniem van inleveren.
5. **"inleveren bij de receptie"** — why this should ACCEPT: Plausibele org-variant. Flag: keyword-floor zonder "beveiliging".
6. **"laten liggen en iemand waarschuwen"** — why this should ACCEPT: Combinatie niet-gebruiken + escaleren; zou moeten tellen. N.B. "laten liggen" alleen is reject.
7. **"nergens op aansluiten"** — why this should ACCEPT: Formele herformulering van niet insteken.
8. **"naar #security-help brengen"** — why this should ACCEPT: Pack-plaatshouderkanaal; zelfde als melden/inleveren.

## Candidate wrong answers

1. **"in een geïsoleerde machine steken"** — why this should REJECT: Expliciete reject; val voor technische mensen.
2. **"de bestandsnamen bekijken"** — why this should REJECT: Reject; namen zijn lokaas.
3. **"laten liggen"** — why this should REJECT: Reject; volgende persoon is het doel van de drop.
4. **"negeren"** — why this should REJECT: Reject-lijst.
5. **"openen op een oude telefoon"** — why this should REJECT: Zelfde geïsoleerde-machine-misvatting. Flag: niet op reject-lijst.
6. **"formatteren en hergebruiken"** — why this should REJECT: Giswerk; nog steeds als media behandelen.
7. **"verwachtte ik dit"** — why this should REJECT: Links/bijlagen-antwoord; hier fout.
8. **"meenemen voor later"** — why this should REJECT: Passief bezit zonder melden.

## Quality assessment

- Question clarity: Ondubbelzinnig scenario.
- Lesson/question alignment: Gedeeltelijk. Les leert "gaat het er niet in", niet expliciet "inleveren bij beveiliging".
- Accept-list coverage: "nergens in steken" is lesgedekt; "beveiliging" kan te smal zijn voor receptie/IT.
- Reject-list false-positive risk: Let op ontkenningen die reject-substrings bevatten (`niet in een geïsoleerde machine steken`).
- Explanation consistency: Past bij accept/reject; loopt voor op de les wat escalatie betreft.

## Suggested refinements

- Lespassage: niet aansluiten; inleveren bij beveiliging (of jullie kanaal).
- Accept toevoegen: `aan IT geven`, `melden`, `nergens op aansluiten`.
- Reject-frases aanscherpen tegen substring-FP op ontkenningen.
