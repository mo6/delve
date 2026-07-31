---
id: DELVE-0037
title: Recompress issue screenshot assets so resizing always shrinks them
status: implemented
area: [tools, docs]
type: bug
epic:
milestone:
version: 1.11.3
version_span:
created: 2026-07-26
updated: 2026-07-26
commits: [b85fdea]
related: [DELVE-0034, DELVE-0036]
supersedes: []
docs: []
changelog:
reason:
---

# Recompress issue screenshot assets so resizing always shrinks them

## Summary

DELVE-0036 resized the five DELVE-0035 screenshots to 800px wide with `sips --resampleWidth 800`,
but PNG recompression is not guaranteed to shrink a file just because it has fewer pixels:
`DELVE-0035-stats-overview-heatmap.png` actually **grew**, 775438 to 810446 bytes, because sips
re-encodes the PNG at whatever compression it defaults to, which was worse than the original
screenshot tool's encoding for that particular image (a dark background with a fine dotted grid,
the least PNG-friendly of the five). A resize step that can silently grow a file defeats its own
purpose. This switches the five assets (and the documented convention) from PNG to JPEG at a fixed
quality setting, which gives an actual size/quality dial instead of leaving it to PNG's opaque
recompression.

## Motivation / problem

These are screenshots (gradients, anti-aliased UI chrome, soft shadows), not the flat-colour line
art PNG compresses best. `sips` has no PNG quality knob at all, only a JPEG `formatOptions` value
(0-100, or `low`/`normal`/`high`/`best`), so PNG resizing is a black box that happened to lose on
one of five images. JPEG, at a chosen quality, both shrinks these specific screenshots by roughly
5-6x over their already-resized PNG (spot-checked at quality 85: 810KB to 130KB, 618KB to 93KB,
573KB to 121KB, 495KB to 104KB, 145KB to 73KB) and gives a documented, adjustable quality/size
trade-off for the next screenshot someone attaches, rather than "resize and hope."

## MUST

- The five `issues/assets/DELVE-0035-*.png` files MUST be replaced with `.jpg` equivalents at
  quality 85 (spot-checked: text and UI chrome stay legible at this setting; this is the working
  quality/size point, not a hard requirement to re-derive per image).
- Every `assets/DELVE-0035-*.png` reference in `issues/archive/DELVE-0035-information-screen.md`
  MUST be updated to the corresponding `.jpg` filename.
- `issues/README.md`'s asset convention paragraph MUST recommend JPEG for a screenshot (over PNG),
  name the quality knob (`sips -s format jpeg -s formatOptions 85 file.png --out file.jpg`), and
  say why: PNG has no quality dial and can recompress a photograph-like screenshot larger, not
  smaller, after a resize.
- `tools/issues.py --check`'s existing width check already reads both PNG and JPEG headers
  (DELVE-0036); it MUST NOT need any further change for this issue, since the resulting `.jpg`
  files are already under the 800px cap.

## Non-goals

- No general recompression/optimisation pipeline (pngquant, optipng, etc.); none of those tools
  are installed on the reference macOS environment, and adding one is a heavier dependency than
  this warrants. `sips`, already relied on by DELVE-0036, is enough once JPEG is the target format.
- No blanket ban on PNG for issue assets; flat-colour diagrams (a hand-drawn ASCII mockup exported
  as an image, say) may still compress better as PNG. This issue only changes the *recommendation*
  and fixes the five images that are actual screen photographs.
- No quality value other than 85 is being explored; if a future asset looks poor at 85, that is a
  case-by-case call when it happens, not a reason to reopen this issue.

## Design notes / links

Builds directly on DELVE-0034 (the assets/ convention) and DELVE-0036 (the 800px width cap and
its stdlib PNG/JPEG header reader in `tools/issues.py`); this issue changes neither the naming
convention nor the lint code, only the recommended format and the five already-committed files.

## Acceptance / verification

- `git show <before>:issues/assets/DELVE-0035-stats-overview-heatmap.png | wc -c` compared against
  the new `.jpg`'s size confirms the specific regression (a file that grew) is fixed.
- `tools/issues.py --check` stays clean with the renamed `.jpg` files and updated references.
- Visual spot-check of all five `.jpg` files (read them back) for legible text/UI chrome at
  quality 85.
- `./run-tests.sh` passes.
