---
id: devices
keeper: gatekeeper
name: Rook the Watchman
pass: 0.75
place: usb-stick
---

# 🔌 The Thing You Carry

Rook has the look of someone who has watched a great many people leave a great many
things behind.

"Everything above this floor was about attackers," he says. "Clever ones. Patient ones.
Now we do the boring floor, where you lose the laptop on a train."

Your device is a key to everything you have access to. Not a copy of your work, a
**key**. It is authenticated, it is trusted, and it is small enough to leave in a taxi.

**Encryption is the one that turns a catastrophe into paperwork.** With full-disk
encryption on, a stolen laptop is a lost *object*, annoying, expensive, insured.
Without it, it's every file you had, plus the sessions in your browser, and a report you
have to make. It's built in and on by default nearly everywhere now, which means the
only real question is whether you ever turned it off.

**Lock your screen.** Encryption protects a device that's *off*. A stolen unlocked
laptop is unlocked. The gap between "I'm just getting coffee" and "someone sat down at
my desk" is the most-used vulnerability in this building, and it belongs to whoever
walks past.

**Updates are the boring one that actually matters.** The vulnerabilities being
exploited right now are mostly not new. They're months old, published, patched, and
still working, because the patch is sitting in a notification you've dismissed eleven
times. "Remind me tomorrow" is a decision, and you've made it eleven times.

**Public Wi-Fi is fine, and this surprises people.** HTTPS means the coffee shop's
network sees where you went, not what you did. The old advice to fear public Wi-Fi
mostly predates universal encryption. What still bites is the **captive portal that
wants you to install something**, and the person sitting behind you with a clear view of
your screen. Shoulder surfing is not a joke; it's the only attack in this entire
training that requires no technology at all.

> The threat on the train is not a hacker on the network. It's the passenger behind you
> reading your screen, and the moment you leave the laptop on the table.

**USB devices found in car parks are not a joke either**, and yes, this still works. So
do "free" charging cables and dubious dongles. The rule is dull: if you don't know where
it came from, it doesn't go in.

Rook shrugs.

"None of this is clever. That's why it's the floor everyone fails. You can spot a
phishing email at ten paces and still leave the thing unlocked in a Pret."

## Questions

### Your work laptop is stolen from a café table while unlocked. Full-disk encryption is enabled. What protection does the encryption provide?

- [ ] Complete; the disk is encrypted, so the data is unreadable
- [x] Almost none in this scenario; encryption protects a powered-off device, and this one is unlocked and running
- [ ] Partial; it protects files but not browser sessions
- [ ] It depends on whether the thief reboots the machine

> Full-disk encryption protects data *at rest*. A running, unlocked machine has already
> decrypted everything; the thief inherits your logged-in session, your files, your
> browser, your authenticated everything.
>
> Encryption is essential and it is not what saves you here. The screen lock is. Which
> is why the boring habit beats the impressive technology.
>
> (Rebooting would *engage* the encryption, the thief's mistake, not their plan.)

### Using public Wi-Fi to access work systems is a serious risk that should be avoided where possible.

- [ ] True
- [x] False

> Mostly outdated advice. When nearly all traffic is HTTPS, the network operator sees
> which sites you contacted, not what you sent; the eavesdropping attack this warning
> was built for largely stopped working.
>
> The real risks on public Wi-Fi are different and less discussed: captive portals that
> ask you to install a certificate or an app, and the person behind you reading your
> screen. Watch for those. The network itself is broadly fine.

### Why are known, patched vulnerabilities more dangerous than newly discovered ones for most organisations?

- [ ] Patched vulnerabilities are more thoroughly documented, so they're easier to exploit
- [x] They're weaponised and automated, and unpatched machines are everywhere; a published patch is a public map
- [ ] Newly discovered vulnerabilities are usually reported privately first
- [ ] Attackers prefer old vulnerabilities because they're less monitored

> Publishing a patch publishes the vulnerability. Within days there's working exploit
> code; within weeks it's in automated toolkits scanning everything. Meanwhile the
> patch is sitting in a notification someone keeps deferring.
>
> Zero-days are genuinely scarier per incident and vanishingly rarer; they're spent on
> targets worth spending them on. The month-old unpatched browser is what actually gets
> you, and "remind me tomorrow" is what leaves it there.

### In a few words, what's the correct thing to do with an unlabelled USB drive found in the office car park?

- ?answer: hand it to security, give it to security, report it to security, don't plug it in, hand it in
- ?reject: plug it into an isolated machine, check the filenames, leave it there, ignore it

> Malicious USB devices don't need you to open a file. Some emulate a keyboard and type
> commands the moment they're connected; there is no "just looking" that's safe, and
> filenames are exactly the bait.
>
> "Isolated machine" is the trap for technical people: it sounds rigorous, most people's
> idea of isolated isn't, and this is a hobby not a job. Leaving it there is passive;
> the next person picks it up, and that's what the drop was for.
>
> Unsure what counts as "hand it to security"? Ask in {{help_channel}}.
