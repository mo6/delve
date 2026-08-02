---
id: DELVE-0091
title: Suggest a proper default name for a new companion when no env-var name is set
status: proposed
area: [ui, delve]
type: feature
epic: DELVE-0011
effort: low
milestone:
version:
version_span:
created: 2026-07-31
updated: 2026-07-31
accepted_by:
accepted_at:
commits: []
related: [DELVE-0090]
supersedes: []
docs: [docs/PETS.md]
changelog:
reason:
---

# Suggest a proper default name for a new companion when no env-var name is set

## Summary

When a learner picks a companion and no `$DELVE_CAT_NAME`/`$DELVE_DOG_NAME` (or the Dragon's
equivalent, once DELVE-0090 lands) environment override is set, the name box today starts empty
and only falls back to a generic phrase ("your kitten", "your dog") if submitted blank. Pre-fill it
instead with a proper suggested name the learner can accept as-is or edit, per species and locale:
Felix (EN) / Tippie (NL) for a cat, Rover (EN) / Willem (NL) for a dog, Toothless (EN) / Molotov
(NL) for a Dragon.

## Motivation / problem

`_pick_companion` (`delve/ui/app.py:229`) already pre-fills the name box as an editable value when
an env var is set (`initial=env`); without one, the box is simply blank and the learner has to
think of a name themselves, with the only fallback being an impersonal placeholder phrase if they
give up and submit nothing. A ready, in-character suggestion (already the norm for the learner's
own name via `$DELVE_NAME`/`ui.default_name`) is a small, low-cost improvement: type a name if you
want one, otherwise accept the suggestion, and the box is never just empty.

## MUST / MUST NOT

1. MUST pre-fill the name box with `"Felix"` (English) / `"Tippie"` (Dutch) for a cat, `"Rover"`
   (English) / `"Willem"` (Dutch) for a dog, and `"Toothless"` (English) / `"Molotov"` (Dutch) for a
   Dragon, whenever the matching `$DELVE_*_NAME` environment variable is not set.
2. MUST NOT change behaviour when the matching environment variable *is* set: it still wins and
   pre-fills the box exactly as today, unaffected by this suggestion.
3. MUST NOT change what happens if the learner clears the suggested name entirely and submits a
   blank field: it still falls back to the existing generic epithet (`pet.default_cat`/
   `pet.default_dog`, "your kitten"/"your dog"), unchanged; the new suggestion is a pre-filled
   editable value, not a new blank-submit fallback.
4. MUST NOT change `--pet-name`/an explicitly passed name: no prompt is shown at all in that case,
   same as today.
5. MUST add the new suggested names as their own locale strings (e.g. `pet.suggest_cat`/
   `pet.suggest_dog`/`pet.suggest_dragon`), distinct from the existing `pet.default_*` keys, in
   both `en.toml` and `nl.toml`.

## Non-goals

- Not a random name pool or a name generator; one fixed suggestion per species per locale, exactly
  as specified.
- Not adding a new `$DELVE_DRAGON_NAME` environment variable here; if the Dragon (DELVE-0090) wants
  one, that follows the existing `$DELVE_CAT_NAME`/`$DELVE_DOG_NAME` pattern as part of that
  issue's own scope (or a quick fast-follow), not this one.
- Not changing the existing generic epithet strings (`pet.default_cat`/`pet.default_dog`) or their
  blank-submit role.

## Design notes / links

- `delve/ui/app.py:229` `_pick_companion` and `delve/ui/app.py:114` `_input_box` are the seam:
  today `initial=env or ""`; this changes the fallback side to
  `env or strings("pet.suggest_" + species)` instead of `""`.
- `delve/__main__.py:141` builds `pet_name_defaults` from `$DELVE_CAT_NAME`/`$DELVE_DOG_NAME`
  today; a Dragon entry only makes sense once DELVE-0090's species exists, hence `related:
  [DELVE-0090]` above. The cat/dog half of this issue has no such dependency and can land on its
  own first if that's easier to sequence.
- Follows the same "an env var pre-fills the box as an editable suggestion" idea `_ask_name`
  already uses for the learner's own name (`ui.default_name`/`$DELVE_NAME`), just extended to the
  no-env-var case for a companion.

## Acceptance / verification

- A `ui`-level test (or `_input_box`/`_pick_companion` unit test) asserting the name box is
  pre-filled with "Felix" for a cat and "Rover" for a dog in English, and "Tippie"/"Willem" in
  Dutch, when no matching env var is set.
- A regression test confirming an env var still wins over the new suggestion.
- A regression test confirming a fully cleared, blank-submitted box still falls back to
  `pet.default_cat`/`pet.default_dog`, not the suggested name re-appearing.
- `./run-tests.sh` green, both locales.
