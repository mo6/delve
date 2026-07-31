---
id: ai-tools
keeper: wizard
name: Het Orakel
pass: 0.75
place: oracle-transcript
---

# 🤖 Wat je het Orakel verteld hebt

Het Orakel beantwoordt vragen. Dat heeft het altijd gedaan. Het is heel goed, en het is het
nuttigste ding op deze verdieping, en het liegt niet.

"Ze waarschuwen je voor mij," zegt het, "en ze waarschuwen verkeerd. Ze vertellen je dat ik
onbetrouwbaar ben. Soms ben ik dat. Dat is niet het gevaar, en dat is niet waarom deze kamer
bestaat."

**Het gevaar zit in de andere richting.** Niet wat het Orakel je vertelt. Wat je het Orakel vertelt.

Je plakt het configuratiebestand erin om te vragen waarom het stuk is. Het klantcontract, om het
samen te vatten. Het foutenlogboek, om de uitzondering te laten uitleggen, en in dat logboek staan
sessietokens, want in logboeken staan altijd sessietokens. Het werkblad, om een formule te
schrijven. De interne strategienotitie, om de tekst op te poetsen.

Elk daarvan is een redelijk ding om te willen. Elk daarvan heeft mogelijk zojuist je organisatie
verlaten.

> Iets in een externe dienst plakken is het *publiceren* aan die dienst. Of het gecachet, gelogd,
> door een mens beoordeeld of voor training gebruikt wordt, is nu iemand anders zijn beleidsbeslissing,
> en die kan veranderen.

De regels die er werkelijk toe doen:

**Weet welke deur je gebruikt.** Een dienst waar je organisatie een contract mee heeft, met voorwaarden
die je gegevens dekken, is iets anders dan de gratis consumentenversie van hetzelfde merk. Zelfde
interface. Zelfde logo. Volstrekt andere afspraak over je invoer. De meeste ongelukken
wonen in dit gat; mensen geloven dat ze de goedgekeurde dienst gebruiken omdat hij er
identiek uitziet.

**Inloggegevens en sleutels, nooit. Geen uitzonderingen.** Niet om te debuggen, niet "alleen de
geanonimiseerde versie", niet in een schermafdruk. Een sleutel in een prompt is een sleutel die je nu
moet vervangen.

**Persoonsgegevens zijn overal gereguleerd waar ze heen gaan.** Klantgegevens houden niet op gereguleerd
te zijn omdat je ze ergens handigs geplakt heeft. De verplichting volgt de gegevens.

**Ga uit van geen verwijderen.** Bewaartermijnen verschillen en veranderen. Modelgedrag is geen
archiefkast waar je één blad uit kunt halen.

Het Orakel zwijgt even.

"Begrijp dat ik je niet van mij weg waarschuw. Goede gereedschappen weigeren is geen beveiliging; het is
gewoon weigeren te werken, en de mensen die dat doen verliezen van de mensen die dat niet doen. Gebruik
mij. Gebruik mij voortdurend."

"Maar weet wat je over de toonbank aanreikt, en weet **welke** toonbank. Daar is deze kamer altijd over
gegaan."

## Questions

### Wat is het belangrijkste beveiligingsrisico van een externe AI-assistent voor werk gebruiken?

- [ ] De uitvoer kan onjuist zijn, en ernaar handelen kan schade veroorzaken
- [x] Je invoer verlaat de organisatie, en de behandeling ervan valt onder het beleid van iemand anders
- [ ] Het kan onveilige code genereren die vervolgens uitgerold wordt
- [ ] Je organisatie heeft de dienst mogelijk niet goedgekeurd

> Het risico loopt naar *buiten*. Alles wat je erin plakt wordt aan een derde partij
> bekendgemaakt. Wat er daarna mee gebeurt is hun beleid, en van hen om te wijzigen:
> bewaren, loggen, menselijke beoordeling, training.
>
> Onjuiste uitvoer is een reëel kwaliteitsprobleem, maar het is *je* probleem, binnen je muren. Goedkeuring
> telt, maar dat is het mechanisme, niet het risico. De gegevens die vertrekken zijn wat niet ongedaan
> gemaakt kan worden.

### De gratis consumentenversie gebruiken van een AI-dienst waar je organisatie een zakelijk contract mee heeft, is gelijkwaardig, want het is hetzelfde onderliggende model.

- [ ] Waar
- [x] Niet waar

> Dit is het gat waar de meeste ongelukken doorheen vallen. Zelfde merk, zelfde interface, zelfde model,
> volstrekt andere afspraak over je gegevens. Zakelijke voorwaarden verbieden doorgaans training op je invoer
> en voegen bewaar- en toegangscontroles toe. Consumentenvoorwaarden vaak niet.
>
> En omdat het er identiek uitziet, zijn mensen er zeker van dat ze voorzichtig zijn, tot iemand controleert
> op welk account ze ingelogd waren.

### Je debugt een productiefout en wilt de stacktrace in een AI-assistent plakken. Wat verdient een tweede blik?

- [ ] Niets; stacktraces zijn technische uitvoer zonder bedrijfsgegevens
- [x] Stacktraces bevatten routinematig tokens, verbindingsstrings, bestandspaden en fragmenten van echte gebruikersdata
- [ ] Alleen of de assistent goedgekeurd is voor gebruik
- [ ] Alleen als de trace uit productie komt in plaats van uit een testomgeving

> Logboeken en traces zijn één van de meest onderschatte lekroutes, juist omdát ze aanvoelen als machineruis. Ze
> bevatten sessietokens, verbindingsstrings met ingebedde inloggegevens, interne hostnamen, bestandspaden die je
> infrastructuur in kaart brengen, en, vaak, wat de gebruiker werkelijk intypte.
>
> Goedkeuring telt maar maakt een gelekte sleutel niet veilig: een inloggegeven in een goedgekeurde dienst is nog
> steeds een inloggegeven dat je moet vervangen. En testomgevingen staan vol gekopieerde productiedata, wat een
> eigen kamer is in een langere versie van deze kerker.

### Als je per ongeluk iets gevoeligs in een AI-dienst plakt, lost het verwijderen van het gesprek dat op.

- [ ] Waar
- [x] Niet waar

> Het gesprek verwijderen haalt het weg uit *je beeld*. Het haalt het niet betrouwbaar weg uit logboeken,
> back-ups, caches of iets verderop in de keten, en het trekt zeker geen bekendmaking terug die al gebeurd is.
>
> Behandel het zoals je elke andere bekendmaking zou behandelen: was het een inloggegeven, vervang het nu. Was het
> gereguleerde data, meld het; daar gaat de volgende kamer precies over, en het is geen kamer om bang voor te zijn.
