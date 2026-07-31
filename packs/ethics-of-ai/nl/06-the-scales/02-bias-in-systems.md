---
id: bias-in-systems
keeper: gatekeeper
name: De Scheefstand
pass: 0.75
---

# Bevooroordeeldheid in systemen

De Scheefstand kantelt een plank totdat de boeken één kant op vallen. "Bevooroordeeldheid is niet altijd haat," zegt die. "Vaak is het geschiedenis, geautomatiseerd."

"Eerst de definitie, want mensen gebruiken dit woord slordig." De Scheefstand recht de plank. "Niet elk verschil in behandeling is discriminatie. Een zestienjarige minder rekenen voor autoverzekering dan een veertigjarige is een verschil in behandeling, en dat is niet waar we het hier over hebben. Discriminatie, in de betekenis die hier telt, is een verschil in behandeling gekoppeld aan groepslidmaatschap, dat mensen benadeelt voor iets wat ze niet zelf gekozen hebben en waarop ze niet beoordeeld zouden moeten worden. Dat is de moreel geladen versie. Houd die twee uit elkaar."

"Bevooroordeeldheid komt op ruwweg drie manieren een systeem binnen." Die telt boeken van de plank. "Eén: de trainingsdata zelf legt al een patroon vast. Voer een wervingsmodel een decennium aan echte aannamebeslissingen van een bedrijf, en het leert wie het bedrijf echt aannam, met alle gebreken erbij. Dit ligt dicht bij wat er gebeurde bij het interne recruitmenttool van een groot warenhuisbedrijf: getraind op jaren cv's van een personeelsbestand dat zwaar mannelijk was scheefgetrokken, leerde het zichzelf dat cv's met vermeldingen van vrouwenactiviteiten een negatief signaal waren, en het moest worden geschrapt."

"Twee: woordassociaties. Modellen die taal leren uit enorme hoeveelheden gewone tekst, pikken de associaties op die *in* die tekst zitten, inclusief de associaties die je liever niet had gezien; bepaalde functietitels clusteren bij één geslacht, bepaalde namen clusteren bij aannames over afkomst. Het model heeft de associatie niet uitgevonden. Het heeft ze gevonden, omdat ze er al waren."

"Drie: proxy's. Een kredietscoringmodel vraagt misschien nooit direct naar etniciteit of buurt, en reproduceert toch hetzelfde patroon door te leunen op een variabele, zoals postcode, die er nauw genoeg mee correleert om hetzelfde werk te doen. Statistische kredietscoring heeft precies dit bezwaar van toezichthouders gekregen, en om precies dezelfde reden: het model heeft het verboden veld niet nodig om het effect ervan te reconstrueren."

"Niets van dit alles vereist dat iemand kwaadaardig is." De Scheefstand zet het laatste boek terug. "Een algoritme heeft geen eigen mening om bevooroordeeld mee te zijn. Het heeft alleen wat je erin gestopt hebt, en wat je erin gestopt hebt, bevat meestal elk onbekeken patroon van de wereld waarop het getraind is. Vooroordeel erin, vooroordeel eruit, alleen met meer vertrouwen in de uitkomst dan de invoer ooit heeft verdiend."

> Een algoritme heeft geen kwaad opzet nodig om te discrimineren; het heeft alleen data nodig die het patroon al bevat, en niemand die het controleerde.

## Questions

### Een groot warenhuisbedrijf schrapt een intern wervingsmodel nadat het ontdekt dat het cv's met vermeldingen van vrouwenactiviteiten benadeelde. Wat is de meest accurate verklaring voor waarom dit gebeurde?

- [x] Het was getraind op jaren van de eigen aannamebeslissingen van het bedrijf, die al zwaar mannelijk scheefgetrokken waren
- [ ] Een programmeur heeft het model opzettelijk gecodeerd om vrouwen te benadelen
- [ ] Het model haperde door een softwarefout die niets te maken had met de trainingsdata
- [ ] Cv's met vermelding van een hobby worden automatisch benadeeld door alle wervingsmodellen

> Er was geen opzettelijke codering en geen ongerelateerde fout, en het patroon was specifiek voor genderactiviteiten, niet voor hobby's in het algemeen. Het model leerde het patroon dat al aanwezig was in de eigen eerdere aanname van het bedrijf, en dat is precies het punt: niemand hoefde het te bedoelen om te laten gebeuren.

### Een zestienjarige bestuurder een andere verzekeringspremie laten betalen dan een veertigjarige bestuurder is een voorbeeld van discriminatie in de moreel geladen betekenis die De Scheefstand beschrijft.

- [ ] Waar
- [x] Niet waar

> De Scheefstand begint met het scheiden van gewone verschillen in behandeling, zoals leeftijdsgebaseerde verzekeringsprijzen, van de moreel geladen betekenis van discriminatie: iemand benadelen op basis van groepslidmaatschap voor iets wat die persoon niet zelf koos en waarop die niet beoordeeld zou moeten worden. Niet elke andere uitkomst voldoet daaraan.

### Een kredietscoringmodel kan uiteindelijk patronen reproduceren die aan etniciteit gekoppeld zijn, zelfs als etniciteit nooit een van de invoervariabelen is.

- [x] Waar
- [ ] Niet waar

> Dit is het proxyprobleem: een variabele zoals postcode kan nauw genoeg correleren met etniciteit dat leunen erop hetzelfde discriminerende patroon reproduceert dat het model nooit direct heeft gevraagd.

### De Scheefstand noemt drie manieren waarop bevooroordeeldheid doorgaans een systeem binnenkomt. Welke van deze past bij een ervan?

- [x] Een model dat leunt op een variabele, zoals postcode, die nauw correleert met een beschermd kenmerk dat het nooit direct gebruikt
- [ ] Een model dat op te veel data in totaal getraind is
- [ ] Een model dat te traag werkt voor beslissingen in real time
- [ ] Een model dat in meer dan één land wordt ingezet

> Datavolume, snelheid en geografisch bereik zijn niet de drie routes die De Scheefstand noemt. Proxy's, zoals een postcode die etniciteit vervangt, zijn een van de drie, naast bevooroordeelde trainingsdata en aangeleerde woordassociaties.
