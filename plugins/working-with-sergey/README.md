# working-with-sergey

A team working agreement, packaged as a skill so Claude can *apply* it rather than just store it.

Most working agreements die in a wiki nobody opens. This one loads into Claude's context, so
it can answer "how do I work with Sergey?" for a new teammate and review a draft message,
meeting invite, proposal or PR **before** it reaches him.

## What it does

| Mode | Trigger | Result |
|---|---|---|
| **Answer** | "Can I book him at 09:30?", "Is email fine for this?" | An answer, with the rule it came from |
| **Review** | You paste a draft DM, invite, announcement, proposal or PR | A list of violations, each with the rule it breaks and the fix |

## Install

```
/plugin marketplace add sergio-bershadsky/ai
/plugin install working-with-sergey@bershadsky-claude-tools
```

## What is in the agreement

Channel and priority ladder (including phone as an urgent channel for permitted callers, and
why a call never becomes the record) · response SLAs · the emoji acknowledgement protocol and
its fallback for
reaction-less tools · a morning collaboration window and a protected afternoon coding
block · plain-English and diagram-first
communication · how to bring an idea · meeting gates · the autonomy boundary and escalation
trigger · T-shirt estimates · the quality bar that blocks a merge · planned and unplanned
absence · feedback norms · technology defaults and the tech mindset a proposal is judged
against (cloud-agnostic and migratable, zero trust, modular components, interfaces and
governance first, machines over meetings, AI-first with AI loop engineering, simple idea
before simple implementation).

Full text: [`skills/working-with-sergey/references/norms.md`](skills/working-with-sergey/references/norms.md).

## Using it as a template

The structure is reusable even though the content is not. Fork it, replace the rules in
`norms.md` with your own, and keep two properties that make it work as a skill rather than a
document:

1. **Every rule is checkable.** "Respond quickly" cannot be enforced. "Within 30 minutes,
   08:00–12:00 CET" can.
2. **The `description` in `SKILL.md` lists triggers only.** If it summarises the workflow,
   Claude follows the summary and skips the body.

## Licence

Unlicense.
