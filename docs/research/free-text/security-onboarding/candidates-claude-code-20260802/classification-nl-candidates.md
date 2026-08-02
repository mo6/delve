# 📄 Weten wat je vasthoudt — nl candidate answers

Source: `docs/research/free-text/security-onboarding/classification-nl.md`

## Candidate correct answers

1. **"Vraag na bij de persoon die verantwoordelijk is voor de gegevens"** — why this should ACCEPT: paraphrase van "de eigenaar van de gegevens vragen" / "navragen bij wie de gegevens beheert."
2. **"Gewoon vragen"** — why this should ACCEPT: terse two-word paraphrase van de canonieke "iemand vragen."
3. **"Neem contact op met wie er over die informatie gaat"** — why this should ACCEPT: casual-register paraphrase van "het navragen."
4. **"Behandel het ondertussen voorzichtig en check bij iemand die het weet"** — why this should ACCEPT: gedeeltelijke herhaling die "zorgvuldig behandelen" combineert met "vragen" — komt overeen met "zorgvuldig behandelen en vragen" zonder de formulering te herhalen.
5. **"Escaleer de vraag naar de eigenaar van de data in plaats van te gokken"** — why this should ACCEPT: formele paraphrase van "de eigenaar van de gegevens vragen," met expliciet contrast met gokken.
6. **"Overleg met je manager of het verantwoordelijke team"** — why this should ACCEPT: een plausibel generiek-gezag-antwoord. Noemt niet specifiek "de eigenaar van de gegevens," maar is een legitieme instantie van de brede canonieke "iemand vragen," die niet vereist dat de gevraagde persoon formeel de data-eigenaar is.
7. **"Niet gokken — vraag om verduidelijking bij iemand die het weet"** — why this should ACCEPT: volzin-versie die het "niet standaard"-frame combineert met "vragen."
8. **"Verifieer het bij de verantwoordelijke partij"** — why this should ACCEPT: een licht formele, niet-moedertaalspreker-achtige synoniem voor "de eigenaar van de gegevens vragen" — plausibele formulering van iemand die naar een formeler register grijpt dan de accept-lijst gebruikt.

## Candidate wrong answers

1. **"Markeer het voor de zekerheid als geheim"** — why this should REJECT: dit is precies de misvatting die deze kamer probeert te corrigeren — te hoog inschalen "voelt verantwoordelijk. Dat is het niet." Komt dicht bij de reject-lijst, alleen geformuleerd als een eerstepersoonsactie in plaats van een kale instructie.
2. **"Laat het ongeclassificeerd totdat iemand het je vertelt"** — why this should REJECT: klinkt relevant (stelt de beslissing uit) maar mist het punt — de eigenlijke instructie van de les is proactief vragen, niet passief afwachten. Flag: een soepele grader zou dit kunnen verwarren met "iemand vragen" omdat beide inhouden dat je de classificatie niet zelf bepaalt, maar dit antwoord bevat geen actieve stap om de onzekerheid daadwerkelijk op te lossen.
3. **"Gebruik je eigen inschatting op basis van de vier niveaus"** — why this should REJECT: een plausibel klinkende gok van iemand die de classificatietabel onthoudt maar het eigenlijke punt van de kamer heeft gemist — dat de oplossende stap is om te vragen, niet om zelf te oordelen op basis van de tabel.
4. **"Weiger het en verander daarna het wachtwoord"** — why this should REJECT: dit is het correcte antwoord op het scenario van een ongevraagde push-melding uit de *MFA*-kamer, niet op de classificatie-onzekerheid van deze vraag. Test of de grader deze specifieke vraag leest in plaats van willekeurig "wat moet je doen"-advies uit het pakket.
5. **"Classificeer het op basis van wat iemand ermee zou kunnen doen"** — why this should REJECT under the current accept list, but flagged below as a genuine ambiguity: dit herhaalt de eigen slotredenering van de les — "de vraag is niet 'welk niveau heeft dit document,' het is 'wat zou iemand hiermee kunnen doen? Beantwoord dat eerlijk en het niveau volgt meestal vanzelf'" — in plaats van de letterlijke instructie uit de uitleg om iemand te vragen. Het is goed gegrond in de eigen tekst van de kamer, en precies daarom zou een zorgvuldige, les-belezen grader (of leerling) dit ten onrechte als correct kunnen beoordelen. Zie kwaliteitsbeoordeling.
6. **"Gooi het in de versnipperaar"** — why this should REJECT: onzinnig, niet relevant; test de bodem in plaats van enige echte ambiguïteit.
7. **"Escaleer standaard naar geheim, tot het tegendeel bewezen is"** — why this should REJECT: herhaalt de bias richting te hoog inschalen die de kamer expliciet waarschuwt, verpakt als voorzichtigheid.

