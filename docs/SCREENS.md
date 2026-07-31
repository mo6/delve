# Delve — screen mock-ups

> Screens at **exactly 100×30**, drawn from the real pilot pack and the real tutorial: the
> first screen a learner ever sees, then the M2 vertical slice end to end (*arrive → keeper
> instructs → examination → explanation → the door appears*), the failure branch (*repelled*),
> the floor filling in, a Dutch assertion, the scroll in both locales, the money objects
> (*the coin reward, the pack, dropping coins*), and the `?` help panel.
>
> M2 is the go/no-go (PLAN §11). This is the cheapest possible way to look at it: no engine, no
> parser, no curses. If the slice is boring on paper it will be boring on a screen.

**These are generated and asserted, not sketched.** Every frame is emitted by
[`tools/screens.py`](../tools/screens.py) onto a real 100×30 grid, asserting that each frame is
exactly 100×30 and every line fits its window. Prose, questions, explanations and scroll text are
**verbatim** from `packs/security-onboarding/` and `delve/tutorial/`.

```bash
./tools.sh screens            # print every screen
./tools.sh screens --check    # assert the geometry, print nothing
```

**Change the design there, not here**, then re-paste. The assertions are the point: they have
caught six real bugs that a hand-drawn mock-up would have rendered as clean art (§8.3).

What a mock-up **can't** show: 16 colours, and the lit/dim/black distinction.

---

## 0. The tutorial floor — the actual first screen

**Dlvl 0** (PLAN §9). This, not screen 1, is what a learner sees first. It exists precisely to
teach the interface, which is why pack authors never write one.

```
        10        20        30        40        50        60        70        80        90       100
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
The Porter looks you over. "First time? Then look down, and I will explain."
                                  ╔════════════════════════════════════════════════════════════════╗
                                  ║                                                                ║
                                  ║ What You're Looking At                                         ║
                                  ║                                                                ║
                                  ║ The Porter watches you walk the last few steps toward him and  ║
            ┌───────────────────┐ ║ seems satisfied by something.                                  ║
            │...................│ ║                                                                ║
            │...................│ ║ "There. You've already learned the hard part, and nobody had   ║
            │...................│ ║ to tell you. You wanted to be over here, so you came over      ║
            │................@.@│ ║ here."                                                         ║
            │...............f...│ ║                                                                ║
            │...................│ ║ That's movement. The arrow keys: up, down, left, right.        ║
            │...................│ ║ You've been doing it for ten seconds.                          ║
            └───────────────────┘ ║                                                                ║
                                  ║                                                                ║
                                  ║ "The rest is just knowing where to look. Four parts."          ║
                                  ║                                                                ║
                                  ║ The top line is the message line. It tells you what just       ║
                                  ║ happened. When something matters, it appears there, and only   ║
                                  ║ there.                                                         ║
                                  ║                                                                ║
                                  ║ (end)                                           (page 1 of 1)  ║
                                  ╚════════════════════════════════════════════════════════════════╝
George the Novice   Dlvl:0  Rooms:0/2  $:0  HP:12(12)  T:14
Next page: space        Back: -            Put it down: Esc
```

Two rooms, so a 2×1 partition and 40×15 cells. The Porter's panel gets **66 columns, not the 73
it gets in chapter 1** — the panel takes whatever space the room leaves (§8.2).

**The last line is new: a contextual hint line** (§8.4). It names the keys that do something
*right now* and changes as you go — `Next page: space` while reading, `Talk to Ada: t` when
standing beside a keeper, `Descend: >` when the stairs open.

## 1. Arrival on Dlvl 1

Chapter 1 of the pilot: 3 rooms, 3×1 partition, cells 33×15 after the `[18×9, 40×15]` clamp. The
learner has come down the `<` and hasn't spoken to anyone.

```
        10        20        30        40        50        60        70        80        90       100
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
Ada the Suspicious does not look up. There is no way out of this room.








    ┌────────────────────┐
    │....................│
    │..<.................│
    │....................│
    │...................@│
    │....................│
    │.......@............│
    │......f.............│
    └────────────────────┘










George the Novice   Dlvl:1  Rooms:0/3  $:0  HP:12(12)  T:14
Move: arrows    Talk: t    Look: ;    Help: ?    Quit: Q
```

Row 1 message, rows 2–28 map, rows 29–30 status and hints. The §7 budget holds.

**Read this screen carefully, because it is the whole bet.** Room 1 is lit, so the learner sees
all of it at once. There is nothing in it but Ada (`@`, right, beside her sealed exit), the
kitten (`f`), and the stairs they arrived by. No corridor, no branch, no second room — those
don't exist until the examination is passed. The east wall is unbroken. See §8.1.

## 2. Ada instructs

A **right-anchored panel**, clear of the room, **as short as it can be** (§8.2): 18 rows of the 27
available, so 9 rows of dungeon stay visible and the learner watches the room the whole time.

```
        10        20        30        40        50        60        70        80        90       100
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
Ada the Suspicious, wizard, teaches.
                           ╔═══════════════════════════════════════════════════════════════════════╗
                           ║                                                                       ║
                           ║ Recognising a Phish                                                   ║
                           ║                                                                       ║
    ┌────────────────────┐ ║ Ada does not look up. She is holding a letter to the lamp, and she    ║
    │....................│ ║ keeps holding it while she talks.                                     ║
    │..<.................│ ║                                                                       ║
    │....................│ ║ "Everyone wants me to teach them the tell," she says. "The spelling   ║
    │.................@.@│ ║ mistake. The odd greeting. They want a checklist so they can stop     ║
    │................f...│ ║ thinking. I will not give you one, because the people who write these ║
    │....................│ ║ letters have read the same checklist, and they are better at it than  ║
    │....................│ ║ you."                                                                 ║
    └────────────────────┘ ║                                                                       ║
                           ║ She puts the letter down.                                             ║
                           ║                                                                       ║
                           ║                                                                       ║
                           ║ --More--                                               (page 1 of 4)  ║
                           ╚═══════════════════════════════════════════════════════════════════════╝
George the Novice   Dlvl:1  Rooms:0/3  $:0  HP:12(12)  T:14
Next page: space        Back: -            Put it down: Esc
```

