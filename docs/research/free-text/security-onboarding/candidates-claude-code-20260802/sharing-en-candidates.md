# 📤 Anyone With The Link — en candidate answers

Source: `docs/research/free-text/security-onboarding/sharing-en.md`

## Candidate correct answers

1. **"Hidden tabs in the workbook"** — why this should ACCEPT: a near-direct paraphrase of the canonical accept-list entry ("hidden tabs"); matches both the letter and spirit of the reference.
2. **"Comments"** — why this should ACCEPT: bare one-word answer, exact meaning match with the accept-list entry "comments." Tests whether the grader can handle terse answers, which the lesson explicitly invites ("name one thing").
3. **"There could be an old tab you forgot was even in there"** — why this should ACCEPT: full-sentence, casual-register paraphrase of "hidden tabs / hidden sheets" that uses none of the accept list's exact words ("old tab you forgot" instead of "hidden sheet").
4. **"The edit trail — who changed what and when"** — why this should ACCEPT: paraphrase of "revision history" using a synonym ("edit trail") a non-native speaker might reach for instead of the more formal "revision history."
5. **"Rows that got filtered out but are still technically in the file"** — why this should ACCEPT: partial restatement of the "filtered rows" reasoning straight from the lesson ("Sharing the container, not the thing... ninety files, you have no idea which" — the underlying idea that hidden data persists even when not displayed), phrased as a fuller explanation rather than a keyword.
6. **"Author and company info baked into the file's properties"** — why this should ACCEPT: paraphrase of "metadata," describing the concept (file properties/author info) without using the word "metadata" at all.
7. **"Linked formulas that quietly pull data in from other spreadsheets"** — why this should ACCEPT: the explanation *explicitly* calls this "a genuinely good answer" ("Linked formulas are a genuinely good answer; they can leak structure and break confusingly"). It is not on the accept list, which is a real gap (see Quality assessment below), but per the lesson's own explanation this must be judged correct.
8. **"Tracked-changes markup that's still switched on from the last round of edits"** — why this should ACCEPT: direct paraphrase of the canonical-adjacent accept entry "tracked changes," using fuller phrasing a careful learner might produce.

## Candidate wrong answers

1. **"It might get corrupted when they open it"** — why this should REJECT: a common but unrelated technical worry (file corruption) that has nothing to do with data traveling silently with the file; misses the point of the question entirely.
2. **"The file size could tip them off to how much is in there"** — why this should REJECT: closely shadows the reject-list entry "file size" but arrived at independently — file size is a visible/knowable property, not something that travels *silently and invisibly*, so it fails the question's actual premise.
3. **"It might look weird if they don't have the same fonts"** — why this should REJECT: a plausible-sounding guess from someone who skipped the lesson prose and free-associated to "things that go wrong when sharing files," matching the reject-list spirit of "font issues" but phrased independently.
4. **"They could just forward it to someone else"** — why this should REJECT: sounds on-topic (a real sharing risk) but answers a different question — it's about *who* gets access after sharing, not about hidden content traveling invisibly inside the file itself. This is the kind of near-miss a lenient grader might accept because it's "about sharing risk," even though it doesn't answer what was asked.
5. **"The share might still be live years after the contractor left"** — why this should REJECT: this is a real point from the same lesson ("Forgetting that shares don't expire... It will be live in ten years") but it answers a *different* implicit question (link lifetime) rather than this one (hidden content in the file). Flag: a lenient LLM grader that pattern-matches "risk mentioned in this lesson" rather than reading the specific question could wrongly accept this.
6. **"The recipient's antivirus might flag it as suspicious"** — why this should REJECT: off-topic, invented risk not discussed anywhere in the lesson; a guess with no grounding in the material.
7. **"banana"** — why this should REJECT: nonsensical, tests the floor of the grader rather than any real ambiguity.
8. **"The formatting won't match on their machine"** — why this should REJECT: directly mirrors reject-list "formatting," independently generated; formatting mismatches are cosmetic and visible on open, the opposite of "travels silently."

## Quality assessment

- **Question clarity:** The question is clearly worded ("besides what's visible on screen... one thing that can travel silently") and points a careful reader toward hidden/non-obvious content. Unambiguous.
- **Lesson/question alignment:** Strong. The lesson's "Attaching more than you meant" paragraph (second tab, tracked changes, comments, metadata) maps directly onto the accept list and the question.
- **Accept-list coverage:** There is a real gap. The explanation explicitly praises "linked formulas" as "a genuinely good answer," but "linked formulas" (or any synonym like "external references," "formula links") is absent from the accept list entirely. Under the *offline keyword floor* (substring matching only, not meaning), a learner who correctly answers "linked formulas" would be wrongly rejected, contradicting the room's own explanation text. This is the single clearest quality issue found across this file.
- **Reject-list false-positive risk:** Moderate. "Formatting" as a reject substring could catch an otherwise-correct answer that happens to mention formatting incidentally (e.g., "hidden conditional formatting rules that reveal which rows were flagged" — arguably a legitimate metadata-adjacent answer, but it contains the substring "formatting" and would be auto-rejected outright by the keyword floor regardless of the surrounding correct content).
- **Explanation consistency:** Inconsistent in one specific way — the explanation endorses "linked formulas" as correct, but the accept list doesn't include it. Everything else in the explanation (hidden sheets, filtered rows, tracked changes, comments, revision history) is consistent with the accept list.

## Suggested refinements

- Add "linked formulas" (and a close synonym like "external references" or "linked data") to the accept list — the explanation already treats this as a fully correct answer, so the reference list should match.
- Consider whether "formatting" belongs on the reject list unqualified, given it can appear as a substring inside otherwise-correct metadata-flavored answers; a narrower reject phrase (e.g., "font/formatting looks different") would reduce false-positive risk without weakening the reject list's intent.
- No change needed to the question wording or lesson prose — both are clear and well-aligned with the intended concept.
