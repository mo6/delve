"""Objects on the floor and in the pack: a generic item model, money above all (OBJECTS.md).

Pure data, like the rest of `engine`: an `ItemDef` is a *kind* of thing (money, a coconut half)
and a `Stack` is a count of one kind lying on a tile or held in a pack. Identical kinds merge into
one stack, so a hundred single coins are one `$` stack of 100 and picking up or dropping is just a
change to the count. Nothing here imports content, session, or a colour type: a def's `colour` is a
plain name string the session turns into a view-model `Colour` at paint time (CLAUDE.md rule 1).

Phase 1 (1.1.0) ships this model, money, and pickup/drop; pack-authored kinds and their flavour
effects (`on_move` and friends) arrive with the pack format at 1.3.0.
"""

from dataclasses import dataclass

# The two closed sets the validator holds a pack's item files to (OBJECTS.md sections 4 and 9),
# kept here beside `ItemDef` because they *are* the field's domain: a glyph is one of NetHack's
# object-class chars (all ASCII, so an object never smuggles a wide cell into the map, CLAUDE.md),
# and a colour is one of the sixteen the view model paints. Constants only, so `engine` still
# imports nothing (rule 1); the colour names deliberately mirror `session.views.Colour`'s values.
OBJECT_GLYPHS = frozenset('$(%!?[*)="')
COLOURS = frozenset({
    "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white",
    "bright_black", "bright_red", "bright_green", "bright_yellow",
    "bright_blue", "bright_magenta", "bright_cyan", "bright_white",
})


@dataclass(frozen=True)
class ItemDef:
    """A kind of object. `carriable` False means it banks rather than filling an inventory slot
    (money); `value` is worth per unit; `bulky` fills a whole tile so nothing else may share it.
    The three flavour strings are the closed effect vocabulary a pack may set (OBJECTS.md sec. 9):
    `look` is the inventory-panel description, `on_pickup` prints once when the kind first enters
    your hands, `on_move` prints each step while you carry it (deduped by kind, so two coconut
    halves clip-clop once)."""

    id: str
    glyph: str            # one ASCII object-class char: $ ( % ! ? [ * ) = "
    name: str             # singular; a stack of several renders as "coconut half (2)"
    colour: str           # a Colour name the session resolves, e.g. "bright_yellow"
    carriable: bool = True
    value: int = 0
    bulky: bool = False
    look: str = ""        # the "look" description, shown in the inventory panel
    on_pickup: str = ""   # printed once, when the kind first enters your hands (one, or default)
    on_pickup_plural: str = ""  # the same for more than one; a `{count}` slot gets the number word
    on_move: str = ""     # printed on some steps while carried (deduped by kind)
    on_move_short: str = ""  # the abbreviated on_move, used after a few full utterances
    on_move_min: int = 1  # least you must carry for on_move to fire (2: a coconut needs its pair)
    plural: str = ""      # the plural name, e.g. "coconut halves"; empty falls back to name + "s"


@dataclass(frozen=True)
class Stack:
    """A count of one kind. Frozen: a change to the count makes a new Stack, so a pile is rebuilt
    rather than mutated, which keeps the snapshot and the tests reasoning about values, not aliases.

    `charge` is per-unit remaining-steps state (DELVE-0067), meaningful only for the torch: `None`
    means "not charge-tracked" (every non-torch kind, and a never-lit torch, which reads as full
    duration). It exists on every `Stack` rather than a torch-only subtype so `merged`/`taken` stay
    one code path; for a non-torch kind it is always `None` on both sides of a comparison, so those
    kinds merge exactly as before.
    """

    defn: ItemDef
    count: int
    charge: int | None = None

    @property
    def worth(self) -> int:
        return self.count * self.defn.value

    def with_count(self, count: int) -> Stack:
        return Stack(self.defn, count, self.charge)


# The built-in currency, the one kind every pack gets for free. A `$` stack's worth is its count.
MONEY = ItemDef(id="money", glyph="$", name="coin", colour="bright_yellow",
                carriable=False, value=1)

