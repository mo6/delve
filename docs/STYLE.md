# Voice, Language, and the LLM Brief

Two audiences. **Part 1–4** is for humans writing a pack. **Part 5** is a copy-paste brief for
an LLM generating one — it restates the rules in prompt form, so you shouldn't need to explain
the format from scratch every time.

Format mechanics live in [AUTHORING.md](AUTHORING.md). This page is about *how it should sound*.

---

## 1. The voice

The whole premise is that this isn't a slide deck. If the writing sounds like a slide deck,
the dungeon is a costume and everyone can tell.

**Write a person, not a policy.** `Ada looks up from a stack of intercepted letters.` costs one
line and turns a compliance document into someone talking. The learner walked across a dungeon
to meet this character. Let them be met.

**Respect the reader's intelligence, and their scepticism.** They have done training before and
it was insulting. Say the true thing, including when the true thing is "the advice you were
given fifteen years ago is now actively dangerous." Nothing buys attention like being told
something that is actually correct.

**Give the keeper an opinion.** Ada refuses to give a checklist and says why. Ives finds the
objection delightful and answers it properly. Opinions are memorable; bullet points are not.

**Never make the learner feel stupid.** Almost every security failure is a competent person
being targeted by a professional, or a kind person holding a door. Write it that way, because
it's true, and because contempt makes people hide their mistakes instead of reporting them.

**Earn the payload.** One blockquote per lesson, holding the single sentence you want carried
into the examination. If everything is emphasised, nothing is.

### No em-dashes. Ever.

**Do not use ` — ` in pack content.** In either language. Use a comma or a semicolon.

This is not a matter of taste. A text peppered with em-dashes reads as machine-written, and
this pack's entire credibility rests on sounding like a person wrote it. One tell undoes a
lesson that took an hour to write.

Choosing the replacement takes a second's thought, because they are not interchangeable:

| The dash was… | Use | Example |
|---|---|---|
| Joining two **independent** clauses | **semicolon** | `A clean scan proves nothing; most of this training was about attacks with no malware.` |
| Introducing a phrase or apposition | **comma** | `Modern phishing is well written, often better than your internal comms.` |
| Before a conjunction (*and, but, en, maar*) | **comma** | `…nothing for a scanner to detect, and it loses more money than the clever attacks.` |
| A **pair** around an aside | **two commas** | `This is why codes, even good app-generated ones, are not the end of the story.` |

Three traps, all of which produced real bugs the first time this was done:

**A semicolon needs an independent clause on *both* sides.** `When a message makes you feel
hurried; that is the attack` is wrong, because `When…` is subordinate. It's a comma.

**If the aside already contains commas, a comma pair turns it to soup.** `what happens next,
retention, logging, human review, training, is their policy` is unreadable. Restructure the
sentence instead of repunctuating it: `What happens to it next is their policy: retention,
logging, human review, training.`

**Some dashes aren't punctuation between clauses at all.** Speech trailing off
(`"I think I might have —"`) wants an ellipsis. A dash introducing a list wants a colon. A
label (`**Placeholder — replace this**`) wants a full stop. Read what the dash was *doing*
before you replace it.

Colons and full stops are fine, incidentally. It's specifically the em-dash that reads as a
machine's tic.

---

## 2. English

- Second person, direct. "You click the link", not "the user clicks the link."
- Contractions are fine. This is speech.
- Plain words over institutional ones: *use* not *utilise*, *about* not *regarding*.
- Sentence-case headings.
- Explain jargon on first use, then use it freely — the learner is here to acquire the jargon.
- Prefer concrete over abstract: "four hundred thousand to a man in another country" beats
  "significant financial loss."

---

## 3. Nederlands

**Tutoyeer altijd. Gebruik `je`/`jij`, nooit `u`.**

Dit is de belangrijkste regel op deze pagina. Een kerker die probeert géén
compliance-training te zijn, moet de speler niet aanspreken als een belastingbrief. `u` schept
precies de afstand die we proberen weg te halen.

