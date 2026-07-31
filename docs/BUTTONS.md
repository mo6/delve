# Answer buttons — a design proposal

**Status: a proposal, not scheduled work.** This is the argument for drawing MCQ and assertion
answers as *buttons* rather than a plain numbered list, so an examination reads as something you
press rather than a form you fill in. Like [DISPLAY.md](DISPLAY.md) and [WIDEMAP.md](WIDEMAP.md),
it lives on the `ui` side of rule 2 and changes nothing about the pack format, the engine, or the
session; until it ships, the current render stands. Nothing here needs a wider terminal or a new
dependency.

Read [SCREENS.md](SCREENS.md) §3 (the examination panel) and §9 (widths and the assertion prompt)
first: the numbers below come from there.

---

## 1. What we draw today, and why it feels flat

The examination reuses the lesson panel (SCREENS.md §3): a 73-column box, 69 columns of writable
text (`windows.PANEL_W` / `TEXT_W`). Inside it:

**Multiple choice** is a numbered list. `windows._draw_menu` prints `1 - <label>`, wrapping the
label under a four-space indent, keys `1`–`n` (digits, so they never clash with the map's
`,`/`d`/`i`, OBJECTS.md):

```
 An email appearing to come from your CEO asks you to urgently buy gift cards…
 What is the strongest single signal that this is an attack?

 1 - Gift cards are an unusual business expense
 2 - It combines manufactured urgency with a request to bypass normal
     purchasing
 3 - A CEO would not normally email someone in your role directly
 4 - The message came by email rather than in person

 Question 1 of 4.
```

**An assertion** (exactly two options, SCREENS.md §9) is a one-line prompt, `windows._draw_prompt`
writing the two labels joined by the localised connector and a `?`:

```
 Bad spelling and grammar are a reliable way to spot phishing.

 True or False?

 Question 2 of 4.
```

Both are legible and both are *inert-looking*. The `1 -` reads as a footnote marker, not a control;
the assertion line reads as a sentence, and the learner has to already know that `w`/`n` (its first
letters) are the keys. The information is there; the affordance is not. There is also a precedent
pulling the other way: free-text and the drop-amount field already draw a real boxed input
(`_draw_freetext`, `_draw_amount`, the `_FIELD` box-drawing set), so the panel already has chrome
that says "interact here." The answers are the one interactive thing that still looks like prose.

---

## 2. The constraints that shape any answer button

Nothing here is negotiable; they are the same rules the rest of the UI lives under (CLAUDE.md).

- **Box-drawing is fine here, but it is a text concern, not a map one.** The "map glyphs are ASCII"
  rule is about the fixed one-cell-per-column grid; a button lives in the *panel*, which is UTF-8
  text like the lesson. Borders use the ACS_ line-drawing set for rooms and the `_FIELD` single-line
  box (`┌─┐│└┘`) for fields, both already shipping. A button reuses that vocabulary; it does **not**
  reach for a new one, and **never an emoji** (double-width in a one-cell world, SCREENS.md §9).
- **16 colours only** (Apple ncurses 6.0 / PDCurses). We already have the palette and `attrs.py`,
  including the solid background-bar pairs added for the coloured Correct./Not quite. line
  (`attrs.bar_attr`, reverse-video fallback on a colourless terminal). A button's highlight is one
  of those, not a new colour API.
- **East Asian *Ambiguous* width.** Every box-drawing character is one cell in an en/nl terminal and
  two in a CJK one. This is already the borders' bet (CLAUDE.md), and it is safe only because the
  scope is en/nl. Buttons inherit that bet and no more; adding a CJK locale would break buttons for
  the same reason it breaks the room borders.
- **69 columns, and a panel height fixed at run start.** The writable width is `TEXT_W = 69`. The
  panel height is computed once from the lesson and held (SCREENS.md §3), and the examination reuses
  it. Buttons cost vertical rows, and that is the whole design tension (§4).
- **Rule 2: `ui` paints a `Frame`; the theme lives on the `ui` side of it.** This is the reason the
  proposal is cheap. The session already hands over everything a button needs: `MenuView.items`
  (each a `key` + `text` + `struck`) and `PromptView` (`choices`, `connector`, `struck`). Drawing
  them as buttons instead of a list is a `windows.py` change and nothing else. No view-model field is
  *required*; §8 notes the one optional field a focus-navigation variant would add.

---

## 3. The crux: vertical space

