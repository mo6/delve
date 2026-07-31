---
id: privacy
keeper: gatekeeper
name: The Veil
pass: 0.75
---

# Privacy

The Veil draws a curtain across a mirror. "What it knows about you," they say, "is already a kind of power."

"People think privacy is about which fields are in the form," The Veil says. "Name, address,
income. Fill them in carefully and you're covered. You're not."

Privacy matters because it protects **autonomy**: your capacity to make your own decisions
without someone else quietly steering them using information you didn't know you'd given
away.

"Here's the harder problem." The Veil pulls the curtain back an inch. "You gave a store your
purchase history, nothing else. From purchase history alone, a decent model can infer you're
pregnant before you've told your family. Nobody asked for that field. Nobody needed to; it
was *derived*. The inference is the private fact, not the receipts it came from."

This is why "it's my data, I decide" gets slippery fast. Ownership language assumes the thing
being protected is a fixed set of facts you control. But an inference isn't a fact you gave
away, it's a conclusion someone else drew, and you can't consent to a conclusion you didn't
know was possible. Some argue for a right to *reasonable inferences*: not just control over
the raw fields, but some say over what may be concluded from them.

"Consent has a ceiling, too," The Veil adds. "You tick a box once, at the start, for a purpose
you understood at the time. A model trained later, on that same data, for a purpose nobody
described to you, is not covered by that tick. Consent for *this* is not consent for
*whatever we think of next*."

"And don't trust the word 'anonymised.'" They almost smile. "Strip the name and the address
and what's left can often still be traced back to one person, because the pattern of the
remaining data is distinctive enough on its own. Anonymisation is a claim to be tested, not a
guarantee to be believed."

> Privacy isn't only about the facts you hand over; it's about what someone else can conclude from them, and whether you ever agreed to that.

## Questions

### A retailer never asks customers about pregnancy, but its purchase-pattern model can flag likely pregnancy months before a customer tells anyone. What does The Veil say is the actual private fact at stake here?

- [x] The inference the model drew, not merely the raw purchase records it was built from
- [ ] The store's internal sales targets for the quarter
- [ ] The customer's name, which the model never touched
- [ ] The price of the products purchased

> No name was ever needed and no sales target is at stake. The Veil's point is precisely
> that the raw purchase data looks harmless on its own; the private fact is the *conclusion*
> drawn from it, which the customer never disclosed and never agreed to have inferred.

### If you consented to a company using your data when you signed up, that consent also covers new uses the company invents for that same data later.

- [ ] True
- [x] False

> Consent is tied to the purpose you understood at the time you gave it. A later, different
> use of the same data, one nobody described to you when you agreed, isn't automatically
> covered just because the data itself hasn't changed.

### Data that has had names and addresses removed is, as a rule, safely anonymous and cannot be traced back to a specific person.

- [ ] True
- [x] False

> Removing obvious identifiers feels like enough, which is exactly why the belief persists.
> But the remaining combination of details, purchases, timestamps, rough location, is often
> distinctive enough to re-identify one person. "Anonymised" is a claim to test, not a fact
> guaranteed by removing a name field.

### Why does "it's my data, I decide" become a difficult standard for privacy once inference is involved?

- [x] You can't meaningfully consent to a conclusion drawn from your data if you never knew that conclusion was possible
- [ ] Because data ownership laws differ between countries
- [ ] Because most people don't read privacy policies
- [ ] Because companies always own the servers the data is stored on

> The difficulty isn't legal variation or unread policies, it's structural: ownership
> language assumes you're protecting a fixed set of facts, but an inference is a conclusion
> someone else drew, one you couldn't have consented to in advance because you didn't know
> it was on the table.
