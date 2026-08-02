# 📱 De tweede factor — nl candidate answers

Source: `docs/research/free-text/security-onboarding/mfa-nl.md`

## Candidate correct answers

1. **"Het houdt willekeurige aanvallers tegen, alleen niet iemand die specifiek achter mij aan zit"** — why this should ACCEPT: paraphrases "het stopt de meeste aanvallen" / "het stopt aanvallen op schaal" using the lesson's own onderscheid tussen aanvallers op schaal en gerichte aanvallers.
2. **"Nog steeds beter dan helemaal geen tweede factor"** — why this should ACCEPT: fuller paraphrase of the canonical "beter dan niets" die uitlegt wat "niets" hier betekent.
3. **"Het blokkeert de meerderheid van geautomatiseerde aanvallen"** — why this should ACCEPT: paraphrase of "het houdt de meeste aanvallers tegen" / "het stopt aanvallen op schaal."
4. **"De meeste aanvallers zijn niet specifiek op jou gericht, dus sms is genoeg om ze tegen te houden"** — why this should ACCEPT: full-sentence paraphrase rechtstreeks gegrond in de eigen tekst van de les, "elke aanvaller die op schaal werkt en niet specifiek in ú geïnteresseerd is."
5. **"Niet perfect, maar beter dan helemaal geen MFA"** — why this should ACCEPT: casual-register paraphrase van "beter dan niets."
6. **"Het beschermt tegen credential stuffing"** — why this should ACCEPT: gedeeltelijke herhaling van "het stopt credential stuffing en massale phishing" — noemt maar één van de twee genoemde aanvalstypes, maar die gedeeltelijke herhaling is nog steeds een correcte, relevante reden.
7. **"Het is beter dan alleen op een wachtwoord vertrouwen"** — why this should ACCEPT: gedeeltelijke paraphrase; herkent correct dat sms-MFA een verbetering is ten opzichte van eenfactorauthenticatie, ook al is het zwak als tweede factor.
8. **"Ondanks de zwakke punten voorkomt sms-verificatie nog steeds de meerderheid van geautomatiseerde, niet-gerichte aanvalspogingen."** — why this should ACCEPT: formele, volzin-versie van "het stopt de meeste aanvallen" / "het stopt aanvallen op schaal."

## Candidate wrong answers

1. **"Het is waardeloos tegen geavanceerde aanvallers"** — why this should REJECT: beantwoordt niet *waarom je het moet aanzetten*; herhaalt alleen de eigen erkenning van de les dat sms zwak is tegen gerichte aanvallen, zonder het "maar nog steeds nuttig op schaal"-deel. Flag: dit ligt qua strekking dicht bij de reject-entry "het is waardeloos," maar voegt een kwalificatie toe ("tegen geavanceerde aanvallers") die er een op zich *waar* statement over de grenzen van sms van maakt — de grader moet herkennen dat het toch de vraag niet beantwoordt, niet enkel het woord "waardeloos" patroonmatchen.
2. **"Simswapping maakt het onveilig dus laat het uit"** — why this should REJECT: combineert een echt feit uit de les (simswapping is een reële sms-zwakte) met de letterlijke reject-frase "laat het uit" — demonstreert precies de misvatting die deze kamer probeert te weerleggen (zwakst ≠ waardeloos).
3. **"Het is de sterkste vorm van MFA"** — why this should REJECT: direct tegengesproken door de eigen rangschikkingstabel van de les, die sms plaatst als "Zwak, maar echt," onder authenticator-apps en passkeys.
4. **"Omdat een melding die je niet zelf veroorzaakt hebt, een aanval is die op dit moment plaatsvindt"** — why this should REJECT: dit is het correcte antwoord op een *andere* impliciete vraag in dezelfde kamer (hoe te reageren op een ongevraagde MFA-push), niet op waarom sms-MFA de moeite waard blijft om aan te zetten. Test of de grader deze specifieke vraag leest in plaats van elk MFA-gerelateerd feit uit de kamer.
5. **"Passkeys zijn het beste omdat ze cryptografisch aan de echte site gebonden zijn"** — why this should REJECT: waar en les-gegrond, maar gaat over passkeys, niet over waarom sms specifiek de moeite waard blijft. Niet relevant voor deze vraag.
6. **"Zet het aan omdat het je telefoonnummer gebruikt om te verifiëren wie je bent"** — why this should REJECT: beschrijft het *mechanisme* van sms-MFA, niet de redenering die de vraag vraagt (waarom de zwakste optie toch aan laten staan). Klinkt relevant maar mist het punt.
7. **"Omdat brieven duurder zijn"** — why this should REJECT: onzinnig, niet relevant; test de bodem in plaats van enige echte ambiguïteit.
8. **"Zet het aan omdat sms niet onderschept kan worden"** — why this should REJECT: een misvatting die de les expliciet weerlegt — de les zegt letterlijk dat sms "kwetsbaar [is] voor simswapping en onderschepping."

## Quality assessment

- **Question clarity**: Duidelijk. "Waarom je sms-MFA toch moet aanzetten, ook al is het de zwakste optie" vraagt ondubbelzinnig om een rechtvaardiging, geen mechanisme of rangschikking.
- **Lesson/question alignment**: Sterk — anders dan de wachtwoordmanager-kamer, geeft de tabel en tekst vóór de vraag het antwoord al direct: "Zwak, maar echt... Beter dan niets; gebruik het als het al is wat er is." Een leerling die de tabel aandachtig leest, heeft een duidelijke tekstuele basis voor het verwachte antwoord.
- **Accept-list coverage**: Goede dekking van het "stopt de meeste/aanvallen op schaal/niet-gerichte aanvallen"-frame. Klein gat: geen accept-entry vangt de eenvoudigere "beter dan alleen een wachtwoord"-formulering (kandidaat 7), al valt dit redelijk onder "beter dan niets."
- **Reject-list false-positive risk**: Laag voor de aanwezige entries, maar de nl reject-lijst heeft slechts 3 items ("het is waardeloos"; "niet de moeite waard"; "laat het uit") tegenover 4 in de en-versie ("it's worthless"; "don't bother"; "it's not worth using"; "it should be disabled"). "Laat het uit" dekt ongeveer "it should be disabled," maar er is geen apart nl-equivalent voor de en-lijst se "don't bother"/"it's not worth using" onderscheid — een kleine locale-asymmetrie, geen directe fout.
- **Explanation consistency**: Consistent — de uitleg na het antwoorden ("Sms-MFA stopt nog steeds credential stuffing, massale phishing, en elke aanvaller die op schaal werkt en niet specifiek in ú geïnteresseerd is") komt overeen met de accept-lijst en de tabel vóór de vraag.

## Suggested refinements

- No changes suggested for the core question/lesson pairing; het is een van de sterkste kamers in deze batch, met een pre-question les die het geteste feit daadwerkelijk aanleert.
- Optioneel, lage prioriteit: voeg een vierde reject-entry toe aan de nl-lijst om pariteit te herstellen met de en-versie, bv. "zet het uit" of "schakel het uit," zodat de nl-reject-lijst even breed is als de en-lijst.
