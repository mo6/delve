---
id: links-and-attachments
keeper: gatekeeper
name: De Postmeester
pass: 0.75
place: suspicious-attachment
---

# 🔗 Links, bijlagen, en de ruimte ertussen

De Postmeester heeft een stempel in zijn hand en heeft hem geen enkele keer gebruikt
zolang je hier staat.

"Twee van jullie per week komen hier beneden," zegt hij. "Ze willen weten welke bijlagen
veilig zijn om te openen. Verkeerde vraag. Stel een betere en ik laat je door."

**Een link is een bewering over een bestemming.** De tekst wordt door de afzender
geschreven. De bestemming óók. Er bestaat geen regel die zegt dat ze het eens moeten
zijn, en een aanvaller heeft geen enkele reden om ze dat te laten zijn.

`https://uwbank.example.com` kan overal ter wereld naartoe wijzen. Net als een knop met
**Document Bekijken**. Net als een logo. Het enige eerlijke deel van een link is het deel
waar je browser werkelijk naartoe gaat, en dat kun je zien vóór je je vastlegt: hover
op een computer, houd ingedrukt op een telefoon, en lees het van *rechts* af.

Lees van rechts, want daar zit de waarheid:

```
https://uwbedrijf.sharepoint.com.login-verify.ru/doc/94812
.................................^^^^^^^^^^^^^^^
het domein is login-verify.ru
```

Alles links van het echte domein is versiering die de aanvaller gekozen heeft om je op je
gemak te stellen. `uwbedrijf.sharepoint.com` is daar geen domein. Het is een *zin*.

> De laatste twee labels vóór de eerste enkele schuine streep vormen het domein. Al het
> overige is iemand die tegen je praat.

**Een bijlage is een programma dat je hebt ingestemd uit te voeren.** Niet altijd, maar
vaak genoeg dat het onderscheid niet aan je is om uit een bestandsnaam op te maken. Een
document kan macro's bevatten. Een PDF kan een script bevatten. Een archief kan de
extensie verbergen van wat erin zit. Een bestand dat `factuur.pdf` heet is misschien geen
PDF, want de naam is gewoon méér tekst die door de afzender geschreven is.

"Nu," zegt de Postmeester. "De betere vraag."

Niet *is deze bijlage veilig*. Dat kun je niet weten, en ik ook niet, en de mensen die je
vertellen dat zij het wel kunnen, verkopen iets.

**Verwachtte ik dit?**

Die vraag kun je wél beantwoorden. Er is geen expertise voor nodig, geen hoveren, geen
analyse. Als er een document binnenkomt dat je niet verwachtte, van wie dan ook, waarover
dan ook, dan kost controleren je één bericht via een ander kanaal, en niet controleren
kost dit gebouw zijn slechtste week.

Eindelijk stempelt hij iets.

"Verwacht: openen. Onverwacht: vragen. Onverwacht *en* dringend: harder vragen. Dat is
alles. Je zou versteld staan hoeveel mensen willen dat het ingewikkelder is, zodat ze een
excuus hebben om het niet te doen."

## Questions

### Waar in deze URL zit de werkelijke bestemming? `https://accounts.google.com.secure-login.example.net/verify`

- [ ] `accounts.google.com`; het staat vooraan en is het meest specifiek
- [x] `secure-login.example.net`, de laatste twee labels vóór de eerste enkele schuine streep
- [ ] `verify`; het laatste padelement is de bestemming
- [ ] De URL is ongeldig en zou niet werken

> Lees domeinen van rechts naar links. `accounts.google.com` is hier een *subdomein*, en
> `secure-login.example.net` heeft het precies zo genoemd zodat het vooraan zou staan,
> waar je het eerst leest.
>
> De URL is volkomen geldig; dat is nu juist het probleem. Dit is legaal, goedkoop, en
> vereist geen enkele inbraak bij Google.

### Door over een link te hoveren en de bestemming te controleren voordat je klikt, wordt de link veilig om aan te klikken.

- [ ] Waar
- [x] Niet waar

> Hoveren vertelt je waar de link *beweert* heen te gaan, wat een echte verbetering is ten
> opzichte van de tekst, maar het is één controle, geen oordeel. Legitieme sites worden
> gekaapt. Linkverkorters verbergen de bestemming volledig. Doorstuurketens beginnen
> ergens respectabels en eindigen daar niet.
>
> Hoveren brengt je van "geen informatie" naar "enige informatie". Het brengt je niet naar
> "veilig", en niets doet dat.

### Er komt een onverwachte factuur binnen als PDF, van een bedrijf waar je werkelijk nooit zaken mee heeft gedaan. Er is geen haast bij en er wordt niets gevraagd. Welke redenering telt?

- [ ] Laag risico; er is geen haast en geen verzoek, dus de gebruikelijke signalen ontbreken
- [ ] Hoog risico; facturen zijn de meest voorkomende malwaredrager
- [x] Het is onverwacht, en dat alleen al is genoeg om hem niet te openen
- [ ] Het hangt ervan af of je mailscanner hem gemarkeerd heeft

> "Verwachtte ik dit?" is de hele toets, en het is degene die werkt zonder expertise. Het
> antwoord is hier nee, dus open hem niet.
>
> De afwezigheid van haast is geen geruststelling; een geduldige aanvaller is een *erger*
> probleem dan een gehaaste. En leunen op de scanner draait de verhouding om: de scanner
> vangt wat al bekend is, en ú bent degene die beslist over het ding dat dat niet is.

### Een bestand met de naam `rapport.pdf` is een PDF.

- [ ] Waar
- [x] Niet waar

> Een bestandsnaam is tekst die gekozen is door wie hem verstuurde, precies zoals de
> zichtbare tekst van een link. Hij kan liegen, en er bestaan decennia aan trucs om hem
> overtuigend te laten liegen, dubbele extensies, tekens die de leesrichting omdraaien,
> archieven die verbergen wat erin zit tot het draait.
>
> Zelfde principe als de link: het deel dat de afzender schrijft is een bewering, geen
> feit.
