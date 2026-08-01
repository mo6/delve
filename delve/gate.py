"""gate: the seam. The ONLY module that knows both the dungeon and the training.

It seals a room's outgoing door, stands the keeper beside it, runs the greet -> instruct ->
examine -> explain lifecycle (PLAN.md section 6), and on a pass turns the SealedWall into a
Door. The shell never parses a question; a pack never places a door (CLAUDE.md rule 1).

M4 gives the gate stakes: a failed sitting spends an attempt and costs `stakes.penalty` HP
(once, never per wrong answer), and running the attempts out is REPELLED. The gate reports the
outcome and the HP owed as a `SittingResult`; the session spends the HP and decides push-back or
respawn. The gate holds the attempt budget because it outlives a single sitting, while an
`Examination` is one sitting and is discarded when it fails.
"""

from dataclasses import dataclass, field
from enum import Enum, auto

from delve.assess.examination import DIFFICULTIES, Examination, Stakes
from delve.assess.question import Question
from delve.content.pack import Room as RoomContent
from delve.engine.entities import Keeper
from delve.engine.rng import Rng
from delve.engine.world import Chapter, Grid, Point, Room, TileKind


class GateState(Enum):
    SEALED = auto()        # exit is stone; keeper waits
    INSTRUCTION = auto()   # lesson panel open
    EXAMINATION = auto()   # a question is posed
    EXPLANATION = auto()   # an answer's explanation is shown
    UNLOCKED = auto()      # passed; the door exists and re-examination is refused


@dataclass(frozen=True)
class SittingResult:
    """What finishing a sitting means to the world: the outcome, and the HP it owes.

    outcome is 'next' (another question), 'passed' (unlocked), 'failed' (re-sit, attempt spent),
    or 'repelled' (attempts exhausted, pushed back). `penalty` is charged by the session on a
    failed or repelled sitting; it is zero at relaxed and on the passing/next paths.
    """

    outcome: str
    penalty: int = 0


