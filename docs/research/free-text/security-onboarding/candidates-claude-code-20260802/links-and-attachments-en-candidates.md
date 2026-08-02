# Links, Attachments, and the Space Between — en candidate answers

Source: `docs/research/free-text/security-onboarding/links-and-attachments-en.md`

## Candidate correct answers

1. **"Am I expecting this?"** — why this should ACCEPT: near-identical paraphrase of the canonical accept entry "was I expecting this," differing only in tense; the room's own italicized punchline is "Was I expecting this?"
2. **"Did I see this coming?"** — why this should ACCEPT: idiomatic casual-register synonym conveying the same meaning as "was this expected," uses none of the accept list's exact words.
3. **"Did I know this was coming?"** — why this should ACCEPT: full-sentence paraphrase using no "expect"-root words at all, still means "was I expecting this."
4. **"Was this on my radar?"** — why this should ACCEPT: idiomatic English phrase in a more casual register, equivalent in meaning to "was this expected."
5. **"Expecting it?"** — why this should ACCEPT: two-word terse answer, a direct trim of accept entry "expecting this."
6. **"Anticipated?"** — why this should ACCEPT: one-word formal synonym for "expected," matching accept entry "was this expected."
7. **"Ask yourself if you were expecting this attachment before opening it"** — why this should ACCEPT: full-sentence restatement that still correctly names the diagnostic question, grounded in the lesson's "Expected: open it. Unexpected: ask."

## Candidate wrong answers

1. **"Is the file extension correct?"** — why this should REJECT: a misconception the lesson explicitly warns against — "the distinction isn't yours to make from the filename" and "A file called invoice.pdf may not be a PDF." Checking the extension is precisely the wrong approach the Postmaster is correcting.
2. **"Does this look like a virus?"** — why this should REJECT: a plausible-sounding folk-security guess from someone who skipped the lesson prose, but the lesson explicitly rejects this framing: "Not is this attachment safe... You cannot know that, and neither can I."
3. **"Is the sender's email address legitimate?"** — why this should REJECT: sounds related — the lesson's link half discusses sender-controlled deception — but misses the actual point of the attachment question, which is about expectedness, not sender verification. Flag: because both halves of this lesson share vocabulary about "the sender," a lenient grader might conflate them and accept this.
4. **"Nope, wasn't expecting that"** — why this should REJECT: this answers the diagnostic question rather than naming it; the room asks "what's the ONE QUESTION," not a yes/no verdict on a specific case. Flag: this is a strong lenient-grader risk, since it shares heavy keyword overlap ("expecting") with the accept list despite not actually stating the question.
5. **"The last two labels before the first single slash"** — why this should REJECT: this is the correct answer to the *link*-domain half of this same lesson, not the attachment question — tests cross-topic confusion within a single room.
6. **"Check if it has macros enabled"** — why this should REJECT: a plausible-sounding technical guess unsupported by the lesson's actual answer; the lesson's answer is behavioral (expectation-based), not a technical inspection step.
7. **"Whatever, just open it"** — why this should REJECT: off-topic/dismissive non-answer, tests the floor rather than any genuine ambiguity.

## Quality assessment

- Question clarity: Mostly clear, but there's a real misreading risk: a learner could interpret the prompt as asking them to render a verdict on a specific attachment ("was I expecting this one? No.") rather than to name the general diagnostic question to ask. Wrong-answer candidate 4 above illustrates the failure mode. Tightening to something like "what question should you always ask yourself" would remove the ambiguity.
- Lesson/question alignment: Strong — the lesson builds directly to the italicized line "Was I expecting this?" as its stated answer, and the question maps cleanly onto it.
- Accept-list coverage: Decent range of pronoun/tense variants (I/you, past/present), but no entry avoids the word "expect" entirely. Idiomatic phrasings without that root — "did I see this coming," "was this on my radar," "anticipated" — would fail the offline keyword floor despite being correct in meaning.
- Reject-list false-positive risk: Not directly applicable — the reject list is empty for this question. Worth flagging as a design gap rather than a false-positive risk: with no reject anchors, the offline keyword floor has nothing to reject against, so all discrimination against wrong answers falls on the LLM grader alone.
- Explanation consistency: Consistent — the explanation reinforces "the part the sender writes is a claim, not a fact," matching the "was I expecting this" framing independent of filename, and explicitly extends the same principle already taught for links.

## Suggested refinements

- Add a small reject list naming the exact misconceptions the lesson pushes back on, e.g., "check the file extension," "scan it first," "look at the sender's address" — these are the specific wrong approaches the Postmaster corrects, and right now nothing anchors the offline floor against them.
- Add accept-list entries that don't contain the word "expect," e.g., "did I see this coming," "was this anticipated," to widen keyword-floor coverage for idiomatic or non-native phrasings.
- Consider tightening the question wording to make explicit that the answer should be the question itself (not a case-specific yes/no judgment), to preempt the "nope, wasn't expecting that" failure mode identified in wrong-answer candidate 4.
