# 🚨 De laatste deur — nl candidate answers

Source: `docs/research/free-text/security-onboarding/reporting-nl.md`

## Candidate correct answers

1. **"Meteen de beveiliging inlichten"** — waarom dit ACCEPT moet zijn: volledige-zin parafrase van het canonieke "het melden," met "inlichten" i.p.v. "melden," met behoud van de urgentie.
2. **"Geef het direct door aan IT-beveiliging"** — waarom dit ACCEPT moet zijn: gebruikt "doorgeven" als synoniem voor "melden," met dezelfde directheid als "direct melden bij beveiliging."
3. **"Meld het, ook al weet je het nog niet zeker"** — waarom dit ACCEPT moet zijn: direct gegrond in de lestekst ("Meld het vóór je het zeker weet. 'Ik denk dat ik misschien...' is een volledige melding"); combineert de kernactie met die redenering.
4. **"Beter nu een loos alarm dan straks een probleem"** — waarom dit ACCEPT moet zijn: gedeeltelijke herformulering van de redenering ("zij onderzoeken veel liever tien loze meldingen... dan dat ze volgende week over de echte horen") die de juiste actie impliceert (meld het) zonder het letterlijke werkwoord te gebruiken; de strekking is ondubbelzinnig ook al is de formulering indirect.
5. **"Direct rapporteren"** — waarom dit ACCEPT moet zijn: tweewoordige, directe parafrase van het canonieke antwoord, met het leenwoord "rapporteren" i.p.v. "melden."
6. **"Gewoon meteen even melden bij IT"** — waarom dit ACCEPT moet zijn: informeel/spreektalig register, correcte betekenis (direct melden) via de losse formulering.
7. **"Dit dient onverwijld gemeld te worden aan de beveiligingsafdeling"** — waarom dit ACCEPT moet zijn: formeel/stijf register dat een niet-moedertaalspreker zou kunnen kiezen; betekent nog steeds "meld het nu."

## Candidate wrong answers

1. **"Eerst even navragen of zij het zelf verstuurd hebben"** — waarom dit REJECT moet zijn: precies het instinct waar de uitleg expliciet voor waarschuwt ("Hen eerst vragen is het vriendelijke instinct en het is waar een aanvaller op rekent").
2. **"Zelf je wachtwoord veranderen, voor de zekerheid"** — waarom dit REJECT moet zijn: klinkt verwant aan accountbeveiliging in het algemeen, maar mist het punt — het account van de collega loopt risico, niet dat van de leerling; dit adresseert het beschreven risico niet.
3. **"Terugsturen en vragen wat ze bedoelen"** — waarom dit REJECT moet zijn: een plausibele gok van iemand die op een raar bericht reageert zonder de les te hebben geïnternaliseerd; direct fout volgens de uitleg's waarschuwing dat je mogelijk de aanvaller berichtjes stuurt.
4. **"De sleutel vervangen en het melden"** — waarom dit REJECT moet zijn: dit is het canonieke combinatieantwoord uit de ai-tools-kamer (een inloggegeven plakken in een AI-dienst), niet dit scenario. Er wordt hier geen inloggegeven genoemd — het account van een collega gedraagt zich vreemd. Dit test of de grader deze specifieke vraag leest in plaats van een aanpalende "meld + herstel"-vorm uit een andere kamer te herkennen.
5. **"Een nieuwe collega aannemen"** — waarom dit REJECT moet zijn: off-topic/onzinnig, test de ondergrens.
6. **"Het discreet aankaarten bij hen, zodat ze niet in verlegenheid raken"** — waarom dit REJECT moet zijn, en gemarkeerd als risico bij een coulante grader: dit echoot de framing van de vraag zelf ("het aankaarten zou hen in verlegenheid kunnen brengen") en klinkt attent, maar het is precies het "eerst vragen"-instinct waar de uitleg voor waarschuwt, nu verpakt als tact in plaats van nieuwsgierigheid. Een coulante grader die let op "is er iets ondernomen" zou dit ten onrechte kunnen goedkeuren.
7. **"Een dagje aankijken hoe het zich ontwikkelt"** — waarom dit REJECT moet zijn, en gemarkeerd als risico bij een coulante grader: klinkt bedachtzaam en verantwoordelijk, maar is "afwachten" in een redelijker klinkende jas. Dit staat lijnrecht tegenover "Snelheid is het hele spel" en de redenering over verblijfstijd in de les.

## Quality assessment

- Question clarity: Duidelijk. Het scenario (vreemde berichten, "waarschijnlijk niets," risico op gêne) is specifiek ontworpen om precies de verkeerde instincten uit te lokken waar de les voor waarschuwt, en de vraag ("wat moet je doen?") is ondubbelzinnig.
- Lesson/question alignment: Sterk — de vraag is een bijna-letterlijke instantiatie van "Meld alles wat vreemd is, niet alleen je eigen fouten. Een raar bericht van een collega" uit de lestekst, en de uitleg bouwt direct voort op de accountovername-framing van de les.
- Accept-list coverage: De vijf accept-items zijn allemaal nauwe varianten opgebouwd uit "meld-" plus een urgentiewoord. Dit dekt de meest waarschijnlijke formuleringen, maar is smal qua woordenschat — er is geen item met woorden als "doorgeven," "escaleren," of "aangeven bij beveiliging," die een leerling realistisch zou typen en die door de offline keyword-substring-ondergrens zouden worden afgewezen ondanks een correcte betekenis.
- Reject-list false-positive risk: Laag voor de vier genoemde formuleringen ("hen eerst vragen," "afwachten," "niets doen," "negeren") — geen daarvan komt waarschijnlijk voor als substring in een oprecht correct antwoord. De reject-lijst heeft echter een dekkingsgat aan de andere kant: de realistischere bijna-mis-formuleringen hierboven ("discreet aankaarten," "een dagje aankijken") staan er niet in, terwijl dat precies het faalscenario is waar de les voor probeert te waarschuwen, en die de offline ondergrens momenteel niet kan opvangen omdat ze met geen enkele reject-zin overeenkomen.
- Explanation consistency: Consistent — de uitleg weerlegt direct "hen eerst vragen" en "afwachten" en onderstreept de urgentie achter "meld het," in lijn met de accept-/reject-lijsten.

## Suggested refinements

- Verbreed de accept-lijst met synoniemen zonder de stam "meld-"/"rapporteer-" die leerlingen realistisch zouden typen (bijv. "doorgeven," "aangeven bij beveiliging," "escaleren"), om offline keyword-ondergrens-fout-negatieven te verminderen.
- Verbreed de reject-lijst met de realistischere "vriendelijk bedoelde maar foute" bijna-missers die deze analyse blootlegde (discreet navragen/aankaarten bij de collega, een dagje observeren voor je iets doet) — deze liggen dichter bij wat de les daadwerkelijk probeert te voorkomen dan de bottere "niets doen"/"negeren"-formuleringen die er al in staan.
- Geen wijziging nodig aan de vraagstelling of de lestekst zelf; die ondersteunen één duidelijk, goed onderbouwd correct antwoord.
