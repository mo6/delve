---
id: password-managers
keeper: shopkeeper
name: Ives, of Ives & Vault
pass: 0.75
reward: 50
place: vault-keyring
---

# 🔐 One Lock Worth Picking

Ives runs a shop with exactly one item in it, and he has never once been asked for
change.

"You've come from Entropy," he says, delighted. "So you know the requirement. Long,
unique, everywhere, forever. Two hundred accounts. And you're about to explain that
you *can't*, and ask me for an exception."

He leans on the counter.

"There isn't one. There's a tool."

A **password manager** generates a long random password for every account, stores them
encrypted, and fills them in for you. You memorise exactly one passphrase, the one
that opens the manager, and after that you never see, type, or know any of the others.

The objection arrives in the same shape every time, so let's have it now:

> *"Isn't putting all my passwords in one place exactly the thing you told me not to
> do? Now one breach loses everything!"*

"It's a fair objection," Ives says. "It's just wrong, and it's wrong for a reason worth
understanding, so listen properly."

**You already have all your eggs in one basket. The basket is your memory, and it's
leaking.** A memorable password is memorable because it has structure, and structure is
what gets guessed. Two hundred accounts on human memory means reuse, not because you're
lazy, but because the alternative is impossible. And reuse means one breach already
loses everything.

A manager doesn't create the single point of failure. It *moves* it, from a place
designed to hold shopping lists and birthdays, to a place designed to hold secrets. The
vault is encrypted with a key derived from your passphrase. The provider cannot read it.
An attacker who steals the encrypted vault has stolen noise.

"Concentrating risk sounds bad," says Ives, "until you ask where it was concentrated
before."

The second objection is quieter and better: *what if the manager is breached?* It
happens. Providers do get compromised. And the answer is that a well-built vault stays
encrypted through it; your master passphrase is not in it, and was never sent. Which
is precisely why the master passphrase must be long, unique, and never reused: it is the
one secret with no backup.

"So you buy one thing from me," Ives says, ringing up nothing. "One passphrase. Four or
five words, unrelated, never used anywhere else, never typed into anything but the
vault. Everything else in your life becomes forty characters of random noise that you
will never see and never need to."

He hands you nothing at all, which is the point.

"Free, incidentally. Every good one is. I just like the ceremony."

## Questions

### What's the strongest response to "a password manager puts all my eggs in one basket"?

- [ ] It's a fair concern, but the convenience is worth the risk
- [x] The eggs were already in one basket, human memory, which forces reuse and leaks structure
- [ ] Vaults are never breached, so the concern is hypothetical
- [ ] Splitting passwords across two managers solves it

> The objection assumes there's a safer status quo. There isn't. Human memory *is* a
> single point of failure, it's already holding everything, and its failure mode,
> reuse, is the most exploited weakness there is. A manager moves the concentration
> to something built for it.
>
> "Worth the risk" concedes a trade that isn't being made. Vaults absolutely do get
> breached, which is why the encryption matters rather than the promise. And two
> managers gives you two attack surfaces and two master passphrases to protect.

### If your password manager's provider is breached and attackers steal the encrypted vaults, your passwords are compromised.

- [ ] True
- [x] False

> Not by itself. The vault is encrypted with a key derived from your master passphrase,
> which the provider never receives and cannot recover. Stolen vault data is noise,
> unless your master passphrase is weak enough to brute-force offline, which is exactly
> why that one has to be long and unique.
>
> The honest caveat: a stolen vault gives attackers unlimited offline attempts, and it
> reveals metadata like which sites you have accounts with. It's a genuinely bad day.
> It is not the same as handing over your passwords.

### Which password is the one you must actually memorise, and what makes it different?

- [ ] Your work account password; it protects the most valuable systems
- [x] The manager's master passphrase; it's the one secret with no backup and no reset
- [ ] Your email password; email can reset every other account
- [ ] None; the manager can store its own master passphrase

> The master passphrase has no recovery path by design. If the provider could reset it,
> they could read your vault, and the whole model collapses. So it's the one secret
> living entirely in your head, and the one that must be long, unique, and never typed
> anywhere but the vault.
>
> Your email password is a genuinely excellent answer; email really is the master key
> to password resets everywhere, and it deserves the strongest protection you can give
> it. But the manager can *hold* it. It can't hold its own key.

### In a few words, name one thing a real password manager gives you that browser-saved passwords generally don't.

- ?answer: cross-device sync, works across browsers, works outside the browser, protected by a master passphrase, covers more than websites, syncs across devices
- ?reject: nothing, they're the same, it's identical

> Browser storage has closed most of the gap and is much better than reuse, if the
> choice is browser or `Summer2024!`, take the browser.
>
> But it's typically tied to one browser, its generation and cross-device story are
> weaker, it doesn't cover things that aren't websites, and it's protected by your
> logged-in session rather than a passphrase you actively supply. Better than nothing,
> not the same thing.
