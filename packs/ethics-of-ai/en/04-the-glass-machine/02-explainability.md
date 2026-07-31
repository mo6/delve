---
id: explainability
keeper: shopkeeper
name: The Why
pass: 0.75
place: black-box
---

# Explainability

The Why sells answers by the word. "An explanation is not a dump of weights," they say. "It is something a person can use."

Their stall is stacked with jars, each labelled with a question a customer once asked a
machine. "Transparency," The Why says, sliding one jar aside, "buys you a look inside.
Explainability is what you pay for on top: a look inside translated into something you can
actually spend."

The words get used loosely, so pin them down. **Transparency** is the raw availability of
the workings. **Explainability**, sometimes dressed up as **interpretability**, **XAI**
(explainable AI), or **comprehensibility**, is that availability turned into an account a
particular audience can follow: a loan officer needs a different explanation than a
regulator, who needs a different one again than the applicant.

"Different customers, different change," The Why says, tapping the till. "There is no single
correct explanation, only a sufficient one for whoever's asking."

A common, cheap version: "you were denied because your income was ten thousand below the
threshold; raise it and you'd have been approved." That's a **counterfactual explanation**,
the smallest change that would have flipped the outcome, and it's genuinely useful. It tells
a person what to do next.

"But watch the limit of that," The Why warns, leaning in. "A counterfactual tells you what
would have changed the answer. It does not tell you the model is broken, or biased, or
buggy. When something has gone wrong, not just unwelcome, you need an autopsy, not a
receipt."

There isn't one trick that produces good explanations, there's a shelf of them, each with a
cost. Build a **simpler model** (a decision tree instead of a deep network) and you can read
it directly, at some cost in accuracy. Bolt a **hybrid** explainer onto a complex model: one
system predicts, a second, simpler one approximates why. **Manipulate the input** and watch
what changes in the output, which is how counterfactuals get generated at scale. Or build
for the **person**, not the model: a visualization, a highlighted phrase, an attention map,
something that meets the reader's actual capacity to understand rather than the engineer's.

"And that capacity," The Why adds, ringing up the sale, "is not fixed. Teach people to read
these things and the same explanation does more work. Algorithmic literacy is half of what
you're buying from me."

> The right explanation is not the most detailed one; it's the one the audience in front of you can actually use.

## Questions

### A bank tells a rejected applicant: "You were declined because your reported income was $8,000 below the threshold; income above that level would have been approved." What kind of explanation is this?

- [ ] A full transparency disclosure of the model's source code
- [x] A counterfactual explanation: the smallest change that would have flipped the decision
- [ ] An interpretability audit
- [ ] Proof that the model is free of bias

> No code was disclosed, and no audit was performed, an audit checks the model systematically,
> not a single applicant's case. Nor does telling someone what would have flipped their
> outcome prove anything about whether the reasoning behind it was sound.

### A counterfactual explanation, such as "you'd have been approved with $8,000 more income", is enough on its own to tell you whether the underlying decision was fair.

- [ ] True
- [x] False

> A counterfactual tells you what to change next time, which is useful. It says nothing
> about whether the threshold itself was reasonable, or whether the model reached it through
> biased reasoning. When something's gone wrong rather than just unwelcome, you need a
> deeper look than the smallest-change answer gives you.

### The Why lists several ways to make a model's decisions explainable. Which of these is one of them?

- [x] Building a simpler model that trades some accuracy for being directly readable
- [ ] Increasing the training dataset so the model reaches higher accuracy
- [ ] Publishing the model's accuracy score alongside its decisions
- [ ] Training the model to run faster so it returns decisions instantly

> More data, a published accuracy score, and faster inference can all be true of a model
> and still leave a person with no idea why *their* case came out the way it did. Only a
> simpler, directly readable model actually trades something for legibility.

### Making an explanation easier to understand depends only on how the model works, not on who is reading it.

- [ ] True
- [x] False

> The Why's whole pitch is that the same underlying model can need a different explanation
> for a loan officer, a regulator, and an applicant. The model doesn't change between those
> three; the sufficient explanation does, because the audience's capacity to use it does.
