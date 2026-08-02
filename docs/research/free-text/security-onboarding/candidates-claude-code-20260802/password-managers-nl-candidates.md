# 🔐 Eén slot dat het forceren waard is — nl candidate answers

Source: `docs/research/free-text/security-onboarding/password-managers-nl.md`

## Candidate correct answers

1. **"Het werkt ook op mijn telefoon, niet alleen in Chrome"** — why this should ACCEPT: casual paraphrase of "synchronisatie tussen apparaten" / "synchroniseert tussen apparaten" — names the same distinguishing capability without the accept list's exact words.
2. **"Overal synchroon"** — why this should ACCEPT: terse two-word direct paraphrase of the canonical answer "synchronisatie tussen apparaten."
3. **"Je hebt een hoofdwachtwoord nodig om het te openen"** — why this should ACCEPT: paraphrases "beveiligd met een hoofdzin." "Hoofdwachtwoord" is the common synonym learners are more likely to actually type than the lesson's own word "hoofdzin."
4. **"Het kan ook dingen als wifi-wachtwoorden en beveiligde notities bewaren, niet alleen inloggegevens"** — why this should ACCEPT: a concrete instantiation of "dekt meer dan websites," giving examples of non-website secrets.
5. **"Als ik van browser wissel, heb ik nog steeds toegang tot mijn wachtwoorden"** — why this should ACCEPT: restates "werkt in elke browser" / "werkt buiten de browser" in plain, first-person terms.
6. **"De gegenereerde wachtwoorden zijn sterker, omdat het daar speciaal voor gebouwd is"** — why this should ACCEPT: uses none of the accept list's exact words but is grounded in the explanation's claim that browser opslag's "genereren... zwakker" is. A legitimate distinguishing feature not currently in the accept list (see coverage gap below).
7. **"Het is niet afhankelijk van of ik ingelogd ben in mijn browser"** — why this should ACCEPT: paraphrases the explanation's "beschermd door je ingelogde sessie in plaats van een zin die je actief opgeeft" — correctly identifies the manager's protection model is independent of browser session state.
8. **"Een wachtwoordmanager is bereikbaar vanaf elk apparaat en elke browser, terwijl in de browser opgeslagen wachtwoorden meestal aan die ene browser vastzitten."** — why this should ACCEPT: full-sentence, formal-register version of "werkt in elke browser," explicitly naming the contrast the question asks for.

## Candidate wrong answers

1. **"Het is eigenlijk hetzelfde als de browser die mijn wachtwoorden onthoudt"** — why this should REJECT: directly contradicts the question's point and mirrors the reject list's "het is hetzelfde," just paraphrased rather than copied.
2. **"Niets, de browser is net zo goed"** — why this should REJECT: a paraphrased instance of the bare reject entry "niets." A substring-based offline floor checking for the literal word "niets" would (correctly, here) catch this — the real risk case is the inverse (see quality assessment).
3. **"Het stopt phishing"** — why this should REJECT: this is the answer to the *MFA* room's discussion of passkeys resisting phishing, not a property of password managers over browser opslag. Tests whether the grader reads this specific question rather than pattern-matching "security tool does something good."
4. **"Het is gratis"** — why this should REJECT: true, and even lifted from this room's own closing line ("Gratis, overigens"), but it doesn't answer what a manager gives you that the browser doesn't — browser-opslag is free too. Flag: tempting for a lenient grader precisely because it's lesson-text, even though non-responsive.
5. **"Het onthoudt mijn wachtwoord zodat ik het niet vergeet"** — why this should REJECT: exactly what browser-saved passwords also do. Sounds related but misses the actual point — the question asks for something the browser *doesn't* give.
6. **"Het maakt automatisch back-ups van mijn foto's"** — why this should REJECT: off-topic, nonsensical answer; tests the floor rather than any real ambiguity.
7. **"Het is veiliger"** — why this should REJECT: too vague to identify *which* thing the manager gives you. Flag: a lenient grader might accept this since it's directionally true and security-adjacent, even though it doesn't name a distinguishing capability.
8. **"Het gebruikt tweefactorauthenticatie"** — why this should REJECT: confuses this room's content with the MFA room. A password manager isn't inherently a second factor; tests cross-room concept confusion.
9. **"Het wordt nooit gehackt"** — why this should REJECT: a misconception the lesson explicitly warns against — it states "Aanbieders worden gekraakt" and only claims the vault stays encrypted through such a breach, not that breaches don't happen.

## Quality assessment

- **Question clarity**: Unambiguous — asks for one specific distinguishing capability, not a general opinion.
- **Lesson/question alignment**: Same gap as the English version. Ives's monologue never actually compares password managers to browser-saved passwords in the pre-question prose; it only argues that concentrating secrets in a manager beats scattering them across memory. The specific distinguishing facts in the accept list surface only in the **post-answer explanation**, which the player hasn't seen when answering.
- **Accept-list coverage**: Good coverage of the "synchronisatie"/"elke browser"/"meer dan websites" family, but missing the "sterkere/willekeurigere wachtwoorden genereren" angle the explanation itself raises. Candidate 6 above would currently fall outside the accept list despite being lesson-grounded.
- **Reject-list false-positive risk**: The bare word "niets" as a reject entry is risky under substring matching. A fully correct answer like *"Het geeft je niets extra's om je zorgen over te maken, want het synchroniseert overal automatisch"* contains the literal substring "niets" and would fail the offline keyword floor despite being correct.
- **Explanation consistency**: Internally consistent with the accept list (vastzit aan één browser, zwakker genereren/synchroniseren, dekt geen niet-websites, sessie- in plaats van zin-beschermd). The mismatch is timing, not content — the explanation teaches what the pre-question prose should have set up.

## Suggested refinements

- Add a line to the pre-question lesson prose that plants the browser-comparison (e.g., Ives naming one browser-storage limitation before the question is asked), so the accept-list knowledge is actually taught rather than only revealed afterward.
- Add an accept entry such as "genereert sterkere/willekeurigere wachtwoorden" to close the coverage gap surfaced by candidate 6.
- Replace the bare reject entry "niets" with a longer, less substring-prone phrase (e.g., "geeft niets extra's"), or rely on the LLM grader layer alone for this entry, to reduce false-positive risk against the offline keyword floor.
