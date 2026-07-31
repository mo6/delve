---
id: bias-in-systems
keeper: gatekeeper
name: The Skew
pass: 0.75
---

# Bias in systems

The Skew tilts a shelf until the books fall one way. "Bias is not always hate," they say. "Often it is history, automated."

"Definition first, because people use this word sloppily." The Skew rights the shelf. "Not
every difference in treatment is discrimination. Charging a sixteen-year-old less for car
insurance than a forty-year-old is a difference of treatment, and it's not what we're
talking about. Discrimination, in the sense that matters here, is a difference of treatment
tied to membership in a group, that disadvantages people for something they didn't choose
and shouldn't be judged on. That's the morally loaded version. Keep the two apart."

"Bias gets into a system three ways, roughly." They count books off the shelf. "One: the
training data itself already encodes a pattern. Feed a hiring model a decade of a company's
actual hiring decisions and it will learn who the company actually hired, warts included.
This is close to what happened at one large retailer's internal recruiting tool: trained on
years of resumes from a workforce that had skewed heavily male, it taught itself that
resumes mentioning women's activities were a negative signal, and had to be scrapped."

"Two: word associations. Models that learn language from huge bodies of ordinary text pick
up the associations *in* that text, including the ones you'd rather they hadn't; certain job
titles cluster near one gender, certain names cluster near assumptions about background. The
model didn't invent the association. It found it, because it was already there."

"Three: proxies. A credit-scoring model might never ask about ethnicity or neighbourhood
directly, and still reproduce the same pattern by leaning on a variable, like postal code,
that correlates with it closely enough to do the same work. Statistical credit scoring has
drawn exactly this objection from regulators for the same reason: the model doesn't need the
forbidden field to reconstruct its effect."

"None of that requires anyone to be malicious." The Skew shelves the last book. "An
algorithm has no opinion of its own to be biased with. It has only what you fed it, and what
you fed it usually includes every unexamined pattern of the world it was trained on. Bias
in, bias out, just with more confidence in the output than the input ever earned."

> An algorithm doesn't need malice to discriminate; it only needs data that already carries the pattern, and nobody who checked.

## Questions

### A large retailer scraps an internal hiring model after discovering it penalised resumes that mentioned women's activities. What is the most accurate explanation for why this happened?

- [x] It was trained on years of the company's own hiring decisions, which had already skewed heavily male
- [ ] A programmer deliberately coded the model to disadvantage women
- [ ] The model malfunctioned due to a software bug unrelated to its training data
- [ ] Resumes mentioning any hobby are automatically penalised by all hiring models

> No deliberate coding and no unrelated bug were involved, and the pattern was specific to
> gendered activities, not hobbies in general. The model learned the pattern already present
> in the company's own past hiring, which is the point: nobody had to intend it for it to
> happen.

### Charging a sixteen-year-old driver a different insurance premium than a forty-year-old driver is an example of discrimination in the morally loaded sense The Skew is describing.

- [ ] True
- [x] False

> The Skew opens by separating ordinary differences of treatment, like age-based insurance
> pricing, from the morally loaded sense of discrimination: disadvantaging someone based on
> group membership for something they didn't choose and shouldn't be judged on. Not every
> different outcome qualifies.

### A credit-scoring model can end up reproducing patterns tied to ethnicity even if ethnicity is never one of its input variables.

- [x] True
- [ ] False

> This is the proxy problem: a variable like postal code can correlate closely enough with
> ethnicity that leaning on it reproduces the same discriminatory pattern the model never
> directly asked about.

### The Skew lists three ways bias tends to enter a system. Which of these matches one of them?

- [x] A model relying on a variable, like postal code, that closely correlates with a protected characteristic it never directly uses
- [ ] A model being trained on too much data overall
- [ ] A model running too slowly for real-time decisions
- [ ] A model being deployed in more than one country

> Data volume, runtime speed, and geographic reach aren't the three routes The Skew names.
> Proxies, like a postal code standing in for ethnicity, are one of the three, alongside
> biased training data and learned word associations.