A full box costs three rows per option (top border, content, bottom border) plus a blank between,
so **four options in boxes is ~15 rows** before the prompt. The lesson-sized panel does not reliably
have them: at the 100×30 minimum the panel is about 25 rows tall, and a two-line MCQ prompt plus a
footer already spends six or seven. Boxing every option is affordable when options are few and
short; it is not affordable for a four-option MCQ whose labels wrap.

So the proposal is **not one button style but two, matched to how many options there are and how
wide they run:**

- **Two options (assertion): real side-by-side boxed buttons.** Only two, each fits in half the
  panel, and the visual payoff is large. This is the case that most needs help (the bare
  `True or False?` line) and most easily affords it.
- **Three or more (MCQ): a key badge and a full-width focus bar, one row per option.** A box per
  option is too tall; instead each option gets a coloured *key badge* (a reverse-video ` 1 ` block
  that reads as a physical key) and the whole row becomes a selectable bar. It costs the same rows
  the current list does, so it always fits, and it still reads as a control rather than a footnote.

A boxed MCQ is offered as a variant (§6) for the rare short-option room, but the row style is the
recommended default because it is the one that always fits.

---

## 4. The assertion: two boxed buttons

Two buttons side by side, each half the width, the key shown as a badge and the label beside it:

```
 Bad spelling and grammar are a reliable way to spot phishing.

 ┌──────────────────────────────┐  ┌──────────────────────────────┐
 │  w   True                    │  │  n   False                   │
 └──────────────────────────────┘  └──────────────────────────────┘

 Question 2 of 4.
```

- The badge (` w `, ` n `) is drawn reverse-video (or a bright pair), so the key stands out from the
  label; it is the letter the session already derives from the label's first character.
- The two labels are the pack's own (`Waar` / `Niet waar` in Dutch), never `True`/`False` in the
  engine (SCREENS.md §9). The connector word is no longer needed *inside* the buttons, but
  `PromptView.connector` stays on the view model (it is the session's word to give, rule 2); a
  screen-reader-style caption could still use it.
- **Struck** (an option the pet ruled out on consultation) dims that whole button, `A_DIM`, exactly
  as the list dims a struck row today.
- Widths: two boxes of 32 + a two-space gutter is 66, inside the 69. The label area is 32 − 4 − 4 =
  ~24 columns, enough for the short labels an assertion uses; a longer label wraps to a second
  content row and the box grows to four rows (still cheap, since there are only two).

---

## 5. Multiple choice: a key badge and a focus bar

One row per option, so it costs what the list costs and always fits. The key is a badge; the row is
a bar that highlights the focused option:

```
 What is the strongest single signal that this is an attack?

  1  Gift cards are an unusual business expense
▐ 2 ▌It combines manufactured urgency with a request to bypass normal purchasing
  3  A CEO would not normally email someone in your role directly
  4  The message came by email rather than in person

 Question 1 of 4.
```

- The badge is ` 1 `…` n ` in reverse video (a coloured pair where colour is available). It reads as
  a key cap without a box around it, so it costs no extra rows.
- A wrapped label indents under the label column, not under the badge, so the badge stays a clean
  left rail.
- **Focus/hover.** The row the learner is about to choose is painted as a full-width bar (the
  `attrs.bar_attr` background used for the answer line). Focus is optional (§8); with keys-only
  input there is simply no focused row, and the badges alone carry the button feel. The mock-up
  above shows option 2 focused.
- **Struck** dims the row and marks the badge, unchanged in meaning from today.

This is deliberately close to the current list in *layout* and far from it in *reading*: same rows,
same wrap, but a key that looks pressable and a row that responds.

**Play-testing settled two things (see `poc/buttons/buttons_poc.py`).** First, the **MCQ stays a
list**: buttons are for **binary** questions only (an assertion or a yes/no prompt, §4), where two
side-by-side buttons pay off; a 3+ option list reads fine as a list and boxing it only costs rows
(§3, and §6 below is dropped). Second, the selection highlight sits on the **badge alone and only for
the selected choice**: the selected key turns black-on-cyan (reverse video with colour off) and every
resting choice is plain. An earlier version also tinted the resting badges, but then the black-and-
white fallback showed no difference between a resting and the selected choice; giving *only* the
selection a background fixes that and keeps the panel quiet.

---

## 6. A boxed-MCQ variant, for short options only *(dropped)*

**Superseded by the play-testing note in §5: buttons are for binary questions only, so an MCQ is
never boxed.** Kept here for the record. When a room's options are few and short (a handful of one-
or two-word answers), the panel has the rows to box each, and it looks best:

