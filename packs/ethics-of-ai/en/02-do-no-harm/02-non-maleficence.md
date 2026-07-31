---
id: non-maleficence
keeper: gatekeeper
name: First Do No Harm
pass: 0.75
place: do-no-harm-plaque
---

# Non-maleficence

First Do No Harm blocks the exit with one arm. "Before you improve the world," they say, "stop cutting it."

"Non-maleficence. The oldest rule in this business, older than computers. Do no harm."

"For a system, that means minimizing risk across every way harm actually shows up. Discrimination: a system that decides worse for some people because of who they are. Privacy: a system that knows more about someone than they agreed to, or leaks it. Physical harm: a device that acts in the world and gets it wrong. Social harm: reputations, opportunities, relationships damaged by an output nobody meant to publish."

"Three sources, and you will see all three again. Design: the harm was built in, in the data, in the objective, in a shortcut nobody flagged. Misuse: someone took a working system and pointed it somewhere it was never meant to go. Inappropriate application: the system itself was fine; the situation it got dropped into was not one it could handle. A model trained on one population, deployed on another. That failure is nobody's malice and still somebody's harm."

"Here is what I will not let you leave with, though. Non-maleficence is necessary. It is not sufficient. A system that harms no one is not yet a good system; it is only not yet a bad one. Doing no harm is the floor you build on, not the building."

"So: name the harm before you name the benefit. If you cannot say what could go wrong, you are not ready to say what could go right."

> Doing no harm is the floor, not the building; necessary, never sufficient on its own.

## Questions

### A well-designed AI system is deployed exactly as intended, but a user deliberately repurposes it to cause harm it was never built for. Which source of harm is this?

- [ ] Design
- [x] Misuse
- [ ] Inappropriate application
- [ ] None of these; deliberate abuse falls outside non-maleficence entirely

> Misuse is a working system deliberately pointed somewhere it was never meant to go. Design harm is baked in from the start; inappropriate application is an unintended context mismatch without malice. Non-maleficence covers all three sources of harm, regardless of who ends up at fault, so the last option is wrong on its face.

### A hospital deploys a diagnostic model trained only on data from one demographic group, then uses it on a much broader population it was never tested against. Even though nobody misused it and no flaw was hidden in the design, this can still cause real harm.

- [x] True
- [ ] False

> This is inappropriate application: the system itself may be sound for the population it was built and tested on, but dropping it into a different context it was never validated for produces real harm without anyone acting maliciously or building in a hidden defect.

### If an AI system has been shown to cause no harm, that alone proves it is an ethically good system.

- [ ] True
- [x] False

> Non-maleficence is necessary but not sufficient. Causing no harm only clears the floor; it says nothing about whether the system does any good, which is a separate duty, beneficence, that has to be asked and answered on its own.

### Which of the following is an example of harm from design, in the threefold breakdown?

- [x] A hiring model trained on historical data that quietly encodes past discrimination into its scoring
- [ ] A chatbot repurposed by a scammer to impersonate a bank
- [ ] A translation tool built for formal documents, used instead on medical instructions where a mistranslation matters more
- [ ] A user sharing a private conversation with a chatbot on social media

> Design harm is baked into how the system was built, here, biased training data shaping the scoring itself. The chatbot scam is misuse; the translation tool dropped into a higher-stakes context it wasn't built for is inappropriate application; the last option isn't a failure of the system at all, it's the user's own choice to share, which makes it a tempting but irrelevant distractor.
