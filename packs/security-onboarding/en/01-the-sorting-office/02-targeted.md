---
id: targeted
keeper: wizard
name: Grigor, Who Was Impersonated
pass: 0.75
place: spear-letter
---

# 🎯 When It Is Written For You

Grigor is a small man at a large desk, and there are two nameplates on it. Both say
GRIGOR.

"One of these is mine," he says. "For eleven days, the other one was also mine, as
far as the accounts department was concerned. They sent four hundred thousand to a
man in another country who signs his letters the way I sign mine, because he read
six months of my letters first."

What Ada taught you was **bulk** phishing: one letter, a million doors, a rounding
error of a success rate. It works because it is cheap.

This is the other kind. **Spear phishing** is written for you specifically, and it is
not cheap, which tells you something important about what it's after.

The attacker has done reading. Your name, your role, your manager's name, the project
you complained about publicly, the conference you attended, the supplier you actually
use. None of that is secret. Most of it is on your own website, and the rest is on
the professional network profile you updated last spring.

> Bulk phishing fails the "does this make sense?" test. Spear phishing is *built* to
> pass it. That's what the reconnaissance buys.

The expensive version of this has a name: **Business Email Compromise**. No malware,
no attachment, nothing for a scanner to find. Just a person who has learned your
organisation's habits, writing a message that fits them perfectly, asking for money
or data through a route that looks exactly like the normal route.

It is, by a wide margin, the most expensive attack in this book. Not the most
sophisticated. The most *expensive*.

"So the tells are gone," Grigor says. "The domain is right, because he has the
account. The tone is right, because he studied. The request makes sense, because he
knows what my requests look like. What is left?"

He taps the nameplate that is his.

"**The transaction is left.** Never mind who is asking. Look at what is being asked.
Money moving somewhere new. Bank details changing. Access being granted. A payroll
account being updated. These are the things worth stealing, so these are the things
worth a second channel."

A second channel means: pick up the phone. Not the number in the message, the number
you already had. Walk to their desk. Message them somewhere else. It takes ninety
seconds and it has never once been the wrong call.

"They can forge my letters," Grigor says. "They cannot forge my voice, and they
cannot be at my desk. So make them try."

## Questions

### What most reliably distinguishes spear phishing from bulk phishing?

- [ ] It always contains malware, where bulk phishing usually doesn't
- [x] It's researched and written for a specific target, so it survives "does this make sense?"
- [ ] It comes from a spoofed internal address
- [ ] It targets senior staff rather than ordinary employees
- [ ] It is sent to far fewer recipients

> The research is the whole difference, and what it buys is *plausibility*. Bulk
> phishing dies on "wait, I don't even bank there." Spear phishing is engineered so
> that question comes back clean.
>
> Fewer recipients is true but it's a consequence, not the mechanism. Targeting
> executives is whaling, a subtype, not the definition. And BEC, the costliest form,
> usually contains no malware at all: just a sentence asking for a bank change.

### The most expensive email attacks are the most technically sophisticated ones.

- [ ] True
- [x] False

> Almost exactly backwards. Business Email Compromise is technically trivial, often
> a plain-text email with no link, no attachment, and nothing for any scanner to
> detect, and it loses organisations more money than the sophisticated attacks do.
>
> It works on process and psychology, not code. Which is why the defence is a process
> and not a product.

### A supplier you've worked with for years emails to say their bank details have changed, and asks that this month's invoice go to the new account. The address, tone, and history are all correct. What do you do?

- [ ] Pay it; the relationship is established and the address checks out
- [ ] Reply to the email asking them to confirm the change
- [x] Call them on the number you already held, not one from the message, and confirm
- [ ] Forward it to finance and let them decide

> Changing bank details is the single highest-value request in a business inbox, and
> it's the classic BEC payload. It deserves a second channel every time, no matter how
> well you know the sender.
>
> Replying to the email is the trap: if the account is compromised, you're asking the
> attacker to confirm their own request, and they will, warmly. The number must come
> from your own records; a number *in* the message is part of the message. And
> forwarding to finance just moves the decision to someone with less context on the
> relationship than you have.

### Because spear phishing relies on public information about you, keeping a low online profile is the main defence.

- [ ] True
- [x] False

> Tempting, but it doesn't survive contact with reality. The information is your
> employer's website, your role, your colleagues' names, the industry you work in.
> You cannot un-publish your own existence, and a job that requires you to be
> contactable requires you to be findable.
>
> Reconnaissance is not the step to defend. The *request* is. Verify the transaction
> through a second channel and it stops mattering how much the attacker knows about
> you, which is fortunate, because it's going to be a lot.
