---
id: devices
keeper: gatekeeper
name: Rook de Nachtwaker
pass: 0.75
place: usb-stick
---

# 🔌 Het ding dat je meedraagt

Rook heeft de blik van iemand die heel veel mensen heel veel dingen heeft zien laten liggen.

"Alles boven deze verdieping ging over aanvallers," zegt hij. "Slimme. Geduldige. Nu doen we
de saaie verdieping, waar je de laptop in de trein laat liggen."

Je apparaat is een sleutel tot alles waar je toegang toe heeft. Geen kopie van je werk, een
**sleutel**. Hij is geauthenticeerd, hij is vertrouwd, en hij is klein genoeg om in een taxi
achter te laten.

**Versleuteling is degene die een ramp in papierwerk verandert.** Met volledige
schijfversleuteling aan is een gestolen laptop een verloren *voorwerp*, vervelend, duur,
verzekerd. Zonder is het elk bestand dat je had, plus de sessies in je browser, plus een melding
die je moet doen. Het zit tegenwoordig vrijwel overal ingebouwd en staat standaard aan, wat
betekent dat de enige echte vraag is of je het ooit heeft uitgezet.

**Vergrendel je scherm.** Versleuteling beschermt een apparaat dat *uit* staat. Een gestolen
ontgrendelde laptop is ontgrendeld. Het gat tussen "ik haal even koffie" en "iemand ging aan mijn
bureau zitten" is de meest gebruikte kwetsbaarheid in dit gebouw, en hij is van wie er langsloopt.

**Updates zijn de saaie die er werkelijk toe doet.** De kwetsbaarheden die op dit moment
uitgebuit worden zijn meestal niet nieuw. Ze zijn maanden oud, gepubliceerd, gepatcht, en werken
nog steeds, omdat de patch in een melding zit die je elf keer heeft weggeklikt. "Herinner me
morgen" is een besluit, en je hebt het elf keer genomen.

**Openbare wifi is prima, en dat verrast mensen.** HTTPS betekent dat het netwerk van het
koffietentje ziet waar je heen ging, niet wat je deed. Het oude advies om openbare wifi te vrezen
stamt grotendeels van vóór universele versleuteling. Wat wél bijt is het **inlogportaal dat je iets
wil laten installeren**, en de persoon achter je met vrij zicht op je scherm. Meekijken is geen
grap; het is de enige aanval in deze hele training waar geen enkele technologie voor nodig is.

> De dreiging in de trein is geen hacker op het netwerk. Het is de passagier achter je die je scherm
> leest, en het moment waarop je de laptop op tafel laat liggen.

**USB-sticks op parkeerterreinen zijn ook geen grap**, en ja, dit werkt nog steeds. Net als "gratis"
oplaadkabels en dubieuze adapters. De regel is saai: als je niet weet waar het vandaan komt, gaat het
er niet in.

Rook haalt zijn schouders op.

"Niets hiervan is slim. Daarom is dit de verdieping waar iedereen zakt. Je herkent een phishingmail
op tien meter afstand en laat het ding alsnog ontgrendeld liggen in een broodjeszaak."

## Questions

### Je werklaptop wordt van een cafétafel gestolen terwijl hij ontgrendeld is. Volledige schijfversleuteling staat aan. Welke bescherming biedt die versleuteling?

- [ ] Volledige; de schijf is versleuteld, dus de gegevens zijn onleesbaar
- [x] Vrijwel geen in dit scenario; versleuteling beschermt een uitgeschakeld apparaat, en dit staat ontgrendeld aan
- [ ] Gedeeltelijke; het beschermt bestanden maar geen browsersessies
- [ ] Dat hangt ervan af of de dief de machine herstart

> Volledige schijfversleuteling beschermt gegevens *in rust*. Een draaiende, ontgrendelde machine
> heeft alles al ontsleuteld; de dief erft je ingelogde sessie, je bestanden, je browser, je
> geauthenticeerde alles.
>
> Versleuteling is essentieel en is niet wat je hier redt. De schermvergrendeling is dat. En daarom
> verslaat de saaie gewoonte de indrukwekkende technologie.
>
> (Herstarten zou de versleuteling juist *activeren*, de fout van de dief, niet zijn plan.)

### Openbare wifi gebruiken voor werksystemen is een serieus risico dat waar mogelijk vermeden moet worden.

- [ ] Waar
- [x] Niet waar

> Grotendeels achterhaald advies. Nu vrijwel al het verkeer HTTPS is, ziet de netwerkbeheerder
> welke sites je benaderde, niet wat je verstuurde; de afluisteraanval waarvoor deze waarschuwing
> gebouwd is, werkt grotendeels niet meer.
>
> De echte risico's op openbare wifi zijn anders en worden minder besproken: inlogportalen die je
> vragen een certificaat of app te installeren, en de persoon achter je die je scherm leest. Let
> daarop. Het netwerk zelf is grotendeels prima.

### Waarom zijn bekende, gepatchte kwetsbaarheden voor de meeste organisaties gevaarlijker dan pas ontdekte?

- [ ] Gepatchte kwetsbaarheden zijn beter gedocumenteerd, dus makkelijker uit te buiten
- [x] Ze zijn bewapend en geautomatiseerd, en ongepatchte machines staan overal; een gepubliceerde patch is een openbare plattegrond
- [ ] Pas ontdekte kwetsbaarheden worden meestal eerst privé gemeld
- [ ] Aanvallers geven de voorkeur aan oude kwetsbaarheden omdat er minder op gelet wordt

> Een patch publiceren publiceert de kwetsbaarheid. Binnen dagen is er werkende exploitcode; binnen
> weken zit het in geautomatiseerde gereedschapskisten die alles scannen. Ondertussen zit de patch in
> een melding die iemand blijft uitstellen.
>
> Zerodays zijn per incident werkelijk enger en verdwijnend zeldzaam; ze worden besteed aan doelwitten
> die het besteden waard zijn. De maand oude ongepatchte browser is wat je werkelijk velt, en "herinner
> me morgen" is wat hem daar laat staan.

### Noem in een paar woorden wat de juiste actie is bij een ongelabelde USB-stick op het parkeerterrein van kantoor.

- ?answer: inleveren bij beveiliging, geven aan beveiliging, melden bij beveiliging, hem er nergens in steken, inleveren
- ?reject: in een geïsoleerde machine steken, de bestandsnamen bekijken, laten liggen, negeren

> Kwaadaardige USB-apparaten hebben je niet nodig om een bestand te openen. Sommige doen zich voor als
> toetsenbord en typen commando's zodra ze aangesloten worden; er bestaat geen "even kijken" dat veilig
> is, en bestandsnamen zijn juist het lokaas.
>
> "Geïsoleerde machine" is de val voor technische mensen: het klinkt grondig, wat de meeste mensen
> geïsoleerd noemen is dat niet, en dit is een hobby en geen functie. Laten liggen is passief; de
> volgende persoon raapt hem op, en dáárvoor is hij neergelegd.
>
> **Plaatshouder:** vervang `#security-help` door het echte kanaal van je organisatie.
