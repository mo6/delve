# Links, bijlagen, en de ruimte ertussen — nl candidate answers

Source: `docs/research/free-text/security-onboarding/links-and-attachments-nl.md`

## Candidate correct answers

1. **"Verwacht ik dit?"** — why this should ACCEPT: bijna identieke parafrase van het canonieke accept-item "verwachtte ik dit," alleen een werkwoordstijd verschoven; dit is letterlijk de gecursiveerde kernzin van de kamer: "Verwachtte ik dit?"
2. **"Zag ik dit aankomen?"** — why this should ACCEPT: idiomatisch, informeel register-synoniem met dezelfde betekenis als "was dit verwacht," gebruikt geen van de exacte accept-woorden.
3. **"Wist ik dat dit zou komen?"** — why this should ACCEPT: volzin zonder enig "verwacht"-stamwoord, toch dezelfde betekenis als "had ik dit verwacht."
4. **"Stond dit op mijn radar?"** — why this should ACCEPT: idiomatische, casual uitdrukking die neerkomt op "was dit verwacht."
5. **"Verwacht?"** — why this should ACCEPT: eenwoordig, beknopt antwoord, directe inkorting van accept-item "verwacht ik dit."
6. **"Anticipeerde ik hierop?"** — why this should ACCEPT: eenwoordig formeel synoniem voor "verwacht," komt overeen met accept-item "was dit verwacht."
7. **"Vraag jezelf af of je deze bijlage verwachtte voordat je hem opent"** — why this should ACCEPT: volzin-herformulering die de diagnostische vraag nog steeds correct benoemt, gegrond in de tekst: "Verwacht: openen. Onverwacht: vragen."

## Candidate wrong answers

1. **"Klopt de bestandsextensie?"** — why this should REJECT: een misvatting die de les expliciet weerlegt — "het onderscheid niet aan je is om uit een bestandsnaam op te maken" en "Een bestand dat factuur.pdf heet is misschien geen PDF." De extensie controleren is precies de foute aanpak die de Postmeester corrigeert.
2. **"Lijkt dit op een virus?"** — why this should REJECT: een plausibele volksbeveiligings-gok van iemand die de lestekst heeft overgeslagen, maar de tekst wijst dit expliciet af: "Niet is deze bijlage veilig... Dat kun je niet weten, en ik ook niet."
3. **"Is het e-mailadres van de afzender legitiem?"** — why this should REJECT: klinkt relevant — de linkhelft van deze les gaat over afzender-gestuurde misleiding — maar mist het punt van de bijlagevraag specifiek, die over verwachting gaat, niet over afzenderverificatie. Let op: omdat beide helften van deze les woordenschat over "de afzender" delen, zou een te soepele grader dit kunnen verwarren en accepteren.
4. **"Nee, had ik niet verwacht"** — why this should REJECT: dit beantwoordt de diagnostische vraag in plaats van hem te benoemen; de kamer vraagt naar "de ENE VRAAG," niet naar een ja/nee-oordeel over een specifiek geval. Let op: dit is een sterk risico voor een te soepele grader, want het deelt veel woordenschat ("verwacht") met de accept-lijst zonder de vraag zelf te formuleren.
5. **"De laatste twee labels vóór de eerste enkele schuine streep"** — why this should REJECT: dit is het juiste antwoord op de link/domein-helft van dezelfde les, niet op de bijlagevraag — test kruisverwarring binnen één kamer.
6. **"Controleren of macro's zijn ingeschakeld"** — why this should REJECT: een plausibel klinkende technische gok die niet onderbouwd wordt door het daadwerkelijke antwoord van de les; het antwoord van de les is gedragsmatig (verwachting-gebaseerd), geen technische inspectiestap.
7. **"Boeit niet, gewoon openen"** — why this should REJECT: off-topic/afwijzend non-antwoord, test de bodem in plaats van enige echte ambiguïteit.

## Quality assessment

- Question clarity: Grotendeels helder, maar er is een reëel risico op misinterpretatie: een leerling zou de vraag kunnen lezen als een verzoek om een oordeel over een specifieke bijlage ("verwachtte ik déze? Nee.") in plaats van het benoemen van de algemene diagnostische vraag. Wrong-answer-kandidaat 4 hierboven illustreert dit faalpatroon. Aanscherpen naar iets als "welke vraag moet je jezelf altijd stellen" zou de ambiguïteit wegnemen.
- Lesson/question alignment: Sterk — de les bouwt direct naar de gecursiveerde zin "Verwachtte ik dit?" als het gestelde antwoord, en de vraag sluit daar naadloos op aan.
- Accept-list coverage: Redelijk bereik aan voornaamwoord-/tijdsvarianten (ik/je, verleden/tegenwoordig), maar geen enkel item vermijdt het woord "verwacht" volledig. Idiomatische formuleringen zonder die stam — "zag ik dit aankomen," "stond dit op mijn radar," "anticipeerde ik hierop" — zouden de offline keyword-floor niet halen ondanks een correcte betekenis.
- Reject-list false-positive risk: Niet direct van toepassing — de reject-lijst is leeg voor deze vraag. Vermeldenswaardig als ontwerplacune eerder dan als vals-positief-risico: zonder reject-ankers heeft de offline keyword-floor niets om tegen af te wijzen, dus alle onderscheidingskracht tegen foute antwoorden rust volledig op de LLM-grader.
- Explanation consistency: Consistent — de uitleg herhaalt "het deel dat de afzender schrijft is een bewering, geen feit," in lijn met het "verwachtte ik dit"-kader, los van de bestandsnaam, en breidt expliciet hetzelfde principe uit dat al voor links werd onderwezen.

## Suggested refinements

- Voeg een korte reject-lijst toe die de exacte misvattingen benoemt waar de les tegen waarschuwt, bijv. "controleer de bestandsextensie," "scan het eerst," "kijk naar het adres van de afzender" — dit zijn de specifieke foute benaderingen die de Postmeester corrigeert, en momenteel verankert niets de offline floor daartegen.
- Voeg accept-items toe die het woord "verwacht" niet bevatten, bijv. "zag ik dit aankomen," "anticipeerde ik hierop," om de keyword-floor-dekking te verbreden voor idiomatische of niet-moedertaal-formuleringen.
- Overweeg de vraagformulering aan te scherpen zodat duidelijk is dat het antwoord de vraag zelf moet zijn (geen geval-specifiek ja/nee-oordeel), om het faalpatroon uit wrong-answer-kandidaat 4 voor te zijn.
