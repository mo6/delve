"""Everything a learner can do, as data. The whole frontend contract's input half.

Direction is re-exported here so `ui` can build a Move without importing `engine` (PLAN.md
section 4, rule 2): the value flows ui -> session -> engine, but ui's import stays inside
session. M2 adds Talk, Answer, Confirm and Dismiss; M4 adds Consult (ask the pet) and Rest
(heal); M5 adds Descend and Ascend for the stairs between chapters.
"""

from dataclasses import dataclass

from delve.engine.world import Direction

__all__ = [
    "Direction", "Move", "Talk", "Answer", "AnswerText", "Type", "GradeReady", "Confirm",
    "Consult", "Rest", "Wait", "Descend", "Ascend", "Dismiss", "Pickup", "Drop", "Inventory",
    "TabCycle", "SubTabCycle", "FocusRow", "Digit", "Backspace", "Quit", "Help", "Command",
]


@dataclass(frozen=True)
class Move:
    direction: Direction


@dataclass(frozen=True)
class Talk:
    pass


@dataclass(frozen=True)
class Answer:
    choice: int   # index into the options as displayed (already shuffled by the gate)


@dataclass(frozen=True)
class AnswerText:
    text: str   # a whole typed free-text answer, submitted for grading (Phase 2, PHASE2.md sec. 4)


@dataclass(frozen=True)
class Type:
    char: str   # one printable character appended to the free-text answer buffer


@dataclass(frozen=True)
class GradeReady:
    # A poll tick while a free-text answer is being graded on a worker (PHASE2.md section 5.3). The
    # UI sends it on a timeout so the session folds in the verdict the instant the worker is done;
    # it carries no payload (the verdict comes from the runner, not the UI).
    pass


@dataclass(frozen=True)
class Confirm:
    yes: bool = True   # space/continue is Confirm(True): proceed through the encounter


@dataclass(frozen=True)
class Consult:
    pass   # ask the pet for a hint on the current question; costs that question's score


@dataclass(frozen=True)
class Rest:
    pass   # rest until healed; the return of HP the failure model needs (PLAN section 6)


@dataclass(frozen=True)
class Wait:
    pass   # stand still for a turn so the companion can move while you hold position (PETS.md)


@dataclass(frozen=True)
class Descend:
    pass   # take the stairs down to the next chapter; only works while standing on '>'


@dataclass(frozen=True)
class Ascend:
    pass   # climb the stairs up to the previous chapter; only works while standing on '<'


@dataclass(frozen=True)
class Dismiss:
    pass


@dataclass(frozen=True)
class Pickup:
    pass   # take carriable items off the tile you stand on (1.1); money auto-collects on a step


@dataclass(frozen=True)
class Drop:
    pass   # open the drop menu: choose a kind, then an amount, and put it on your tile


@dataclass(frozen=True)
class Inventory:
    pass   # open the read-only info panel (pack/progress/grader tabs); Esc puts it away


@dataclass(frozen=True)
class TabCycle:
    delta: int   # move the info panel's active primary tab by +1/-1 (Tab/Shift-Tab), wraps


@dataclass(frozen=True)
class SubTabCycle:
    delta: int   # move the info panel's active sub-tab by +1/-1 ('['/']', DELVE-0055); wraps, and
                 # is a no-op on a primary tab with no sub-tabs (only Scoring has any so far)


@dataclass(frozen=True)
class FocusRow:
    delta: int   # move the info panel's keyboard focus between its tab rows (up/down, DELVE-0056):
                 # negative moves to the primary row, positive to the active tab's sub-tab row (a
                 # no-op there is no such row). Left/right then cycle whichever row has focus.


@dataclass(frozen=True)
class Select:
    delta: int   # move the assertion's button focus by +1/-1 (the arrows); Enter confirms it


@dataclass(frozen=True)
class Digit:
    value: int   # a typed digit (0-9) appended to the drop-amount field, clamped to the maximum


@dataclass(frozen=True)
class Backspace:
    pass   # delete the last digit typed into the drop-amount field


@dataclass(frozen=True)
class Quit:
    pass


@dataclass(frozen=True)
class Help:
    pass   # open/close the ? help overlay (DELVE-0028); free, like re-reading a lesson


Command = (
    Move | Talk | Answer | AnswerText | Type | GradeReady | Confirm | Consult | Rest | Wait
    | Descend | Ascend | Dismiss | Pickup | Drop | Inventory | TabCycle | SubTabCycle | FocusRow
    | Select | Digit | Backspace | Quit | Help
)
