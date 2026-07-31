# Answer buttons — proof of concept

A throwaway spike for the answer-button design in [docs/BUTTONS.md](../../docs/BUTTONS.md), so the
look can be felt in a real terminal before any of it is built into the game. It imports nothing from
`delve` and lives outside the test gate, like `poc/llm-grader/`.

```
python3 poc/buttons/buttons_poc.py
```

It draws the examination panel for every question type. **The button style is for binary questions
only** (an assertion, a yes/no prompt); a 3+ option MCQ stays a plain numbered list, and a free-text
question is a typed input line. **Only the selected choice gets a background** on its key badge
(black-on-cyan, or reverse video with colour off), so the selection stands out even in black and
white; resting choices are plain. Press `c` to toggle colour and see the monochrome fallback.

- **Tab** cycles the four: the MCQ list (BUTTONS.md §5), the two-button assertion (§4), a **Yes / No**
  prompt in the same button style, and a **free-text** typed input line (Phase 2).
- Choice demos: **arrows / hjkl** move the selection; **1-4**, **w/n**, or **y** jump to an option;
  **Enter/Space** choose it; **q** quits.
- Free-text demo: **type** the answer, **Backspace** deletes, **Enter** submits, **Esc** quits
  (`q` is a typable letter there).

This is a design sketch, not the real renderer: it hard-codes sample content from
[docs/SCREENS.md](../../docs/SCREENS.md) and does its own box-drawing. If the look is adopted, the
real work is a `delve/ui/windows.py` change and regenerated SCREENS.md frames (BUTTONS.md §10, §11),
not this file.
