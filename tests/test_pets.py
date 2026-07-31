"""The companion (1.2.0, PETS.md): a chosen cat or dog that moves for itself, races the learner
for money, and is caught by a bump; or no pet at all. The engine step is exercised on hand-built
grids (pure, no session); selection, the wait key, retrieval, the cat's free consult, and the
snapshot are driven headless against `session`.
"""

import json

from delve.engine import pet as petmod
from delve.engine.entities import Pet
from delve.engine.items import MONEY, ItemDef, Stack
from delve.engine.rng import Rng
from delve.engine.world import Grid, Point, Tile, TileKind
from delve.session.commands import Consult, Move, Talk, Wait
from delve.session.run import new_run
from delve.session.snapshot import apply_dict, to_dict


def _grid(w: int, h: int) -> Grid:
    g = Grid.blank(w, h)
    for y in range(h):
        for x in range(w):
            g.tiles[y][x] = Tile(TileKind.FLOOR, ".")
    return g


def _free_adjacent(run):
    """A walkable tile next to the player that is not a keeper's, and the direction onto it."""
    from delve.engine import actions
    from delve.engine.world import Direction
    for d in Direction:
        dest = actions.step(run.chapter, run.player.pos, d)
        if dest is not None and dest not in run.keepers:
            return d, dest
    raise AssertionError("player is boxed in")


# -- the engine step (pure) ----------------------------------------------------------------------


def test_a_dog_fetches_a_coin_and_drops_it_beside_you():
    g = _grid(10, 3)
    player = Point(1, 1)
    pet = Pet(pos=Point(6, 1), species="dog", name="Rex")
    items = {Point(7, 1): [Stack(MONEY, 30)]}
    rng = Rng(1)
    for _ in range(20):                                 # it seeks the nearby coin and grabs it
        if petmod.step(g, items, player, pet, set(), rng).kind == "grabbed":
            break
    assert pet.carried == 30 and items == {}
    gave = 0
    for _ in range(30):                                 # then it heels back and sets it down by you
        ev = petmod.step(g, items, player, pet, set(), rng)
        if ev.kind == "gave":
            gave = ev.coins
            break
    assert gave == 30 and pet.carried == 0
    # DELVE-0016: the coins are dropped on the dog's tile (beside you), not handed over, so you
    # collect them by stepping across; the engine never banks.
    (coin_pos, pile), = items.items()
    assert pile == [Stack(MONEY, 30)]
    assert petmod._cheby(coin_pos, player) <= 1 and coin_pos != player


STONE = ItemDef(id="smooth-stone", glyph="*", name="smooth stone", colour="white")


def test_a_dog_fetches_an_object_and_drops_it_beside_you():
    # DELVE-0016: the dog fetches any floor item, not only coins, and sets it down beside you like
    # money (the Peddler-room smooth-stone report).
    g = _grid(10, 3)
    player = Point(1, 1)
    pet = Pet(pos=Point(6, 1), species="dog", name="Rex")
    items = {Point(7, 1): [Stack(STONE, 1)]}
    rng = Rng(1)
    for _ in range(20):
        if petmod.step(g, items, player, pet, set(), rng).kind == "grabbed_item":
            break
    assert pet.carried_item == Stack(STONE, 1) and items == {}   # in its paws, off the floor
    delivered = None
    for _ in range(30):
        ev = petmod.step(g, items, player, pet, set(), rng)
        if ev.kind == "gave_item":
            delivered = ev.item
            break
    assert delivered == Stack(STONE, 1) and pet.carried_item is None
    (drop_pos, pile), = items.items()                            # set down beside you, not banked
    assert pile == [Stack(STONE, 1)]
    assert petmod._cheby(drop_pos, player) <= 1 and drop_pos != player


def test_a_dog_carries_one_object_at_a_time():
    # While carrying an object the dog heels to deliver; it does not scoop a second stack it passes.
    g = _grid(12, 3)
    player = Point(1, 1)
    pet = Pet(pos=Point(6, 1), species="dog", carried_item=Stack(STONE, 1))
    items = {Point(5, 1): [Stack(STONE, 1)]}                     # a second stone on the way home
    rng = Rng(1)
    for _ in range(30):
        ev = petmod.step(g, items, player, pet, set(), rng)
        if ev.kind == "gave_item":
            break
    assert items.get(Point(5, 1)) == [Stack(STONE, 1)]           # the passed stone is untouched


def test_a_cat_walks_past_an_object():
    # The cat is money-only; widening fetch is the dog's story alone (DELVE-0016 non-goal).
    g = _grid(8, 3)
    pet = Pet(pos=Point(4, 1), species="cat")
    items = {Point(5, 1): [Stack(STONE, 1)]}
    for _ in range(20):
        petmod.step(g, items, Point(0, 1), pet, set(), Rng(1))
    assert pet.carried_item is None and items == {Point(5, 1): [Stack(STONE, 1)]}


