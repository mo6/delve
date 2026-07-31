---
id: who-is-responsible
keeper: wizard
name: Who Signs
pass: 0.75
place: signed-ledger
---

# Who is responsible?

Who Signs holds a contract with every line blank. "Someone always signs," he says. "Find them before the harm does."

"By now you know the machine is not the one to blame. Good. That was the easy half. The hard half is this: once you take the machine off the hook, responsibility does not land neatly on one remaining person. It scatters. Designers who chose the training data. Engineers who tuned the objective. A company that approved the launch. An operator who deployed it in a context nobody tested. A user who trusted an output they should have questioned. All of them touched the outcome. None of them touched all of it."

"You will hear two comforting phrases used to paper over this. 'A human is in the loop.' 'A human is on the loop.' Both are meant to reassure you that a person is watching, ready to catch a mistake before it lands. In practice, in a system moving fast enough, at scale enough, that human is often reviewing so many decisions, so quickly, with so little context, that their presence is closer to a formality than a safeguard. Naming a human in the process is not the same as that human actually being able to stop the harm."

"So how do you individuate responsibility across that many hands, none of them decisive alone? Not by finding the one guilty party; usually there isn't one. By asking what each role actually owed, and how well they met it. A designer owes care in what the system learns from. A deployer owes honesty about where it has and hasn't been tested. An operator owes attention to the warning signs their own role is positioned to see. The quality of someone's responsibility is measured against what their specific role made possible for them to know and do, not against some equal share of blame handed out to everyone in the org chart."

"That is what accountability actually means here, and it is worth being precise about: being answerable. Able to explain what the system did, why, and what your part in that was. Not one person carrying all of it. Many people, each owing an honest answer for their own piece."

> Responsibility scatters across many hands; accountability means each of them can give an honest answer for their own piece, not that one person carries all of it.

## Questions

### Naming a specific person as the human "in the loop" or "on the loop" guarantees that person can actually catch and stop a harmful decision before it happens.

- [ ] True
- [x] False

> In a fast, large-scale system, the named human is often reviewing so many decisions with so little context that their role becomes closer to a formality than a real safeguard. Existing on paper is not the same as being functionally able to intervene.

### According to Who Signs, how should responsibility be assessed across designers, deployers, operators, and users in a distributed AI system?

- [x] By what each specific role owed and could reasonably know or do, not by splitting blame equally
- [ ] By finding the single person who is ultimately guilty
- [ ] By assigning all responsibility to whichever role is easiest to identify
- [ ] Responsibility cannot be assessed at all once more than one party is involved

> Who Signs is explicit that there usually isn't one guilty party and that an equal share for everyone in the org chart misses how differently each role could actually know or act. The right measure is what a given role made possible for that person to know and do.

### A hospital deploys a diagnostic model built by an outside vendor. A doctor relies on its output without checking the case details it flagged as "high confidence, atypical presentation". The outcome is bad. Which best reflects Who Signs' framing of the doctor's responsibility here?

- [x] The doctor's responsibility depends on what their role reasonably required, such as attending to an explicit flag urging closer review, not on whether the vendor's model was flawed
- [ ] The doctor bears no responsibility at all, since the vendor built the model
- [ ] The doctor bears all the responsibility, since they made the final decision
- [ ] Responsibility is irrelevant once a model is involved in a decision

> The flag existed specifically for a clinician's role to attend to, so the doctor's responsibility is measured against that role's reasonable duty, not against an all-or-nothing split between doctor and vendor. Whether the model itself was also flawed is a separate question about the vendor's own role.

### Accountability, as Who Signs uses the term, means being answerable, able to explain what happened and one's own part in it, rather than one person absorbing all the blame.

- [x] True
- [ ] False

> That is exactly the definition Who Signs gives: many people, each owing an honest answer for their own piece, not a single carrier of all responsibility.
