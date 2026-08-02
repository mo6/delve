---
id: social-engineering
keeper: wizard
name: Iolanthe, Who Is Not The Auditor
pass: 0.75
place: visitor-badge
---

# 🎭 The Attack That Is Just A Conversation

Iolanthe is wearing a lanyard. It has a photograph on it. The photograph is of her, and
the lanyard is not real, and she has been in this building for three days.

"Nobody stopped me," she says pleasantly. "Two people held doors. One man carried my
box. He was lovely."

Every attack so far needed something technical, an email, a link, a device. This one
needs a plausible sentence and someone who would rather not make a fuss.

**Social engineering exploits helpfulness, not stupidity.** It targets the good
instincts: the wish to be useful, to not seem paranoid, to not embarrass someone who
might be senior, to keep things moving. These are the qualities that make an
organisation function. That's exactly why they're the attack surface.

The shapes it takes:

**Pretexting**, a story that explains why they need the thing. "I'm from the auditors,
I need to check the server room." "IT here, we're seeing errors on your account, can you
confirm your password?" The story does the work; the request rides in behind it, sounding
like a consequence.

**Tailgating**, following someone through a door they opened. Almost never challenged,
because challenging it means being rude to a stranger who is probably fine. They're
usually carrying something. That's not an accident: hands full means the door is *your*
job now.

**Vishing**, the same thing by phone, where the number is trivially spoofed and there's
time pressure and a friendly voice. "This is the bank's fraud team." Caller ID is a
suggestion, not a fact.

**Authority and urgency, together.** Always together. Someone important needs something
immediately, and the process that would normally catch it is the thing you're being
asked to skip *because* they're important and it's urgent.

> The attacker doesn't need you to believe them. They need you to find it *awkward* to
> check.

"So here is the whole defence," Iolanthe says, taking off the lanyard, "and it costs
you nothing but a moment of social discomfort."

**Verify through a channel they didn't give you.** They say they're from IT: hang up and
call IT on the number you already had. They say they're expected: check with the person
expecting them. They're at the door: walk them to reception. Not because they're
certainly lying, most people aren't, but because the check is cheap and the alternative
is me, on your third floor, for three days.

"Nobody was stupid," she says. "Everybody was *nice*. Be nice. Check anyway."

## Questions

### What does social engineering primarily exploit?

- [ ] Ignorance of security policy among non-technical staff
- [x] Normal social instincts, helpfulness, deference, and reluctance to cause a fuss
- [ ] Carelessness and lack of attention to detail
- [ ] Gaps in physical access controls

> It targets your virtues, which is what makes it so hard to defend against. The urge to
> hold a door, to help someone struggling, to not challenge someone who might be senior,
> to not seem paranoid; these are what a functioning workplace runs on.
>
> Framing this as ignorance or carelessness gets it backwards and makes it worse: it
> tells people the victims were stupid, so *they* won't report it when it happens to
> them.

### Someone in a delivery uniform, arms full of boxes, reaches your building's badge-controlled door as you badge in. What's the reasoning?

- [ ] Hold the door; refusing help to someone visibly struggling is unreasonable
- [ ] Hold the door, but watch where they go and report anything odd
- [x] Don't hold it; walk them to reception to be signed in, politely
- [ ] Ask to see their badge, and hold the door if they produce one

> Full arms are a *technique*, not a coincidence. It makes holding the door feel like
> basic decency and makes refusing feel cruel; that's the entire design of the
> approach.
>
> The polite version isn't refusal, it's redirection: "let me walk you round to
> reception." You're still helping. They're just being signed in.
>
> Watching where they go means they're already inside. And a badge you're shown is
> cardboard; evaluating it in a doorway is theatre, which is why Iolanthe's works.

### If a caller can tell you your full name, your manager's name, and your office location, they have demonstrated legitimate knowledge of your organisation.

- [ ] True
- [x] False

> All of that is reconnaissance, and it's cheap, your website, a professional network,
> a press release, an org chart someone shared too widely, or a receptionist who was
> being helpful.
>
> This is the same lesson Grigor taught two floors up, wearing a different costume:
> knowing things about you proves research, not identity. It's *supposed* to feel like
> proof. That's what it's for.

### In a few words, what's the one tell that an IT support call asking for your password is illegitimate, regardless of the surrounding context?

- ?answer: no legitimate support needs your password, they never need your password, asking for a password is the tell, real support never asks for your password, the request itself is the tell
- ?reject: it was unsolicited, they created urgency, IT should have access already

> Some requests are self-invalidating. Nobody legitimate needs your password, ever;
> support staff have their own access paths and don't want your credentials. So the
> request doesn't need evaluating against context; it's disqualifying on its own.
>
> Unsolicited contact and manufactured urgency are both real signals, and they're both
> *contextual*; they'd make you suspicious. This one makes you certain. Learn the
> handful of requests that are never legitimate and you don't have to out-think anyone.