def test_a_dog_leaves_fresh_money_alone_after_delivering():
    """After handing a purse over, the dog wanders off and ignores money for a cooldown, rather than
    pouncing straight back onto coins dropped at its feet (play-testing note)."""
    g = _grid(10, 3)
    player = Point(1, 1)
    pet = Pet(pos=Point(2, 1), species="dog", carried=30)
    rng = Rng(1)
    for _ in range(5):                                  # it is adjacent, so it delivers at once
        if petmod.step(g, {}, player, pet, set(), rng).kind == "gave":
            break
    assert pet.carried == 0 and pet.cooldown > 0

    items = {Point(3, 1): [Stack(MONEY, 20)]}           # coins right beside it
    grabbed = any(petmod.step(g, items, player, pet, set(), rng).kind == "grabbed"
                  for _ in range(petmod.FETCH_COOLDOWN))
    assert not grabbed and items                        # left untouched through the whole cooldown


def test_a_carrying_cat_stays_near_you_rather_than_fleeing():
    """Once a cat holds coins and there is nothing left to grab, it keeps to the learner's close
    surroundings instead of bolting to a corner (play-testing: 'the cat keeps to a corner')."""
    g = _grid(14, 3)
    player = Point(1, 1)
    pet = Pet(pos=Point(11, 1), species="cat", carried=30)   # far off, holding your coins
    for _ in range(20):
        petmod.step(g, {}, player, pet, set(), Rng(1))
    assert pet.carried == 30                                  # still holding, until you bump it
    assert petmod._cheby(pet.pos, player) <= petmod.KEEP_CLOSE + 1   # it came back and stayed near


def test_a_cat_chases_money_from_several_tiles_away():
    """A cat now goes for coins in range, not only ones it mills into (play-testing note)."""
    g = _grid(10, 3)
    pet = Pet(pos=Point(2, 1), species="cat")
    items = {Point(6, 1): [Stack(MONEY, 5)]}             # four tiles east, within interest
    grabbed = False
    for _ in range(12):
        if petmod.step(g, items, Point(0, 1), pet, set(), Rng(1)).kind == "grabbed":
            grabbed = True
            break
    assert grabbed and pet.carried == 5                  # it sought the coin out and took it


def test_a_cat_keeps_collecting_coins_before_it_is_caught():
    """A carrying cat still seeks and grabs more money, accumulating it, rather than freezing on the
    first purse until caught (play-testing: 'the cat only picks up money once')."""
    g = _grid(12, 3)
    pet = Pet(pos=Point(2, 1), species="cat")
    items = {Point(4, 1): [Stack(MONEY, 5)],
             Point(6, 1): [Stack(MONEY, 5)],
             Point(8, 1): [Stack(MONEY, 5)]}
    for _ in range(40):                                  # the player never catches it
        petmod.step(g, items, Point(0, 1), pet, set(), Rng(1))
    assert pet.carried == 15 and items == {}             # every purse taken, not only the first


def test_an_empty_pet_grabs_money_it_mills_into():
    g = _grid(6, 3)
    pet = Pet(pos=Point(2, 1), species="cat")
    items = {Point(3, 1): [Stack(MONEY, 5)]}
    ev = petmod.step(g, items, Point(0, 1), pet, set(), Rng(1))
    assert pet.pos == Point(3, 1) and pet.carried == 5 and items == {}
    assert ev.kind == "grabbed"


def test_the_pet_never_steps_on_the_player_or_a_keeper():
    g = _grid(3, 3)
    player, keeper = Point(1, 1), Point(0, 1)
    pet = Pet(pos=Point(2, 1), species="cat")
    for seed in range(40):
        petmod.step(g, {}, player, pet, {keeper}, Rng(seed))
        assert pet.pos != player and pet.pos != keeper and g.walkable(*pet.pos)


# -- selection: species, name, none --------------------------------------------------------------


def test_the_default_companion_is_a_named_cat():
    run = new_run(seed=99, cols=100, rows=30)
    assert run.pet.species == "cat" and run.pet.name == "your kitten"


def test_choosing_a_dog_and_naming_it():
    run = new_run(seed=99, cols=100, rows=30, pet_species="dog", pet_name="Rex")
    assert run.pet.species == "dog" and run.pet.name == "Rex"


def test_a_soloist_has_no_pet_and_no_one_to_consult():
    run = new_run(seed=99, cols=100, rows=30, pet_species="none")
    assert run.pet is None
    frame = run.apply(Consult())
    assert "no companion" in frame.messages[-1].lower()


# -- the wait key and retrieval ------------------------------------------------------------------


def test_wait_advances_a_turn():
    run = new_run(seed=99, cols=100, rows=30)
    before = run.turn
    run.apply(Wait())
    assert run.turn == before + 1


def test_bumping_the_pet_takes_its_purse_without_swapping():
    run = new_run(seed=99, cols=100, rows=30, pet_species="dog", pet_name="Rex")
    d, dest = _free_adjacent(run)
    run.pet.pos = dest
    run.pet.carried = 30
    here, gold = run.player.pos, run.player.gold
    run.apply(Move(d))
    assert run.player.pos == here                # bumped: you do not step onto the pet
    assert run.player.gold == gold + 30 and run.pet.carried == 0


