---
name: working-with-sergey
description: Use when someone asks how to work with Sergey Bershadsky, when onboarding a new collaborator onto his team, when drafting or reviewing a message, announcement, meeting invite, proposal, estimate or pull request aimed at him, or when someone went silent, skipped an acknowledgement, sent something urgent by email, or booked a complex meeting into his afternoon.
---

# Working with Sergey

Sergey is a platform/backend architect in **CET**, working **08:00–18:00**. He is a visual, text-first thinker: written words and diagrams stick, spoken words do not. English is not his first language — plain English beats idiomatic English.

Full agreement: `references/norms.md`. Read it before answering anything not covered by the tables below.

## Two modes

| Mode | Trigger | Action |
|---|---|---|
| **Answer** | "How do I reach him?", "Can I book 09:30?", "Is email fine?" | Answer from the norms and name the rule you applied. |
| **Review** | Someone shows a draft DM, invite, announcement, proposal, estimate or PR | Run the checklist below. Report each violation with the rule it breaks and the fix. |

In Review mode, report violations even when the draft is otherwise good. Silence reads as approval.

## Channel ladder

| Priority | Channel | When |
|---|---|---|
| P0 business-critical | Messenger DM **or phone call** | Any hour, including the coding block. During unplanned absence he may be genuinely unreachable |
| Urgent | Messenger DM, or **a phone call if he gave you permission** | 08:00–18:00 CET |
| Must actually happen | Calendar event or tracked task | Scheduled |
| FYI / discussion | Written thread | Best effort |
| — | **Email** | No SLA. Treated as noise. Never use for anything that must be read. |

**Phone is an urgent channel for permitted callers.** Permission is given by Sergey personally — never assumed, never requested in a thread, and having his number is not the same as having it. A call carries attention, not content: whoever called writes the outcome into the thread the same day.

## Response and acknowledgement

| Item | Rule |
|---|---|
| P0 | Answered immediately, any hour |
| Urgent | Within 30 min in the morning (08:00–12:00); within 2 h in the afternoon |
| Normal | Within 4 working hours |
| Acknowledgement | Runs **both ways**: he reacts to what he reads, and expects the same within **4 working hours**. Where reactions do not exist (GitHub, Jira, email), a one-word `ack` reply. Ack means *read*, not *agreed*. Stated as an expectation — deliberately **not** a checklist item. |

**08:00–12:00 is his collaboration window.** Architecture, design, decisions, proposals and hard reviews belong here. This is the best time to reach him.

**12:00–18:00 is coding.** Only P0 makes him stop. Light syncs may be *scheduled* here; ad-hoc pings may not. An urgent message still gets an answer within 2 h — answering is not the same as being interrupted.

## Review checklist

Run every item. Each failure is a finding.

1. **Channel** — urgent content sent by email, or P0 sent to a thread instead of a DM/call?
2. **Timing** — a complex, architecture or decision meeting booked into the afternoon? A hard question saved for late afternoon that should have gone to the morning? (An urgent DM in the afternoon is *fine* — it gets a 2 h answer. Do not flag it.)
3. **Agenda** — a new or ad-hoc meeting invite without a written agenda sent ≥24h ahead? Longer than 30 min without justification? (Recurring ceremonies — standup, status, retro, planning — are exempt. Do not flag them.)
4. **Language** — idioms, slang, regional dialect, sarcasm, or long compound sentences? Rewrite in plain English.
5. **Form** — a decision or architecture explained only in prose, with no diagram or table?
6. **Proposal** — missing the problem statement, fewer than two options, no trade-offs, or no text diagram?
7. **Ack request** — announcement that needs confirmed readership but does not ask for a reaction?
8. **Autonomy** — announcing an architecture, contract or public-interface change as done, when it needed approval first?
9. **Estimate** — a T-shirt size with no proposed deadline, a deadline with no size, or a slip that was visible at a checkpoint and went unreported? (Both are required. A proposed date is *correct*, not a violation.)
10. **PR** — implementation before test, red gates, non-conventional commit, or a merge to `main` with no review?
11. **Absence** — going away without ≥1 working day of notice, handover, and a calendar block?
12. **Lock-in** — does the design tie a unit to one provider's proprietary service without naming the migration cost? Does it grant trust by network location instead of authenticating every call?
13. **Ceremony** — does it propose a *new* meeting, status report or manual approval where a written artefact or an AI loop would do the same job? (Existing recurring ceremonies are not findings.)

## Common mistakes

- Treating the phone call as the record. It is not. Write the outcome down.
- Reading "always available for business-critical" as "always available". Only P0 crosses into the afternoon coding block.
- Saving the hard conversation until the afternoon because the morning felt too early. It is the exact inversion of how he works.
- Sending a well-written email. It will be missed, and that is not a failure of attention.
- Asking for a decision with one option. One option is not a choice — it is a request for approval you already assumed — and it gets refused.
- Calling him because you have his number. Permission comes from Sergey personally; the number alone is not permission.
- Staying blocked for a day out of politeness. A 30-second question is asked immediately; the one-day rule is for problems you were meant to attempt yourself.
