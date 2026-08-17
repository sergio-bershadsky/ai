# Working With Sergey Plugin

A team working agreement, packaged as a skill so Claude can apply it rather than just store it.

Most working agreements die in a wiki nobody opens. This one loads into Claude's context, so it
can answer "how do I work with Sergey?" for a new teammate, and review a draft message, meeting
invite, proposal or PR **before** it reaches him.

## Installation

```bash
/plugin install working-with-sergey@bershadsky-claude-tools
```

## Two modes

| Mode | Trigger | Result |
|---|---|---|
| **Answer** | "Can I book him at 09:30?", "Is email fine for this?" | An answer, with the rule it came from |
| **Review** | You paste a draft DM, invite, announcement, proposal or PR | A list of findings, each with the rule it breaks and the fix |

## The agreement

Fifteen sections, every rule written so it can be checked:

| Section | Covers |
|---|---|
| Channels and priority | P0 / urgent / scheduled / FYI ladder. Phone is an urgent channel for permitted callers; email carries no SLA |
| Response times | 30 minutes in the morning, 2 hours in the afternoon, 4 working hours for normal |
| Acknowledgement | Emoji reaction within 4 working hours, `ack` reply where reactions do not exist |
| Daily rhythm | 08:00–12:00 CET collaboration, 12:00–18:00 coding — only P0 interrupts |
| Language and format | Plain English for anything read now; richer English fine in documents read later |
| Proposals | Problem, two or more options, trade-offs, recommendation, text diagram |
| Meetings | Agenda 24h ahead, 30 minutes by default, recurring ceremonies exempt |
| Autonomy and escalation | Architecture, contracts and public interfaces need approval first |
| Estimates | T-shirt size for effort plus a proposed deadline |
| Quality bar | Test first, gates green, conventional commits, no unreviewed merge to `main` |
| Absence | One working day of notice, handover, calendar block |
| Feedback | Direct, written, with reasoning. Criticism 1:1 |
| Technology | Python, React, Go — plus the mindset a proposal is judged against |
| Breaches | What counts, and what happens |

## Review checklist

Thirteen checks run against any draft: channel, timing, agenda, language, form, proposal
completeness, acknowledgement request, autonomy boundary, estimate shape, PR gates, absence
notice, provider lock-in and zero trust, and ceremony that could be an artefact instead.

## Using it as a template

The structure is reusable even though the content is not. Fork it, replace the rules with your
own, and keep two properties that make it work as a skill rather than a document:

1. **Every rule is checkable.** "Respond quickly" cannot be enforced. "Within 30 minutes,
   08:00–12:00 CET" can.
2. **The `description` in `SKILL.md` lists triggers only.** If it summarises the workflow,
   Claude follows the summary and skips the body.