@dataclass
class Gate:
    content: RoomContent
    keeper: Keeper
    door_pos: Point
    sealed_glyph: str
    # What passing reveals at door_pos. A mid-chapter room opens a door; the last room of a
    # chapter reveals the stairs down, or, in the final chapter, the pedestal the scroll rests on
    # (PLAN.md section 6). The gate stays ignorant of chapters; the installer picks the target.
    unlock_kind: TileKind = TileKind.DOOR
    unlock_glyph: str = "+"
    stakes: Stakes = field(default_factory=lambda: DIFFICULTIES["standard"])
    state: GateState = GateState.SEALED
    passed: bool = False
    # Coins already paid for this pass; the on-pass reward is once-only (OBJECTS.md).
    rewarded: bool = False
    attempts_used: int = 0     # failed sittings since the last fresh budget (reset by REPELLED)
    hints_used: int = 0        # questions the pet was consulted on (for the scroll, later)
    free_consult_used: bool = False   # the cat's one free consult for this room has been spent
    sittings: int = 0          # sittings finished (pass or fail): the room_results attempt count
    passed_score: float = 0.0  # the score of the sitting that passed, recorded once for the scroll
    _exam: Examination | None = field(default=None, repr=False)
    _order: list[int] = field(default_factory=list, repr=False)   # display index -> option index
    # Display indices the pet ruled out (advisory, still selectable) and ones gold eliminated
    # (gone from the sitting). Both clear on `_shuffle` / exam teardown so a re-sit starts fresh
    # (DELVE-0018); neither is drawn from `self.rng`.
    _struck: int | None = field(default=None, repr=False)
    _eliminated: set[int] = field(default_factory=set, repr=False)
    last_question: Question | None = field(default=None, repr=False)
    last_correct: bool = False

    # -- reading -------------------------------------------------------------------------

    @property
    def lesson(self):
        return self.content.lesson

    # -- examination ---------------------------------------------------------------------

    def begin_exam(self, rng: Rng, text_grader=None) -> None:
        self._exam = Examination(list(self.content.questions), self.content.pass_mark,
                                 text_grader=text_grader)
        self._shuffle(rng)
        self.state = GateState.EXAMINATION

    def _shuffle(self, rng: Rng) -> None:
        q = self._exam.current()
        order = list(range(len(q.options)))
        if q.kind == "mcq":          # assertions keep the author's order; MCQ shuffles
            rng.shuffle(order)
        self._order = order
        self._struck = None
        self._eliminated = set()

    def current_question(self) -> Question:
        return self._exam.current()

    def display_options(self) -> list[str]:
        """Option texts in the shuffled order shown to the learner. Never reveals which is
        correct: the explanation only enters a frame after an answer (PLAN.md section 4)."""
        q = self._exam.current()
        return [q.options[i].text for i in self._order]

    def progress(self) -> tuple[int, int]:
        return self._exam.idx + 1, self._exam.total

    @property
    def assisted_here(self) -> bool:
        """True when the pet has already been consulted on the current question."""
        return self._exam is not None and self._exam.assisted_now

    @property
    def struck(self) -> int | None:
        """Display index the pet ruled out on this question, or None."""
        return self._struck

    @property
    def eliminated(self) -> frozenset[int]:
        """Display indices removed by a paid gold elimination this question (DELVE-0018)."""
        return frozenset(self._eliminated)

    def standing_count(self) -> int:
        """How many options are still selectable on the current question."""
        return len(self._order) - len(self._eliminated)

    def next_wrong_to_eliminate(self) -> int | None:
        """The original-order index of the next wrong option that is still standing, or None when
        every wrong one is already gone. Deterministic (first wrong in author order, skipping
        eliminated), never drawn from the exam shuffle RNG (DELVE-0018)."""
        q = self._exam.current()
        for i, opt in enumerate(q.options):
            if opt.correct:
                continue
            display = self._order.index(i)
            if display not in self._eliminated:
                return i
        return None

    def eliminate(self, original: int) -> int:
        """Remove one wrong option from the current question by its original index. Returns the
        display index that was eliminated. Does **not** call `Examination.assist`: paying gold
        keeps the question's score (DELVE-0018), unlike a pet consult."""
        display = self._order.index(original)
        self._eliminated.add(display)
        return display

    def answer(self, display_choice: int) -> bool:
        original = self._order[display_choice]
        self.last_question = self._exam.current()
        correct = self._exam.grade(original)
        self.last_correct = correct
        self.state = GateState.EXPLANATION
        return correct

    def answer_text(self, answer: str) -> bool:
        """Grade a typed free-text `answer` and move to the explanation, the string twin of
        `answer` (PHASE2.md section 4), in one synchronous call. The exam holds the grader, so the
        gate stays ignorant of how the verdict was reached, LLM or keyword floor."""
        self.last_question = self._exam.current()
        correct = self._exam.grade_text(answer)
        self.last_correct = correct
        self.state = GateState.EXPLANATION
        return correct

    def record_text_verdict(self, correct: bool) -> bool:
        """Record a free-text verdict the session already computed (its grader-runner, sync inline
        or async on a worker, PHASE2.md section 5.3), skipping the exam's own grader. The scoring
        bookkeeping and the move to EXPLANATION are the same as `answer_text`; only who graded
        differs."""
        self.last_question = self._exam.current()
        self._exam.record_text(correct)
        self.last_correct = correct
        self.state = GateState.EXPLANATION
        return correct

    def consult(self, original: int, free: bool = False) -> int:
        """Record the pet's help on the current question and return the display index of the option
        it rules out. A paid consult stops the question counting toward the score; a `free` one
        (the cat's first per room, OBJECTS.md section 8) shows the same strike at no cost. A repeat
        consult on the same question re-reports the strike for free either way. The display index
        is stored on the gate so a later overlay rebuild (arrow focus) keeps the strike visible."""
        if self._exam.assist(free=free):
            self.hints_used += 1
            if free:
                self.free_consult_used = True
        display = self._order.index(original)
        self._struck = display
        return display

    def proceed(self, rng: Rng, grid: Grid) -> SittingResult:
        """Advance past an explanation: next question, or finish the sitting. A failed sitting
        spends an attempt and owes `stakes.penalty` HP; exhausting the attempts is REPELLED,
        which resets the budget so the learner may re-read and try again (PLAN.md section 6)."""
        self._exam.advance()
        if not self._exam.finished:
            self._shuffle(rng)
            self.state = GateState.EXAMINATION
            return SittingResult("next")
        self.sittings += 1
        if self._exam.passed():
            self.passed_score = self._exam.score()
            self._unlock(grid)
            self._exam = None
            return SittingResult("passed")

        self._exam = None
        self.state = GateState.SEALED
        self.attempts_used += 1
        exhausted = self.stakes.attempts is not None and self.attempts_used >= self.stakes.attempts
        if exhausted:
            self.attempts_used = 0          # a fresh budget after a re-read; REPELLED is not death
            return SittingResult("repelled", self.stakes.penalty)
        return SittingResult("failed", self.stakes.penalty)

    def _unlock(self, grid: Grid) -> None:
        t = grid.at(self.door_pos.x, self.door_pos.y)
        t.kind = self.unlock_kind
        t.glyph = self.unlock_glyph
        self.state = GateState.UNLOCKED
        self.passed = True

    def reopen(self, grid: Grid) -> None:
        """Re-apply an earned pass to the world when resuming from a snapshot: paint the door,
        stairs or pedestal and mark the gate passed, without re-running the examination. Passing
        is final (CLAUDE.md rule 3), so a resumed run never re-sits a room it already cleared."""
        self._unlock(grid)

    def abandon(self) -> None:
        """Esc out of a sitting without penalty; the room re-seals for a fresh attempt."""
        if not self.passed:
            self.state = GateState.SEALED
        self._exam = None


