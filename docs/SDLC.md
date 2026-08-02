# The agentic SDLC: skills and agents for Delve's own development

Future-reference design note, not scheduled work, in the same spirit as [DISPLAY.md](DISPLAY.md) and [WEBDISPLAY.md](WEBDISPLAY.md): ideas and possibilities, not a plan anyone is committed to building. Where those two are about how Delve looks, this one is about how Delve gets *built*: how the project's own development lifecycle (research, design, define issues, develop, test) maps onto Claude Code's agents and skills, done in a way that does not burn tokens proving what a checklist could prove for free.

Nothing here proposes changing the lifecycle. Delve already has one, and it is unusually well specified for a project this size: [issues/AGILE.md](../issues/AGILE.md) (epics, features, stories, Definition of Ready / Done), `docs/` (the *why*), `CHANGELOG.md` (the *when*), and `./run-tests.sh` (the one gate). This document is about **wiring tooling onto that shape**, not inventing a new one. Read [issues/README.md](../issues/README.md) and [issues/AGILE.md](../issues/AGILE.md) first; this note assumes both.

---

## 0. Vocabulary: skill, agent, hook

Three different mechanisms, worth telling apart before mapping anything onto them:

| Mechanism | What it is | Cost shape |
|---|---|---|
| **Skill** | A packaged procedure (`.claude/skills/`), invoked by name. Its instructions load into the *current* conversation only when invoked. | Cheapest. No new context window, no re-derivation; the one-line description sits in every conversation, the body only on call. |
| **Agent** (subagent) | A separate context window (`.claude/agents/*.md`), with its own tool grant and optionally its own model. Fresh unless it's a **fork**, which inherits the caller's context and shares its prompt cache. | Fresh agents re-derive everything from a prompt; forks are cheap because they share cache and context. Worth it only when the raw work (exploration, a long tool trace) would otherwise sit in the main thread and never be needed again. |
| **Hook** | A shell command bound to an event (`PostToolUse`, etc.), configured in `settings.json`. No LLM call at all. | Free at inference time. Right tool for "always do X after Y", where an instruction would otherwise have to be remembered every session. |

The recurring mistake to avoid is reaching for an agent when a skill (or a hook) would do the job for a fraction of the tokens. **Section 6 turns this into a priority order.**

---

## 1. The five phases, as they already exist in Delve

| Phase | Already lives in | Owned by |
|---|---|---|
| **Research** | `docs/`, `issues/archive/`, `CHANGELOG.md`, the `NetHack/` reference clone | whoever is about to design or fix something |
| **Design** | `docs/*.md` essays (`PLAN.md`, `DISPLAY.md`, `WIDEMAP.md`, this file); the "Design notes / links" section of an issue | the maintainer role |
| **Define issues** | `issues/`, `issues/AGILE.md`, `tools/issues.py` | the maintainer role, per CLAUDE.md's "every change gets an issue first" |
| **Develop** | the codebase itself, against an issue's acceptance criteria | the maintainer or pack-author role |
| **Test** | `./run-tests.sh` (pytest, ruff incl. `S`, `pip-audit`, `./tools.sh screens --check`, `./tools.sh issues --check`, `delve validate`), plus the in-session `/code-review` and `/security-review` skills | everyone, as the Definition of Done |

None of this needs replacing. The gaps are the places where the process currently depends on a human (or an agent) *remembering* a convention rather than a tool *enforcing* it, and the places where a fresh, expensive agent gets reached for when a cheap skill would do.

---

## 2. Research: fork, don't spawn fresh

Research in this repo means one of: "has this been decided before" (`docs/`, `issues/archive/`), "how does NetHack do this" (`NetHack/`, read-only reference), or "where does this behaviour live" (the codebase itself). All three are read-only, exploratory, and produce far more raw output than anyone needs kept.

- **In-conversation research** (mid-task, "what did we settle on X"): fork yourself. A fork inherits full context and shares the prompt cache, so it is not re-deriving the five rules or the settled-decisions table from scratch the way a fresh agent would. Its tool trace stays out of the main thread; only its summary comes back.
- **Cold-start research** (a new conversation, no prior context, "where is the reward-tile logic"): the built-in `Explore` agent already does this at the right cost; it is read-only by construction (no `Edit`/`Write`) so it cannot widen scope into an accidental change while "just looking".
- **A possible narrow skill, `precedent`**: given a question, search `docs/`, `issues/archive/` and `rejected/`, and `CHANGELOG.md`, and return a short brief, not the matched files: relevant settled decisions (PLAN §3), prior `related:`/`supersedes:` issues, and whether the five rules bear on it. This is what a Definition of Ready item ("dependencies and related issues are linked") already requires by hand; a skill just makes the search mechanical instead of a grep someone remembers to run.

