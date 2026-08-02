---
id: mfa
keeper: gatekeeper
name: De Tweede Factor
pass: 0.75
place: hardware-token
---

# 📱 De tweede factor

De poortwachter hier heeft geen naam die iemand gebruikt. Hij stelt iedereen twee vragen,
en heeft nog nooit genoegen genomen met een goed antwoord op alleen de eerste.

"Iets dat je weet," zegt hij. "Iets dat je hebt. Iets dat je bent. Breng mij er twee."

Dat is het hele idee. Een wachtwoord is *iets dat je weet*, en het probleem met dingen die
je weet, is dat ze op afstand van je afgenomen kunnen worden, geraden, gephisht, gelekt,
hergebruikt. **Meervoudige verificatie** eist een tweede ding van een andere *soort*, zodat
het stelen van het eerste niet genoeg is.

Twee wachtwoorden zijn geen twee factoren. Twee dingen die je weet is één factor, tweemaal.

Niet alle tweede factoren zijn gelijk, en de volgorde is het kennen waard:

| Factor | Oordeel |
|---|---|
| **Passkeys / hardwaresleutels** | Sterkst. Cryptografisch gebonden aan de echte site; een phishingpagina kan ze niet gebruiken, want zij ís de site niet. |
| **Codes uit een authenticator-app** | Goed. Offline, niet gekoppeld aan je telefoonnummer. |
| **Sms-codes** | Zwak, maar echt. Kwetsbaar voor simswapping en onderschepping. Beter dan niets; gebruik het als het al is wat er is. |
| **Push-meldingen met "goedkeuren?"** | Gemakkelijk. En de reden dat we dit gesprek voeren. |

> Een tweede factor maakt je niet onphishbaar. Het verandert wát de aanvaller moet stelen,
> en, bij passkeys, óf stelen überhaupt mogelijk is.

Want aanvallers pasten zich aan, natuurlijk. Dat doen ze altijd. Op twee manieren:

**MFA-moeheid**, ook wel push bombing. De aanvaller heeft je wachtwoord al. Hij logt keer
op keer in, en je telefoon licht keer op keer op, aan je bureau, in een vergadering, om
twee uur 's nachts, en opnieuw om kwart over twee. Ze hopen niet dat je erin trapt. Ze hopen
dat je *moe* bent, en dat je uiteindelijk op goedkeuren tikt om het te laten stoppen. Het
werkt vaak genoeg om bedrijven te hebben geveld waar je van gehoord heeft.

**Realtime doorgeven.** Een phishingpagina die je code op het moment dat je hem typt
doorstuurt naar de echte site. Je code was echt. Je login was echt. Hij was alleen niet van
je. Dit is waarom codes, zelfs goede uit een app, niet het einde van het verhaal zijn, en
waarom passkeys, die weigeren zich bij het verkeerde domein te authenticeren, de richting
zijn waarin dit gaat.

De poortwachter buigt zich voorover.

"Hoor dus de regel, want het is één zin en er valt niet over te onderhandelen. **Een
melding die je niet zelf veroorzaakt heeft, is een aanval die op dit moment plaatsvindt.**
Geen storing. Niet het systeem dat raar doet. Iemand heeft je wachtwoord, in zijn hand, nu,
en staat aan de deur op de bel te drukken."

"Weiger hem. Ga dan dat wachtwoord wijzigen, en vertel het iemand. In die volgorde."

## Questions

### Je telefoon trilt met een inlogverzoek. Je logt nergens op in. In de minuut erna trilt hij nog twee keer. Wat is er gebeurd, en wat doe je?

- [ ] Een storing; negeer de meldingen en ga verder
- [ ] Iemand heeft zijn gebruikersnaam verkeerd getypt; weiger en negeer het
- [x] Iemand heeft je wachtwoord en probeert binnen te komen; weiger, wijzig het wachtwoord, meld het
- [ ] Keur er één goed om te zien welk systeem het is, en onderzoek het dan

> Een ongevraagd goedkeuringsverzoek betekent dat iemand je wachtwoord al heeft. Dat is
> geen risico op een toekomstig lek; het is een lek dat nú loopt, en de herhaling is push
> bombing; ze wedden erop dat je zwicht om het te laten ophouden.
>
> Weigeren is nodig maar niet genoeg: ze hebben het wachtwoord nog steeds, en ze zijn
> vanavond terug. Wijzig het en meld het. En keur er nooit één goed "om te zien wat het is"
>; goedkeuren *ís* het slagen van de aanval.

### Zowel een wachtwoord als een beveiligingsvraag vereisen is meervoudige verificatie.

- [ ] Waar
- [x] Niet waar

> Beide zijn *iets dat je weet*, dus dat is één factor, tweemaal gevraagd. Erger nog:
> antwoorden op beveiligingsvragen zijn vaak te achterhalen, de meisjesnaam van je moeder
> en de straat waar je opgroeide zijn geen geheimen, dat is huiswerk.
>
> Meervoudig betekent factoren van verschillende *soorten*: iets dat je weet, plus iets dat je
> hebt, plus iets dat je bent.

### Waarom zijn passkeys en hardwaresleutels sterker dan codes uit een authenticator-app?

- [ ] De codes die ze genereren zijn langer en veranderen vaker
- [x] Ze zijn cryptografisch gebonden aan de echte site, dus een phishingpagina kan ze niet gebruiken
- [ ] Ze kunnen niet kwijtraken, in tegenstelling tot een telefoon
- [ ] Ze werken offline, waar app-codes een netwerkverbinding nodig hebben

> Domeinbinding is het hele voordeel. Een passkey authenticeert eenvoudigweg niet bij
> `micros0ft.com`, want dat is `microsoft.com` niet; de controle is cryptografisch, geen
> inschatting die je moe maakt. Dat verslaat realtime doorgeven volledig, want er is geen
> code om door te geven.
>
> Hardwaresleutels zijn juist véél makkelijker kwijt te raken dan een telefoon. En app-codes
> werken al offline; dat is hun voordeel boven sms, geen zwakte.

### Noem in een paar woorden waarom je sms-MFA toch moet aanzetten, ook al is het de zwakste optie.

- ?answer: het stopt de meeste aanvallen, beter dan niets, het stopt credential stuffing en massale phishing, het houdt de meeste aanvallers tegen, het stopt aanvallen op schaal
- ?reject: het is waardeloos, niet de moeite waard, laat het uit

> Sms is werkelijk de zwakste optie; simswapping is echt en niet moeilijk tegen een gericht
> slachtoffer. Maar "zwakst" is niet "waardeloos".
>
> Sms-MFA stopt nog steeds credential stuffing, massale phishing, en elke aanvaller die op
> schaal werkt en niet specifiek in ú geïnteresseerd is. Als een systeem alleen sms biedt,
> zet het aan. Het perfecte richt hier veel schade aan als vijand van het goede.