The last page. The panel height is **held constant** across pages — one that resized per page
would jitter under the reader:

```
Ada the Suspicious, wizard, teaches.
                           ╔═══════════════════════════════════════════════════════════════════════╗
                           ║                                                                       ║
                           ║ "The mismatch is always there," Ada says. "It has to be. They cannot  ║
                           ║ forge the whole world, only the parts you look at. Your job is to     ║
    ┌────────────────────┐ ║ look at one more part than they paid for."                            ║
    │....................│ ║                                                                       ║
    │..<.................│ ║ She finally looks up.                                                 ║
    │....................│ ║                                                                       ║
    │.................@.@│ ║ "So. Not a checklist. A habit. When a message makes you feel that you ║
    │................f...│ ║ must act now, that is the moment to do the opposite. Slow down and    ║
    │....................│ ║ check one thing. Just one. Almost every attack in this building dies  ║
    │....................│ ║ right there."                                                         ║
    └────────────────────┘ ║                                                                       ║
                           ║                                                                       ║
                           ║                                                                       ║
                           ║                                                                       ║
                           ║ (end)                                                  (page 4 of 4)  ║
                           ╚═══════════════════════════════════════════════════════════════════════╝
George the Novice   Dlvl:1  Rooms:0/3  $:0  HP:12(12)  T:14
Next page: space        Back: -            Put it down: Esc
```

No page ends mid-sentence, and `yourcompany-hr.net` on page 3 is not split. Both took work; §8.3.

This panel **retires PLAN §3's stated reason for a 100-column terminal** (§8.5).

## 3. The examination

**The same panel.** Same side, same width, same height as the lesson. A keeper who teaches from a
side panel and then asks from a box over the room would be two interfaces wearing one character;
the panel is her frame for the whole encounter, so nothing jumps as the gate advances through
PLAN §6's states.

```
Ada the Suspicious examines you.
                           ╔═══════════════════════════════════════════════════════════════════════╗
                           ║                                                                       ║
                           ║ An email appearing to come from your CEO asks you to urgently buy     ║
                           ║ gift cards for a client, and to keep it quiet until the deal closes.  ║
    ┌────────────────────┐ ║ What is the strongest single signal that this is an attack?           ║
    │....................│ ║                                                                       ║
    │..<.................│ ║  1  Gift cards are an unusual business expense                        ║
    │....................│ ║  2  It combines manufactured urgency with a request to bypass normal  ║
    │.................@.@│ ║     purchasing                                                        ║
    │................f...│ ║  3  A CEO would not normally email someone in your role directly      ║
    │....................│ ║  4  The message came by email rather than in person                   ║
    │....................│ ║                                                                       ║
    └────────────────────┘ ║ Question 1 of 4.                                                      ║
                           ║                                                                       ║
                           ║                                                                       ║
                           ║                                                                       ║
                           ║                                                                       ║
                           ╚═══════════════════════════════════════════════════════════════════════╝
George the Novice   Dlvl:1  Rooms:0/3  $:0  HP:12(12)  T:14
Answer: 1-4             Ask your kitten: ?   Put it down: Esc
```

