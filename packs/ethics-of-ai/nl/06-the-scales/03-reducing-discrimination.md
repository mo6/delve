---
id: reducing-discrimination
keeper: wizard
name: Remedie
pass: 0.75
---

# Discriminatie verminderen

Remedie heeft een gereedschapskist en geen illusies. "Je kunt bevooroordeeldheid niet wegwensen," zegt ze. "Je kunt meten, herontwerpen en weigeren."

Ze legt haar gereedschap neer als een chirurg, niet als een verkoper. "Eerste les, en die stelt elke keer teleur: er is geen enkele regel code die bevooroordeeldheid uit een model verwijdert. Er bestaan technieken, een dataset herwegen, een gecorreleerde variabele weghalen, een drempel per groep aanpassen, en elk daarvan helpt *iets*. Geen van allemaal is een remedie, en er een als remedie behandelen is precies hoe een echt schadelijk systeem met een schoon geweten mag blijven draaien."

"Hier is de valstrik, en het is een echte, geen hypothetische." Ze houdt een moersleutel omhoog. "Soms repareert een team de *wiskunde*: de dataset wordt herbalanceerd, de metriek wordt bijgesteld, de demo ziet er schoon uit. En het *gebruik* waarvoor het systeem gebouwd is, is nog steeds onrechtvaardig, zeg een wervingstool die iedereen met een gat in de loopbaan uitfiltert, wat vrouwen onevenredig treft, hoe zorgvuldig je de trainingsdata daaronder ook hebt herbalanceerd. Het model repareren zonder te vragen of de inzet zelf het probleem is, heet **ethics-washing**: het technische werk doen dat verantwoord oogt, terwijl de daadwerkelijke schade precies blijft waar ze was."

De gereedschapskist van Remedie heeft dus drie lades, en geen ervan is optioneel. **Meten**: je kunt geen ongelijkheid herstellen die je nooit hebt gecontroleerd, en de meeste teams hebben nooit gecontroleerd. Loop de cijfers per groep na voordat je live gaat, en opnieuw daarna, want een reparatie kan de schade opzij schuiven in plaats van ze weg te nemen. **Herontwerpen**: soms is de eerlijke oplossing geen parameter, maar de pijplijn; verander welke data verzameld wordt, verander wat het systeem überhaupt gevraagd wordt te voorspellen. **Weigeren**: en soms, na meten en herontwerpen, is het eerlijke antwoord dat dit systeem helemaal niet gebouwd zou moeten worden, niet met een voorbehoud en een disclaimer, gewoon niet gebouwd. Die lade gaat het minst open en is het meest nodig.

"Nog één ding, want dit is waar mensen te vroeg gaan ontspannen." Ze sluit de gereedschapskist. "Dit is geen taak die je afrondt. Een model dat elke eerlijkheidscontrole bij lancering doorstond, kan afdrijven als de bevolking die het gebruikt verandert, en een controle die één keer uitgevoerd en weggelegd wordt, is een jaar later niets waard. Discriminatie verminderen is een onderhouden praktijk, zoals een tuin, geen diploma dat je inlijst."

> Een herbalanceerde dataset kan de daadwerkelijke schade precies laten waar ze was; het model repareren is niet hetzelfde als het systeem repareren waarvan het onderdeel is.

## Questions

### Een trainingsdataset herwegen om één gemeten ongelijkheid te corrigeren, is over het algemeen genoeg om een model niet-discriminerend te maken.

- [ ] Waar
- [x] Niet waar

> Herwegen helpt tegen de specifieke ongelijkheid waarop het gericht is, maar Remedie is expliciet dat geen enkele techniek een remedie is. Een reparatie kan de schade zelfs opzij schuiven in plaats van ze weg te nemen, en precies daarom telt meten achteraf net zo zwaar als meten vooraf.

### Een wervingsmodel wordt herbalanceerd zodat de trainingsdata niet langer naar geslacht scheeftrekt, maar het systeem wordt nog steeds gebruikt om automatisch elke sollicitant met een gat in de arbeidsgeschiedenis uit te filteren, wat vrouwen onevenredig treft. Wat is hier daadwerkelijk gebeurd?

- [x] De wiskunde is gerepareerd terwijl het onderliggende gebruik van het systeem onrechtvaardig bleef, een voorbeeld van wat Remedie ethics-washing noemt
- [ ] Het systeem is volledig eerlijk gemaakt omdat het probleem met de trainingsdata is opgelost
- [ ] De herbalancering heeft een nieuwe fout geïntroduceerd die niets met eerlijkheid te maken heeft
- [ ] Het filtercriterium heeft niets met een eerlijkheidskwestie te maken

> De reparatie van de trainingsdata is echt, en precies dat maakt dit geval gevaarlijk: het ziet opgelost uit. Maar het filter dat vrouwen onevenredig wegzeeft, draait er nog steeds onder, wat precies het patroon van ethics-washing van Remedie is: het technische werk dat verantwoord oogt terwijl de daadwerkelijke schade op zijn plek blijft.

### Remedie beschrijft drie dingen die een team kan doen aan een discriminerend systeem: meten, herontwerpen en een derde. Wat is dat?

- [x] Weigeren om het systeem überhaupt te bouwen of in te zetten, als dat het eerlijke antwoord is
- [ ] Het probleem melden aan een pr-team
- [ ] Het systeem een andere naam geven zodat het minder aandacht trekt
- [ ] Wachten tot de volgende modelupdate het automatisch oplost

> Een systeem een andere naam geven of het probleem naar pr doorschuiven, verandert hoe het eruitziet, niet wat het doet, en Remedie is duidelijk dat discriminatie zichzelf niet oplost bij een toekomstige update. De derde echte optie die ze noemt, is weigering: soms is het juiste antwoord het systeem helemaal niet te bouwen.

### Een eerlijkheidscontrole die een model bij lancering doorstond, blijft onbeperkt geldig, ongeacht hoe de bevolking die het systeem gebruikt in de loop van de tijd verandert.

- [ ] Waar
- [x] Niet waar

> Het slotpunt van Remedie is precies dat een model kan afdrijven als de bevolking waarop het gebruikt wordt verandert, dus is een controle die na lancering wordt weggelegd, een jaar later niets waard. Discriminatie verminderen moet onderhouden worden, niet eenmalig gecertificeerd.
