---
id: mfa
keeper: gatekeeper
name: The Second Factor
pass: 0.75
place: hardware-token
---

# 📱 The Second Factor

The gatekeeper here has no name that anyone uses. It asks two questions of everyone,
and it has never once accepted a good answer to only the first.

"Something you know," it says. "Something you have. Something you are. Bring me two."

That is the whole idea. A password is *something you know*, and the trouble with things
you know is that they can be taken from you at a distance, guessed, phished, breached,
reused. **Multi-factor authentication** demands a second thing of a different *kind*, so
that stealing the first is not enough.

Two passwords are not two factors. Two things you know is one factor, twice.

Not all second factors are equal, and the ordering is worth knowing:

| Factor | Verdict |
|---|---|
| **Passkeys / hardware keys** | Strongest. Cryptographically bound to the real site; a phishing page cannot use them, because it isn't the site. |
| **Authenticator app codes** | Good. Offline, not tied to your phone number. |
| **SMS codes** | Weak, but real. Vulnerable to SIM swapping and interception. Better than nothing; use it if it's all there is. |
| **Push "approve?" prompts** | Convenient. And the reason we're having this conversation. |

> A second factor doesn't make you unphishable. It changes what the attacker has to
> steal, and, with passkeys, whether stealing is even possible.

Because attackers adapted, of course. They always do. Two ways:

**MFA fatigue**, also called push bombing. The attacker has your password already. They
log in over and over, and your phone lights up over and over, at your desk, in a
meeting, at two in the morning, and again at two-fifteen. They are not hoping you'll be
fooled. They are hoping you'll be *tired*, and that eventually you'll tap approve to
make it stop. It works often enough to have taken down companies you've heard of.

**Real-time relay.** A phishing page that forwards your code to the real site the
instant you type it. Your code was genuine. Your login was genuine. It just wasn't
yours. This is why codes, even good app-generated ones, are not the end of the story,
and why passkeys, which refuse to authenticate to the wrong domain at all, are where
this is heading.

The gatekeeper leans down.

"So hear the rule, because it is one sentence and it is not negotiable. **A prompt you
did not cause is an attack in progress.** Not a glitch. Not the system being strange.
Someone has your password, in their hand, right now, and is standing at the door
pressing the bell."

"Deny it. Then go and change that password, and tell someone. In that order."

## Questions

### Your phone buzzes with a login approval request. You are not logging in to anything. It buzzes twice more over the next minute. What has happened, and what do you do?

- [ ] A system glitch; dismiss the prompts and carry on
- [ ] Someone mistyped their username; deny it and ignore it
- [x] Someone has your password and is trying to get in; deny, change the password, report it
- [ ] Approve one to see which system it's for, then investigate

> An unprompted approval request means someone already has your password. That's not a
> risk of a future breach; it's a breach in progress, and the repetition is push
> bombing; they're betting you'll cave to make it stop.
>
> Denying is necessary but not sufficient: they still have the password, and they'll be
> back tonight. Change it and report it. And never approve one "to see what it is";
> approving *is* the attack succeeding.

### Requiring both a password and a security question is multi-factor authentication.

- [ ] True
- [x] False

> Both are *something you know*, so that's one factor asked twice. Worse, security
> question answers are often discoverable, your mother's maiden name and the street
> you grew up on are not secrets, they're research.
>
> Multi-factor means factors of different *kinds*: something you know, plus something
> you have, plus something you are.

### Why are passkeys and hardware security keys stronger than authenticator app codes?

- [ ] The codes they generate are longer and change more frequently
- [x] They're cryptographically bound to the real site, so a phishing page can't use them
- [ ] They can't be lost, unlike a phone
- [ ] They work offline, where app codes need a network connection

> Domain binding is the whole advantage. A passkey will simply not authenticate to
> `micros0ft.com`, because it isn't `microsoft.com`; the check is cryptographic, not a
> judgement call you make while tired. That defeats real-time relay entirely, because
> there's no code to relay.
>
> Hardware keys are certainly *more* losable than a phone. And app codes already work
> offline; that's their advantage over SMS, not a weakness.

### In a few words, why should you still enable SMS-based MFA even though it's the weakest option?

- ?answer: it stops most attacks, better than nothing, it stops credential stuffing and bulk phishing, it blocks most attackers, still stops scale attacks
- ?reject: it's worthless, don't bother, it's not worth using, it should be disabled

> SMS is genuinely the weakest option; SIM swapping is real and not difficult against
> a targeted victim. But "weakest" is not "worthless."
>
> SMS MFA still stops credential stuffing, bulk phishing, and every attacker working at
> scale who isn't specifically interested in you. If a system offers only SMS, turn it
> on. Perfect is doing a lot of damage as the enemy of good here.