Let op de valkuilen — `u` → `je` is geen zoek-en-vervang:

| Situatie | Fout | Goed |
|---|---|---|
| Inversie (werkwoord vóór onderwerp) | ~~Wat doet je?~~ | **Wat doe je?** |
| Inversie | ~~Dat krijgt je niet van mij~~ | **Dat krijg je niet van mij** |
| Inversie | ~~kunt je~~ | **kun je** |
| `hebben` | ~~Je heeft~~ | **Je hebt** |
| Beklemtoond / eindpositie | ~~niet van je~~ | **niet van jou** |
| Wederkerend | ~~je voelde zich~~ | **je voelde je** |

De regel achter de eerste vier: **bij inversie verliest het werkwoord zijn `-t`.** `je krijgt`
(geen inversie, `-t` blijft) maar `krijg je` (inversie, `-t` weg). Bij `u` gebeurde dat niet, dus
elke omgezette zin met inversie is fout tot je hem nakijkt.

### Koppen en titels: zinskapitaal

**Alleen het eerste woord krijgt een hoofdletter.** Nederlands kent geen title case — niet in
koppen, niet in titels. Dit is een anglicisme dat er makkelijk insluipt, zeker bij vertalen.

| Fout (Engelse gewoonte) | Goed |
|---|---|
| ~~`# Wanneer Het Voor Je Geschreven Is`~~ | `# Wanneer het voor je geschreven is` |
| ~~`# Een Phish Herkennen`~~ | `# Een phish herkennen` |
| ~~`title: De Kluis`~~ | `title: De kluis` |
| ~~`# De Grotten der Naleving`~~ | `# De grotten der naleving` |

Geldt óók voor `title:` in de frontmatter en voor de naam van de rol — een Nederlandse titel is
een zin, geen opsomming (`Het diner`, niet `Het Diner`).

**Eigennamen houden hun hoofdletter**, ook middenin een kop: `# Wat je het Orakel verteld hebt`.

Bij namen van poortwachters: een epitheton volgt `Karel de Grote` en houdt zijn hoofdletters —
`Ada de Achterdochtige`, `Winterkoning van de Wacht`. Maar een bijzin is gewoon een zin:
`Grigor, wiens naam geleend werd`, niet ~~`Grigor, Wiens Naam Geleend Werd`~~.

### Wat níét vertaalt

De **structuurwoorden van het formaat blijven Engels**, in elke taal — net als de sleutels in de
frontmatter:

```markdown
---
keeper: wizard          ← blijft Engels, is een sleutelwoord
name: Ada de Achterdochtige
---

## Questions            ← blijft Engels, de parser zoekt hierop
```

De regel: **het formaat is Engels, de inhoud niet.** Je schrijft ook geen `poortwachter: tovenaar`.
Mapnamen en bestandsnamen zijn om dezelfde reden slugs die niet vertalen.

Verder:

- Leenwoorden die in Nederlands vakjargon normaal zijn, gewoon gebruiken: *phishing*, *link*,
  *social engineering*, *vishing*, *passkey*. Niet geforceerd vertalen.
- Wél vertalen wat een gewoon Nederlands woord heeft: *wachtwoord*, *bijlage*, *wachtwoordzin*,
  *inloggegevens*, *meelopen*.
- Namen van poortwachters mogen Nederlands zijn en mogen een grap bevatten. *Winterkoning van
  de Wacht* is een vogel én een wachter; *Rook de Nachtwaker* leest dubbel. Doe dat.
- Schrijf Nederlands, geen vertaald Engels. Als een zin alleen werkt met de Engelse
  woordvolgorde erachter, herschrijf hem.

---

## 4. Questions

**Distractors must be tempting.** A wrong answer nobody would pick teaches nothing and wastes a
line. The best distractors are *true but irrelevant*, or *right answer to a different question*.
Look at how the pilot pack does it: "Gift cards are an unusual business expense" is entirely
true — it's just not evidence.

