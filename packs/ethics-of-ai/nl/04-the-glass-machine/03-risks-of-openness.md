---
id: risks-of-openness
keeper: gatekeeper
name: Het Gesloten Boek
pass: 0.75
---

# Risico's van openheid

Het Gesloten Boek houdt de deur dicht. "Openheid is niet gratis," zegt die. "Soms geeft ze een wapen aan de verkeerde hand."

Die nodigt je niet uit. Die staat in de deuropening en laat je je zaak bepleiten.

"Stel dat een bank precies publiceert hoe haar fraudemodel een transactie markeert: welke kenmerken, welke drempels, welke combinatie het alarm laat afgaan." Het Gesloten Boek slaat de armen over elkaar. "Dan leest een fraudeur hetzelfde document. Die hoeft het model niet te verslaan. Die moet gewoon onder elke drempel blijven die je net hebt verteld."

Dat is **gaming**: eenmaal openbaar, kan iedereen precies tot de rand van een regel lopen en daar stoppen. Een spamfilter dat op bepaalde woorden scoort, wordt verslagen door spam die die woorden vermijdt en alles verder gewoon laat staan. De verklaring informeerde niet alleen de eerlijke gebruiker, ze briefte ook de tegenstander.

Erger dan gaming is een **adversarial attack**: niet onder een drempel blijven, maar precies de vorm van een model uitbuiten om het naar een specifiek verkeerd antwoord te dwingen, soms met een verandering te klein voor een mens om op te merken. Gedetailleerde verklaringen van hoe een model zijn invoer weegt, maken zulke aanvallen goedkoper om te bouwen, omdat je niet langer naar het doelwit hoeft te raden.

"Nog twee." Het Gesloten Boek telt op de vingers. "Verklaringen kunnen precies de privacy lekken die het systeem eigenlijk moest beschermen. Zeg iemand dat zijn lening werd afgewezen omdat "aanvragers uit jouw postcode twee keer zo vaak in default gaan als het gemiddelde" en je hebt iets onthuld over iedereen in die postcode, of ze daarmee instemden of niet. En verklaringen kunnen intellectueel eigendom lekken: beschrijf een model precies genoeg om zijn beslissing te verantwoorden, en je hebt het misschien precies genoeg beschreven om het te herbouwen."

De vraag om openheid is dus niet gratis te vervullen. Ze gaat ten koste van veiligheid, van privacy, van de reden dat het model als verdediging bestond in de eerste plaats.

"Niets van dit alles betekent elke deur dichtgooien," voegt die toe, terwijl die je uiteindelijk laat passeren. "Het betekent dat de juiste hoeveelheid transparantie een ontwerpkeuze is, geen maximum waar je standaard naar grijpt. Volledige openheid is voor sommige systemen een doel. Voor andere is het een cadeau aan de mensen die het systeem net moest tegenhouden."

> Meer openheid is niet automatisch beter; ze kan precies de rand die je onthult, in handen leggen van wie het systeem probeert te verslaan.

## Questions

### Hoe meer detail een systeem openbaart over hoe het tot een beslissing komt, hoe veiliger het is.

- [ ] Waar
- [x] Niet waar

> Meer openbaarmaking kan een systeem makkelijker maken om te gamen of aan te vallen, omdat iedereen die de verklaring leest precies leert waar de randen liggen. Veiligheid en openheid gaan ten koste van elkaar; meer van het ene is niet automatisch meer van het andere.

### Een spamfilter documenteert publiekelijk dat het berichten met het woord "gratis" scoort. Spammers beginnen in plaats daarvan "kosteloos" te schrijven en komen erdoorheen. Een voorbeeld van wat is dit?

- [x] Gaming: tegenstanders die hun gedrag aanpassen om net buiten een openbaar gemaakte regel te blijven
- [ ] Een adversarial attack die met een onmerkbare verandering een verkeerde classificatie moet afdwingen
- [ ] Een privacylek door de verklaring
- [ ] Diefstal van intellectueel eigendom via de verklaring

> Er gebeurde hier niets onmerkbaars; de spammers maakten een duidelijke, opzettelijke woordkeuze zodra ze de regel kenden. Dat is het gamen van een openbaar gemaakte drempel, niet de gerichtere manipulatie van een adversarial attack, en er is geen persoonlijke data of bedrijfsgeheim blootgelegd.

### Een bank verklaart een afwijzing met de zin: "aanvragers uit jouw postcode gaan twee keer zo vaak in default als het gemiddelde." Welk risico brengt dit specifieke type verklaring met zich mee, voorbij de individuele aanvrager?

- [x] Ze onthult mogelijk gevoelige statistische informatie over iedereen in die postcode
- [ ] Ze bewijst dat het model technisch onnauwkeurig is
- [ ] Ze garandeert dat de aanvrager een bezwaar zal winnen
- [ ] Ze maakt het model makkelijker om opnieuw te trainen

> De uitspraak zegt niets over de nauwkeurigheid van het model en garandeert geen enkele uitkomst van een bezwaar. Wat ze wel doet, is een claim op groepsniveau over een hele buurt in de afwijzingsbrief van één persoon zetten, wat een privacyblootstelling is voor iedereen in die postcode, niet alleen voor de aanvrager die de brief leest.

### Volledige transparantie is altijd het juiste doel voor elk AI-systeem, ongeacht wat het systeem doet.

- [ ] Waar
- [x] Niet waar

> Het hele argument van Het Gesloten Boek is dat de juiste hoeveelheid openbaarmaking een bewuste ontwerpkeuze is, afgewogen tegen het risico van gaming, aanvallen, privacy en intellectueel eigendom, geen maximum waar elk systeem standaard naar zou moeten grijpen. Voor sommige systemen geeft volledige openbaarmaking een voordeel aan precies de mensen die het systeem moet tegenhouden.
