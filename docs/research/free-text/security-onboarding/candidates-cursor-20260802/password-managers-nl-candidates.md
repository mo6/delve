# Eén slot dat het forceren waard is — nl candidate answers

Source: `docs/research/free-text/security-onboarding/password-managers-nl.md`

## Candidate correct answers

1. **"synchronisatie tussen apparaten"** — why this should ACCEPT: Canonieke accept-entry.
2. **"een hoofdzin"** — why this should ACCEPT: Korte vorm van "beveiligd met een hoofdzin"; les benadrukt één onthoudbare zin.
3. **"werkt buiten de browser"** — why this should ACCEPT: Directe accept-entry.
4. **"dekt ook apps"** — why this should ACCEPT: Informele parafrase van "dekt meer dan websites".
5. **"versleutelde kluis"** — why this should ACCEPT: Les leert de versleutelde kluis vs geheugen; betekenis-aligned. Flag: keyword-floor kan falen.
6. **"unieke willekeurige wachtwoorden per site"** — why this should ACCEPT: Kern van wat Ives verkoopt. Flag: browsers kunnen dat ook deels.
7. **"werkt in elke browser"** — why this should ACCEPT: Accept-lijstidee.
8. **"één zin opent al het andere"** — why this should ACCEPT: Formele herformulering van het single-secret model.

## Candidate wrong answers

1. **"niets / het is hetzelfde"** — why this should REJECT: Expliciete reject.
2. **"alle eieren in één mand"** — why this should REJECT: Het bezwaar dat Ives weerlegt; geen voordeel t.o.v. browsers.
3. **"wachtwoorden veilig hergebruiken"** — why this should REJECT: Tegengesteld aan de les.
4. **"kortere wachtwoorden"** — why this should REJECT: Giswerk; managers maken langere random secrets mogelijk.
5. **"beter dan niets"** — why this should REJECT: MFA/sms-acceptidee, geen manager-vs-browser verschil. Flag: soepele grader.
6. **"de transactie"** — why this should REJECT: Juist voor targeted, hier fout.
7. **"browser-autofill"** — why this should REJECT: Dat geeft de browser al; geen differentiator.
8. **"spaghetti"** — why this should REJECT: Off-topic floor test.

## Quality assessment

- Question clarity: Duidelijke vergelijkingsvraag, maar de les noemt browserwachtwoorden niet.
- Lesson/question alignment: Zwak. Les = risico concentreren in een kluis; browser-gaten staan alleen in de uitleg.
- Accept-list coverage: Plausibele goede antwoorden (`versleutelde kluis`, `unieke wachtwoorden`) ontbreken op de lijst.
- Reject-list false-positive risk: Laag.
- Explanation consistency: Uitleg past bij accept-lijst; les leert de vergelijking niet.

## Suggested refinements

- Korte lescontrast met browseropslag toevoegen, of de vraag herijken op wat de les wél leert.
- Accept toevoegen: `versleutelde kluis`, `unieke willekeurige wachtwoorden`, `nooit zelf typen`.
