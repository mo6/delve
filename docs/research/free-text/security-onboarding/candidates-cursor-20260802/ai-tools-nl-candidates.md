# Wat je het Orakel verteld hebt — nl candidate answers

Source: `docs/research/free-text/security-onboarding/ai-tools-nl.md`

## Candidate correct answers

1. **"het melden"** — why this should ACCEPT: Canonieke accept; behandelen als bekendmaking.
2. **"de sleutel vervangen en het melden"** — why this should ACCEPT: Volledige accept; les: sleutel in prompt moet vervangen.
3. **"behandelen als elke andere bekendmaking"** — why this should ACCEPT: Directe accept-entry.
4. **"beveiliging vertellen en het geheim wijzigen"** — why this should ACCEPT: Informele parafrase van vervangen + melden.
5. **"aannemen dat het weg is en escaleren"** — why this should ACCEPT: Betekenis uit "ga uit van geen verwijderen" + meldpad. Flag: keyword-floor kan missen.
6. **"nu vervangen"** — why this should ACCEPT: Gedeeltelijk correct bij inloggegevens. Flag: incompleet bij alleen persoonsgegevens.
7. **"de juiste mensen waarschuwen"** — why this should ACCEPT: Informeel melden; zou moeten tellen.
8. **"melden; de chat wissen volstaat niet"** — why this should ACCEPT: Correct en wijst de veelgemaakte fout af.

## Candidate wrong answers

1. **"het gesprek verwijderen"** — why this should REJECT: Expliciete reject; les "ga uit van geen verwijderen".
2. **"verwijderen en verdergaan"** — why this should REJECT: Reject-lijst.
3. **"de chat weghalen"** — why this should REJECT: Reject-lijst.
4. **"de AI vragen het te vergeten"** — why this should REJECT: Zelfde misvatting. Flag: niet op reject-lijst.
5. **"AI nooit meer gebruiken"** — why this should REJECT: Orakel: gereedschappen weigeren is geen beveiliging.
6. **"inleveren bij beveiliging"** — why this should REJECT als fysieke USB-bedoeling; "melden bij beveiliging" moet ACCEPT. Flag: ambigu.
7. **"verwachtte ik dit"** — why this should REJECT: Bijlagen-antwoord; hier fout.
8. **"browsercache legen"** — why this should REJECT: Verkeerd model van waar de data heen ging.

## Quality assessment

- Question clarity: Duidelijk scenario van per ongeluk plakken.
- Lesson/question alignment: Gedeeltelijk. Les: credentials vervangen + geen verwijderen; "melden" staat sterker in de uitleg.
- Accept-list coverage: Goed voor melden/vervangen. Mist mogelijk `waarschuwen`, `escaleren`.
- Reject-list false-positive risk: Let op `"niet het gesprek verwijderen, maar melden"` met reject-substring.
- Explanation consistency: Past bij accept-lijst; les onderwijst melden voor niet-credential pastes minder.

## Suggested refinements

- Leszin: per ongeluk gevoelige paste is een bekendmaking; meld het; bij inloggegevens eerst vervangen.
- Accept toevoegen: `iemand vertellen`, `escaleren`, `ga ervan uit dat wissen niet werkt`.
- Reject-frases aanscherpen tegen ontkenningen.
