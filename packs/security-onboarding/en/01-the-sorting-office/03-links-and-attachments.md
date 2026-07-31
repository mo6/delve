---
id: links-and-attachments
keeper: gatekeeper
name: The Postmaster
pass: 0.75
place: suspicious-attachment
---

# 🔗 Links, Attachments, and the Space Between

The Postmaster has a stamp in one hand and has not used it once while you have been
standing here.

"Two of you a week come down here," he says. "They want to know which attachments are
safe to open. Wrong question. Ask a better one and I will let you past."

**A link is a claim about a destination.** The text is written by the sender. The
destination is also written by the sender. There is no rule that they must agree, and
an attacker has no reason to make them.

`https://yourbank.example.com` can point anywhere in the world. So can a button that
says **Review Document**. So can a logo. The only honest part of a link is the part
your browser will actually go to, and you can see it before you commit; hover on a
desktop, long-press on a phone, and read it from the *right* end.

Read from the right, because that's where the truth is:

```
https://yourcompany.sharepoint.com.login-verify.ru/doc/94812
...................................^^^^^^^^^^^^^^^
the domain is login-verify.ru
```

Everything to the left of the real domain is decoration the attacker chose to make you
comfortable. `yourcompany.sharepoint.com` there is not a domain. It is a *sentence*.

> The last two labels before the first single slash are the domain. Everything else
> is someone talking to you.

**An attachment is a program you have agreed to run.** Not always, but often enough
that the distinction isn't yours to make from the filename. A document can carry
macros. A PDF can carry a script. An archive can hide the extension of what's inside
it. A file called `invoice.pdf` may not be a PDF, because the name is just more text
written by the sender.

"Now," says the Postmaster. "The better question."

Not *is this attachment safe*. You cannot know that, and neither can I, and the people
who tell you they can are selling something.

**Was I expecting this?**

That question you can answer. It needs no expertise, no hovering, no analysis. If a
document arrives that you were not expecting, from anyone, about anything, the cost of
checking is one message on a different channel, and the cost of not checking is this
building's worst week.

He stamps something, finally.

"Expected: open it. Unexpected: ask. Unexpected *and* urgent: ask harder. That's the
whole of it. You'd be amazed how many people want it to be more complicated, so they
can be excused for not doing it."

## Questions

### Where in this URL is the actual destination? `https://accounts.google.com.secure-login.example.net/verify`

- [ ] `accounts.google.com`; it appears first and is the most specific
- [x] `secure-login.example.net`, the last two labels before the first single slash
- [ ] `verify`; the final path element is the destination
- [ ] The URL is malformed and wouldn't resolve

> Read domains from the right. `accounts.google.com` is a *subdomain* here, and
> `secure-login.example.net` chose to name it that precisely so it would sit at the
> front where you'd read it first.
>
> The URL is perfectly well formed; that's the problem. This is legal, cheap, and
> requires no compromise of anything belonging to Google.

### Hovering over a link to check its destination before clicking makes the link safe to click.

- [ ] True
- [x] False

> Hovering tells you where the link *claims* it will go, which is a real improvement
> over the text, but it's one check, not a verdict. Legitimate sites get compromised.
> Link shorteners hide the destination entirely. Redirect chains start somewhere
> respectable and don't end there.
>
> Hovering moves you from "no information" to "some information." It doesn't move you
> to "safe," and nothing does.

### An unexpected invoice arrives as a PDF from a company you've genuinely never dealt with. It's not urgent and makes no requests. What's the reasoning that matters?

- [ ] It's low risk; there's no urgency and no request, so the usual signals are absent
- [ ] It's high risk; invoices are the most common malware carrier
- [x] It's unexpected, and that alone is enough to justify not opening it
- [ ] It depends on whether your mail scanner flagged it

> "Was I expecting this?" is the whole test, and it's the one that works without
> expertise. The answer here is no, so don't open it.
>
> The absence of urgency is not reassurance; a patient attacker is a *worse* problem
> than a hurried one. And relying on the scanner inverts the relationship: the scanner
> catches what's already known, and you're the one deciding about the thing that isn't.

### A file named `report.pdf` is a PDF.

- [ ] True
- [x] False

> A filename is text chosen by whoever sent it, exactly like the display text of a
> link. It can lie, and there are decades of tricks for making it lie convincingly,
> double extensions, right-to-left override characters, archives that hide what's
> inside until it's running.
>
> Same principle as the link: the part the sender writes is a claim, not a fact.
