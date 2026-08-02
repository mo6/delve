# Lengte verslaat slimheid — nl candidate answers

Source: `docs/research/free-text/security-onboarding/passphrases-nl.md`

## Candidate correct answers

1. **"Alleen als het gelekt is"** — why this should ACCEPT: parafraseert de canonieke accept-items "als daar een reden voor is"/"na een lek" samen; een compacte herformulering van hetzelfde idee.
2. **"Als ik denk dat iemand anders het weet"** — why this should ACCEPT: volzin zonder de exacte woorden van de accept-lijst, maar drukt "bij een vermoeden van misbruik" / "bij verdenking van compromittering" uit, gegrond in de uitleg's vermelding van "een gedeeld geheim."
3. **"Nadat mijn bedrijf gehackt werd"** — why this should ACCEPT: informele parafrase van "na een lek," rechtstreeks gegrond in de tekst: "Wanneer één van die sites gelekt wordt... neemt de aanvaller je schitterende wachtwoordzin en probeert hem overal waar je verder bestaat."
4. **"Als er een concrete reden is, zoals een datalek"** — why this should ACCEPT: gedeeltelijke herformulering die de canonieke zin "als daar een reden voor is" combineert met het specifieke voorbeeld uit de uitleg ("een lek").
5. **"Indien nodig"** — why this should ACCEPT: tweewoordige idiomatische uitdrukking die neerkomt op "als daar een reden voor is," in een informeler register dan de accept-lijst.
6. **"Als ik het per ongeluk met iemand gedeeld heb"** — why this should ACCEPT: gegrond in de eigen lijst van triggers in de uitleg, die "een gedeeld geheim" noemt als geldige reden om te wijzigen — dit is een concreet voorbeeld van die trigger.
7. **"Niet routinematig, alleen als er echt iets mis is"** — why this should ACCEPT: een volzin die de vast-schema-misvatting expliciet ontkent terwijl het correcte concept ("als daar een reden voor is") bevestigd wordt — een gedeeltelijke herformulering van het eigen contrast van de les tussen routinematig verlopen en reden-gebaseerd wijzigen.

## Candidate wrong answers

1. **"Eén keer per kwartaal"** — why this should REJECT: dezelfde vast-schema-misvatting als reject-items "elke 90 dagen"/"elke drie maanden," anders geformuleerd; een veelvoorkomende misvatting die de les expliciet weerlegt.
2. **"Elke maand, voor de zekerheid"** — why this should REJECT: een routine/vast-schema-misvatting met een frequentie die niet letterlijk in de reject-lijst staat. Let op: de offline keyword-floor (alleen substring-matching) zou dit niet opvangen, omdat het geen van de vermelde reject-strings bevat — een echt keyword-floor-gat.
3. **"Wanneer het systeem me dwingt"** — why this should REJECT: een plausibel klinkende gok van iemand die de lestekst heeft overgeslagen; beschrijft reactief-op-beleid gedrag in plaats van een echte trigger, en de les bekritiseert expliciet "gedwongen om steeds te wijzigen," met de zwakkere wachtwoorden die dit oplevert.
4. **"Nooit, een wachtwoordzin hoeft niet te veranderen"** — why this should REJECT: klinkt relevant maar slaat door naar een ander fout uiterste; de les noemt wel degelijk geldige redenen om te wijzigen (lek, vermoeden, gedeeld geheim), dus "nooit" mist die nuance volledig.
5. **"Als hij lang genoeg is"** — why this should REJECT: dit zou een plausibel antwoord zijn op een *andere* vraag over dezelfde wachtwoordzin — de lengte/entropie ervan — maar deze vraag gaat over het timing-moment van wijzigen, niet over de sterkte van de wachtwoordzin. Test of de grader deze specifieke vraag leest in plaats van "kwaliteit van de wachtwoordzin" in het algemeen te herkennen.
6. **"Gebruik een wachtwoordmanager"** — why this should REJECT: een correct-lijkend antwoord voor de password-managers-kamer elders in dit pakket, hier fout — kruisbesmetting tussen kamers.
7. **"Wanneer ik er zin in heb"** — why this should REJECT: off-topic/lichtzinnig non-antwoord, test de bodem in plaats van enige echte ambiguïteit.

## Quality assessment

- Question clarity: Helder en goed afgebakend — "als het niet op een vast schema is" pareert bij voorbaat het meest voorkomende foute antwoord (routinematig verlopen) al in de vraag zelf.
- Lesson/question alignment: Zwak. De formulering "een reden, een lek, een vermoeden, een gedeeld geheim," die op de accept-lijst aansluit, staat niet in de les — die staat in de uitleg die pas na het antwoorden getoond wordt. De lestekst zelf (entropie, complexiteit versus slimheid, uniciteit, credential stuffing) zegt nergens wanneer je een wachtwoordzin moet wijzigen; die betoogt alleen dat lang + uniek wint van slimme mangling. Een speler die alleen de les leest heeft daarin geen tekstuele basis voor het antwoord van de accept-lijst en zou op voorkennis moeten leunen, niet op wat deze kamer onderwees.
- Accept-list coverage: Redelijk maar onvolledig: de uitleg noemt "een gedeeld geheim" als expliciete trigger, maar geen enkel accept-item dekt dit (bijv. "ik heb het wachtwoord met iemand anders gedeeld" zou momenteel niets hebben om onder de keyword-floor tegen te matchen). Ook noteer: de nl-lijst telt vier accept-items tegenover vijf in de en-versie van deze vraag — functioneel vergelijkbaar gedekt, maar iets smaller in aantal formuleringen. Idiomatische zinnen als "indien nodig" gebruiken bovendien geen van de accept-substrings en zouden de offline keyword-floor niet halen ondanks een correcte betekenis.
- Reject-list false-positive risk: Laag voor de zinnen zoals ze er staan, maar er is een dekkingsgat in de andere richting — de reject-lijst verankert alleen op "90 dagen"/"drie maanden"/"routinematig"/"vast schema." Een fout antwoord met een andere frequentie ("elke maand," "eens per kwartaal," "jaarlijks") glipt volledig langs de offline floor en leunt volledig op de LLM-grader, zoals te zien in wrong-answer-kandidaten 1 en 2.
- Explanation consistency: Consistent, en zelfs rijker dan de accept-lijst — de uitleg noemt "een gedeeld geheim" als trigger zonder bijbehorend accept-item.

## Suggested refinements

- Voeg "een gedeeld geheim" / "als ik het met iemand gedeeld heb" toe aan de accept-lijst, aangezien de uitleg deze trigger expliciet noemt maar geen accept-item hem momenteel dekt.
- Voeg enkele extra frequentie-varianten toe aan de reject-lijst (bijv. "elke maand," "eens per jaar," "jaarlijks") om het keyword-floor-gat uit wrong-answer-kandidaten 1 en 2 te dichten.
- Voeg vóór de vraag een kort lesmoment toe dat daadwerkelijk reden-gebaseerd wijzigen onderwijst (lek, vermoeden, gedeeld geheim) — die inhoud bestaat nu alleen in de uitleg na afloop, waardoor de les de accept-lijst waarmee ze gekoppeld is niet ondersteunt. Als alternatief: richt de vraag opnieuw op wat de les wél onderwijst (bijv. waarom mangling faalt, of lengte versus uniciteit) — de vraagformulering zelf is prima, het is de koppeling les/vraag die het gat is, niet de formulering.
