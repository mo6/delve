---
id: why-transparency
keeper: wizard
name: Glass
pass: 0.75
---

# Why transparency

Glass taps the pane. "If you cannot see what it does," she says, "you cannot decide whether to trust it."

She walks you around a box the size of a wardrobe, humming faintly, wires running to
somewhere you can't follow. "This one denies loan applications. Somewhere inside is the
reason it denied yours. You are entitled to know it, and not because the law says so first;
the law says so because you are."

Transparency is the demand that the reasoning behind a decision be available to the people
that decision falls on, in a form they can actually use. Not available in principle, buried
in a filing cabinet nobody visits; available to the person standing in the corridor asking
why.

Three things ride on it. **Accountability**: someone has to answer for a decision, and you
cannot hold a black box responsible for anything, only the people who built and deployed it,
and only if the workings are visible enough to trace a fault back to a cause. **Trust**: you
don't have to trust a system you don't understand, but you shouldn't, and pretending
otherwise is how people get hurt by things they had no reason to expect. **Contestation**:
the whole point of knowing why is that you might disagree, and be right. A denial you can't
inspect is a denial you can't appeal.

"Now," Glass says, tapping the glass again, "here's where it gets difficult. Some of what's
inside this box, even I struggle to read. A modern model weighs millions of numbers against
each other in ways nobody designed by hand; it learned the pattern, and the pattern doesn't
come with a caption."

That's the honest problem. Complex machine learning is opaque even to its own engineers, not
because anyone is hiding anything, but because "why" doesn't live in any single line of code
you could point to.

"And don't let anyone tell you the fix is just publishing the source." She says this like
it's an old argument she's tired of winning. "Hand an ordinary person the code for a neural
network and you have handed them nothing. Transparency that only a specialist can read is
transparency for specialists, not for the person who got turned down for the loan."

> Transparency means the reason is available to the person it affects, in a form they can use, not just available in principle.

## Questions

### According to Glass, what is the strongest test of whether a system is transparent?

- [ ] Whether its source code has been published
- [x] Whether the person affected by its decision can get a reason they can actually use
- [ ] Whether a regulator has reviewed and approved it
- [ ] Whether its accuracy score is publicly reported

> Publishing source code and passing regulatory review are both real things that can happen
> to an opaque system; neither one puts a usable reason in front of the person it affected.
> An accuracy score tells you how often the system is right, never why it decided this case.

### Publishing a model's source code is enough to make it transparent to the people it affects.

- [ ] True
- [x] False

> Code is transparent to someone who can read code. The applicant turned down for a loan
> almost never can, so handing them the source hands them nothing they can use. Transparency
> is measured by what the affected person can understand, not by what exists somewhere.

### Why is transparency hard to fully deliver for complex machine learning models, even when nobody is hiding anything?

- [ ] Companies deliberately obscure the code to protect trade secrets
- [x] A model's "why" is distributed across millions of learned weights with no single line that explains it
- [ ] Regulations prevent companies from disclosing how models work
- [ ] Machine learning models run too fast for a human to observe in real time

> Deliberate obscuring and legal restriction both happen sometimes, but Glass's point is
> about honest difficulty: a modern model's reasoning isn't hidden in a drawer, it's spread
> across weights nobody assigned by hand, so there's no single sentence to hand over even
> if everyone involved wants to.

### A system that never explains its decisions can still be trusted, as long as it is usually right.

- [ ] True
- [x] False

> "Usually right" is a comfort to the majority and no comfort at all to the person in the
> minority who was wronged and has no way to see why, let alone contest it. Trust and
> contestation are both about the cases the accuracy score doesn't cover.
