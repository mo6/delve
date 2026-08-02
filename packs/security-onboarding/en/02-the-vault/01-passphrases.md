---
id: passphrases
keeper: wizard
name: Entropy, Keeper of Keys
pass: 0.75
place: sticky-note
---

# 🔑 Length Beats Cleverness

Entropy is not a person. It is a very old creature in the shape of one, and it counts
while it speaks, always, under its breath.

"You were taught to be clever," it says. "Substitute a three for an E. An at-sign for
an A. Add an exclamation mark, because the box demanded a symbol. `P@ssw0rd!`, and
you felt *cunning*, didn't you."

It stops counting for a moment.

"Every trick you were taught, the cracking dictionaries learned in an afternoon. They
are rules in a config file. `a→@`. `e→3`. `o→0`. Append a year. Capitalise the first
letter, because the box demanded a capital and you are a person who does the minimum
the box demands."

The thing that makes a secret hard to guess is not how strange it looks to you. It is
how many possibilities a machine must try. That quantity has a name, and it is the
creature's name too.

A password built from a common word plus predictable mangling has almost no entropy,
*no matter how unreadable it looks*, because the mangling is a known transformation
of a known word. The machine isn't guessing character by character. It's guessing
`common word × known rules`, and that space is tiny.

A **passphrase**, four or five unrelated words, is enormous by comparison. Not
because words are magic, but because the number of ways to pick five unrelated words
from a large vocabulary is a very large number, and the attacker gets no shortcut.

```
  P@ssw0rd!2024         looks strong.  Cracks in seconds.
  correct horse battery staple    looks silly.  Doesn't.
```

> Complexity is what a password looks like to *you*. Entropy is what it costs a
> *machine*. Only one of those is doing any work.

The other half is worse, and simpler:

**Length beats cleverness, but uniqueness beats length.** A magnificent forty-character
passphrase used in two places is a bad password in both. When one of those sites is
breached, and one of them will be, the attacker takes your magnificent passphrase and
tries it everywhere else you exist. This is called credential stuffing, it is fully
automated, and it is the single most reliable attack in this entire dungeon.

"So," says Entropy, counting again. "Long. Unique. Every single time."

It looks at you with something almost like sympathy.

"And you cannot do that. Not for two hundred accounts. Not with a human memory. Which
is why the next room exists, and why I am going to let you through to it."

## Questions

### Why does `Tr0ub4dor&3` provide poor security despite looking complex?

- [ ] It's too short; it needs at least sixteen characters
- [x] It's a dictionary word with predictable substitutions, which cracking tools apply by default
- [ ] It doesn't contain enough distinct symbols
- [ ] It contains a number at the end, a known weak pattern

> The mangling is the problem. `o→0`, `a→4`, `e→3`, append a digit; these are *rules
> in a config file*, applied automatically to every word in the dictionary. The
> attacker isn't guessing eleven characters; they're guessing "troubadour, mangled",
> and that space is small enough to exhaust quickly.
>
> Length is a real factor, but it's not what's wrong here; the mangling would still be
> the weakness at sixteen characters. And "more symbols" is the exact instinct that
> produced this password in the first place.

### A password that is long and hard for a human to read is therefore hard for a computer to crack.

- [ ] True
- [x] False

> This is the central confusion, and almost every bad password policy is built on it.
> Human unreadability and machine difficulty are unrelated properties.
>
> `P@ssw0rd!` is unreadable and trivial. `correct horse battery staple` is perfectly
> readable and enormously harder. The machine doesn't struggle with strangeness; it
> struggles with *quantity of possibilities*.

### You use one genuinely excellent 40-character passphrase, unique to you, nowhere else in the world, for all of your accounts. What's the risk?

- [ ] Low; the passphrase has more than enough entropy to resist cracking
- [x] Severe; one breach at any site hands an attacker every other account you own
- [ ] Moderate; it depends on whether the sites store passwords properly
- [ ] Low, provided none of the sites are high-value targets

> Entropy protects against *guessing*. It does nothing about a site that gets breached
> and hands over your password directly, at which point strength is irrelevant, because
> nobody had to guess anything.
>
> Then it's replayed everywhere automatically. That's credential stuffing, and reuse is
> the only thing that makes it work. Hashing helps at the breached site, but you can't
> audit it, you'll learn it was bad *afterwards*, and "none of my sites are valuable"
> ignores that the low-value site is exactly where the attacker starts.

### In a few words, when should you actually change a password, if not on a fixed schedule?

- ?answer: when there's a reason, after a breach, when compromised, if there's a suspicion, on suspicion of compromise
- ?reject: every 90 days, on a fixed schedule, routinely, every three months

> Long-standing policy, now withdrawn by the people who originated it; NIST and the
> UK's NCSC both advise against routine expiry.
>
> It backfires predictably: forced to change constantly, people pick weaker passwords
> and iterate them (`Summer2024!` → `Autumn2024!`), which is exactly what an attacker
> guesses next. It also trains everyone to treat passwords as disposable rather than
> valuable.
>
> Change a password when there's a *reason*, a breach, a suspicion, a shared secret.
> Not because a calendar said so.
