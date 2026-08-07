# Working with Sergey — team working agreement

This is the full agreement. You can read it in ten minutes, and you can hand it to a new
teammate on day one. Every rule here is written so you can check it. If a rule is unclear
enough that two people would read it differently, that is a bug — say so.

Sergey is a platform and backend architect. He is in **CET** and works **08:00–18:00**.
He thinks in text and pictures. Spoken information does not stay with him. English is not
his first language, so plain English works and idiomatic English does not.

---

## 1. One minute version

| Situation | Do this |
|---|---|
| Production is down and it is costing money | Messenger DM or phone call. Any hour. |
| Urgent but not critical | Messenger DM. 30 minutes in the morning, 2 hours in the afternoon. |
| You need to think together | **Morning, 08:00–12:00 CET.** That is his collaboration window. |
| After 12:00 CET | He is coding. Only P0 makes him stop. |
| It must actually happen | Put it in the calendar or in a tracked task. |
| Normal question | Written thread. Answer within 4 working hours. |
| You want it read | Never email. |
| He wrote to you | React with an emoji within 4 working hours. |
| You will be away | Say so at least one working day before. |

---

## 2. Channels and priority

| Priority | Channel | Availability |
|---|---|---|
| **P0** — business critical | Messenger DM **or phone call** | Always, any hour, including holidays and the afternoon coding block |
| **Urgent** | Messenger DM (Slack, Teams, Telegram), or a **phone call if you have permission** | 08:00–18:00 CET |
| **Must happen** | Calendar event, or a ticket on the board | Scheduled |
| **Normal / FYI** | Written thread | Working hours |
| **Email** | — | **No SLA.** Email is full of automated noise. Nothing important should arrive there. |

**Phone is an urgent channel, open to permitted callers.** Anyone who already has his
number and has been given permission may call him directly when something is urgent.

**Permission is given by Sergey personally.** You do not ask for it in a thread, and you do
not have it by default. Having his number is not the same as having permission. New joiners
are not on the list.

**A call carries attention, not content.** Spoken decisions do not survive the call.

> **Rule:** whoever made the call writes the outcome into the messenger thread afterwards,
> on the same day. If it is not written, it did not happen.

---

## 3. Response times

| You send | You get an answer |
|---|---|
| P0 | Immediately, any hour |
| Urgent, **08:00–12:00** CET | Within 30 minutes — this is his collaboration window |
| Urgent, **12:00–18:00** CET | Within 2 hours — he is coding and replies at a natural break |
| Normal | Within 4 working hours |
| Email | No promise at all |

If you need an answer faster than the channel promises, raise the priority and change the
channel. Do not send the same message three times in the same channel.

If your question needs thinking together rather than a quick answer, do not send it at
15:00 and wait. Bring it to the morning.

---

## 4. Acknowledgement

Sergey reacts with an emoji to every message he has read. He asks you to do the same.

| Rule | Detail |
|---|---|
| **Window** | Within **4 working hours** of being tagged or DM'd |
| **How** | An emoji reaction on the message |
| **Where reactions do not exist** | GitHub, Jira, email: reply with one word — `ack` |
| **Meaning** | Ack means *I have read this*. It does not mean *I agree*. Disagreement is a separate, written reply. |
| **Announcements** | Announcements and important messages always need an ack. This is the case where silence hurts most. |

An unanswered announcement is not neutral. It reads as "nobody cares".

---

## 5. Working hours and daily rhythm

Sergey is an early bird. He does his hardest **thinking with other people** in the morning,
and his **implementation alone** in the afternoon.

| Block | Time (CET) | What belongs there |
|---|---|---|
| **Collaboration** | 08:00–12:00 | Complex work that needs other people: architecture, design, decisions, proposals, hard reviews, difficult conversations. **This is the best time to reach him.** |
| **Coding** | 12:00–18:00 | Focused implementation, plus routine simple work and trivial communication. **Only P0 interrupts.** |
| **Outside hours** | 18:00–08:00 | P0 only. |

**"Interrupt" and "answer" are not the same thing.** In the afternoon, only P0 makes him
stop what he is doing. An urgent message still gets an answer within two hours, at a
natural break. A light meeting agreed in advance is not an interruption at all.

