# Links, bijlagen, en de ruimte ertussen — nl candidate answers

Source: `docs/research/free-text/security-onboarding/links-and-attachments-nl.md`

## Candidate correct answers

1. **"verwachtte ik dit"** — why this should ACCEPT: Canonieke accept-entry en de Postmeesters "betere vraag".
2. **"had ik deze bijlage verwacht"** — why this should ACCEPT: Volzin-parafrase van dezelfde vraag.
3. **"verwacht?"** — why this should ACCEPT: Ultrashort vorm; nog steeds de verwachtingscheck.
4. **"had ik hierom gevraagd"** — why this should ACCEPT: Betekenis-aligned zonder accept-woorden; verwachting als eerder verzoek.
5. **"stond dit op mijn radar"** — why this should ACCEPT: Informele registervariant van verwachting.
6. **"was dit aangekondigd"** — why this should ACCEPT: Synoniem dat een niet-native of voorzichtige leerling kan kiezen.
7. **"bij onverwacht: eerst vragen"** — why this should ACCEPT: Gedeeltelijke herhaling van "Onverwacht: vragen"; moet nog tellen.
8. **"lag dit in de lijn der verwachting"** — why this should ACCEPT: Formele formulering van dezelfde check.

## Candidate wrong answers

1. **"is de bestandsnaam veilig"** — why this should REJECT: Precies de verkeerde vraag die de Postmeester afwijst.
2. **"klopt de extensie"** — why this should REJECT: Zelfde misvatting; namen/extensies zijn afzendertekst.
3. **"hover over de link"** — why this should REJECT: Gerelateerde lesinhoud over links, niet de bijlagebeslisregel. Flag: soepele grader kan "controleren" goedkeuren.
4. **"scannen met antivirus"** — why this should REJECT: Klinkt veilig maar de les zegt dat je veiligheid zo niet kent.
5. **"de transactie"** — why this should REJECT: Juist voor targeted/spear phishing, hier fout.
6. **"het domein van rechts lezen"** — why this should REJECT: Juist voor linkinspectie in dezelfde les, niet deze vraag.
7. **"openen als het er officieel uitziet"** — why this should REJECT: Giswerk zonder les; uiterlijk is wat aanvallers vervalsen.
8. **"banaan"** — why this should REJECT: Off-topic floor test.

## Quality assessment

- Question clarity: Iets onhandig: de vraag noemt al "onverwachte bijlage" en vraagt dan naar de ene vraag die bepaalt of je opent; zorgvuldige lezer kan "vraag na" zeggen i.p.v. "verwachtte ik dit".
- Lesson/question alignment: De betere vraag in de les is duidelijk "Verwachtte ik dit?". De uitleg gaat vooral over bestandsnaamtrucs en herhaalt die expect-check nauwelijks.
- Accept-list coverage: Nauwe cluster rond "verwacht*". Keyword-floor mist mogelijk `eerst vragen`, `had ik dit aangevraagd`.
- Reject-list false-positive risk: Lege reject-lijst; geen FP-risico, maar ook geen keyword-vangnet voor "veilig" / "bestandsnaam".
- Explanation consistency: Zwak t.o.v. de accept-lijst; uitleg steunt de "ongeacht bestandsnaam"-clausule meer dan de expect-vraag.

## Suggested refinements

- Prompt herformuleren zonder "onverwachte" erin te bakken.
- Accept toevoegen: `eerst vragen`, `had ik dit aangevraagd`, `stond dit te gebeuren`.
- Reject toevoegen: `is het veilig`, `bestandsnaam controleren`, `extensie vertrouwen`.
- Uitleg laten beginnen met "Verwachtte ik dit?" vóór de bestandsnaam-aside.
