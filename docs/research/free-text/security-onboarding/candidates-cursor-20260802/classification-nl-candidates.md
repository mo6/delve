# Weten wat je vasthoudt — nl candidate answers

Source: `docs/research/free-text/security-onboarding/classification-nl.md`

## Candidate correct answers

1. **"iemand vragen"** — why this should ACCEPT: Canonieke accept-entry.
2. **"de eigenaar van de gegevens vragen"** — why this should ACCEPT: Directe accept-entry.
3. **"zorgvuldig behandelen en vragen"** — why this should ACCEPT: Volledige accept-frase uit lijst en uitleg.
4. **"navragen bij wie de gegevens beheert"** — why this should ACCEPT: Accept-lijstparafrase.
5. **"een collega vragen die het weet"** — why this should ACCEPT: Informele vorm van iemand vragen.
6. **"een second opinion over het niveau"** — why this should ACCEPT: Synoniem voor vragen i.p.v. standaard hoog.
7. **"vragen wat iemand ermee zou kunnen doen"** — why this should ACCEPT: Marisols diagnostische vraag; verdedigbaar. Flag: kan keyword-accept missen.
8. **"de informatie-eigenaar raadplegen"** — why this should ACCEPT: Formele registervariant.

## Candidate wrong answers

1. **"als geheim markeren"** — why this should REJECT: Expliciete reject; te hoog inschalen.
2. **"het hoogste label gebruiken"** — why this should REJECT: Exact reject en wat de vraag uitsluit.
3. **"standaard vertrouwelijk"** — why this should REJECT: Zelfde fout met ander niveau. Flag: staat niet op reject-lijst.
4. **"wat zou iemand hiermee kunnen"** — why this should REJECT/ACCEPT borderline: lesvraag, niet de "bij twijfel"-procedure. Flag: soepele grader kan ACCEPTEN.
5. **"alles openbaar maken"** — why this should REJECT: Omgekeerde onderclassificatiefout.
6. **"beter dan niets"** — why this should REJECT: MFA-antwoord; hier fout.
7. **"inleveren bij beveiliging"** — why this should REJECT: Devices-USB-antwoord; hier fout.
8. **"classificeren als banaan"** — why this should REJECT: Off-topic floor test.

## Quality assessment

- Question clarity: Duidelijke anti-overclassificatieprompt.
- Lesson/question alignment: Gedeeltelijk. Les leert waarom te hoog inschalen faalt en "wat zou iemand hiermee kunnen?", maar niet expliciet "vraag de eigenaar bij twijfel".
- Accept-list coverage: Smalle cluster rond "vragen". Alleen Marisols diagnostiek antwoorden kan de keyword-floor missen.
- Reject-list false-positive risk: Antwoord als "niet als geheim markeren, maar vragen" kan reject-substring `als geheim markeren` raken.
- Explanation consistency: Past bij accept-lijst; loopt voor op de les.

## Suggested refinements

- Leszin toevoegen: bij twijfel zorgvuldig behandelen en de eigenaar vragen.
- Accept toevoegen: `een collega vragen`, `niet zelf het label raden`.
- Reject-frases aanscherpen zodat ontkennende correcte antwoorden niet substring-matchen.
