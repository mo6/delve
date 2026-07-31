# Free-text rubrics (PoC fixture)

These are the worked examples from [docs/PHASE2.md](../../docs/PHASE2.md) §9, in the proposed
Delve free-text format: an H3 prompt, a `- ?answer:` accept set, an optional `- ?reject:` set, and
the `>` explanation shown after answering. `grade.py` parses this exact shape, so it doubles as a
check that the format is answerable to real pack content.

The accept set feeds *both* the LLM prompt (as the rubric) and the keyword fallback (as match
targets), so the two grading paths agree on what "right" means.

### A message you didn't expect makes you feel you must act right now. In a word or two, what is that feeling, and why is it the attacker's main tool?

- ?answer: urgency, time pressure, being rushed, panic, a sense of hurry
- ?reject: fear of getting fired, curiosity, greed

> Urgency is the lever, because thinking is what kills the attack. The mail wants you moving
> before you check the one thing that would give it away. Manufactured time pressure, plus a
> reason not to verify, is the signature; everything else is set dressing.

### A mail comes from a colleague's real, correct address, asking you to open an attachment. Nothing about the address is wrong. In one sentence, why is that not enough to trust it?

- ?answer: the account could be compromised, account takeover, their account was hacked, a correct address only proves it came from that account not that they sent it
- ?reject: it is always safe, the mail system marks it internal

> A correct sender address proves the mail came from that account, not that your colleague
> sent it. Account takeover is exactly the case where every address check passes, which is why
> "verify the sender" can't be the whole habit.

### The guard's whole scene turns on one question about the coconut. What does he want to know?

- ?answer: where you got it, how you got a tropical coconut to England, the coconut's origin, its supply chain, its provenance
- ?reject: whether the king is brave, whether the quest is holy

> Not "is the king brave", not "is the quest holy": just where the coconut came from. The
> simplest prop has a supply-chain problem, and one honest question about provenance unravels
> the whole conceit.