```
 Which tier classifies customer PII?

 ┌─────────────────────────────────────────────────────────────────┐
 │  1   Public                                                     │
 └─────────────────────────────────────────────────────────────────┘
 ┌─────────────────────────────────────────────────────────────────┐
 │  2   Internal                                                   │
 └─────────────────────────────────────────────────────────────────┘
```

The renderer can pick this automatically: box every option when
`sum(rows_per_option) + prompt + footer` fits the fixed panel height, otherwise fall to the row
style of §5. The choice is made once, from the same measurement the panel height already comes from,
so it never jitters mid-question (the same discipline as the panel height itself, SCREENS.md §3).
Simpler and less clever: always use §5 for MCQ and §4 for assertions, and treat the boxed MCQ as a
later refinement. Recommended: ship §4 and §5, leave §6 as a follow-up.

---

## 7. Colour, state, and the monochrome floor

Every state maps to something `attrs.py` already provides:

| State | Colour terminal | Colourless terminal |
|---|---|---|
| Key badge | reverse-video, or a bright pair | reverse-video |
| Focused row/button | solid background bar (`bar_attr`) | reverse-video |
| Normal | default | default |
| Struck (pet ruled out) | `A_DIM` | `A_DIM` |

There is no new colour and no new API; the badge and the bar are the reverse/`bar_attr` treatments
that already degrade cleanly, so a 16-colour terminal, an 8-colour one, and a monochrome one all get
a coherent look. The buttons must never rely on colour *alone* to say "this is the key": the badge is
a spatial cue (a boxed or reverse block on the left rail) that survives with colour off.

---

## 8. Interaction: keys stay primary

The number and letter keys are the input, unchanged. They are fast, they are taught (the hint line
already says `Answer: 1-4` / `Antwoord: w of n`, SCREENS.md §3, §9), and most people run this once;
a button that *requires* arrowing to it would be slower and would fight the tutorial. So:

- **Recommended: keys only.** Buttons are pure affordance; pressing `2` answers, exactly as now.
  No view-model change at all.
- **Optional: focus navigation as a second path.** Arrows move a highlight, Enter presses the
  focused button, keys still work. This is the only part that touches the view model: a `selected`
  index the session owns and the `Frame` carries (a new field, filled by session, painted by `ui`,
  rule 2 intact). It is additive and can come later; nothing in §4–§7 needs it.

Whichever, the hint line keeps saying which keys work right now, because for the audience that skips
the tutorial the hint line is the safety net (CLAUDE.md, "the hint line is not decoration").

---

## 9. Portability

- **ACS fallback.** The room borders already fall from ACS_ line-drawing to an ASCII stand-in on a
  terminal that cannot line-draw (`ui/walls.py`); button borders take the same fallback, so a hostile
  terminal shows `+`/`-`/`|` boxes and reverse-video badges rather than nothing. The `_FIELD` set is
  the single-line box the free-text and amount fields already draw, so this is proven chrome.
- **Windows.** Double-line window frames are the real Unicode bet (CLAUDE.md); the buttons here use
  the *single*-line `_FIELD` set and reverse video, both of which PDCurses handles, so they add no
  new Windows risk beyond what the field boxes already carry. Still on the M1 Windows-verification
  list, with everything else.
- **CJK stays out of scope** (§2): the width bet only holds for en/nl.

---

## 10. Keep the mock-ups honest

The frames above are hand-drawn *for the argument*; they are not evidence. Per the repo rule
(CLAUDE.md, "the mock-ups are generated, not drawn"), before any of this is built the examination
frames in SCREENS.md must be regenerated through `tools/screens.py`, and the generator taught the
button layout, so the assertions there (every frame exactly 100×30, the 69-column panel) keep
catching width bugs. A button that overflows the panel by a column is exactly the class of bug that
generator exists to catch; do not hand-edit SCREENS.md to match a hoped-for render.

---

## 11. Recommendation

Ship **§4 only** as the button work: two boxed buttons for a **binary** question (an assertion or a
yes/no prompt). A 3+ option **MCQ stays the numbered list** it is today (§5), because boxing it costs
rows and reads no better; §6 is dropped. The selection highlight sits on the **selected badge alone**
(black-on-cyan, reverse video with colour off), every resting choice plain, so the black-and-white
fallback still shows the selection. This is a `windows.py`-only change, keys-only input, no view-model
change. §8's focus navigation stays a later, additive refinement. Regenerate the SCREENS.md frames as
part of the work, never after it.

The badge highlight is reverse-video by default (identical on all three platforms) with an optional
colour pair on top; that is what the POC (`poc/buttons/buttons_poc.py`) already does, and it is the
thing to look at before committing to the render.
