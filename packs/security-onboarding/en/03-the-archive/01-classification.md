---
id: classification
keeper: wizard
name: Marisol the Archivist
pass: 0.75
place: classification-stamp
---

# 📄 Knowing What You're Holding

Marisol has been filing the same box for some time and does not appear to resent it.

"Nobody leaks a document they know is secret," she says. "That's not how any of this
happens. It happens because someone held something valuable and did not *notice*."

Every organisation sorts information into tiers. The names differ; the shape almost
never does:

| Tier | Roughly | If it got out |
|---|---|---|
| **{{tier_public}}** | Already published, or intended to be | Nothing |
| **{{tier_internal}}** | The everyday business of the place | Awkward. Useful to a competitor or an attacker. |
| **{{tier_confidential}}** | Customer data, contracts, finances, personal records | Serious. Legal, financial, and human consequences. |
| **{{tier_restricted}}** | Credentials, keys, security details, unannounced plans | Severe. This is what the dungeon is for. |

"Now, the useful part," Marisol says, "which is not the table."

**Two mistakes, and they aren't symmetrical.**

The first is under-classifying: treating something valuable as ordinary. This is the one
the table is meant to prevent, and it's the one everyone worries about.

The second is over-classifying: marking everything {{tier_restricted}} because it's the safe
choice for you personally. It feels responsible. It is not. When everything is secret,
the label stops carrying information, people route around it to do their jobs, and the
genuinely dangerous document sits in a pile of two thousand identically-marked ones
being ignored at identical speed.

"Over-classification doesn't protect the thing," she says. "It hides it in a crowd of
things that didn't need protecting, and teaches everyone that the marking is noise."

**Aggregation is the trap that catches careful people.** Individually harmless facts can
combine into something that isn't. A name is nothing. A name with a role is nothing much.
A spreadsheet of every name, role, manager, office, and phone number is a map of your
organisation, and it's the first thing Grigor's impersonator would have wanted.

The classification of a collection is not the highest classification in it. It can be
higher than any single row.

"So the question isn't 'what tier is this document,'" Marisol says, finally closing the
box. "It's '**what could someone do with this?**' Answer that honestly and the tier
usually answers itself. Answer it lazily and no table on any wall will save you."

## Questions

### Why is over-classifying information a real problem rather than a harmless excess of caution?

- [ ] It creates administrative overhead in reviewing and declassifying
- [x] It devalues the label, so people route around it and genuinely sensitive material hides in the crowd
- [ ] It prevents legitimate business from happening
- [ ] It's a compliance violation in most frameworks

> A label only works if it's *informative*. Mark everything {{tier_restricted}} and it stops
> meaning "be careful" and starts meaning "ignore me", and the one document that
> mattered is now camouflaged among two thousand that didn't.
>
> The overhead is real but minor. Blocking legitimate work is a *symptom* of the same
> disease, and it's what causes the routing-around. Compliance mostly doesn't care if
> you're too careful.

### A document containing only publicly available information is always {{tier_public}}.

- [ ] True
- [x] False

> This is aggregation, and it's the trap that catches conscientious people rather than
> careless ones. Every individual fact can be public while the *collection* is not.
>
> Names, roles, and office locations are each nothing. Compiled into a single
> spreadsheet, they're a targeting map, precisely the reconnaissance that makes spear
> phishing work. The set can be worth more than the sum of its rows.

### You're about to share a project update containing a customer's name and their contract value. What determines its classification?

- [ ] The document's format; a slide deck is less sensitive than a database export
- [ ] The size of the audience it's going to
- [x] What someone could do with it, which here means it's customer and financial data, so {{tier_confidential}} at least
- [ ] Whether the customer has asked for confidentiality

> "What could someone do with this?" is the question that survives every edge case.
> Named customer plus commercial terms is confidential business information regardless
> of what it's wrapped in.
>
> Format is irrelevant; a slide with a contract value on it is exactly as damaging as a
> database row with the same number. Audience size affects your *handling*, not the
> classification. And the customer's expectations may not even be known to them; the
> obligation is yours either way.

### In a few words, what should you actually do when you're unsure how to classify something, instead of defaulting to the highest label?

- ?answer: ask someone, ask the data owner, handle it carefully and ask, check with whoever owns the data, ask whoever owns it
- ?reject: mark it restricted, use the highest label, default to restricted, classify it as restricted

> This is over-classification wearing the costume of caution, and it moves your
> uncertainty onto everyone downstream.
>
> The actual default when unsure: handle it carefully *and ask someone*. A thirty-second
> question to whoever owns the data resolves it properly. Slapping the highest label on
> it resolves nothing and degrades the system for everyone else.
