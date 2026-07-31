"""RunState <-> a serialisable dict: the learner's mark on the dungeon, and nothing else.

The dungeon regenerates tile-for-tile from (seed, cols, rows, pack) (PLAN.md section 10), so a
snapshot stores only what the layout cannot: where the learner stands, their HP and gold, the
turn, which tiles they have seen, and which gates they have passed (with the score to re-award
on the scroll). Resuming rebuilds the run with `new_game` and lays this mark back over it,
re-opening every earned door without re-examining a thing.

It is JSON-shaped (lists, dicts, numbers, strings) so the store can keep it as a text blob.
"""

from delve.engine.entities import Pet
from delve.engine.items import Stack, by_id
from delve.engine.world import Point


def _pet_dict(pet):
    """The companion, or None for a soloist. Carries species and name (chosen at the start, not in
    the run record), the carried purse (a cat may be holding the learner's coins across a save), and
    the object a dog is fetching (`carried_item`, DELVE-0016), so a mid-fetch resume drops it in the
    same place (PETS.md section 9)."""
    if pet is None:
        return None
    d = {"pos": [pet.pos.x, pet.pos.y], "species": pet.species, "name": pet.name,
         "carried": pet.carried, "cooldown": pet.cooldown}
    if pet.carried_item is not None:
        d["carried_item"] = [pet.carried_item.defn.id, pet.carried_item.count]
    return d


def _restore_pet(run, pd) -> None:
    """Lay the saved companion back over the rebuilt run. None is a soloist; a bare list is a
    pre-1.2 snapshot (position only). Otherwise restore species, name, the carried purse, and any
    object a dog was fetching (dropping a kind the registry no longer knows, like a stale pile)."""
    if pd is None:
        run.pet = None
        return
    if isinstance(pd, list):                          # pre-1.2: only a position was stored
        if run.pet is not None:
            run.pet.pos = Point(*pd)
        return
    if run.pet is None:
        run.pet = Pet(pos=Point(*pd["pos"]))
    run.pet.pos = Point(*pd["pos"])
    run.pet.species = pd.get("species", run.pet.species)
    run.pet.name = pd.get("name", run.pet.name)
    run.pet.carried = pd.get("carried", 0)
    run.pet.cooldown = pd.get("cooldown", 0)
    restored = _unstack([pd["carried_item"]]) if pd.get("carried_item") else []
    run.pet.carried_item = restored[0] if restored else None


def _stacks(pile) -> list:
    return [[s.defn.id, s.count, s.charge] for s in pile]


def _unstack(raw) -> list:
    """Rebuild a pile from `[[def-id, count], ...]` or `[[def-id, count, charge], ...]`, dropping
    any kind the registry no longer knows (a pack item from a pack that is gone); its coins/objects
    simply vanish, never crash. A pre-DELVE-0067 snapshot has no third element; a floor torch it
    saved defaults to `charge=None` (full duration) on load, the accepted non-goal for an old save.
    """
    out = []
    for entry in raw:
        def_id, count, *rest = entry
        charge = rest[0] if rest else None
        defn = by_id(def_id)
        if defn is not None:
            out.append(Stack(defn, count, charge))
    return out


def to_dict(run) -> dict:
    """The learner's mark, ready to be JSON-encoded and written to `runs.snapshot`."""
    return {
        "idx": run.idx,
        "turn": run.turn,
        "finished": run.finished,
        "scroll_claimed": run._scroll_claimed,
        "greeted": sorted(run._greeted),
        "player": {
            "pos": [run.player.pos.x, run.player.pos.y],
            "hp": run.player.hp,
            "max_hp": run.player.max_hp,
            "gold": run.player.gold,
            "inventory": _stacks(run.player.inventory),
            "torch_charge": run.player.torch_charge,
        },
        "pet": _pet_dict(run.pet),
        "chapters": [
            {
                "discovered": sorted([p.x, p.y] for p in cr.discovered),
                "visited_rooms": sorted(cr.visited_rooms),
                "items": [[p.x, p.y, _stacks(pile)] for p, pile in sorted(cr.items.items())],
                "passed": {
                    rid: {"score": g.passed_score, "sittings": g.sittings, "hints": g.hints_used}
                    for rid, g in cr.gates.items() if g.passed
                },
            }
            for cr in run.chapters
        ],
    }


def apply_dict(run, data: dict) -> None:
    """Lay a snapshot back over a freshly built run (same seed, size and pack). Re-opens every
    earned gate so the doors, stairs and pedestal the learner earned are open again."""
    run.idx = data["idx"]
    run.turn = data["turn"]
    run.finished = data["finished"]
    run._scroll_claimed = data["scroll_claimed"]
    run._greeted = set(data["greeted"])

    p = data["player"]
    run.player.pos = Point(*p["pos"])
    run.player.hp = p["hp"]
    run.player.max_hp = p["max_hp"]
    run.player.gold = p["gold"]
    run.player.inventory = _unstack(p.get("inventory", []))
    # A pre-1.25 snapshot (before DELVE-0062) has no torch charge at all; falling back to 0 leaves
    # the learner dark on resume rather than crashing, the same graceful-tail treatment `_pet_dict`
    # already gives an older save shape.
    run.player.torch_charge = p.get("torch_charge", 0)
    _restore_pet(run, data.get("pet"))

    for cr, cdata in zip(run.chapters, data["chapters"], strict=True):
        cr.discovered = {Point(x, y) for x, y in cdata["discovered"]}
        cr.visited_rooms = set(cdata.get("visited_rooms", []))
        cr.items = {Point(x, y): _unstack(raw) for x, y, raw in cdata.get("items", [])}
        for rid, gd in cdata["passed"].items():
            gate = cr.gates[rid]
            gate.passed_score = gd["score"]
            gate.sittings = gd["sittings"]
            gate.hints_used = gd["hints"]
            gate.reopen(cr.chapter.grid)
