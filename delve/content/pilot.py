"""The hard-coded M2 slice: the pilot's first room, 'Recognising a Phish' (Ada the Suspicious).

Verbatim from packs/security-onboarding/en/01-the-sorting-office/01-phishing.md, with Markdown
emphasis flattened to plain text (token styling is a later polish). M2 renders this without a
parser; M3 will produce the identical `Room` object from the Markdown, which is why the shape is
fixed now. Explanations keep their paragraph break as a blank line so the panel can page them.
"""

from delve.assess.question import Option, Question
from delve.content.lesson import Block, Lesson
from delve.content.pack import Room

_LESSON = Lesson(
    title="🎣 Recognising a Phish",
    blocks=(
        Block("para", "Ada does not look up. She is holding a letter to the lamp, and she keeps "
                      "holding it while she talks."),
        Block("para", '"Everyone wants me to teach them the tell," she says. "The spelling '
                      "mistake. The odd greeting. They want a checklist so they can stop "
                      "thinking. I will not give you one, because the people who write these "
                      'letters have read the same checklist, and they are better at it than you."'),
        Block("para", "She puts the letter down."),
        Block("para", "A phishing message wants one of three things: your credentials, your "
                      "money, or your click. It has no other purpose. Everything else is set "
                      "dressing: the logo, the footer, the plausible name of a colleague. All of "
                      "it paid for out of the attacker's time budget, and that budget is larger "
                      "than you think."),
        Block("para", "What it needs from you is a decision made quickly. So it manufactures "
                      "urgency: a deadline, a threat, an authority you would rather not "
                      "disappoint. The invoice is overdue. The account will be suspended. The "
                      "CEO is in a meeting and needs this now."),
        Block("quote", "The hurry is not a side effect of the attack. The hurry is the attack."),
        Block("para", "Underneath the urgency there is almost always a mismatch, something that "
                      "does not fit, and would not survive ten seconds of unhurried attention:"),
        Block("bullet", "A sender domain that is nearly right. micros0ft.com. "
                        "yourcompany-hr.net."),
        Block("bullet", "A link whose text says one thing and whose destination says another."),
        Block("bullet", "A request that bypasses a process which exists precisely to stop this "
                        "request."),
        Block("bullet", "A channel that is wrong: your bank does not text you a login link."),
        Block("para", '"The mismatch is always there," Ada says. "It has to be. They cannot forge '
                      "the whole world, only the parts you look at. Your job is to look at one "
                      'more part than they paid for."'),
        Block("para", "She finally looks up."),
        Block("para", '"So. Not a checklist. A habit. When a message makes you feel that you must '
                      "act now, that is the moment to do the opposite. Slow down and check one "
                      'thing. Just one. Almost every attack in this building dies right there."'),
    ),
)

_QUESTIONS = (
    Question(
        prompt="An email appearing to come from your CEO asks you to urgently buy gift cards for "
               "a client, and to keep it quiet until the deal closes. What is the strongest "
               "single signal that this is an attack?",
        options=(
            Option("The message came by email rather than in person", False),
            Option("It combines manufactured urgency with a request to bypass normal purchasing",
                   True),
            Option("Gift cards are an unusual business expense", False),
            Option("A CEO would not normally email someone in your role directly", False),
        ),
        explanation="Urgency plus process-bypass is the signature, and secrecy is what makes it "
                    'fatal; "don\'t tell anyone" exists solely to stop you doing the one check '
                    "that kills it.\n\n"
                    "The other answers are all genuinely odd, and oddness is worth noticing. But "
                    "oddness alone isn't evidence: CEOs do email people directly, unusual "
                    "expenses do happen, and plenty of legitimate business runs on email. "
                    'Suspicion that fires on "unusual" fires constantly and teaches you to '
                    "ignore it.",
    ),
    Question(
        prompt="Poor spelling and grammar are a reliable way to spot a phishing email.",
        options=(Option("True", False), Option("False", True)),
        explanation="This was decent advice fifteen years ago and is now actively dangerous. "
                    "Modern phishing is well written, often better written than your actual "
                    "internal comms.\n\n"
                    "There's an old theory that attackers left errors in deliberately, to filter "
                    "for gullible targets. Whether or not that was ever true, it isn't now. "
                    "Assume the letter is beautiful. Look at the domain instead.",
    ),
    Question(
        prompt="You receive a message from a colleague's real, correct email address, asking you "
               "to review an attached document. Nothing about the address is wrong. What does "
               "this tell you?",
        options=(
            Option("It is safe; the sender address matches, so the sender is genuine", False),
            Option("It is unsafe; attachments from colleagues are the most common attack", False),
            Option("Almost nothing on its own; a correct address is what a compromised account "
                   "looks like", True),
            Option("It is safe if your mail system marked it as internal", False),
        ),
        explanation="A correct sender address proves the mail came from that account. It does not "
                    "prove your colleague sent it. Account takeover is exactly the scenario where "
                    'every address check passes, and it\'s why "verify the sender" can\'t be the '
                    "whole habit.\n\n"
                    "The judgement moves to the content: were you expecting this? Does the "
                    "request make sense from this person? Is it urgent in a way that discourages "
                    "checking? If in doubt, ask them, on a channel that isn't the email.",
    ),
    Question(
        prompt="A message that survives your check of the sender domain and the link destination "
               "has been proven legitimate.",
        options=(Option("True", False), Option("False", True)),
        explanation="Checks raise confidence; they don't confer proof. A compromised account "
                    "passes the domain check. A link to a legitimate-but-hijacked site passes "
                    'the destination check. The habit isn\'t "run the checklist and then trust"; '
                    'it\'s "stay willing to be wrong, especially when you\'re being hurried."',
    ),
)

PHISHING_ROOM = Room(
    id="phishing",
    keeper_name="Ada the Suspicious",
    keeper_kind="wizard",
    lesson=_LESSON,
    questions=_QUESTIONS,
    pass_mark=0.75,
)
