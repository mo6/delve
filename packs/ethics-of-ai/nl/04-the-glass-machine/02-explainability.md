---
id: explainability
keeper: shopkeeper
name: Het Waarom
pass: 0.75
place: black-box
---

# Verklaarbaarheid

Het Waarom verkoopt antwoorden per woord. "Een verklaring is geen dump van gewichten," zegt die. "Het is iets wat een mens kan gebruiken."

De kraam staat vol potten, elk met een label van een vraag die een klant ooit aan een machine stelde. "Transparantie," zegt Het Waarom, terwijl die een pot opzijschuift, "geeft je een blik naar binnen. Verklaarbaarheid is waar je daarbovenop voor betaalt: een blik naar binnen vertaald naar iets wat je ook echt kunt uitgeven."

Die woorden worden losjes gebruikt, dus laten we ze vastpinnen. **Transparantie** is de rauwe beschikbaarheid van de werking. **Verklaarbaarheid**, soms opgetut als **interpreteerbaarheid**, **XAI** (explainable AI), of **begrijpelijkheid**, is die beschikbaarheid omgezet in een verhaal dat een specifiek publiek kan volgen: een kredietbeoordelaar heeft een andere verklaring nodig dan een toezichthouder, die op zijn beurt weer een andere nodig heeft dan de aanvrager.

"Andere klant, ander wisselgeld," zegt Het Waarom, terwijl die op de kassa tikt. "Er is geen enkele juiste verklaring, alleen een voldoende verklaring voor wie er ook vraagt."

Een gangbare, goedkope versie: "je werd afgewezen omdat je inkomen 10.000 onder de drempel lag; kom daarboven en je was goedgekeurd." Dat is een **contrafeitelijke verklaring**, de kleinste verandering die de uitkomst had kunnen omdraaien, en ze is echt nuttig. Ze zegt iemand wat die de volgende keer moet doen.

"Maar let op de grens daarvan," waarschuwt Het Waarom, terwijl die dichterbij leunt. "Een contrafeitelijke verklaring zegt je wat het antwoord had veranderd. Ze zegt je niet dat het model kapot is, of bevooroordeeld, of buggy. Als er echt iets mis is, niet alleen iets onwelkoms, heb je een autopsie nodig, geen kassabon."

Er is niet één trucje dat goede verklaringen oplevert, er is een hele plank vol, elk met een prijs. Bouw een **eenvoudiger model** (een beslisboom in plaats van een diep netwerk) en je kunt het rechtstreeks aflezen, tegen een prijs in nauwkeurigheid. Plak een **hybride** verklaarmodule op een complex model: één systeem voorspelt, een tweede, eenvoudiger systeem benadert het waarom. **Manipuleer de invoer** en kijk wat er in de uitvoer verandert, en zo worden contrafeitelijke verklaringen op schaal gegenereerd. Of bouw voor de **mens**, niet voor het model: een visualisatie, een gemarkeerde zinsnede, een attention map, iets wat aansluit bij wat de lezer werkelijk kan begrijpen, in plaats van bij wat de ingenieur kan begrijpen.

"En dat vermogen," voegt Het Waarom toe, terwijl die de verkoop afrekent, "ligt niet vast. Leer mensen deze dingen te lezen en dezelfde verklaring doet meer werk. Algoritmische geletterdheid is de helft van wat je hier bij mij koopt."

> De juiste verklaring is niet de meest gedetailleerde; het is de verklaring die het publiek voor je ook echt kan gebruiken.

## Questions

### Een bank vertelt een afgewezen aanvrager: "Je werd afgewezen omdat je opgegeven inkomen 8.000 onder de drempel lag; met een inkomen boven dat niveau was je goedgekeurd." Wat voor soort verklaring is dit?

- [ ] Een volledige transparantie-openbaarmaking van de broncode van het model
- [x] Een contrafeitelijke verklaring: de kleinste verandering die de beslissing had kunnen omdraaien
- [ ] Een interpreteerbaarheidsaudit
- [ ] Een bewijs dat het model vrij is van bevooroordeeldheid

> Er is geen code openbaar gemaakt en er is geen audit uitgevoerd, een audit onderzoekt het model systematisch, niet één aanvraag van één klant. En iemand vertellen wat de uitkomst had omgedraaid, bewijst evenmin iets over de vraag of de redenering daarachter deugde.

### Een contrafeitelijke verklaring, zoals "je was goedgekeurd met 8.000 meer inkomen", is op zichzelf genoeg om te weten of de onderliggende beslissing eerlijk was.

- [ ] Waar
- [x] Niet waar

> Een contrafeitelijke verklaring zegt je wat je de volgende keer moet veranderen, en dat is nuttig. Ze zegt niets over of de drempel zelf redelijk was, of of het model daar via bevooroordeelde redenering op uitkwam. Als er echt iets mis is, niet alleen iets onwelkoms, heb je een dieper onderzoek nodig dan het antwoord met de kleinste verandering je geeft.

### Het Waarom noemt verschillende manieren om de beslissingen van een model verklaarbaar te maken. Welke van deze is er een van?

- [x] Een eenvoudiger model bouwen dat wat nauwkeurigheid inlevert in ruil voor directe leesbaarheid
- [ ] De trainingsdataset vergroten zodat het model een hogere nauwkeurigheid haalt
- [ ] De nauwkeurigheidsscore van het model publiceren naast zijn beslissingen
- [ ] Het model trainen om sneller te werken zodat het direct beslissingen teruggeeft

> Meer data, een gepubliceerde nauwkeurigheidsscore en snellere inferentie kunnen allemaal waar zijn van een model en toch iemand geen idee geven waarom *zijn* geval zo uitpakte. Alleen een eenvoudiger, rechtstreeks leesbaar model levert daadwerkelijk iets in voor leesbaarheid.

### Of een verklaring makkelijker te begrijpen is, hangt alleen af van hoe het model werkt, niet van wie het leest.

- [ ] Waar
- [x] Niet waar

> Het hele verkooppraatje van Het Waarom is dat hetzelfde onderliggende model een andere verklaring nodig heeft voor een kredietbeoordelaar, een toezichthouder en een aanvrager. Het model verandert niet tussen die drie; de voldoende verklaring wel, omdat het vermogen van het publiek om ze te gebruiken verschilt.