def _seed_stone(run):
    """Register the smooth stone and drop one on a walkable tile within the dog's reach, so it has
    an object to fetch. Returns the tile."""
    from delve.engine.items import register
    register(STONE)
    px, py = run.pet.pos.x, run.pet.pos.y
    for r in range(1, petmod.SPECIES["dog"].interest + 1):
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                t = Point(px + dx, py + dy)
                if (run.chapter.grid.walkable(t.x, t.y) and t != run.player.pos
                        and t != run.pet.pos and t not in run.keepers):
                    run.items[t] = [Stack(STONE, 1)]
                    return t
    raise AssertionError("nowhere to seed a stone")


def test_a_dog_delivers_a_fetched_object_beside_you_with_a_message():
    run = new_run(seed=99, cols=100, rows=30, pet_species="dog", pet_name="Rex")
    _seed_stone(run)
    dropped = False
    for _ in range(60):
        frame = run.apply(Wait())
        if "smooth stone" in frame.messages[-1] and "beside you" in frame.messages[-1]:
            dropped = True
            break
    assert dropped                                          # the "sets it down beside you" line
    here = [p for p, pile in run.items.items() if any(s.defn.id == STONE.id for s in pile)]
    assert len(here) == 1 and petmod._cheby(here[0], run.player.pos) <= 1


def _run_to_delivery(run):
    """Wait until the dog sets the fetched stone down, and return the tile it landed on. The fetch
    (seek then heel then deliver) is pure BFS with no idle milling, so it draws no pet RNG at all,
    which is what lets a resumed run reproduce it tile-for-tile."""
    for _ in range(60):
        run.apply(Wait())
        here = [p for p, pile in run.items.items() if any(s.defn.id == STONE.id for s in pile)]
        if run.pet.carried_item is None and here and run.pet.cooldown > 0:
            return here[0]
    raise AssertionError("the dog never delivered")


def test_a_dog_fetch_lands_the_object_on_the_same_tile_on_a_rebuild():
    a = new_run(seed=99, cols=100, rows=30, pet_species="dog", pet_name="Rex")
    _seed_stone(a)
    b = new_run(seed=99, cols=100, rows=30, pet_species="dog", pet_name="Rex")
    _seed_stone(b)
    assert _run_to_delivery(a) == _run_to_delivery(b)        # identical dog moves and drop tile


def test_a_dog_fetch_survives_a_resume_from_snapshot():
    control = new_run(seed=99, cols=100, rows=30, pet_species="dog", pet_name="Rex")
    _seed_stone(control)
    expected = _run_to_delivery(control)

    mid = new_run(seed=99, cols=100, rows=30, pet_species="dog", pet_name="Rex")
    _seed_stone(mid)
    mid.apply(Wait())                                        # a couple of BFS steps into the fetch
    mid.apply(Wait())
    resumed = new_run(seed=99, cols=100, rows=30, pet_species="dog", pet_name="Rex")
    from delve.engine.items import register
    register(STONE)                                          # the pack would; a bare run must too
    apply_dict(resumed, json.loads(json.dumps(to_dict(mid))))
    assert _run_to_delivery(resumed) == expected            # the fetch finishes on the same tile


# -- the cat's free consult (OBJECTS.md section 8) -----------------------------------------------


def test_the_cats_free_consult_saves_a_pass_the_dog_would_lose():
    # test_stakes.test_consulting_costs_the_pass: a dog consulting the first two questions drops the
    # score below the pass. A cat's first consult is free, so only the second costs: 3 of 4 count,
    # exactly the 0.75 pass mark, and the room is passed.
    from test_stakes import _approach, _correct, _sit

    run = new_run(seed=7, cols=100, rows=30, pet_species="cat")
    _approach(run)
    run.apply(Talk())

    def choose(run):
        if run.active.progress()[0] <= 2:
            run.apply(Consult())
        return _correct(run)

    _sit(run, choose)
    assert run.gates["phishing"].passed
    assert run.gates["phishing"].free_consult_used


# -- snapshot ------------------------------------------------------------------------------------


def test_snapshot_round_trips_the_pet():
    run = new_run(seed=1, cols=100, rows=30, pet_species="dog", pet_name="Rex")
    run.pet.carried = 15
    pos = run.pet.pos
    data = json.loads(json.dumps(to_dict(run)))
    run2 = new_run(seed=1, cols=100, rows=30)          # rebuilt as the default cat
    apply_dict(run2, data)
    assert run2.pet.species == "dog" and run2.pet.name == "Rex"
    assert run2.pet.carried == 15 and run2.pet.pos == pos


def test_snapshot_round_trips_a_soloist():
    run = new_run(seed=1, cols=100, rows=30, pet_species="none")
    data = json.loads(json.dumps(to_dict(run)))
    run2 = new_run(seed=1, cols=100, rows=30)          # rebuilt with a cat, then cleared
    apply_dict(run2, data)
    assert run2.pet is None
