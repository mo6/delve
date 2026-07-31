---
id: reducing-discrimination
keeper: wizard
name: Remedy
pass: 0.75
---

# Reducing discrimination

Remedy has a toolbox and no illusions. "You cannot delete bias by wishing," she says. "You can measure, redesign, and refuse."

She lays out her tools like a surgeon, not a salesperson. "First lesson, and it disappoints
people every time: there is no single line of code that removes bias from a model.
Techniques exist, reweighting a dataset, removing a correlated variable, adjusting a
threshold per group, and every one of them helps *something*. None of them is a cure, and
treating one as a cure is how a genuinely harmful system gets to keep running with a clean
conscience attached."

"Here's the trap, and it's a real one, not a hypothetical." She holds up a wrench.
"Sometimes a team fixes the *math*: the dataset gets rebalanced, the metric gets tuned, the
demo looks clean. And the *use* the system was built for is still unjust, say, a hiring tool
that filters out anyone with a career break, which disproportionately means women, however
carefully you've rebalanced the training data underneath it. Fixing the model without asking
whether the deployment itself is the problem is what gets called **ethics-washing**: doing
the technical work that looks responsible, while leaving the actual harm exactly where it
was."

So Remedy's toolbox has three drawers, and none of them is optional. **Measure**: you cannot
fix a disparity you never checked for, and most teams never checked. Run the numbers by group
before you ship, and again after, because a fix can shift the harm sideways instead of
removing it. **Redesign**: sometimes the honest fix isn't a parameter, it's the pipeline;
change what data gets collected, change what the system is even asked to predict. **Refuse**:
and sometimes, after measuring and redesigning, the honest answer is that this system
shouldn't be built at all, not with a caveat and a disclaimer, just not built. That drawer
gets opened the least and needed the most.

"One more thing, because it's the part people relax on too early." She closes the toolbox.
"This isn't a task you finish. A model that passed every fairness check at launch can drift
as the population using it changes, and a check run once and filed away is worth nothing a
year later. Reducing discrimination is a maintained practice, like a garden, not a
certificate you frame."

> A rebalanced dataset can leave the actual harm exactly where it was; fixing the model is not the same as fixing the system it's part of.

## Questions

### Reweighting a training dataset to correct one measured disparity is generally enough to make a model non-discriminatory.

- [ ] True
- [x] False

> Reweighting helps against the specific disparity it targets, but Remedy is explicit that
> no single technique is a cure. A fix can even shift the harm sideways rather than removing
> it, which is exactly why measuring afterward matters as much as measuring before.

### A hiring model is rebalanced so its training data no longer skews by gender, but the system is still used to automatically filter out any applicant with a gap in their employment history, which disproportionately affects women. What has actually happened here?

- [x] The math was fixed while the underlying use of the system remained unjust, an example of what Remedy calls ethics-washing
- [ ] The system has been made completely fair because the training data issue was resolved
- [ ] The rebalancing introduced a new bug unrelated to fairness
- [ ] The filtering criterion is unrelated to any fairness concern

> The training data fix is real, which is exactly what makes this case dangerous: it looks
> resolved. But the filter that disproportionately screens out women is still running
> underneath, which is precisely Remedy's ethics-washing pattern, the technical work looking
> responsible while the actual harm stays in place.

### Remedy describes three things a team can do about a discriminatory system: measure, redesign, and a third. What is it?

- [x] Refuse to build or deploy the system at all, if that's what the honest answer requires
- [ ] Report the issue to a public relations team
- [ ] Rename the system so it attracts less scrutiny
- [ ] Wait for the next model update to fix it automatically

> Renaming a system or routing the problem to public relations changes how it looks, not
> what it does, and Remedy is clear that discrimination doesn't fix itself on a future
> update. The third real option she names is refusal: sometimes the right answer is not
> building the system at all.

### A fairness check that a model passed at launch remains valid indefinitely, regardless of how the population using the system changes over time.

- [ ] True
- [x] False

> Remedy's closing point is specifically that a model can drift as the population it's used
> on changes, so a check filed away after launch is worth nothing a year later. Reducing
> discrimination has to be maintained, not certified once.