The token-efficiency point is not "use fewer research steps." It is **don't let the raw output of research sit in the context that then has to carry the design and the diff too.**

---

## 3. Design: a checklist pass, not a generator

A Delve design essay (`DISPLAY.md`, `WIDEMAP.md`, this file) is not free text; it is answerable to a fixed, short set of constraints: the five rules, the settled-decisions table (PLAN §3), locale impact (`en`+`nl`, identical trees), and screen/tutorial coupling (`docs/SCREENS.md`, and `delve/tutorial/` if a screen's look changes). That is a small, closed reading list, which makes it a poor fit for an open-ended agent and a good fit for a narrow one.

**Possible skill/agent, `design-review`**: not a drafting tool, a checking one. Takes a drafted design (or an issue's "Design notes" section) and checks it against that fixed list, flags anything that looks like it crosses rule 1's boundary (`engine` importing `content`/`assess`/`session`/`ui`, or `ui` importing anything but `session`), and runs `./tools.sh screens --check` if the change touches what a screen looks like. Fixed reading list, bounded tool grant (`Read`, `Grep`, one `Bash` allowance for the check scripts), no `Write`. Cheap because it never has to explore; it only has to compare a draft against documents that do not change often.

Catching a rule-1 violation or a missed locale at design time is a checklist read. Catching the same thing after code exists is a rewrite. That asymmetry is the entire argument for this phase existing as tooling at all.

---

## 4. Define issues: the most mechanical phase, and the best skill candidate

This phase is already almost entirely deterministic: `./tools.sh issues --check` prints the next free id, `issues/TEMPLATE.md` has the six sections, `issues/AGILE.md` has the epic/feature/story front matter and a Definition of Ready checklist that is, itself, already a list of yes/no questions. Deterministic and repeatable is exactly the shape a **skill** wants, not an agent.

- **`write-issue`**: runs `./tools.sh issues --check` for the id, scaffolds `TEMPLATE.md` with front matter, asks (via a real question, not a guess) for `type`/`epic:`/`area:` when those aren't obvious from the request, drafts stories in `As a <role>, I want ..., so that ...` form, and walks the Definition of Ready checklist before leaving `status: proposed`. Ends by running `./tools.sh issues` to regenerate the index.
- **`archive-issue`**: the done-side counterpart. Walks the Definition of Done checklist, confirms `./run-tests.sh` is green, checks the issue's "Peer review" section actually has an entry per reviewer rather than being blank, moves the file to `archive/`, fills `commits:`, regenerates the index. This is currently a sequence of manual steps AGENTS.md documents in prose ("move the file into archive/... fill commits:... regenerate the index"); a skill turns "remember to do all of that" into "run one command."

Both skills are thin wrappers around tooling that already exists (`tools/issues.py`, `TEMPLATE.md`, `AGILE.md`). That is the point: nothing new to design, just less to hold in working memory each time.

One step in this phase is deliberately **not** folded into `write-issue`'s automation, because it
is the one place a mechanical pass would defeat its own purpose: the **peer-review acceptance
gate** (DELVE-0045). A drafted issue sits at `status: proposed` until it is shown to a peer (in
this solo, no-remote project, the human maintainer) and explicitly asked whether it is accepted;
`write-issue` can walk the rest of the Definition of Ready unattended, but this one item has to
stop and wait for an actual answer, not infer one from the absence of an objection. Acceptance is
then recorded on the issue itself, `accepted_by:`/`accepted_at:` in the front matter, at the same
moment `status:` moves to `in-progress` and strictly before any code for the issue is written;
`./tools.sh issues --check` enforces the fields are present the same way it already enforces
`effort:`. This is the concrete instance of §1's general point: a tool enforcing beats a human
remembering, and here the tool enforces that the *ask* happened, even though it cannot make the
answer be yes.

The Definition of Done has the same gate at the other end (DELVE-0093 added it, after a review that
found real drift a mechanical check alone would have missed): before an issue is committed, merged,
or archived, the maintainer is asked outright, "commit and close this out?", and an agent never
infers a yes from silence any more than it infers acceptance at the Ready end. What's new relative
to the Ready-side gate is that this one leaves a **written trail**: every review that happened
(a reviewing agent's pass, the maintainer's own) is appended as a line in the issue's own "Peer
review" section before the question is asked, not summarised in a chat transcript that scrolls away.
That is deliberate: `accepted_by:`/`accepted_at:` records *that* a yes was given for the Ready gate,
a single fact; the Done gate can have several reviewers across several passes, so it needs a small
running log inside the issue rather than one more pair of front-matter fields, and future work on
an issue (or a later audit of "was this actually reviewed") reads that section instead of trusting
that a review happened because the issue is sitting in `archive/`.

---

## 5. Develop: stays in the main thread, with narrow exceptions

Most development work should not be delegated at all. The main thread already has the full conversation's context (the issue, the design discussion, the five rules), and re-deriving that in a fresh agent costs more than it saves for anything that isn't genuinely separable.

The exceptions are narrow, high-value, and match a pattern CLAUDE.md already calls out as easy to get wrong by hand:

- **A `pack-author` skill or agent, scoped to `packs/` and `delve/tutorial/`.** Bakes in `AUTHORING.md` and `STYLE.md` mechanically: no em-dash, Dutch tutoyeer and sentence-case headings, the "option count infers type, never a True/False label check" rule. After a change to one locale, it produces (or flags the absence of) the matching change in the other, which is exactly the "enumerate every occurrence and classify by hand" discipline CLAUDE.md's "Editing content that already exists" section already prescribes after two automated passes failed. A narrower tool grant here is also a safety property: an agent that can only touch `packs/` and the tutorial trees cannot accidentally cross rule 1 into `engine/` while writing a lesson.
- **A `screens-sync` hook**, not a skill: a `PostToolUse` hook on edits under `ui/` that reminds to run `./tools.sh screens` and re-paste into `SCREENS.md`, and to grep `delve/tutorial/` in both locales (CLAUDE.md names this exact gotcha: the tutorial hard-codes what a screen looks like, and "a structural validator will not catch this"). This is the clearest hook candidate in the whole document, because the rule it enforces is silent and convention-only today; a hook fires every time at effectively no token cost, where a written instruction only fires when someone remembers to reread it.

Everything else in "develop" (engine logic, session state machine, grader work, tests) is core-loop work best done directly, in the thread that already holds the issue's acceptance criteria.

---

## 6. Test: already centralised; the opportunity is not repeating it

`./run-tests.sh` is deliberately exhaustive and non-short-circuiting (CLAUDE.md: "it runs every step even when one fails"). That is correct behaviour for a gate and wasteful behaviour for a context window if the full log gets pasted in and re-read on every failure.

- **A `gate-check` skill**: runs `./run-tests.sh` (or a narrowed `pytest -k`/file target for a tight edit-run loop, both already supported), and on failure extracts just the failing test name or `ruff`/`pip-audit` id rather than carrying the whole log forward. The habit this replaces is "run the gate, paste everything, reason over all of it again"; the replacement is "run the gate, summarise the delta."
- **`/code-review` and `/security-review` already exist as skills in this environment** and are the right tool for a review pass; nothing here proposes replacing them. For a large or branch-wide review, `/code-review ultra` offloads the work to a separate, multi-agent cloud run rather than an in-session sweep, which is the real token-efficiency move at that scale: the interactive session's context stays untouched while the heavy reading happens elsewhere.
- **`docs/SECURITY.md` already treats security scanning as a gate, not a one-off review** (`ruff`'s `S` rules, `pip-audit`, both wired into `./run-tests.sh`). Section 7 below extends that same pattern to the surface a server adds.

---

## 7. The client-server future: what changes, and what to decide before code exists

Delve is explicitly headed toward a client-server model with multiple authenticated users (PLAN §11 Phase 3, PLAN §13.5). Two things are already true and worth restating here rather than re-deriving them later:

- **Identity today is trust-based** (PLAN §10): "Who are you?" matches or creates a `users` row by name, no authentication behind it. Fine for a trophy case, explicitly not fine as an audit record.
- **PLAN §13.5 already answers the architecture question that matters**: a served build is the only configuration where the server, not the client, holds state and grades. That is the one thing that would *force* a server to exist (auditable scrolls), not "should the UI look nicer." A web/served client is expected to consume the same `Command → Frame` contract (or a JSON projection of it); it "never grades, never opens doors, never imports `engine`" ([WEBDISPLAY.md](WEBDISPLAY.md) §2.3). That sentence is, in effect, rule 1 restated one layer out.

What follows from that for the SDLC, once server work actually starts (not before):

- **A sixth rule-shaped boundary, written down before the first server-side line, the same way rule 2 was drawn before any UI code existed** (PLAN §3's own phrase for that: "a package boundary drawn before any code exists to move"): the client talks to the server only through the `Frame`/`Command` contract; the server owns `session`, `gate`, `assess`, and `progress`; nothing client-side ever touches SQLite or a grader directly. The `design-review` skill in §3 is the natural place to check this, the same way it already checks the existing four-layer boundary.
- **A fourth story role.** `issues/AGILE.md` names three: learner, pack author, maintainer. A server implies an **administrator** role (PLAN §11 already uses the word, for whoever receives a scroll export): manages a deployment, sees aggregate results, is not the same actor as a maintainer editing engine code. Add it to AGILE.md's role list when the first server-facing story is written, not speculatively now; a role with no story yet is unfalsifiable.
- **A new attack-surface row in `docs/SECURITY.md`.** The table there is deliberately scoped: "no server" is implicit in every current row (the local LLM socket, the setup subprocess, local SQLite). Real auth, sessions, and multi-tenant data (can learner A ever see learner B's runs or scrolls) is a materially different threat model, and the project's own gate pattern (a table plus a checklist, checked every `run-tests.sh`) is the template to extend, not replace. Any change that touches auth should be a mandatory `/security-review` pass before merge, the same way a `ruff -S` finding is mandatory to fix or explicitly suppress today.
- **A new testing surface, not just more tests.** Session isolation (one authenticated user's `Frame` never carries another's data), token/session expiry, and rate limiting are not covered by anything `./run-tests.sh` checks today, because none of it exists to check. When it does, it belongs in the same Definition of Done pattern AGILE.md already uses: acceptance criteria in Given/When/Then, testable headlessly, no exception for auth just because it is new.
- **Identity stops being purely a design choice and starts being a migration.** `PLAN §10` already flags this as trust-based by choice, not oversight. The corresponding SDLC point: the `research`/`design` phases (§2, §3 above) are where the migration path from "type your name" to real auth gets decided, before a single `users` row schema exists to migrate.

None of this is scheduled. It is what to have *decided on paper* before the first server-side commit, the same discipline PLAN.md already applies to everything else in this project.

---

## 8. If any of this gets built: priority order

Cheapest and lowest-risk first, each following the project's own rule that a change to the system gets an issue first (this document does not, being itself a design essay about process, not a change to the game):

1. **`write-issue` / `archive-issue` skills** (§4). All the machinery they wrap already exists; nothing to design, only to script.
2. **`gate-check` skill and the `screens-sync` hook** (§5, §6). Both wrap existing tools (`tools/screens.py`, `tools/issues.py --check`, `./run-tests.sh`) around gotchas CLAUDE.md already documents in prose. Converting a remembered convention into an enforced one is the highest payoff for the lowest design risk in this list.
3. **`pack-author` skill** (§5). Highest content-quality payoff given the pilot pack's own history (the "~300 hand decisions" lesson in CLAUDE.md), but needs care in scoping its tool grant correctly (packs/ and the tutorial trees only).
4. **`design-review` skill** (§3). Most useful once there is more than one maintainer, or once client-server work raises the cost of a missed boundary violation.
5. **Client-server SDLC additions** (§7): the sixth boundary, the administrator role, the `SECURITY.md` server row. Deliberately last; writing these before a server-facing issue exists would be designing for a hypothetical, which CLAUDE.md already warns against in general and which PLAN §13.5 warns against specifically for this project.

---

## Open questions

1. **Where do project-specific skills/agents live?** `.claude/skills/` and `.claude/agents/` are currently empty; nothing in this document requires them to exist yet. Answer when §8's item 1 is actually built.
2. **Does a `design-review` or `pack-author` agent need its own restricted model** (a cheaper model for high-volume, low-judgment checklist work, reserving the primary model for judgment-heavy design and architecture)? Worth measuring once one exists, not assumed now.
3. **Administrator role scope**, once real: does it only view aggregate results (PLAN §11's Phase 3 hall of fame), or does it also manage deployments and pack distribution (PLAN §13 open question 3, pack distribution)? Likely answered together, since both are server-side.