Ada is visible while she asks. Options stay a **numbered list** (buttons are for binary questions,
BUTTONS.md §5): each is a key badge (` 1 `) then its text, keys `1`-`n` (which never clash with the
map's `d`/`,`/`i`, OBJECTS.md) and **shuffled** — option `2` is correct and the order differs from
the file, which is why "all of the above" is banned. The arrows move a focus and Enter answers it,
as well as the direct number keys; the focused option's badge is a colour highlight (black-on-cyan)
the ASCII frame cannot show. `Question 1 of 4` is the whole panel footer; `pass: 0.75` and
`difficulty: standard` set the stakes, but the panel does not spell them out.

Two things the narrower panel bought, both small and both fine: option `2` (78 characters) now
**wraps with a hanging indent** rather than fitting on one line, and `(1-4, or ? to consult your
kitten)` moved out of the panel and onto the **hint line**, where it belongs and costs no rows.

## 4. The explanation

Shown after answering, right or wrong — AUTHORING §10 calls it the highest-value text in the pack.
Same panel again.

```
Correct.
                           ╔═══════════════════════════════════════════════════════════════════════╗
                           ║                                                                       ║
                           ║ 2 - It combines manufactured urgency with a request to bypass         ║
                           ║     normal purchasing                                                 ║
    ┌────────────────────┐ ║                                                                       ║
    │....................│ ║ Urgency plus process-bypass is the signature, and secrecy is what     ║
    │..<.................│ ║ makes it fatal; "don't tell anyone" exists solely to stop you doing   ║
    │....................│ ║ the one check that kills it.                                          ║
    │.................@.@│ ║                                                                       ║
    │................f...│ ║ The other answers are all genuinely odd, and oddness is worth         ║
    │....................│ ║ noticing. But oddness alone isn't evidence: CEOs do email people      ║
    │....................│ ║ directly, unusual expenses do happen, and plenty of legitimate        ║
    └────────────────────┘ ║ business runs on email. Suspicion that fires on "unusual" fires       ║
                           ║ constantly and teaches you to ignore it.                              ║
                           ║                                                                       ║
                           ║                                                                       ║
                           ║ --More--                                                              ║
                           ╚═══════════════════════════════════════════════════════════════════════╝
George the Novice   Dlvl:1  Rooms:0/3  $:0  HP:12(12)  T:14
Continue: space
```

## 5. The door appears

Four questions passed. `SealedWall` becomes `Door`. The moment the entire design is built around.

```
The wall grinds. Where there was stone, there is a door.








    ┌────────────────────┐
    │....................│
    │..<.................│
    │....................│
    │..............f@...@+
    │....................│
    │....................│
    │....................│
    └────────────────────┘










George the Novice   Dlvl:1  Rooms:1/3  $:0  HP:12(12)  T:14
Move: arrows    The door is a + . Walk through it.
```

Compare against screen 1. That's §8.1, and it's the finding — though note the hint line is now
doing some of the work of announcing it.

## 6. Repelled

The other way an examination ends. Attempts run out, the door does not appear, and the learner is
pushed back. **This is the most important screen in the file to get the tone right on** — CLAUDE.md
rule 4 is "REPELLED is not death", and PLAN §6 calls it the design's most important guardrail.
Tension is supposed to come from the dungeon; this screen must never read as punishment for
learning slowly.

```
        10        20        30        40        50        60        70        80        90       100
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
Ada the Suspicious shakes her head. You are pushed back from the door.




                           ╔═══════════════════════════════════════════════════════════════════════╗
                           ║                                                                       ║
                           ║ REPELLED                                                              ║
                           ║                                                                       ║
    ┌────────────────────┐ ║ Ada the Suspicious turns back to her work. "Not yet," she says. There ║
    │....................│ ║ is no edge in it. "You have read it once. Read it twice."             ║
    │..<.................│ ║                                                                       ║
    │....................│ ║ The wall is stone again. Nothing you earned is gone: every door you   ║
    │............@......@│ ║ opened is still open, and the way back is still the way back.         ║
    │...........f........│ ║                                                                       ║
    │....................│ ║     Ask her to teach it again    t    free, always and forever        ║
    │....................│ ║     Ask your kitten              ?    costs score, not health         ║
    └────────────────────┘ ║     Rest until you heal          s                                    ║
                           ║                                                                       ║
                           ║ She does not seem to be in any hurry.                                 ║
                           ║                                                                       ║
                           ║                                                                       ║
                           ╚═══════════════════════════════════════════════════════════════════════╝
George the Novice   Dlvl:1  Rooms:0/3  $:0  HP:3(12)  T:31
Read it again: t        Ask your kitten: ?   Rest: s        Help: ?
```

Everything on the screen is working to make this a pause, not a defeat. The keeper is the same
panel she taught from, not a new red box. The message names a push, not a death. The three offered
actions all lead *forward* and two are explicitly free. `Rooms:0/3` is unchanged — nothing earned
was lost — and no death screen, no respawn, no score change appears, because none happens: REPELLED
leaves the run exactly where it was minus some HP.

**Same room as screen 1, and that's deliberate:** the learner is pushed back across the room they
already know, to the keeper they already met, with the lesson they can reread one keypress away.
The screen's whole job is to make the next thing you do obvious and cheap.

The `HP:3(12)` is a third failed sitting at `standard` (12 − 3×3). It reads that way because the
penalty is charged **per failed sitting, not per wrong answer** — a fork this screen forced into the
open (§8.10). Under the old per-wrong-answer wording it was unreachable; per-sitting, REPELLED
always lands before HP:0.

One thing this screen surfaced that the design still hasn't settled (§8.10): the panel offers **rest
to heal** (`s`), which no part of PLAN or AUTHORING defines. A struggling learner accumulates HP
loss across a floor and needs it back, or REPELLED becomes a slow death by another name. The
mechanism is invented here; it's an M4 task.

## 7. Two rooms and a corridor

Room 1 cleared and remembered; room 2 lit; **room 3 does not exist yet**. The corridor is the
L-shape carved between consecutive cells in serpentine order — no spanning tree, no reroll.

```
Grigor, Who Was Impersonated, looks up. There are two nameplates on his desk.






                                      ┌───────────────────────┐
    ┌────────────────────┐            │.......................│
    │....................│            │.......................│
    │..<.................│            │.......................│
    │....................│      ######+....................@.@│
    │...................@+#######     │...................f...│
    │....................│            │.......................│
    │....................│            │.......................│
    │....................│            └───────────────────────┘
    └────────────────────┘









George the Novice   Dlvl:1  Rooms:1/3  $:0  HP:12(12)  T:14
Talk to Grigor: t          Move: arrows              Help: ?
```

**This is the screen that answers "does it feel like a dungeon?"**, and it's the first one that
does. Room 1 and the corridor render **dim** (visited); room 2 **lit**; room 3 and its corridor
are **black**, because they are not yet real. Room 2's east wall is unbroken; Grigor stands beside
it.

Ada is still in room 1 — she re-instructs forever (PLAN §7). Whether she should still be *drawn*
there is undecided and matters; §8.9.

## 8. The floor complete

All three keepers satisfied. The whole chain, and the stairs down.

```
A staircase grinds open in the floor. You have finished the Sorting Office.






                                      ┌───────────────────────┐
    ┌────────────────────┐            │.......................│
    │....................│            │.......................│       ┌───────────────────────┐
    │..<.................│            │.......................│       │.......................│
    │....................│      ######+......................@+####   │.......................│
    │...................@+#######     │.......................│   #   │.......................│
    │....................│            │.......................│   ####+......................@│
    │....................│            │.......................│       │.......................│
    │....................│            └───────────────────────┘       │.................@.>...│
    └────────────────────┘                                            │................f......│
                                                                      └───────────────────────┘
George the Novice   Dlvl:1  Rooms:3/3  $:0  HP:12(12)  T:14
Descend: >              Move: arrows              Help: ?
```

The 3×1 partition and the serpentine walk are visible: three rooms jittered inside 33×15 cells,
two L-corridors, `>` earned in the last room. **This is the whole floor**, and it uses about a
quarter of the map area — sparse, but NetHack floors are sparse too.

## 9. An assertion, in Dutch

```
Ada de Achterdochtige overhoort je.
                           ╔═══════════════════════════════════════════════════════════════════════╗
                           ║                                                                       ║
                           ║ Slechte spelling en grammatica zijn een betrouwbare manier om         ║
                           ║ phishing te herkennen.                                                ║
    ┌────────────────────┐ ║                                                                       ║
    │....................│ ║  w  Waar                                                              ║
    │..<.................│ ║  n  Niet waar                                                         ║
    │....................│ ║                                                                       ║
    │.................@.@│ ║ Vraag 2 van 4.                                                        ║
    │................f...│ ║                                                                       ║
    │....................│ ║                                                                       ║
    │....................│ ║                                                                       ║
    └────────────────────┘ ║                                                                       ║
                           ║                                                                       ║
                           ║                                                                       ║
                           ║                                                                       ║
                           ║                                                                       ║
                           ╚═══════════════════════════════════════════════════════════════════════╝
George de Beginner   Dlvl:1  Kamers:0/3  €:0  HP:12(12)  T:14
Antwoord: w of n        Vraag je katje: ?    Leg het weg: Esc
```

Two options, so it's an assertion, drawn as a **numbered-style list** — the same look and navigation
as an MCQ (§3), since its answers are too few for boxed buttons to buy anything — with **no
`True`/`False` anywhere in the engine**. The labels are the pack's own `Waar` / `Niet waar`, each
behind a key badge (` w ` / ` n `, the label's first letter, which also answers it directly). The
arrows move the focus and Enter confirms it; the focused choice's badge is a colour highlight the
ASCII frame cannot show. The footer is just the localised counter `Vraag 2 van 4.`; the panel does
not spell out the stakes. `Dlvl` stays (NetHack's own
label); `Rooms` becomes `Kamers`; the purse is **`€`**.

The `[wn]` key derivation has moved to the hint line (`Antwoord: w of n`) — which makes §8.6's
collision bug *more* visible, not less, since the hint line has to name the keys out loud.

## 10. The scroll, in both locales

```
You pick up the scroll.
            ╔══════════════════════════════════════════════════════════════════════════╗
            ║                                                                          ║
            ║  The Scroll of Vigilance                                                 ║
            ║                                                                          ║
            ║  Be it known to all who keep the Caverns:                                ║
            ║                                                                          ║
            ║  George went down into the dark on 17 July 2026, and came back up.       ║
            ║                                                                          ║
            ║  Four floors. Twelve keepers. Ada, who would not give a checklist.       ║
            ║  Grigor, who was impersonated for eleven days. Entropy, who counts. The  ║
            ║  Second Factor, who asks twice. Marisol among her shelves. Rook, who     ║
            ║  watches the coffee shops. Iolanthe, who was never the auditor. The      ║
            ║  Oracle, who told the truth about what it is given. And Wren, at the     ║
            ║  last door, who said: tell us fast.                                      ║
            ║                                                                          ║
            ║  Score: 91.7%                                                            ║
            ║                                                                          ║
            ║  Carry it out with you. The keepers stay down here; the habits do not.   ║
            ║                                                                          ║
            ║                                                                          ║
            ║  The Caverns of Compliance, sealed 17 July 2026                          ║
            ╚══════════════════════════════════════════════════════════════════════════╝
George the Novice   Dlvl:4  Rooms:12/12  $:1,250  HP:9(12)  T:2841
Read it again: r        Trophy case: #trophies            Finish: Q
```

```
Je pakt de rol op.
            ╔══════════════════════════════════════════════════════════════════════════╗
            ║                                                                          ║
            ║  De rol der waakzaamheid                                                 ║
            ║                                                                          ║
            ║  Aan allen die de grotten bewaken, zij bekend:                           ║
            ║                                                                          ║
            ║  George daalde af in het donker op 17 juli 2026, en kwam weer boven.     ║
            ║                                                                          ║
            ║  Vier verdiepingen. Twaalf poortwachters. Ada, die geen lijstje wilde    ║
            ║  geven. Grigor, wiens naam elf dagen lang geleend werd. Entropie, die    ║
            ║  telt. De Tweede Factor, die tweemaal vraagt. Marisol tussen haar        ║
            ║  rekken. Rook, die de koffietentjes in de gaten houdt. Iolanthe, die     ║
            ║  nooit de accountant was. Het Orakel, dat de waarheid vertelde over wat  ║
            ║  het krijgt aangereikt. En Winterkoning, bij de laatste deur, die zei:   ║
            ║  vertel het ons snel.                                                    ║
            ║                                                                          ║
            ║  Score: 91,7%                                                            ║
            ║                                                                          ║
            ║  Neem hem mee naar buiten. De poortwachters blijven hier beneden; de     ║
            ║  gewoonten niet.                                                         ║
            ║  De grotten der naleving, verzegeld op 17 juli 2026                      ║
            ╚══════════════════════════════════════════════════════════════════════════╝
George de Beginner   Dlvl:4  Kamers:12/12  €:1.250  HP:9(12)  T:2841
Lees opnieuw: r         Prijzenkast: #trofeeen            Klaar: Q
```

**Six things differ between those frames, and every one is wrong by default:**

| | `en` | `nl` |
|---|---|---|
| Currency symbol | `$` | `€` |
| Thousands separator | `1,250` | `1.250` |
| Decimal separator | `91.7%` | `91,7%` |
| Month name | `July` | `juli` — **lower case** |
| Space after symbol | `$1,250` | `€ 1.250` |
| Rooms label | `Rooms` | `Kamers` |

None of that is translation. It's **locale data**: §8.4 and PLAN §8.

The Dutch frame has also **lost its blank line before the footer** — Dutch runs ~15% longer than
English and ate the window's slack. §8.3.

---

## 11. Objects: the coin reward, and your pack

Money finally has a source (OBJECTS.md 1.1.0). Passing a room drops coins on the floor of the room,
and you can open your pack and set coins back down. Three frames, all on Dlvl 1 so they line up with
the screens above.

**The reward appears.** The keeper is satisfied; her door opens (`+`), and a `$` drops on the floor
of the room, **away from the exit**. On the way out the learner is always nearer the coins than a
roaming pet, so there is no race; in the room there is, and even before the pet roams it is a detour
worth taking (a play-testing remark). The amount is **scaled by the passing score**, so a better
answer earns more. It is a real stack on the tile, glinting until a step banks it (auto-collected).

```
Ada the Suspicious leaves 20 coins on the floor.








    ┌────────────────────┐
    │....................│
    │..<.................│
    │....................│
    │.................@.@+
    │................f...│
    │...$................│
    │....................│
    └────────────────────┘










George the Novice   Dlvl:1  Rooms:1/3  $:0  HP:12(12)  T:14
Move: arrows    Coins ($) collect when you step on them.
```

`$:0` still, because the coins are across the room, not yet in hand: walk over to the `$` and the
status line moves. That walk is the whole point of money on tiles (OBJECTS.md §5), a concrete pull
to explore rather than a counter that ticks on its own.

**Your pack (`i`).** Read-only, a count per kind, anchored right so room 1 stays in view, the same
"a panel beside the room, never a takeover" rule as the keeper's panel. Money reads as `70 coins`
here while the status line shows `$:70`: natural language in the pack, the currency mark in the
ledger. The pack holds only money today; pack-authored carriables (the Holy Grail coconuts) arrive
at 1.3.0 and will fill it then. **DELVE-0040** grew the plain "Your pack" title into a primary tab
strip named by a fixed `Info` title (**DELVE-0041**); Pack is the default tab and keeps exactly
this content; Grader is reachable with `Tab`/`Shift-Tab` or the left/right arrows but shows a
placeholder until its own child story gives it real content. Scoring shows real bars since
**DELVE-0042**/**DELVE-0043** (renamed from "Progress": it shows score, not completion), drawn in
colour on a real terminal, which this ASCII mock-up cannot render. On a colour terminal the active
tab is a filled pill, not the bracket marker shown here.

```
You look through your pack.








    ┌────────────────────┐
    │....................│
    │..<.................│                            ╔══════════════════════════════════════════╗
    │....................│                            ║                                          ║
    │.................@.@│                            ║ Info   Pack  Scoring  Grader             ║
    │................f...│                            ║                                          ║
    │....................│                            ║ 70 coins                                 ║
    │....................│                            ║                                          ║
    └────────────────────┘                            ╚══════════════════════════════════════════╝










George the Novice   Dlvl:1  Rooms:2/3  $:70  HP:12(12)  T:52
Tabs: arrows or Tab     Put away: Esc
```

**Dropping coins (`d`).** Because `$100` is a hundred `$1`, any amount can be set down, so you
**type** the number into an input field rather than nudging a stepper (a play-testing remark: the
stepper was fiddly for large counts). The digits sit in a single-line box with a cursor, the range
under it is the most you hold, and Enter drops. The keys route through one small `AmountView`, so
nothing new crosses the `ui → session` line (rule 2).

```
You count out some coins to set down.








    ┌────────────────────┐                            ╔══════════════════════════════════════════╗
    │....................│                            ║                                          ║
    │..<.................│                            ║ Drop how many?                           ║
    │....................│                            ║                                          ║
    │.................@.@│                            ║ ┌────────────────────┐                   ║
    │................f...│                            ║ │ 30                 │                   ║
    │....................│                            ║ └────────────────────┘                   ║
    │....................│                            ║                                          ║
    └────────────────────┘                            ║ 1 to 70                                  ║
                                                      ╚══════════════════════════════════════════╝









George the Novice   Dlvl:1  Rooms:2/3  $:70  HP:12(12)  T:53
Type a number   Backspace: fix   Drop: Enter   Cancel: Esc
```

**Help (`?`, DELVE-0028).** The same right-anchored panel shape as the pack, but its own two-tab
strip: Keys (shown here, the default tab) lists every key active in the learner's current context,
each with a one-line explanation, read from a single command catalogue (`session/help.py`) that a
test holds to agreement with `ui/keys.py`'s actual bindings. Objectives (not shown; a second tab,
reached the same way as Grader above) gives a static pack/chapter/room/progress summary; it
carried an optional cached LLM passage too until DELVE-0060 moved that off this tab entirely, onto
the room-entry toast below, since it routinely landed on page 2 here, behind a `--More--` a learner
had no reason to press. `?` now always means help, everywhere, including stacked over a lesson, a
question or the backpack (dismissing it hands back exactly what was open before); the pet consult,
which used to sit on `?` inside a question, moved to `@` to make room.

```
You wonder what you can do here.






                                                      ╔══════════════════════════════════════════╗
                                                      ║                                          ║
    ┌────────────────────┐                            ║ Help   Keys  Objectives                  ║
    │....................│                            ║                                          ║
    │..<.................│                            ║ arrows: Move around the room             ║
    │....................│                            ║ t: Talk to (or re-read) a keeper         ║
    │.................@.@│                            ║ s: Rest until your HP is full            ║
    │................f...│                            ║ ,: Pick up whatever is on your tile      ║
    │....................│                            ║ d: Drop something from your pack         ║
    │....................│                            ║ i: Open your pack and progress           ║
    └────────────────────┘                            ║ ?: Open or close this help               ║
                                                      ║ q: Quit                                  ║
                                                      ║                                          ║
                                                      ╚══════════════════════════════════════════╝







George the Novice   Dlvl:1  Rooms:0/3  $:0  HP:12(12)  T:14
Tabs: Tab or arrows     Put away: ? or Esc
```

**The ambient room-entry toast (DELVE-0060).** A small, top-anchored block, deliberately *not*
vertically centred like every panel above: it reads as ambient weather over the room rather than a
panel the room is paused for, because nothing about the frame below is actually paused for it. One
short passage is generated per room (not once per run, the way the Objectives passage above used
to be), queued the first time the learner stands inside it, gated or not; it appears once the
background call resolves, and fades on its own a few turns later, no dismiss key needed. The hint
line still reads exactly as an ordinary walking frame, the concrete proof: the toast is independent
of `Frame.overlay` and never blocks movement, talk, or opening a panel, and `ui/render.py` only
hides it while a panel *is* open (the same "a panel owns the screen" precedent the top message line
already follows).

```
You step into the room.

                                                      ╔══════════════════════════════════════════╗
                                                      ║ The Archive                              ║
                                                      ║                                          ║
                                                      ║ Dust motes drift through the dim         ║
                                                      ║ afternoon light as ledgers stack in      ║
                                                      ║ uneven towers, waiting for someone       ║
                                                      ║ patient enough to set them straight.     ║
    ┌────────────────────┐                            ╚══════════════════════════════════════════╝
    │....................│
    │..<.................│
    │....................│
    │.................@..│
    │................f...│
    │....................│
    │....................│
    └────────────────────┘

George the Novice   Dlvl:1  Rooms:1/3  $:70  HP:12(12)  T:119
Move: arrows    Talk: t    Look: ;    Help: ?    Quit: Q
```

These are generated by `tools/screens.py` like every frame above (screens 12-16), and `--check`
holds them to 100×30 and asserts each line fits its box.

---

## 8. What the mock-ups found

### 8.1 The payoff is one character — and this is the M2 question

Screens 1 and 5 are before and after passing an examination. **They differ by a single glyph**:
one wall segment became a `+`. That is the reward for a four-page lesson and four correct answers,
and PLAN §12 lists "the novelty wears off and it's just a quiz with extra walking" as the project's
top risk.

Options, none costed: lean on the message line, which is already doing the work ("The wall
grinds…"); make the door's *arrival* an event; reveal the corridor beyond on opening (costs the
mystery); or accept it, since NetHack's payoffs are frequently one glyph and it works there because
the anticipation is earned.

**Do not settle this on paper** — it's what M2 is for. Screen 7 is the counter-evidence and worth
weighing: the floor filling in *does* look like a dungeon, and that accumulates across a chapter
even if each door is one cell.

### 8.2 Panel: minimising pages is the wrong objective, and placement is still open

The teaching panel must not take more vertical space than it needs — every row it leaves is a row
of dungeon still visible. The obvious rule, "shortest panel that costs no extra page," **is wrong**:

| Pages | Body | Panel | Map rows kept | Worst page |
|---|---|---|---|---|
| 3 | 19 | 24 tall | **3** | 8 rows empty |
| **4** | **13** | **18 tall** | **9** | **3 rows empty** |
| 5 | 11 | 16 tall | 11 | 4 rows empty |

Four pages is shorter, shows three times the map, *and* packs better. Minimising page count
actively produces a taller, emptier panel, because paragraph-aligned pages can only break where
the author left a blank line. So the objective is **wasted rows, not pages** — PLAN §7's "pages
are cheap" applied one level down. Height is computed once and held for the encounter.

**The examination now uses the same panel** (§3), which resolves the split-personality problem an
earlier version of this document flagged. The keeper has one frame for greet, instruct, examine and
explain.

**Placement is still undecided, and the naive rule doesn't fit.** The panel is 73 wide in chapter 1
but only **66** on the tutorial floor, because the panel takes what the room leaves — and cells
clamp to 40 wide (PLAN §7), so 73 + 40 = 113 > 100 and "beside the room" is **not satisfiable in
general**. Room 1 is in the left cell so the panel goes right; a right-cell room needs it left; a
middle room in a 3×2 chapter has no good side, and would be squeezed to ~38 columns, which is not a
reading surface.

Candidates, unpicked: panel on whichever side has more space, overlaying when neither fits; shrink
to the space available (fewer columns, more pages — now known to be cheap); or **stop trying to
show the whole room and only guarantee the keeper and the player stay visible**, which is far
easier to satisfy and probably all the effect needs.

### 8.3 Rendering real text found six bugs that art would have hidden

Every one came from `tools/screens.py`'s assertions or output, not from reading the plan:

1. **`textwrap` splits on hyphens**, so `yourcompany-hr.net` rendered as `yourcompany-` / `hr.net`
   across a page break. In a phishing lesson **the domain is the payload**. Fixed with
   `break_on_hyphens=False`; the engine's renderer needs the same, and it generalises: URLs,
   domains and code spans are content, not prose.
2. **Naive line-count pagination breaks paragraphs mid-sentence** and left a page with two lines on
   it. Pages now fill with whole blocks.
3. **Dutch overflows windows that fit English.** The nl scroll consumed the two spare rows the en
   scroll has. There's now an assertion; the lesson is that **a window height verified against
   `en/` is not verified.**
4. **Minimising pages made the panel worse** (§8.2) — found only by printing the frontier.
5. **The tutorial panel silently overwrote its own bottom border** (`╚═there.═══`) because its
   height formula was three rows short and, unlike the lesson path, **had no assertion**. Same
   class as #6, found the same way: it was drawn before it was asserted.
6. Three prose lines overran their window on the first run, caught by `assert len(line) <= TEXT_W`.

### 8.4 The hint line, and currency/date/number formatting

**The hint line resolves §8.8.** An earlier version of this document said the status block was two
lines carrying one line of content, and that "later should be named, or it's a row spent on
nothing." This is later: the name and stats consolidate onto one line, and the freed row becomes a
**contextual hint line** naming the keys that work *right now*.

It earns the row three times over. It's the safety net for the learner who **skipped the tutorial**
and would otherwise get no interface teaching at all; it lets the examination move
`(1-4, or ? …)` out of the panel; and PLAN §3 says the audience "is not developers", in an app
"most people run exactly once". It's un-NetHack, and correct here for exactly that reason. Worth
deciding whether repeat learners can turn it off.

**Formatting is locale data, not translation.** `nl` uses `€`, and that pulls in five more things
(§9's table), each wrong by default:

```toml
# delve/strings/nl.toml
[format]
currency      = "€"
currency_sep  = " "        # "€ 1.250" — Dutch spaces it, English does not
thousands     = "."
decimal       = ","
months        = ["januari", "februari", "maart", ...]   # lower case: Dutch
date          = "{d} {month} {y}"
```

- **Not `locale.setlocale`.** Process-global, depends on locales being *installed* on the host,
  differs per platform — the exact dependency class PLAN §3 rejected gettext for.
- **Not `strftime('%B')`** for month names, same reason.
- **Dutch month names are lower case.** A rule, not a preference. `%B` would capitalise them on a
  Dutch host and nobody would notice for a year.

Open: **which locale a scroll formats in.** Not obviously the run's locale — a scroll is a durable
record read later, possibly by an administrator in another language.

### 8.5 The 100-column rationale was wrong, and PLAN §3 has been corrected

PLAN §3 justified 100×30 as *"a lesson window at 100 columns is a meaningfully better reading
surface than one at 80."* **Dead.** The panel is 69 columns — narrower than 80. The decision
survives on a better reason, now in PLAN §3: 100 is what lets a readable panel sit *beside* a
visible room instead of on top of it. At 80 they can't coexist and the lesson is a slide deck.

### 8.6 The assertion prompt's keys are underived, and can collide

`Antwoord: w of n` in screen 9 comes from `Waar` / `Niet waar` — first letters. English
`True`/`False` gives `t`/`f`; `Safe`/`Unsafe` gives `s`/`u`. Nothing in AUTHORING §10 says this,
and it is the **same class of bug as the True/False rule it replaced**: the format has no opinion
about language, but the *prompt* quietly does. It breaks on any pair sharing an initial —
`Waar`/`Wel waar`, `Sure`/`Sceptical`.

The hint line makes this worse, not better: it has to name the keys out loud, so a collision is
now printed on screen every turn.

Cheapest fix: don't derive keys from labels. Use `1`/`2` and print the labels. Either way **the
validator should reject an initial collision**.

### 8.7 Changing the interface silently invalidated the tutorial — in both locales

The tutorial's *job* is to describe the interface, so it hard-codes it. Two changes in this pass
broke it, and nothing would have caught either:

- `01-the-screen.md` said **"Walls are `-` and `|`"**. They're line-drawing now (§9.3).
- It said **"The bottom two lines are you. Your name, and then: …"**. That's now one line plus a
  hint line, and the Porter's "Three parts" is four.

Both fixed by hand in `en/` and `nl/`. But this is a **coupling worth naming**: the tutorial is
engine-provided precisely so it can't drift per-pack (PLAN §9), and this is the first time that
promise was tested — it held only because a human remembered. A renderer change that invalidates
pack prose is invisible to any validator that only checks structure. No fix proposed; worth
knowing before M6.

And while fixing it, a real bug in content that has shipped since `nl/` was written:

> **The Dutch tutorial was teaching an English status line.** Its example read
> `Dlvl:0  Rooms:1/2  $:0  HP:12(12)  T:14` — `Rooms`, not `Kamers`; `$`, not `€`. A Dutch learner
> was being taught to read a screen they would never see. Found by rendering the Dutch status line
> beside the Dutch tutorial for the first time.

### 8.8 There is no keeper glyph

The glyph set `- | . # @ < > + f` has nothing for a keeper, and nothing for gold though `$` appears
in the status line. These use `@` for both learner and keeper — NetHack-authentic (shopkeepers,
priests and watchmen are all `@`, told apart by colour) — but look at screen 7, where three `@`s
share a screen and only colour says which is you.

The hint line helps a little (`Talk to Grigor: t` names who's adjacent) but doesn't fix it.
Options: keep `@` and rely on colour; give keepers their own letter (`w`/`s`/`g`, but lowercase
reads as *monster* to anyone who knows NetHack); or keep `@` and pin the keeper's name in the
message line. **Decide before M2.**

### 8.9 Smaller things, each a real gap

| | |
|---|---|
| **PLAN §7's status example is wrong.** | It shows `Ada the Suspicious` on the status line, but Ada is the *keeper* in `01-phishing.md`. The learner's name belongs there. |
| **"the Novice" implies a rank system that doesn't exist.** | Invented to fill the line. Related: `Player.xp` in PLAN §5 is **vestigial** — nothing awards, reads or displays it. Give xp a job or delete the field. |
| **`Rooms:1/3` — passed, or visited?** | PLAN §7 never says which. Screen 7 reads it as *passed* while standing in room 2. They differ the moment someone backtracks. |
| **Where does gold come from?** | `$:0` for the whole slice; shopkeepers charge it, hints cost it, and nothing says how a learner *earns* any. A currency you cannot obtain is a disabled feature. |
| **Are keepers drawn on remembered tiles?** | Screen 7 draws Ada in the dimmed room 1. NetHack would not. But PLAN §7 wants backtracking *inviting*, and you don't walk back to a room you can't see anyone in. Undecided. |
| **The pet consult key.** | The hint line now commits to `?` — but `?` is help in NetHack and `#chat` is its idiom. The hint line forced this choice into the open, which is a point in its favour. |

### 8.10 REPELLED was unreachable under the old numbers; the penalty is now per failed sitting

Drawing screen 6 forced a question the design had answered only in pieces, and the pieces didn't
fit. **The penalty is now charged per *failed sitting*, not per wrong answer** (PLAN §6,
AUTHORING §4), which resolves it. Here is what was broken and why the fix works.

**The old arithmetic never reached REPELLED.** AUTHORING §4 used to read "3 HP **per wrong
answer**", with 3 attempts and starting HP 12 on a room needing `pass: 0.75` — 3 of 4. Failing a
sitting means ≥2 wrong, so a sitting cost **≥6 HP**, and HP hit zero on the *second* failure while
REPELLED needs a *third*:

| Difficulty | Old: per wrong answer | New: per failed sitting | REPELLED now lands at |
|---|---|---|---|
| `relaxed` | 0, ∞ attempts — never repels | 0, ∞ attempts — never repels | n/a (by design) |
| `standard` | ≥6 HP/sitting → HP:0 on 2nd fail | 3 HP/sitting, 3 sittings | **HP 3**, on the 3rd miss |
| `strict` | ≥10 HP/sitting → HP:0 on 1st–2nd | 5 HP/sitting, 2 sittings | **HP 2**, on the 2nd miss |

Under the old reading, HP:0 fired before attempts ran out at every difficulty — backwards, because
HP:0 respawns you at the chapter entrance (PLAN §6) while REPELLED only pushes you back one room, so
the *milder* consequence was the unreachable one and this screen could never show. Per-sitting
penalties fix it: a room's total bleed is now `penalty × attempts` (9 at standard, 10 at strict),
capped below 12, so REPELLED always arrives first and HP:3(12) on this mock-up is exactly what a
third failed sitting produces. HP:0 becomes what it should be — the *cumulative* outcome of
struggling across a whole floor, not something a single room can inflict.

This also has a design reason, not only an arithmetic one: a wrong answer already earns its
explanation, which is the teaching. Charging HP per wrong answer would tax the exploration the app
wants; charging per failed *room* puts the weight on the outcome that should carry it.

**Still open: how HP returns.** A learner only loses HP by failing sittings and REPELLED caps the
per-room loss, so a competent run spends nothing — but a struggling one accumulates damage across
the floor and needs it back. Nothing in PLAN or AUTHORING defines regeneration; a `Potion` (§5) is
the only named source, and this screen invents a `rest` action (`s`) to cover the gap. Without some
return, a wounded learner walks a slow path to HP:0, the punishment the guardrail forbids. The
penalty *model* is settled; the heal mechanism is an M4 task.

---

## 9. Unicode, emoji, and borders

### 9.1 Scope: English and Dutch environments only

**Delve targets `en` and `nl` environments. Not CJK.** A stated constraint (PLAN §8), and it's what
makes §9.3 safe. The cost, named so it isn't a surprise: **if Delve ever adds a CJK locale, the
borders break** — every box-drawing character is East Asian *Ambiguous*, one cell in a Western
terminal and **two** in a CJK-configured one, which tears the grid apart.

### 9.2 "ASCII only" was already false

```
$ grep -rPo "[^\x00-\x7F]" packs/ delve/tutorial/ | ...
  98 é     16 ó     16 →     15 ë     10 á      8 í      7 ï      5 ú      2 è      1 ü
```

**178 non-ASCII characters already ship in the packs.** Dutch cannot be written without `é` and
`ë`. The rule that's actually true:

> **Map glyphs are ASCII. Everything else is UTF-8.**
>
> The glyph set `- | . # @ < > + f` is the game's alphabet, like `+` for a door — not language, it
> doesn't translate, and it lives in a fixed grid where one cell means one column. Prose, menus,
> the status line, the hint line and the scroll are text, and text is UTF-8.

`€` is text, same width class as the `é` that shipped months ago. Settled, costs nothing.

### 9.3 Borders: `ACS_` for rooms, Unicode for windows

**Rooms** draw with curses' alternate character set — `ACS_HLINE`, `ACS_VLINE`, `ACS_ULCORNER`.
Verified:

```
ACS_* constants after initscr(): 43
sample: ACS_BBSS, ACS_BLOCK, ACS_BOARD, ACS_BSBS, ACS_BSSB, ACS_BSSS, ACS_BTEE, ACS_BULLET, ...
window.box() / window.border(): both present
```

This **isn't Unicode at all**: curses maps ACS per terminal itself — no code page bet, no font bet,
no width bet — and PDCurses provides the same names. It's what NetHack's `DECgraphics` does. The
`┌─┐` above is only how ACS *looks*; Markdown can't show ACS.

**Windows** use double-line (`╔═╗`), which has **no ACS equivalent** and is a genuine Unicode bet.
Taken deliberately: legal under §9.1, the terminal must already be UTF-8 for `é`, and it makes a
window frame instantly distinguishable from a room wall — which matters in screen 2, where a panel
sits beside a room.

- **This is the riskiest thing in the design on Windows.** PDCurses is already PLAN §12's stated
  Windows risk. **Add it to the M1 Windows test** alongside `é` and `€`. If it fails, rooms keep
  ACS and windows fall back to single-line ACS — the fallback is one dict.
- Map glyphs stay ASCII regardless. Walls are terrain drawn *by* the renderer; `@`, `f`, `<`, `>`,
  `+`, `#` are the alphabet.

### 9.4 Emoji: no. Arithmetic, not taste

Measured with `unicodedata.east_asian_width` on Python 3.14:

| Character | Codepoint | Width class | Plane |
|---|---|---|---|
| 💀 skull | U+1F480 | **WIDE (2 cells)** | astral |
| 🚪 door | U+1F6AA | **WIDE (2 cells)** | astral |
| 🧙 mage | U+1F9D9 | **WIDE (2 cells)** | astral |
| ⚔️ swords | U+2694 U+FE0F | ambiguous **+ variation selector** | BMP |
| `@` | U+0040 | narrow (1 cell) | BMP |

Three reasons, any one fatal: **width** (a 2-cell glyph in a 1-cell grid rewrites layout,
corridors, the cap and the budget, for decoration); **the astral plane** (above U+FFFF, where
PDCurses is worst); **multi-codepoint sequences** (⚔️ is two codepoints, ZWJ emoji five or more, so
`glyph: str` stops meaning "a character").

And the aesthetic reason, which outranks all three: this is NetHack. The `@` *is* the game.

---

## 10. What the mock-ups confirmed

- **The §7 screen budget is right.** 1 + 27 + 2 = 30; the map area is genuinely 100×27.
- **The generator geometry works.** Screen 8 is the real chapter 1: 3 rooms → 3×1 → 33×15 cells,
  jittered, two L-corridors, connected by construction.
- **The pack format survives contact with a screen.** Every word in screens 0, 2–4 and 9–11 is
  verbatim. Nothing needed reformatting; the 189-character question and the five-option question
  both render without special handling.
- **Dutch renders with no format change at all.** `[wn]` (§8.6) is the *prompt*; `€` (§8.4) is
  locale data. Neither is the format.
- **`€` costs nothing.** Same width class as the `é` shipping since `nl/` was written.
- **Line-drawing borders are a real improvement and mostly free** — ACS for rooms is portable by
  construction (§9.3).

And one claim it **disproved**: PLAN §3's "100 columns is a better reading surface than 80" (§8.5).
The decision survives; the reason doesn't.
