---
id: risks-of-openness
keeper: gatekeeper
name: The Closed Book
pass: 0.75
---

# Risks of openness

The Closed Book keeps the door shut. "Openness is not free," they say. "Sometimes it hands a weapon to the wrong hand."

They don't invite you in. They stand in the doorway and make you argue your case.

"Say a bank publishes exactly how its fraud model flags a transaction: which features, which
thresholds, which combination trips the alarm." The Closed Book folds their arms. "Now a
fraudster reads the same document. They don't need to beat the model. They need to stay
under every threshold you just told them about."

That's **gaming**: once a rule is public, anyone can walk right up to its edge and stop. A
spam filter that scores certain words gets beaten by spam that avoids those words and keeps
everything else. The explanation didn't just inform the honest user, it briefed the
adversary.

Worse than gaming is an **adversarial attack**: not staying under a threshold, but exploiting
the exact shape of a model to force a specific wrong answer, sometimes with a change too
small for a human to notice. Detailed explanations of how a model weighs its inputs make
these attacks cheaper to build, because you're no longer guessing at the target.

"Two more." The Closed Book counts on their fingers. "Explanations can leak the very privacy
the system was supposed to protect. Tell someone their loan was denied because 'applicants
from your postal code default at twice the average rate' and you've disclosed something
about everyone in that postal code, whether they consented to that or not. And explanations
can leak intellectual property: describe a model precisely enough to justify its decision,
and you may have described it precisely enough to rebuild."

So the demand for openness is not free to grant. It trades against security, against
privacy, against the very reason the model existed as a defence in the first place.

"None of that means shut every door," they add, finally letting you pass. "It means the
right amount of transparency is a design decision, not a maximum you reach for by default.
Full disclosure is a goal for some systems. For others it's a gift to the people you built
the system to stop."

> More openness is not automatically better; it can hand the exact edge you disclosed to the person trying to beat the system.

## Questions

### The more detail a system discloses about how it reaches a decision, the more secure it is.

- [ ] True
- [x] False

> More disclosure can make a system easier to game or attack, since anyone reading the
> explanation learns exactly where the edges are. Security and openness trade against each
> other; more of one is not automatically more of the other.

### A spam filter publicly documents that it scores messages containing the word "free". Spammers start writing "complimentary" instead and get through. What is this an example of?

- [x] Gaming: adversaries adjusting their behaviour to stay just outside a disclosed rule
- [ ] An adversarial attack designed to force a misclassification with an imperceptible change
- [ ] A privacy leak caused by the explanation
- [ ] Intellectual property theft via the explanation

> Nothing imperceptible happened here; the spammers made an obvious, deliberate wording
> change once they knew the rule. That's gaming a disclosed threshold, not the more targeted
> manipulation of an adversarial attack, and no personal data or trade secret was exposed.

### A bank explains a rejection by saying "applicants from your postal code default at twice the average rate." What risk does this specific kind of explanation create, beyond the individual applicant?

- [x] It discloses potentially sensitive statistical information about everyone in that postal code
- [ ] It proves the model is technically inaccurate
- [ ] It guarantees the applicant will win an appeal
- [ ] It makes the model easier to retrain

> The statement says nothing about the model's accuracy and guarantees no appeal outcome.
> What it does is put a group-level claim about an entire neighbourhood into one person's
> denial letter, which is a privacy exposure for everyone in that postal code, not just the
> applicant reading it.

### Full transparency is always the right goal for every AI system, regardless of what the system does.

- [ ] True
- [x] False

> The Closed Book's whole argument is that the right amount of disclosure is a deliberate
> design decision weighed against gaming, attack, privacy and IP risk, not a maximum every
> system should reach for by default. For some systems, full disclosure hands an advantage
> to the exact people the system exists to stop.