# The built-in torch (DELVE-0062), the other kind every pack gets for free, under every pack, with
# no pack-authoring involved. `name` is never actually shown: like money, its display word is
# localised through dedicated `Strings` keys (`item.torch_one`/`item.torches`) rather than this
# field, so the exact Dutch word ("fakkel", never "toorts") is pinned in one place regardless of
# this constant (`RunState._label`/`_item_phrase`, the same bypass `MONEY` already gets).
TORCH = ItemDef(id="torch", glyph="(", name="torch", colour="bright_yellow", carriable=True)

# Steps of light one torch gives before it burns out (DELVE-0062), roughly a floor's worth of
# normal walking. Tunable here without touching the mechanic itself.
TORCH_DURATION_STEPS = 150

# def-id -> ItemDef, so a snapshot can round-trip a stack by id. Money and the torch are always
# here; a pack's kinds register when the session assembles it (`new_game`), so `by_id` resolves
# them on resume too (OBJECTS.md section 10). The map is a process global keyed by id; a fresh pack
# load overwrites its own ids, which is what a re-run wants.
REGISTRY: dict[str, ItemDef] = {MONEY.id: MONEY, TORCH.id: TORCH}


def by_id(def_id: str) -> ItemDef | None:
    return REGISTRY.get(def_id)


def register(defn: ItemDef) -> None:
    """Make a pack-authored kind resolvable by id, so a `Stack` of it round-trips through the
    snapshot. Idempotent by id; the session calls it for every kind a pack defines."""
    REGISTRY[defn.id] = defn


def merged(pile: list[Stack], stack: Stack) -> list[Stack]:
    """Return `pile` with `stack` added: its count folded into a matching kind at the same charge,
    or appended. A bulky kind never shares a tile, so it may only be added to an empty pile; the
    caller checks `can_place` first, this trusts it. The charge check (DELVE-0067) is a no-op for
    every non-torch kind, whose `charge` is always `None` on both sides; it only ever keeps two
    differently-charged torches from folding into one indistinguishable pile."""
    out = list(pile)
    for i, s in enumerate(out):
        if s.defn.id == stack.defn.id and s.charge == stack.charge:
            out[i] = s.with_count(s.count + stack.count)
            return out
    out.append(stack)
    return out


# Sentinel for `taken`'s `charge` parameter: "any charge matches" (the original, charge-blind
# behaviour). A real charge value, including `None` itself, is a real filter; only this sentinel
# means "don't filter", so a caller can still explicitly ask for the `None`-charge (fresh) stack.
ANY_CHARGE = object()


def can_place(pile: list[Stack], defn: ItemDef) -> bool:
    """Whether a stack of `defn` may join `pile`: always, unless a bulky kind is involved, which
    demands the tile to itself (nothing already there, and it is not landing on a bulky item)."""
    if not pile:
        return True
    if defn.bulky:
        return False
    return not any(s.defn.bulky for s in pile)


def taken(pile: list[Stack], def_id: str, count: int,
          charge=ANY_CHARGE) -> tuple[Stack | None, list[Stack]]:
    """Remove up to `count` of `def_id` from `pile`. Returns the removed stack (or None) and the
    pile that remains, with the kind dropped entirely when its count reaches zero. By default
    (`charge=ANY_CHARGE`) the first stack of `def_id` matches regardless of its charge, exactly the
    original behaviour; pass a specific `charge` (DELVE-0067) to take from the one stack that has
    it, needed once a pile can hold two differently-charged torches side by side."""
    out: list[Stack] = []
    took: Stack | None = None
    for s in pile:
        if s.defn.id == def_id and (charge is ANY_CHARGE or s.charge == charge) and took is None:
            n = min(count, s.count)
            took = Stack(s.defn, n, s.charge)
            if s.count > n:
                out.append(s.with_count(s.count - n))
        else:
            out.append(s)
    return took, out
