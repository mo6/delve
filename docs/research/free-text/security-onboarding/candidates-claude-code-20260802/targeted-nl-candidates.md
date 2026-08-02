# Wanneer het voor je geschreven is — nl candidate answers

Source: `docs/research/free-text/security-onboarding/targeted-nl.md`

## Candidate correct answers

1. **"Het geldbedrag dat wordt overgemaakt"** — why this should ACCEPT: parafraseert het canonieke accept-item "de transactie" zonder de exacte woorden te gebruiken. Direct gegrond in Grigors tekst: "Geld dat ergens nieuws heen gaat. Rekeningnummers die veranderen."
2. **"Wat er precies gevraagd wordt"** — why this should ACCEPT: volzin-parafrase die neerkomt op "het verzoek," bijna letterlijk overgenomen uit Grigors eigen woorden: "Kijk naar wát er gevraagd wordt."
3. **"Bel ze even na op het nummer dat je al had"** — why this should ACCEPT: komt overeen met accept-item "verifieer via een tweede kanaal," met het concrete voorbeeld uit de tekst zelf: "Niet het nummer uit het bericht, het nummer dat je al had."
4. **"Dubbelchecken via een ander kanaal"** — why this should ACCEPT: informeel registervariant ("dubbelchecken" i.p.v. "verifieer," "ander kanaal" i.p.v. "tweede kanaal"), zelfde betekenis als de accept-items.
5. **"De aanvraag"** — why this should ACCEPT: eenwoordig, casual/niet-native synoniem voor "het verzoek"; een leerling die niet exact "verzoek" kent grijpt plausibel naar dit woord.
6. **"Controleer de transactie via een tweede kanaal"** — why this should ACCEPT: directe parafrase van het canonieke item "de transactie," met "controleer" als formeel register-synoniem van "verifieer."
7. **"Nagaan of de bankgegevens echt gewijzigd moeten worden, via een ander kanaal"** — why this should ACCEPT: gedeeltelijke herformulering van de redenering in de tekst ("Rekeningnummers die veranderen"), nog steeds correct omdat zowel het object als de tweede-kanaal-methode genoemd worden.

## Candidate wrong answers

1. **"Hun LinkedIn-profiel"** — why this should REJECT: variant van het afgewezen concept ("je online profiel," "je zichtbaarheid"), maar dan toegepast op de aanvaller in plaats van de speler; de les stelt juist dat vooronderzoek niet de stap is om te verdedigen, ongeacht wiens profiel het betreft.
2. **"Hoeveel informatie er over mij online staat"** — why this should REJECT: parafrase van reject-item "hoeveel ze over je weten." Let op: de offline keyword-floor doet alleen substring-matching en deze zin bevat geen van de letterlijke reject-strings, dus een te soepele offline check zou dit ten onrechte kunnen doorlaten; een LLM-grader moet dit semantisch alsnog afwijzen.
3. **"Het e-maildomein van de afzender"** — why this should REJECT: plausibele gok van iemand die de lestekst heeft overgeslagen, maar de tekst zegt expliciet: "Het domein klopt, want hij heeft het account" — het domein controleren is precies het signaal dat bij spear phishing niet meer werkt.
4. **"Of de toon van het bericht klopt"** — why this should REJECT: klinkt relevant (toon wordt letterlijk genoemd) maar mist het punt — Grigor zegt expliciet: "De toon klopt, want hij heeft gestudeerd," dus toon is geen bruikbaar signaal meer. Let op: een te soepele grader zou dit als een vorm van waakzaamheid kunnen aanzien en ten onrechte accepteren.
5. **"De sterkte van mijn wachtwoord"** — why this should REJECT: dit zou een plausibel antwoord zijn op de passphrases-kamer, niet op deze vraag — test of de grader deze specifieke vraag leest in plaats van "beveiliging" in het algemeen te herkennen.
6. **"Of de bijlage veilig is om te openen"** — why this should REJECT: correct-lijkend antwoord voor de links-and-attachments-kamer, hier fout — kruisbesmetting tussen kamers; dit scenario bevat helemaal geen bijlage.
7. **"Niks, spear phishing is niet te voorkomen"** — why this should REJECT: off-topic/defaitistisch non-antwoord, test de bodem in plaats van enige echte ambiguïteit.
8. **"Mijn privacy-instellingen op social media"** — why this should REJECT: een veelvoorkomende misvatting die de les expliciet weerlegt: "Je kunt je eigen bestaan niet ongedaan publiceren, en een baan waarin je bereikbaar moet zijn, vereist dat je vindbaar bent."

## Quality assessment

- Question clarity: Grotendeels helder, maar de accept-lijst combineert twee soorten geldige antwoorden — het *object* dat geverifieerd moet worden ("de transactie," "het verzoek") en de *methode* om te verifiëren ("verifieer via een tweede kanaal"). De vraag vraagt grammaticaal om een object ("wat moet je... verifiëren"), maar één canoniek-aanpalend accept-item beantwoordt met een methode. Een leerling kan redelijkerwijs beide kanten op antwoorden, en de vraag maakt niet duidelijk welke bedoeld is.
- Lesson/question alignment: Sterk. Grigors monoloog bouwt direct naar het antwoord toe ("De transactie blijft over... dít zijn de dingen die een tweede kanaal waard zijn"), dus de les onderbouwt de accept-lijst duidelijk.
- Accept-list coverage: Redelijk bereik, maar smal qua woordenschat — "het geld," "de betaling" en "een telefoontje" ontbreken, terwijl de eigen concrete voorbeelden uit de les ("Geld dat ergens nieuws heen gaat," "pak de telefoon") daar rechtstreeks naar wijzen. Onder de offline keyword-floor (alleen substring-matching) zou een antwoord als "verifieer de geldoverboeking" geen enkel accept-substring raken, ondanks een correcte betekenis.
- Reject-list false-positive risk: Laag voor de drie genoemde zinnen zoals ze er staan; ze zijn onderscheidend genoeg om niet per ongeluk als substring in een correct antwoord voor te komen.
- Explanation consistency: Consistent. De uitleg herhaalt "Verifieer de transactie via een tweede kanaal" en wijst reconnaissance-gebaseerde antwoorden expliciet af, precies in lijn met de accept/reject-verdeling.

## Suggested refinements

- Voeg "het geld," "de betaling" en "een telefoontje" toe aan de accept-lijst om de offline keyword-floor-dekking te verbreden, aangezien de eigen concrete taal van de les hier al naar wijst.
- Overweeg de vraag aan te scherpen zodat ondubbelzinnig om het object van verificatie gevraagd wordt (bijv. "welk onderdeel van het bericht moet je in plaats daarvan verifiëren, in een paar woorden?"), of laat expliciet weten dat zowel object- als methode-antwoorden geldig zijn, aangezien de huidige accept-lijst beide al mengt.
- Overweeg een parafrase van het reject-concept toe te voegen, bijv. "hun online aanwezigheid" of "hun digitale voetafdruk," om het keyword-floor-gat uit wrong-answer-kandidaat 2 te dichten.
