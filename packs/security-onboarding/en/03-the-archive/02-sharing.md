---
id: sharing
keeper: gatekeeper
name: The Link-Warden
pass: 0.75
place: open-share-link
---

# 📤 Anyone With The Link

The Link-Warden stands where four corridors meet and watches all of them at once.

"Nothing gets stolen here," it says. "Everything here was *given away*. By people in a
hurry, who were being helpful."

The most common data breach in a modern organisation is not an intrusion. Nobody picks
a lock. Someone shares a folder with the wrong scope, and then goes to lunch.

**"Anyone with the link" is a public link.** Not semi-public. Not
private-but-convenient. The link is a password that anyone can copy and nobody can take
back. It is now in a chat log, a forwarded email, a screenshot, a ticket, a browser
history, and, if the link ever reached anywhere a crawler can see, an index.

You cannot know where the link has been. That's the entire property of a link.

> A link-shared document is protected by the *secrecy of a URL*. URLs are the least
> secret thing your organisation produces.

Four ways people give things away, all of them well-intentioned:

**Sharing wide because narrow is fiddly.** Adding six named people takes a minute.
"Anyone with the link" takes a second, and it works immediately, and nobody has to ask
you for access later. Every incentive points the wrong way.

**Sharing the container, not the thing.** You share one file. But it lives in a folder,
and you shared the *folder* in 2023, and it now contains ninety files, and you have no
idea which.

**Forgetting that shares don't expire.** The contractor finished eighteen months ago.
The share is still live. It will be live in ten years, because nothing ever removes it.

**Attaching more than you meant.** The spreadsheet has a second tab. The document has
tracked changes and comments. The PDF was exported from something with metadata in it.
The screenshot has your whole desktop in the background, including the thing you were
reading.

"So," says the Link-Warden. "Two questions. Not a policy. Two questions."

**Who, specifically, needs this?** Name them. If you cannot name them, you do not know
who you're sharing with, and neither does anyone else.

**When should this stop?** Set the expiry now, while you're thinking about it. You will
not come back and do it later. You never have.

## Questions

### Why is "anyone with the link" effectively public sharing?

- [ ] Because search engines will always index the document eventually
- [x] Because a link can be forwarded, logged, and screenshotted, and you can never know where it's been
- [ ] Because cloud providers scan link-shared documents
- [ ] Because it's the default setting and defaults are always insecure

> The link is the credential, and it's a credential that copies itself effortlessly and
> silently. Once it's out, it's in chat logs, forwarded mail, tickets, browser
> histories, and there's no mechanism anywhere that tells you so.
>
> Indexing is a real but *situational* risk, not the mechanism. Providers don't hand
> your documents to strangers. And the default is often the opposite; the point isn't
> that it's a bad default, it's that it's a tempting choice.

### You share a single file with an external partner using "anyone with the link". What's the risk you've most likely overlooked?

- [ ] The partner might forward the link to a competitor
- [x] The file's parent folder may already be shared more broadly, or the link may reach places you'll never see
- [ ] The file could be modified without your knowledge
- [ ] The partner's email could be compromised in transit

> The blind spot is *scope you didn't set*. Inherited folder permissions and the
> uncontrolled travel of the link itself are what actually bite, and neither is visible
> from where you're standing when you click Share.
>
> A malicious partner is a real risk but it's the one you already considered. Editing is
> a permission setting. And email interception is largely a solved problem compared to
> the link simply being *forwarded*, in the clear, by someone helpful.

### Access that was granted appropriately remains appropriate for as long as the relationship lasts.

- [ ] True
- [x] False

> Access granted correctly on day one decays into over-access by month six, because
> roles change, projects end, and nothing ever revokes anything.
>
> "The relationship lasts" is doing sneaky work in that sentence, the contractor whose
> engagement ended, the colleague who moved teams, the partner whose project shipped.
> All still in the share. Set the expiry when you create the share; you will not come
> back to do it.

### Besides what's visible on screen, name one thing that can travel silently with a shared spreadsheet.

- ?answer: hidden tabs, hidden sheets, filtered rows, comments, revision history, tracked changes, metadata
- ?reject: file size, formatting, font issues, compatibility

> Documents carry more than what's on screen. Hidden sheets, filtered-out rows, tracked
> changes, comments, and full revision history all travel with the file, and none of it
> is visible in the view you were looking at when you decided it was fine to send.
>
> Linked formulas are a genuinely good answer; they can leak structure and break
> confusingly. But they tend to *fail loudly* on the recipient's machine. Hidden data
> arrives silently and works perfectly.