**Explanations teach the wrong answers, not just the right one.** This is the highest-value text
in the pack: it lands at the exact moment the learner has committed and is most receptive. Say
why the tempting answer was tempting. A blockquote that only says "correct, a Pod is the unit"
has wasted the moment.

**Assertions state misconceptions, not truisms.** The whole point of a two-option question is to
put a plausible falsehood in front of someone and make them reject it. "Passwords should be
strong" teaches nothing. "Passwords should be changed every 90 days" is a widely-held belief
that is wrong, and rejecting it is a real act of learning.

**Every question must be fair on a first read.** Nobody re-sits an examination — passing is
final. No trick phrasing, no double negatives, no dependence on a detail the lesson never
mentioned.

**No "all of the above."** Options are shuffled at runtime.

---

## 5. Object flavour (optional)

Objects (`AUTHORING.md` section 14) are seasoning, and their text is the smallest surface in the
pack, so it has to earn its line. Two rules beyond the usual voice:

**One line, and in the room's world.** `on_pickup` and `on_move` print on the message row, a
single line each. Write them in the pack's voice, not a manual's: "You bang the coconuts together.
Clip-clop, clip-clop." belongs to Monty Python; "You pick up a USB stick you found on the floor.
In real life, this is how they get in." is the security pack teaching in one breath. A teaching
object should land its point in the pickup line, because that is the moment the learner acted.

**`on_move` repeats, so it must survive repetition.** It prints on *every* step while carried. A
joke that is funny once is grating by the tenth tile; the coconut clop works precisely because it
is the whole bit. If a line would wear out, leave `on_move` off and let `on_pickup` carry it.

The em-dash rule holds here too: none, in either language.

---

## 6. The LLM brief

Copy everything below, fill in the four blanks, and attach `AUTHORING.md`.

````text
You are writing a training pack for Delve, a NetHack-style training application. Learners
walk a dungeon; in each room a keeper teaches one lesson and then examines them on it. Passing
makes a door appear in the wall. It is deliberately not a slide deck.

TOPIC:      <what the training is about>
AUDIENCE:   <who takes it, and what they already know>
LANGUAGE:   <en | nl>
SIZE:       <n> chapters of 3-4 rooms each

STRUCTURE
  pack.md                  frontmatter: id, title, difficulty, scroll. Body = intro screen.
  NN-chapter-slug/
    chapter.md             frontmatter: id, title. Body = a few lines on arrival.
    NN-room-slug.md        frontmatter: id, keeper, name, pass. Body = lesson + questions.
  scroll.md                the award. Supports {name} {score} {date} {pack}.

  A chapter is a dungeon floor; a room is one lesson. 3-4 rooms per chapter, never more than 6.
  A chapter break must be a real break in the material. Filenames set the order.
  Folder and file names are slugs and stay identical across languages. Only content translates.
  You never write a map. There is no map syntax. The engine generates every floor.

ROOM FILE FORMAT
  ---
  id: stable-slug          # never changes; progress records point at it
  keeper: wizard           # wizard (scholarly) | shopkeeper (transactional) | gatekeeper (terse)
  name: <give them a name> # always
  pass: 0.75
  ---

  # Lesson title

  <Lesson prose. Open by putting the keeper in the room doing something. Standard Markdown.
   Max ~60 lines. Exactly one blockquote, holding the sentence to carry into the exam.>

  ## Questions

  ### <question prompt>

  - [ ] wrong but tempting
  - [x] correct
  - [ ] wrong but tempting

  > <Explanation. Shown after answering, right or wrong. Explain why the WRONG answers were
  > tempting, not just why the right one is right. This is the most valuable text you write.>

  Question type is inferred from option count -- never declare it:
    exactly 2 options  -> assertion, rendered as a two-way prompt
    3+ options         -> multiple choice, OPTIONS ARE SHUFFLED (so never "all of the above")
  Every question needs an explanation. 4 questions per room is a good target.

