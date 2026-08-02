# Prompt: generate candidate answers for a free-text question

## How to run this

This file is self-contained: it names its own inputs and output location. To run the whole batch,
say to Claude Code or Cursor:

> Process `docs/research/free-text/security-onboarding/candidate-answers-prompt.md` and follow its
> instructions.

That single line is enough; nothing else needs to be attached. The agent is expected to locate the
22 input files itself (see below), not wait for them to be pasted in. Every file path in this
document, including this one, is relative to the project's root directory: run this from the
project root, not from inside `docs/` or any other subdirectory.

---

## Input files (process every one)

All 22 live in `docs/research/free-text/security-onboarding/` (this file's own directory), named
`<room-id>-<locale>.md`. List that directory to find them rather than trusting this checklist alone
if the two ever drift. Process every one; do not stop after the first few or silently skip any. If
a genuine limit (context length, tool budget) makes finishing all 22 in one pass impossible, say so
explicitly and list exactly which ones were not processed, rather than ending quietly partway
through.

- [ ] `targeted-en.md`
- [ ] `targeted-nl.md`
- [ ] `links-and-attachments-en.md`
- [ ] `links-and-attachments-nl.md`
- [ ] `passphrases-en.md`
- [ ] `passphrases-nl.md`
- [ ] `password-managers-en.md`
- [ ] `password-managers-nl.md`
- [ ] `mfa-en.md`
- [ ] `mfa-nl.md`
- [ ] `classification-en.md`
- [ ] `classification-nl.md`
- [ ] `sharing-en.md`
- [ ] `sharing-nl.md`
- [ ] `devices-en.md`
- [ ] `devices-nl.md`
- [ ] `social-engineering-en.md`
- [ ] `social-engineering-nl.md`
- [ ] `ai-tools-en.md`
- [ ] `ai-tools-nl.md`
- [ ] `reporting-en.md`
- [ ] `reporting-nl.md`

(`phishing` has no free-text question and is intentionally absent, DELVE-0096's M2 golden-slice
exception; do not create a file for it. Don't process this prompt file, or any `-candidates.md`
output file from a previous run, as if it were an input.)

## Instructions

You are helping validate free-text training questions from a security-awareness game called Delve.
Each input file above is one room's research file: the keeper's lesson (the prose a player reads
before answering), the question itself, the current accept/reject reference lists, the explanation
shown after answering, and the exact grading prompt sent to an LLM grader.

For **each** input file, independently, do four things:

### 1. Generate 5-10 plausible **correct** answers

Answers a real learner might type that mean the same thing as the reference answers, but are not
copies of them. Vary the phrasing on purpose:

- one-word or two-word answers, and full-sentence answers
- a direct paraphrase of the canonical (first) accept-list entry
- an answer that uses none of the accept list's exact words but is clearly correct in meaning
- an answer that only partially restates the reasoning from the lesson/explanation, if that partial
  restatement should still count as correct
- a plausible answer in the *other* register than the accept list uses (formal vs. casual, or a
  synonym a non-native speaker might reach for)

For each, say **why** it should be judged correct, referencing the lesson or explanation.

### 2. Generate 5-10 plausible **wrong** answers

Answers a real learner might type that are wrong, but for genuinely different reasons, not just
copies of the reject list:

- a common misconception the lesson explicitly warns against
- an answer that sounds related but misses the actual point of the question
- a plausible-sounding guess from someone who skipped the lesson prose
- an answer that would have been correct for a *different* question in this pack (tests whether the
  grader is actually reading this question, not pattern-matching a nearby concept)
- an off-topic or nonsensical answer (tests the floor, not the ambiguity)

For each, say **why** it should be judged wrong, and flag any of these that you think a lenient
grader (human or LLM) might mistakenly accept.

### 3. Evaluate the question and lesson for quality

Answer explicitly, in your own words:

- Does the lesson prose actually support one clear, defensible correct answer, or could a learner
  who read carefully still reasonably answer differently than the accept list expects?
- Is the question's wording unambiguous? Could it be read more than one way?
- Does the accept list cover the realistic range of correct phrasings, or is it too narrow (would
  reject a clearly-correct answer under the offline keyword floor, which only does substring
  matching, not meaning)?
- Does the reject list risk catching a legitimate correct answer that happens to contain one of its
  phrases as a substring?
- Is the explanation consistent with the accept list, or does it hint at a slightly different
  "correct" idea than what the accept list encodes?

### 4. Suggest refinements

If you found any ambiguity or gaps in steps 1-3, propose concrete fixes:

- rewording the question prompt
- additions to the accept or reject list (still written as short reference phrases, not full
  sentences, per this pack's authoring convention)
- a change to the lesson prose, if the ambiguity is really that the lesson never actually taught
  the thing the question asks
- if you found nothing worth changing, say so explicitly rather than inventing a change

## Output

Write results into a new subdirectory, `docs/research/free-text/security-onboarding/candidates/`
(create it if it doesn't exist yet; do not put output files alongside the inputs).

For **each** input file processed, create **one new Markdown file** in that subdirectory, named
`<room-id>-<locale>-candidates.md` (matching that input file's `<room-id>-<locale>` prefix, e.g.
`targeted-en-candidates.md` for `targeted-en.md`). In batch mode this means 22 new files, one per
input file above. Use this structure for every one of them:

```markdown
# <room title> — <locale> candidate answers

Source: `docs/research/free-text/security-onboarding/<room-id>-<locale>.md`

## Candidate correct answers

1. **"<answer text>"** — why this should ACCEPT: ...
2. ...

## Candidate wrong answers

1. **"<answer text>"** — why this should REJECT: ...
2. ...

## Quality assessment

- Question clarity: ...
- Lesson/question alignment: ...
- Accept-list coverage: ...
- Reject-list false-positive risk: ...
- Explanation consistency: ...

## Suggested refinements

- ... (or: "No changes suggested; the question and lesson support one clear answer.")
```

The `Source:` line is a project-root-relative path (this instruction assumes it is being run from
the project's root directory, and every path in it, including this one, is relative to that root),
not a path relative to the candidates file's own location.

Do not modify the pack content itself (`packs/security-onboarding/...`) or any source research
file; only write the new `-candidates.md` files into `candidates/`. These are research artifacts
for a human to review, not an automated content change.

When running in batch mode, finish with a short summary listing every input file processed and the
name of the candidates file it produced (the checklist above, checked off), so it's easy to confirm
nothing was missed.