The common mistake is saving the hard conversation for the afternoon because the morning
feels too early. It is the opposite: bring hard things early, and leave the afternoon for
things that do not need his full attention.

---

## 6. Language and format

The plain-English rule is about **reading speed, not format**. Sergey reads a document at his
own pace and can handle richer English there. He cannot do that in the middle of a
conversation.

| Where | Language |
|---|---|
| **Read now** — chat, DMs, calls, meetings, announcements, PR comments | **Plain English.** Short sentences. Common words. No idioms, no slang, no regional expressions, no sarcasm. "Let's park this" and "ballpark it" do not land. "Let us decide this later" does. |
| **Read later** — ADRs, specs, READMEs, this agreement | Normal written English is fine. He will take the time to read it properly. |

- **Written over spoken, always.** If it was said out loud, write it down afterwards.
- **Show, do not narrate.** A table, a diagram, or a short list beats three paragraphs of
  prose. Text diagrams (ASCII, Markdown tables, Mermaid) are welcome and preferred.
- **One message, one topic.** Long mixed messages get partially answered.

---

## 7. Bringing an idea or a proposal

Follow this order. Skipping a step usually means the idea gets sent back, not rejected.

1. **Write it down first.** The written structure comes before any live conversation.
2. The written proposal must contain:
   - the problem, stated in one paragraph
   - **at least two options** — one option is not a choice, it is a request for approval
     you have already assumed
   - the trade-offs of each option
   - your recommendation and why
   - **a text diagram** of the proposed shape
3. **A 30-minute walk-through is the default, not a requirement.** Skip it when the written
   proposal already answers everything. Ask for the time when it leaves an open question.
   The demo follows the written text; it never replaces it.
4. **Write the decision back** as an ADR in the repository, with a status.

Sergey is sensitive to ideas, methodology, and the reasoning behind them. Explain *why* it
matters, not only what it does.

---

## 8. Meetings

| Rule | Detail |
|---|---|
| **Agenda** | Written agenda, sent **at least 24 hours ahead**. No agenda, no meeting. |
| **Ceremonies** | Recurring ceremonies — standup, status, retro, planning — are **exempt from the agenda rule**. They already have a fixed shape. |
| **Length** | 30 minutes by default. Longer needs a reason in the agenda. |
| **Slot — complex** | **Morning, 08:00–12:00 CET.** Architecture, design, decisions, proposals, the 30-minute idea demo. |
| **Slot — light** | Afternoon is acceptable for standups, status and short syncs only. |
| **Outcome** | Written back into the thread or the ADR the same day, by the organiser. |
| **Calendar** | If it is in the calendar, it will happen. If it is only in a chat message, it probably will not. |

The calendar is the reliable channel for commitments. Use it for anything that has to occur.

---

## 9. Decisions, autonomy, and escalation

### Ask before you do it

- Architecture changes
- Contract changes — API shapes, schemas, message formats, anything another party depends on
- Public interfaces
- Technology choices that deviate from the defaults in section 14

### Just do it, then report

Everything inside those boundaries. Send a short written summary after the fact.

### Escalation

| Situation | Action |
|---|---|
| Blocked for **more than one working day** with no clear path | Escalate to Sergey |
| A short question you cannot answer yourself | **Ask immediately** — do not wait a day |
| A decision you are less than 80% sure about | Bring it as a proposal (section 7) |

The one-day rule is for problems you were meant to attempt yourself. It is not a reason to
sit silently on a question that takes thirty seconds to answer.

### Where decisions live

ADRs in the repository, with a status. Not in chat history, not in someone's memory.

---

## 10. Estimates and deadlines

Two separate things, and both are needed:

| Thing | Form |
|---|---|
| **Effort** | A T-shirt size: **S, M or L**. Not hours. |
| **Commitment** | A **proposed deadline** — a reasonable date you put forward yourself. |

- **Re-estimate at every checkpoint.** Precision comes from repeating the estimate as you
  learn, not from being clever at the start.
- A **slip** is one of two things: the size grew, or the proposed date is now at risk.
- Report a slip at the checkpoint where you first see it, not at the deadline. Do not let a
  size change quietly.
- When something will not fit, bring a **proposed scope cut** together with the news.

---

## 11. Code review and quality bar

