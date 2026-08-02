# Comparison: `candidates-claude-code-20260802/` (Claude Code) vs `candidates-cursor-20260802/` (Cursor)

Two independent runs of `candidate-answers-prompt.md` against the same 22 source files. This
document summarizes where they agree, where they disagree, and which findings should be trusted.
It does not modify either candidates set or the source pack content.

## Headline takeaways

1. **One verified factual error in the Claude Code (`candidates-claude-code-20260802/`) run** — `passphrases-en/nl`.
   See below. **Fixed** (2026-08-02): the alignment verdict and its dependent "no change needed"
   refinement were corrected in both files to match the cursor run's (accurate) finding.
2. **A systematic gap in the Claude Code run's reject-list risk analysis.** Across most rooms
   (ai-tools, reporting, devices, password-managers, and others), `candidates-claude-code-20260802/` rates reject-list
   false-positive risk as "Low" without testing negated or compound phrasings. Cursor's run
   consistently constructs a concrete counterexample (e.g. "don't delete the conversation, report
   it" substring-matching the reject phrase "delete the conversation") and catches real risk the
   Claude Code run missed. Treat cursor's reject-list FP findings as the more reliable ones
   pack-wide, not just room-by-room.
3. Everywhere else, the two runs largely converge on the same core answer sets and the same
   headline quality issues, generated independently — which is itself a useful confidence signal
   when both catch the same gap (e.g. `sharing`'s missing "linked formulas", `reporting`'s soft
   near-miss reject gap).

## Per-room comparison

### targeted (en/nl)
Runs agree, no notable divergence. Both call lesson/question alignment strong, both note the same
accept-list vocabulary gap (missing "money"/"payment"/"call" phrasings), both rate reject-list FP
risk low. **Verdict: comparable.**

### links-and-attachments (en/nl)
Agree on accept-list gaps (over-anchored on "expect*" root) and the empty-reject-list design gap.
**Disagreement:** explanation consistency — `candidates-claude-code-20260802/` says "Consistent"; cursor says "Weak,
explanation focuses on filename-as-claim, barely restates the expect-check." This is a real
verdict conflict, not just phrasing difference — worth checking against the source file directly.
Different (additive, non-conflicting) framings of the question-ambiguity risk otherwise.
**Verdict: comparable, but adjudicate the explanation-consistency conflict against source.**

### passphrases (en/nl) — real, verified disagreement
`candidates-claude-code-20260802/` claims lesson/question alignment is "Strong," citing a quote ("a reason, a breach,
a suspicion, a shared secret") as if it were in the visible lesson prose. **That quote is actually
from the post-answer Explanation**, not the "What the player sees" lesson — verified against
`passphrases-en.md`. The visible lesson only covers entropy/length/uniqueness/credential-stuffing
and never states *when* to change a passphrase. Cursor's run correctly identifies this as "Poor"
alignment and proposes real fixes (teach reason-based change in the lesson, or re-aim the question).
**Verdict: cursor was correct here; `candidates-claude-code-20260802/`'s alignment rating and "no change needed"
refinement have been corrected to match (2026-08-02).**

### password-managers (en/nl)
Both converge on the central problem: accept-list facts (cross-browser, non-website coverage,
passphrase-vs-session) only appear in the post-answer explanation, never the pre-question lesson.
**Disagreement:** `candidates-claude-code-20260802/` flags "nothing" as a substring-risky reject entry (with a concrete
counterexample); cursor calls it safe, "Low" FP risk — unresolved conflict on the same entry.
Non-overlapping accept-list gap proposals on both sides (complementary, not contradictory).
**Verdict: comparable; `candidates-claude-code-20260802/`'s reject-risk claim here is the better-substantiated one
(exception to the general pattern above), cursor's accept-list gap list is broader.**

### mfa (en/nl)
Strong overlap — both call this one of the pack's best-aligned rooms, both catch the same
cross-room-confusion wrong answers (passkeys, deny-push, "verify via second channel"). Cursor
proposes concrete accept-list additions; `candidates-claude-code-20260802/` reaches similar ground but concludes "no
changes," a threshold difference rather than a factual one. One-sided: `candidates-claude-code-20260802/`'s nl file
flags a real reject-list locale-parity gap (nl has 3 entries vs en's 4) that cursor's nl run
doesn't mention. **Verdict: comparable; cursor slightly more actionable on en, `candidates-claude-code-20260802/`
slightly more actionable on nl (parity finding).**

### classification (en/nl)
Both independently catch the same core tension: the lesson's closing line ("what could someone do
with this?") teaches a self-assessment path that competes with the accept-list's "ask someone,"
and both flag the same reject-list substring risk. One-sided: cursor also flags "default to
confidential" as a missing reject entry (a different over-classification phrasing) that
`candidates-claude-code-20260802/` doesn't raise. **Verdict: comparable; core finding agrees, cursor adds one extra gap.**

### sharing (en/nl)
Both runs *independently* flag the same headline gap: "linked formulas" is praised in the
explanation but absent from the accept list — strong convergent signal. Disagreement: `candidates-claude-code-20260802/`
rates a "formatting" reject-substring collision as moderate risk with a specific case; cursor
rates it low and doesn't flag that case. Cursor proposes two extra accept candidates
(`candidates-claude-code-20260802/` doesn't); `candidates-claude-code-20260802/` proposes narrowing the "formatting" reject entry (cursor
doesn't). **Verdict: comparable — same headline finding either way; `candidates-claude-code-20260802/` has more detail
on this particular reject-list risk (another exception to the general pattern).**

### devices (en/nl) — complementary, not comparable
Real disagreement, each side catching something real the other missed:
- Cursor: lesson only teaches "don't plug it in," never "hand it to security" (which only appears
  in explanation/reject list) — alignment is "Partial," not "Strong" as `candidates-claude-code-20260802/` rated it.
- `candidates-claude-code-20260802/`: concrete reject-substring collision — "check the filenames" would false-reject
  "don't check the filenames — hand it to security." Cursor missed this specific case entirely.
**Verdict: read both — genuinely complementary, neither run is strictly better here.**

### social-engineering (en/nl)
Both converge on the core theme (password ask is the disqualifying tell) and both independently
flag "verify through a second channel / hang up and call IT" as a near-miss wrong answer with
near-identical reasoning. **Disagreement is in the recommendation, not the analysis:** cursor
concludes this is risky enough to add "second channel"/"hang up and call"/"caller ID" to the
reject list; `candidates-claude-code-20260802/` reaches the same analysis but explicitly declines to change anything.
**Verdict: cursor more actionable — turns a shared observation into a concrete list-edit
recommendation `candidates-claude-code-20260802/` declined to make.**

### ai-tools (en/nl)
Heavy overlap on accept/reject answer sets. Cursor catches a concrete reject-list false positive
`candidates-claude-code-20260802/` missed: "don't delete the conversation, report it" substring-matches the reject
phrase "delete the conversation." Cursor also flags a wording ambiguity `candidates-claude-code-20260802/` didn't:
"hand it to security" is ambiguous between the USB-physical sense (reject, from `devices`) and the
report-to-security sense (accept, correct here). **Verdict: cursor more actionable — caught a real
FP and an ambiguity `candidates-claude-code-20260802/` missed.**

### reporting (en/nl)
Strong independent double-catch: both runs, working separately, identified that the reject list
only catches blunt refusals ("do nothing," "wait and see") but misses softer near-miss phrasings
the lesson specifically warns against — high-confidence signal since neither run saw the other's
work. Disagreements: (1) `candidates-claude-code-20260802/` again missed a reject-substring FP cursor caught ("don't
ask them first, report it" vs. reject phrase "ask them first"); (2) cursor surfaced a distinct
wrong-answer type `candidates-claude-code-20260802/` didn't include: "investigate whether it's really malicious first"
as a diligence-sounding delay tactic, not currently on the reject list. **Verdict: comparable on
the core finding (mutually reinforcing); cursor edges ahead on two additional catches.**

## Recommendation

- ~~Correct or drop the `passphrases-en/nl` alignment claim in `candidates-claude-code-20260802/`~~ — done.
- When reconciling into actual pack changes, prefer cursor's reject-list false-positive analysis
  as the default read, and treat `candidates-claude-code-20260802/`'s "Low risk" verdicts on reject lists as
  under-tested unless it gives a specific counterexample (it does for password-managers and
  sharing, which held up).
- `devices` is the one room where both sets of findings should be kept — they don't overlap.
- Everything else: substantial independent agreement on both answer sets and headline quality
  issues, which is a reasonably strong signal those findings are real rather than an artifact of
  one run's biases.
