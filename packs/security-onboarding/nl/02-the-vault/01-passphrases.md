---
id: passphrases
keeper: wizard
name: Entropie, Hoedster der Sleutels
pass: 0.75
place: sticky-note
---

# 🔑 Lengte verslaat slimheid

Entropie is geen mens. Het is een zeer oud wezen in de vorm van een mens, en het telt
onder het praten door, altijd, zachtjes.

"Je is geleerd slim te zijn," zegt het. "Een drie in plaats van een E. Een apenstaartje
in plaats van een A. Een uitroepteken erbij, want het vakje eiste een symbool.
`W@chtw0ord!`, en je voelde je *sluw*, nietwaar?"

Even stopt het met tellen.

"Elke truc die je geleerd is, hebben de kraakwoordenboeken in één middag geleerd. Het
zijn regels in een configuratiebestand. `a→@`. `e→3`. `o→0`. Plak er een jaartal
achter. Zet de eerste letter als hoofdletter, want het vakje eiste een hoofdletter en je
bent iemand die precies het minimum doet dat het vakje eist."

Wat een geheim moeilijk raadbaar maakt, is niet hoe vreemd het er voor ú uitziet. Het is
hoeveel mogelijkheden een machine moet proberen. Die hoeveelheid heeft een naam, en het
is ook de naam van het wezen.

Een wachtwoord dat gebouwd is uit een gewoon woord plus voorspelbare verminking heeft
bijna geen entropie, *hoe onleesbaar het er ook uitziet*, omdat de verminking een bekende
bewerking is van een bekend woord. De machine raadt niet teken voor teken. Hij raadt
`gewoon woord × bekende regels`, en die ruimte is minuscuul.

Een **wachtwoordzin**, vier of vijf niet-verwante woorden, is daarbij vergeleken
enorm. Niet omdat woorden magisch zijn, maar omdat het aantal manieren om vijf
niet-verwante woorden uit een grote woordenschat te kiezen een heel groot getal is, en
de aanvaller krijgt geen sluiproute.

```
  W@chtw0ord!2024              ziet er sterk uit.  Gekraakt in seconden.
  paard accu nietje correct    ziet er dwaas uit.  Niet gekraakt.
```

> Complexiteit is hoe een wachtwoord er voor *je* uitziet. Entropie is wat het een
> *machine* kost. Slechts één van die twee doet werk.

De andere helft is erger, en simpeler:

**Lengte verslaat slimheid, maar uniciteit verslaat lengte.** Een schitterende
wachtwoordzin van veertig tekens die op twee plekken gebruikt wordt, is op allebei die
plekken een slecht wachtwoord. Wanneer één van die sites gelekt wordt, en één ervan zál
gelekt worden, neemt de aanvaller je schitterende wachtwoordzin en probeert hem overal
waar je verder bestaat. Dit heet credential stuffing, het is volledig geautomatiseerd, en
het is de betrouwbaarste aanval in deze hele kerker.

"Dus," zegt Entropie, weer tellend. "Lang. Uniek. Elke keer opnieuw."

Het kijkt je aan met iets dat op medelijden lijkt.

"En dat kun je niet. Niet voor tweehonderd accounts. Niet met een menselijk geheugen.
En daarom bestaat de volgende kamer, en daarom laat ik je erdoor."

## Questions

### Waarom biedt `Tr0ub4dor&3` slechte beveiliging, ondanks dat het er complex uitziet?

- [ ] Het is te kort; er zijn minstens zestien tekens nodig
- [x] Het is een woordenboekwoord met voorspelbare vervangingen, die kraaktools standaard toepassen
- [ ] Het bevat niet genoeg verschillende symbolen
- [ ] Het eindigt op een cijfer, een bekend zwak patroon

> De verminking is het probleem. `o→0`, `a→4`, `e→3`, een cijfer erachter; dat zijn
> *regels in een configuratiebestand*, automatisch toegepast op elk woord in het
> woordenboek. De aanvaller raadt geen elf tekens; hij raadt "troubadour, verminkt", en
> die ruimte is klein genoeg om snel uit te putten.
>
> Lengte is een echte factor, maar het is niet wat hier mis is; de verminking zou ook
> bij zestien tekens de zwakte zijn. En "meer symbolen" is precies het instinct dat dit
> wachtwoord in de eerste plaats voortbracht.

### Een wachtwoord dat lang en voor een mens moeilijk leesbaar is, is daarmee moeilijk te kraken voor een computer.

- [ ] Waar
- [x] Niet waar

> Dit is de kernverwarring, en bijna elk slecht wachtwoordbeleid is erop gebouwd.
> Onleesbaarheid voor mensen en moeilijkheid voor machines zijn ongerelateerde
> eigenschappen.
>
> `W@chtw0ord!` is onleesbaar en triviaal. `paard accu nietje correct` is prima leesbaar
> en enorm veel moeilijker. De machine worstelt niet met vreemdheid; hij worstelt met
> *hoeveelheid mogelijkheden*.

### Je gebruikt één werkelijk uitstekende wachtwoordzin van 40 tekens, uniek voor je, nergens anders ter wereld, voor al je accounts. Wat is het risico?

- [ ] Laag; de wachtwoordzin heeft ruim genoeg entropie om kraken te weerstaan
- [x] Ernstig; één lek bij welke site dan ook geeft een aanvaller al je andere accounts
- [ ] Middelmatig; het hangt ervan af of de sites wachtwoorden goed opslaan
- [ ] Laag, mits geen van de sites een waardevol doelwit is

> Entropie beschermt tegen *raden*. Het doet niets tegen een site die gelekt wordt en je
> wachtwoord rechtstreeks weggeeft; op dat moment is sterkte irrelevant, want niemand
> hoefde iets te raden.
>
> Daarna wordt het automatisch overal herhaald. Dat is credential stuffing, en hergebruik
> is het enige dat het laat werken. Goede hashing helpt bij de gelekte site, maar je kunt
> het niet controleren, je hoort *achteraf* dat het slecht was, en "geen van mijn sites is
> waardevol" negeert dat de onbelangrijke site precies is waar de aanvaller begint.

### Wachtwoorden horen elke 90 dagen routinematig gewijzigd te worden.

- [ ] Waar
- [x] Niet waar

> Langlopend beleid, inmiddels ingetrokken door de mensen die het bedacht hebben; zowel
> NIST als het Britse NCSC raden routinematig verlopen inmiddels af.
>
> Het werkt voorspelbaar averechts: gedwongen om steeds te wijzigen kiezen mensen zwakkere
> wachtwoorden en tellen ze door (`Zomer2024!` → `Herfst2024!`), wat precies is wat een
> aanvaller als volgende raadt. Het leert iedereen bovendien wachtwoorden als wegwerpartikel
> te zien in plaats van als iets waardevols.
>
> Wijzig een wachtwoord wanneer er een *reden* is, een lek, een vermoeden, een gedeeld
> geheim. Niet omdat een kalender het zei.
