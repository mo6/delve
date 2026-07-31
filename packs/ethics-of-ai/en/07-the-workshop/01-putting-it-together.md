---
id: putting-it-together
keeper: wizard
name: Praxis
pass: 0.75
---

# Putting it together

Praxis clears a bench. "Name a system," they say. "We will walk it through every door you have already opened."

They don't wait long for an example, they already have one ready. "A city council wants
software that flags which families are statistically likely to need a child-welfare
intervention soon, so caseworkers know where to visit first. Reasonable goal. Overworked
caseworkers, finite hours, real children at risk if nobody gets there in time. Now: walk it
through the rooms behind you, one at a time, and tell me if it survives."

"**Benefiting people, and avoiding harm**, first." Praxis holds up one finger. "Does it
actually help, and does it avoid harm in the process? A flag that gets a caseworker to a
family sooner helps. A flag that a caseworker treats as a verdict rather than a lead, that
turns a statistical hint into a removal decision, causes exactly the harm the tool claimed to
prevent. The same system passes or fails this test depending entirely on how it's used, not
on its accuracy score."

"**Rights**, second." A second finger. "Whose autonomy is at stake? The family's, obviously,
who never consented to being scored, and didn't choose the data trail that produced their
score: past contact with services, a neighbourhood's baseline rate. A rights-respecting
version of this tool tells a family it exists, and gives them a way to contest a flag they
believe is wrong."

"**Transparency**, third." Praxis is counting now. "Can the caseworker who acts on the flag
actually see why it fired? If the answer is 'the model said so' with nothing underneath, the
caseworker isn't making a decision, they're rubber-stamping one they can't inspect, which
puts all the accountability on a person who had none of the actual information."

"**Fairness**, fourth, and here's where it usually breaks." They tap the bench. "Train this
on historic caseworker visits and you train it on historic bias in who got visited: families
already over-policed get flagged more, which sends more visits their way, which generates
more data confirming the pattern. The system doesn't discover risk. It can manufacture the
appearance of it."

"Say all four survive, on paper." Praxis leans back. "Here's the part everyone skips: a
guideline that says 'be fair, be transparent' changes nothing on its own, because a developer
under deadline needs a procedure, not a poster. Which specific metric gets measured, by whom,
before launch, on what cadence after. Skip that step and you haven't done ethics, you've
decorated the project with its vocabulary. That's the whole difference between a principle
and a practice."

> A system can satisfy every principle in the abstract and still cause harm, because the harm lives in how it gets implemented and checked, not in the poster on the wall.

## Questions

### In Praxis's child-welfare scenario, what turns the flagging tool from a helpful lead into a source of harm?

- [x] A caseworker treating the flag as a verdict rather than one input to their own judgement
- [ ] The tool being built by a city council rather than a private company
- [ ] The tool running on cloud infrastructure instead of local servers
- [ ] The tool having a name that sounds clinical

> Who built it, where it runs, and what it's called don't determine whether it helps or
> harms. Praxis's point is that the exact same tool passes or fails depending on whether a
> caseworker treats its output as a lead to investigate or a verdict already reached.

### Training a risk-flagging tool on historic caseworker visit data guarantees the tool measures actual risk, since it's based on real past cases.

- [ ] True
- [x] False

> Historic visits reflect who was actually visited, which already carries any bias in who
> got over-policed in the past. A model trained on that data can reproduce and amplify the
> pattern rather than measuring risk cleanly, exactly the feedback loop Praxis describes.

### A written guideline telling developers to "be fair and transparent" is generally enough, by itself, to change what gets built.

- [ ] True
- [x] False

> Praxis is explicit that this is the step everyone skips: a general guideline gives a
> developer under deadline nothing concrete to act on. It takes a specific metric, a named
> owner, and a schedule before a principle actually changes a decision.

### What does Praxis say is the actual difference between a principle and a practice, in this context?

- [x] A practice specifies a concrete procedure, who measures what, by what metric, on what schedule, while a principle stays a general statement
- [ ] A practice is written by lawyers and a principle is written by engineers
- [ ] A principle applies to hiring tools and a practice applies to welfare tools
- [ ] There is no real difference; the words are interchangeable

> Praxis never draws the line by profession or by which tool it's applied to; both words
> apply to any system. The distinction is specificity: a practice names who checks what,
> measured how, on what cadence, while a principle stops at the sentiment.
