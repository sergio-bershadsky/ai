---
name: secondbrain-discussion
description: |
  This skill should be used when the user asks to "document discussion", "save meeting notes",
  "record conversation", "capture meeting", or mentions needing to document team discussions
  with participants, decisions, and action items.
---

# Document Discussion

Capture team discussions with participants, decisions, and action items.

## Prerequisites

Verify Discussions entity is enabled:
1. Check for `.claude/data/discussions/schema.yaml`
2. If not found, suggest enabling discussions via `secondbrain-init`

## Workflow

### Step 1: Gather Information

Collect from user or conversation context:

1. **Participant(s)** — Who was in the discussion
2. **Topic** — Main subject discussed
3. **Source** — manual, meeting, slack
4. **Key Points** — Discussion content
5. **Decisions** — What was decided
6. **Action Items** — Follow-up tasks

### Step 2: Generate Discussion File

**Filename format:** `docs/discussions/YYYY-MM-DD-<participant>-<topic-slug>.md`

Example: `docs/discussions/2026-01-15-sergey-kubernetes-migration.md`

### Step 3: Create Discussion Document

```markdown
---
date: 2026-01-15
participants:
  - Sergey Bershadsky
  - Kate Angelopoulos
topic: Kubernetes Migration Planning
status: documented
source: meeting
tags: [kubernetes, infrastructure, planning]
---

# Kubernetes Migration Planning

**Date:** 2026-01-15
**Participants:** Sergey Bershadsky, Kate Angelopoulos

## Context

Why did this discussion happen?

## Discussion Points

### Migration Timeline

**Discussion:**
- Discussed phased approach
- Agreed on staging first

**Outcome:**
Start with staging environment by end of Q1

### Resource Requirements

**Discussion:**
- Node sizing
- Cost implications

**Outcome:**
Will use 3 node cluster initially

## Decisions Made

| Decision | Owner | Deadline |
|----------|-------|----------|
| Set up staging cluster | Sergey | 2026-01-31 |
| Document runbook | Kate | 2026-02-15 |

## Action Items

- [ ] Create staging environment — @sergey
- [ ] Write migration runbook — @kate
- [ ] Schedule follow-up review — @sergey

## Open Questions

- What's the rollback strategy?
- How do we handle stateful services?

## Follow-up

- Next discussion scheduled for: 2026-01-22
- Related topics to explore: CI/CD pipeline changes
```

### Step 4: Update Records

Add to monthly file `.claude/data/discussions/YYYY-MM.yaml`:

```yaml
- date: 2026-01-15
  member: sergey
  topic: Kubernetes Migration Planning
  file: docs/discussions/2026-01-15-sergey-kubernetes-migration.md
  source: meeting
  participants:
    - Sergey Bershadsky
    - Kate Angelopoulos
```

### Step 5: Confirm Creation

```
## Discussion Documented

**Date:** 2026-01-15
**Topic:** Kubernetes Migration Planning
**Participants:** Sergey Bershadsky, Kate Angelopoulos
**Source:** meeting
**File:** docs/discussions/2026-01-15-sergey-kubernetes-migration.md

### Summary
- 2 decisions recorded
- 3 action items created
- 2 open questions noted

### Next Steps
- Follow up on action items
- Address open questions in next discussion
```

## Monthly Partitioning

Discussions are partitioned by month:
- `discussions/2025-12.yaml` — December 2025
- `discussions/2026-01.yaml` — January 2026

Past months become immutable, preserving history.

## Sources

| Source | Description |
|--------|-------------|
| manual | Hand-documented discussion |
| meeting | From a scheduled meeting |
| slack | From Slack conversation |

## Tips

1. **Capture decisions explicitly** — Use the table format
2. **Create action items** — Every decision should have an owner
3. **Note open questions** — Track what needs follow-up
4. **Link to related content** — Reference ADRs, notes, etc.
5. **Document context** — Future readers need to understand "why"