def install_gates(chapter: Chapter, gated: list[RoomContent],
                  difficulty: str = "standard") -> dict[str, Gate]:
    """Seal each gated room's outgoing door and stand its keeper beside it. `gated`'s room ids
    must match chapter room ids (the run builds the chapter with those ids). The pack difficulty
    sets the base stakes; each room's frontmatter may override attempts or penalty (M4)."""
    base = DIFFICULTIES.get(difficulty, DIFFICULTIES["standard"])
    gates: dict[str, Gate] = {}
    for content in gated:
        door = chapter.exits[content.id]
        room = next(r for r in chapter.rooms if r.id == content.id)
        glyph = "|" if door.x in (room.x, room.x + room.w - 1) else "-"
        _seal(chapter.grid, door, glyph)
        keeper = Keeper(pos=_keeper_spot(room, door), name=content.keeper_name,
                        kind=content.keeper_kind)
        stakes = base.resolve(content.attempts, content.penalty)
        gates[content.id] = Gate(content=content, keeper=keeper, door_pos=door,
                                 sealed_glyph=glyph, stakes=stakes)
    return gates


def install_chapter_gates(chapter: Chapter, content_rooms, difficulty: str = "standard",
                          *, final: bool = False) -> dict[str, Gate]:
    """Gate every room of a full chapter (M5), in the order the layout placed them. Each room but
    the last seals its outgoing door; the last room's pass instead reveals the way onward, the
    stairs down, or, in the `final` chapter, the pedestal the scroll rests on. `content_rooms` is
    the content-side room list, whose ids match the chapter's room ids one to one."""
    base = DIFFICULTIES.get(difficulty, DIFFICULTIES["standard"])
    rooms_by_id = {r.id: r for r in chapter.rooms}
    gates: dict[str, Gate] = {}
    for i, content in enumerate(content_rooms):
        room = rooms_by_id[content.id]
        stakes = base.resolve(content.attempts, content.penalty)
        if i < len(content_rooms) - 1:
            door = chapter.exits[content.id]
            glyph = "|" if door.x in (room.x, room.x + room.w - 1) else "-"
            _seal(chapter.grid, door, glyph)
            keeper = Keeper(pos=_keeper_spot(room, door), name=content.keeper_name,
                            kind=content.keeper_kind)
            gate = Gate(content=content, keeper=keeper, door_pos=door, sealed_glyph=glyph,
                        stakes=stakes)
        else:
            target = chapter.stairs_down
            kind, glyph = (TileKind.PEDESTAL, "_") if final else (TileKind.STAIRS_DOWN, ">")
            keeper = Keeper(pos=_keeper_beside(room, target), name=content.keeper_name,
                            kind=content.keeper_kind)
            # The last room seals nothing on the grid: the stairs simply do not exist yet, so
            # there is no way out to walk past (CLAUDE.md rule 2). The pass paints them in.
            gate = Gate(content=content, keeper=keeper, door_pos=target, sealed_glyph=".",
                        unlock_kind=kind, unlock_glyph=glyph, stakes=stakes)
        gates[content.id] = gate
    return gates


def _seal(grid: Grid, door: Point, glyph: str) -> None:
    t = grid.at(door.x, door.y)
    t.kind = TileKind.SEALED
    t.glyph = glyph


def _keeper_spot(room: Room, door: Point) -> Point:
    """Where the keeper stands: diagonally beside the sealed door, not on the tile inline with
    it. She guards the exit without plugging it, so once the door opens the learner can walk
    straight through (PLAN.md section 7, 'beside its room's sealed exit'). Doors sit at a wall's
    midpoint, so the shifted tile is always interior floor."""
    if door.x in (room.x, room.x + room.w - 1):        # vertical wall: step inward, then along
        inward = door.x + 1 if door.x == room.x else door.x - 1
        along = door.y - 1 if door.y - 1 > room.y else door.y + 1
        return Point(inward, along)
    inward = door.y + 1 if door.y == room.y else door.y - 1   # horizontal wall
    along = door.x - 1 if door.x - 1 > room.x else door.x + 1
    return Point(along, inward)


def _keeper_beside(room: Room, target: Point) -> Point:
    """Where the last room's keeper stands: on an interior floor tile next to the stairs (or
    pedestal), guarding them without standing on them. The stairs sit near the room's centre, so
    an adjacent interior tile always exists."""
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)):
        p = Point(target.x + dx, target.y + dy)
        if p != target and room.contains(p):
            return p
    return target
