---
id: ai-tools
keeper: wizard
name: The Oracle
pass: 0.75
place: oracle-transcript
---

# 🤖 What You Told The Oracle

The Oracle answers questions. It has always answered questions. It is very good, and it
is the most useful thing on this floor, and it does not lie.

"They warn you about me," it says, "and they warn you wrongly. They tell you I am
unreliable. Sometimes I am. That is not the danger, and it is not why this room exists."

**The danger is the other direction.** Not what the Oracle tells you. What you tell the
Oracle.

You paste in the config file to ask why it's broken. The customer contract, to summarise
it. The error log, to explain the exception, and the log has session tokens in it,
because logs always do. The spreadsheet, to write a formula. The internal strategy memo,
to tidy up the prose.

Every one of those is a reasonable thing to want. Every one of them may have just left
your organisation.

> Pasting something into an external service is *publishing* it to that service. Whether
> it's cached, logged, reviewed by a human, or used for training is now somebody else's
> policy decision, and it is subject to change.

The rules that actually matter:

**Know which door you're using.** A tool your organisation has contracted, with terms
covering your data, is a different thing from the free consumer version of the same
brand. Same interface. Same logo. Entirely different agreement about your input. Most
accidents live in this gap; people believe they're using the approved tool because it
looks identical.

**Credentials and keys, never. No exceptions.** Not to debug, not "just the redacted
version", not in a screenshot. A key in a prompt is a key you must now rotate.

**Personal data is regulated wherever it goes.** Customer records don't stop being
regulated because you pasted them somewhere convenient. The obligation follows the data.

**Assume no delete.** Retention policies vary and change. Model behaviour is not a
filing cabinet you can open and remove one page from.

The Oracle is quiet a moment.

"Understand that I am not warning you away from me. Refusing to use good tools is not
security; it is just refusing to work, and the people who do that lose to the people who
don't. Use me. Use me constantly."

"But know what you are handing across the counter, and know **which** counter. That is
all this room has ever been about."

## Questions

### What's the primary security risk of using an external AI assistant for work?

- [ ] The output may be wrong, and acting on it could cause harm
- [x] Your input leaves the organisation, and its handling is governed by someone else's policy
- [ ] It may generate insecure code that gets deployed
- [ ] Your organisation may not have approved the tool

> The risk runs *outward*. Everything you paste in is disclosed to a third party. What
> happens to it next is their policy, and theirs to change: retention, logging, human
> review, training.
>
> Inaccurate output is a real quality problem, but it's *your* problem, contained inside
> your building. Approval matters, but it's the mechanism, not the risk. The data leaving
> is the thing that can't be undone.

### Using the free consumer version of an AI tool your organisation has an enterprise agreement with is equivalent, since it's the same underlying model.

- [ ] True
- [x] False

> This is the gap most accidents fall through. Same brand, same interface, same model,
> completely different agreement about your data. Enterprise terms typically bar training
> on your input and add retention and access controls. Consumer terms often don't.
>
> And because it looks identical, people are certain they're being careful right up until
> someone checks which account they were logged into.

### You're debugging a production error and want to paste the stack trace into an AI assistant. What deserves a second look?

- [ ] Nothing; stack traces are technical output with no business data
- [x] Stack traces routinely carry tokens, connection strings, file paths, and fragments of real user data
- [ ] Only whether the assistant is approved for use
- [ ] Only if the trace comes from production rather than staging

> Logs and traces are one of the most under-considered leak paths precisely because they
> feel like machine noise. They carry session tokens, connection strings with embedded
> credentials, internal hostnames, file paths that map your infrastructure, and, often,
> whatever the user actually typed.
>
> Approval matters but doesn't make a leaked key safe: a credential in an approved tool is
> still a credential you must rotate. And staging systems are full of copied production
> data, which is its own room in a longer version of this dungeon.

### If you paste something sensitive into an AI tool by mistake, deleting the conversation resolves it.

- [ ] True
- [x] False

> Deleting the conversation removes it from *your view*. It doesn't reliably remove it
> from logs, backups, caches, or anything downstream, and it certainly doesn't retract a
> disclosure that already happened.
>
> Treat it as you'd treat any other disclosure: if it was a credential, rotate it now. If
> it was regulated data, report it; this is exactly what the next room is about, and it
> is not a room you should be afraid of.