These block a merge:

| Gate | Rule |
|---|---|
| **Tests first** | The failing test is written before the implementation. Test-after is not the same thing. |
| **All gates green** | Lint, types, tests, coverage. A red gate is not "almost done". |
| **Conventional commits** | Commit messages follow the conventional format. |
| **Review** | No merge to `main` without a review. |

---

## 12. Absence

Disappearing without a word is the one thing that genuinely damages trust here.

### Planned absence

| Requirement | Detail |
|---|---|
| **Notice** | At least **one working day** ahead |
| **Where** | The team channel, in writing |
| **Handover** | Name who covers your open items |
| **Calendar** | Block the time, so nobody schedules into it |

### Unplanned absence — illness, emergency, dead phone, no network

| Requirement | Detail |
|---|---|
| **During** | Send a short message when you are able to, from any channel that works |
| **After** | A written explanation within **24 hours of returning**: what happened, what slipped |
| **Judgement** | The explanation is not graded. Real emergencies happen. |

The distinction that matters is not *how good your reason was*. It is **whether you told
anyone**. Planned absence with no notice is a broken promise. Unplanned absence with a
message afterwards is just life.

---

## 13. Feedback and disagreement

- **Direct, in writing, with reasoning.** State the argument, not just the position.
- **Disagreement is expected.** Agreeing by default is worse than pushing back. Say "yes"
  only when you actually think it is true.
- **Criticism goes 1:1.** Praise goes in public.
- Written first, so it can be re-read and thought about. If the thread does not converge,
  move to a call — then write the outcome back.

---

## 14. Technology defaults

| Need | Default |
|---|---|
| Prototype, script, automation | **Python** |
| Web and desktop UI | **React** |
| Polished, high-performance network service | **Go** |

Deviating from these is a technology choice, which means it is an architecture decision,
which means section 9 applies: ask first, with two options and a diagram.

### Tech mindset

The defaults above are the *what*. This is the *why*, and it is what a proposal is judged
against.

| Principle | What it means in practice |
|---|---|
| **Cloud agnostic** | Cloud-native services are fine. Lock-in is not. Every unit should be movable to another provider without a rewrite. If a design depends on one provider's proprietary service, say so openly and state what the exit would cost. |
| **Zero trust** | Security perimeters are built on zero trust. Network location grants no trust. Every call is authenticated and authorised, including internal ones. |
| **Dynamic, modular components** | Highly modular, component-based architecture. Clear boundaries, replaceable parts, no component that cannot be swapped without touching its neighbours. |
| **Interfaces and governance first** | About 80% of his attention goes to interfaces, governance, methodology, and how the stack grows as the company scales. Bring him contract, boundary and strategy questions. Line-level implementation detail only if he asks for it. |
| **Prefer machines over meetings** | He deliberately wants *less* human communication, not more: fewer meetings, fewer status conversations, fewer approvals carried by voice. Anything that can be a written artefact, an automated check, or an AI loop should be exactly that. What survives — the genuinely hard thinking — is what the morning window is for. |
| **Use AI as much as possible** | AI is a default tool, not an exception that needs justifying. If a task can be done by AI, the question is why it is not. |
| **AI loop engineering** | A must-have, not a side experiment. Building repeatable AI loops — agents, skills, feedback loops — is treated as core engineering work. |
| **Simple idea, then simple implementation** | The idea has to be simple *before* any code is written. A complicated implementation of a simple idea is a warning sign. A simple implementation of a complicated idea is usually a lie. |

**When modularity and simplicity disagree:** modularity exists to serve migratability, not
cleverness. The simplest thing that can still be moved wins.

---

## 15. What counts as a breach

Missing a rule by accident is not a breach. These are:

- **Going silent** — no notice before, no message during, and no explanation within 24 hours
  of returning
- **No acknowledgement** after it was explicitly asked for
- **Sending urgent or critical work by email**
- **Merging to `main`** unreviewed, or with red gates
- **Shipping an architecture or contract change** without asking

**First time:** Sergey raises it with you 1:1, in writing. No audience.

**If it repeats:** it becomes a topic in your regular 1:1, and with your lead.

None of this is about punishment. Each item on the list makes someone else's work
unpredictable. That is the whole reason it is written down.