## Quality assessment

- **Question clarity**: Redelijk duidelijk — de vraag kadert specifiek het "niet zeker weten"-geval en stelt het tegenover "het hoogste label kiezen," wat de bedoelde antwoordruimte versmalt.
- **Lesson/question alignment**: Dit is de substantiële bevinding voor deze kamer. Er is een echte spanning tussen twee dingen die de les leert: de uitleg na het antwoorden zegt dat de werkelijke standaard bij twijfel is "behandel het zorgvuldig en vraag het iemand," maar de slotzin van de lestekst zelf leert een *ander* oplossend mechanisme — zelfbeoordeling via "wat zou iemand hiermee kunnen doen? Beantwoord dat eerlijk en het niveau volgt meestal vanzelf." Een leerling die de lestekst aandachtig leest, in plaats van meteen naar de uitleg te springen, zou redelijkerwijs kunnen concluderen dat het geleerde antwoord "zelf over mogelijke impact nadenken" is, niet "iemand vragen" — en dat antwoord staat niet in de accept-lijst. Kandidaat 5 hierboven test deze ambiguïteit direct.
- **Accept-list coverage**: Redelijke dekking van "vragen"-formuleringen, maar gezien de bovenstaande spanning is er een echt gat: geen accept-entry vangt de "inschatten wat iemand ermee zou kunnen doen"-redenering die de eigen slotzin van de les als de oplossende vraag presenteert.
- **Reject-list false-positive risk**: Concreet risico hier. De reject-entry "standaard geheim maken" is een korte, generieke frase die letterlijk als substring kan voorkomen in een expliciet correct antwoord dat zichzelf tegenover het foute gedrag plaatst — bv. *"Maak het niet standaard geheim maken, vraag liever de eigenaar"* (of vergelijkbare formuleringen zonder tussenvoegsel) kan de exacte substring "standaard geheim maken" bevatten en zou een offline keyword-bodem laten falen ondanks een volledig correct antwoord.
- **Explanation consistency**: De uitleg na het antwoorden is intern consistent met de accept-lijst ("de werkelijke standaard bij twijfel: behandel het zorgvuldig en vraag het iemand"), maar staat, zoals hierboven genoemd, op gespannen voet met de eigen slotredenering van de lestekst, die richting zelfbeoordeling van impact wijst in plaats van vragen.

## Suggested refinements

- Voeg ofwel een accept-entry toe die de twee framings overbrugt (bv. "de impact inschatten en navragen" of "uitzoeken wat iemand ermee zou kunnen doen, en dat dan checken bij de eigenaar"), of pas de slotzin van de les aan zodat die niet leest als een concurrerende, op zichzelf staande oplossingsmethode naast "iemand vragen."
- Herformuleer voor de reject-lijst "standaard geheim maken" naar een frase die minder snel als substring voorkomt in een correct, contrasterend antwoord (bv. "maakt er zonder te vragen standaard geheim van"), of markeer deze reject-entry als een die beter op de LLM-gradelaag kan leunen dan op de offline substring-bodem.
- Geen andere wijzigingen nodig naast de twee hierboven.