PUNCTUATION -- NON-NEGOTIABLE
  NEVER use an em-dash ( -- the long dash, U+2014 ) anywhere in the content, in any
  language. It is the clearest tell that a text was machine-written, and this pack's
  credibility depends on not reading that way. Use a comma or a semicolon.
    two independent clauses  -> semicolon   ("A clean scan proves nothing; most of this
                                              training was about attacks with no malware.")
    a phrase or apposition   -> comma       ("Modern phishing is well written, often better
                                              than your internal comms.")
    before and/but/en/maar   -> comma
    a pair around an aside   -> two commas  ("codes, even good app-generated ones, are not")
  A semicolon needs an independent clause on BOTH sides: "When you feel hurried; that is
  the attack" is wrong, because "When..." is subordinate. Use a comma.
  If the aside already contains commas, a comma pair becomes unreadable. Restructure the
  sentence instead of repunctuating it.
  Colons, full stops and ellipses are fine. It is specifically the em-dash to avoid.

VOICE
  - Write a person, not a policy. The keeper has opinions and says them.
  - The reader has done bad training before and resents it. Say true things, including
    "the advice you were given years ago is now wrong." That is what buys attention.
  - Never make the learner feel stupid. Security failures are competent people being targeted
    by professionals, or kind people holding a door. Write it that way -- it's true, and
    contempt makes people hide incidents instead of reporting them.
  - Concrete beats abstract. Distractors must be tempting: true-but-irrelevant is ideal.
  - Assertions state misconceptions, not truisms.
  - Every question must be fair on a FIRST read. Passing is final; nobody re-sits.

IF LANGUAGE IS nl
  - TUTOYEER. Use je/jij, never u. This is not optional.
  - Inversion drops the verb's -t: "je krijgt" but "krijg je"; "kun je" not "kunt je";
    "Je hebt" not "Je heeft"; "niet van jou" not "niet van je"; "je voelde je" not "zich".
  - SENTENCE CASE in every heading and title -- only the first word is capitalised.
    Dutch has no title case; assuming it does is the most common translation tell.
      "# Wanneer het voor je geschreven is"   NOT  "# Wanneer Het Voor Je Geschreven Is"
      "# Een phish herkennen"                 NOT  "# Een Phish Herkennen"
      "title: De kluis"                       NOT  "title: De Kluis"
    Applies to frontmatter `title:` and the scroll name too. Proper nouns keep their
    capital inside a heading: "# Wat je het Orakel verteld hebt".
    Keeper epithets follow "Karel de Grote" and keep caps ("Ada de Achterdochtige"),
    but a relative clause is just a sentence ("Grigor, wiens naam geleend werd").
  - Keep loanwords that are normal in Dutch technical usage (phishing, link, passkey).
    Translate what has a real Dutch word (wachtwoord, bijlage, inloggegevens).
  - Dutch keeper names, and a pun is welcome.
  - Write Dutch, not translated English. If a sentence only works with English word order
    behind it, rewrite it.

THE FORMAT IS ENGLISH, THE CONTENT IS NOT -- in every language
  - `## Questions` stays literally "## Questions". The parser looks for it.
  - Frontmatter keys stay English: `keeper:`, `name:`, `pass:`. You would not write
    `poortwachter: tovenaar`.
  - Folder and file names are slugs and never translate. Only the content inside does,
    so that locale subtrees stay diffable against each other.

ORGANISATION-SPECIFIC CONTENT
  Never invent contact channels, policy names, or classification tiers. Use obvious
  placeholders (security@example.com, #security-help) and mark them in the text as
  placeholders to be replaced.

Output each file separately with its full path. Do not write any code.
````

**Then check the generated pack against the checklist in AUTHORING.md §13, and run
`python -m delve validate <pack>`.** An LLM will reliably produce plausible-looking questions
whose distractors are all obviously wrong — that's the failure mode to look for first, and the
validator can't catch it.
