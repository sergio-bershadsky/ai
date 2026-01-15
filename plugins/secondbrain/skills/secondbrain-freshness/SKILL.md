---
name: secondbrain-freshness
description: |
  This skill should be used when the user asks for "freshness check", "freshness report",
  "what needs attention", "stale items", "review backlog", or mentions wanting to see
  what secondbrain content needs review or updating.
---

# Freshness Report

Generate a comprehensive freshness report for all secondbrain entities.

## Prerequisites

Verify secondbrain is initialized:
1. Check for `.claude/data/config.yaml`
2. If not found, indicate no secondbrain project found

## Workflow

### Step 1: Load Configuration

Read `.claude/data/config.yaml` to get:
- All enabled entities
- Freshness thresholds per entity
- Monthly partitioning settings

### Step 2: Analyze Each Entity

For each enabled entity:

1. Load all records
2. Check date fields (created, date, date_updated)
3. Compare against freshness threshold
4. Categorize by staleness level:
   - **Critical** (2x threshold): Needs immediate attention
   - **Stale** (1x threshold): Should be reviewed
   - **Warning** (0.75x threshold): Approaching staleness

### Step 3: Generate Report

Format by entity and urgency:

```
## Freshness Report

Generated: 2026-01-15 10:30

### Summary

| Entity | Critical | Stale | Warning | OK |
|--------|----------|-------|---------|-----|
| ADRs | 2 | 5 | 3 | 12 |
| Tasks | 0 | 8 | 4 | 15 |
| Notes | 1 | 3 | 6 | 25 |
| Discussions | 0 | 2 | 1 | 10 |

**Total needing attention:** 30 items

---

### Critical (Needs Immediate Attention)

#### ADRs (2 items)

| ID | Title | Status | Age |
|----|-------|--------|-----|
| ADR-0003 | API Gateway Selection | proposed | 95 days |
| ADR-0007 | Database Migration | draft | 78 days |

#### Notes (1 item)

| ID | Title | Age |
|----|-------|-----|
| 2025-10-01-legacy-system | Legacy System Overview | 106 days |

---

### Stale (Should Review)

#### Tasks (8 items)

| ID | Title | Status | Priority | Age |
|----|-------|--------|----------|-----|
| TASK-0012 | Update documentation | in_progress | medium | 45 days |
| TASK-0015 | Fix login bug | todo | high | 42 days |
...

---

### Recommended Actions

1. **ADR-0003:** 95 days in "proposed" status
   - Action: Review and move to admitted/rejected

2. **ADR-0007:** 78 days in "draft" status
   - Action: Complete draft or cancel

3. **TASK-0012:** 45 days in progress
   - Action: Check if blocked, update status

4. **2025-10-01-legacy-system:** 106 days old note
   - Action: Archive or update content
```

### Step 4: Offer Remediation

For each critical/stale item, offer specific actions:

- **Draft ADRs:** Complete or cancel
- **Proposed ADRs:** Review and decide
- **In-progress tasks:** Check if blocked
- **Old notes:** Archive or refresh
- **Stale discussions:** Mark resolved or schedule follow-up

### Step 5: Update Last Check

Update `.claude/data/config.yaml`:

```yaml
meta:
  last_freshness_check: 2026-01-15T10:30:00
```

## Staleness Thresholds

Default thresholds (configurable per entity):

| Entity | Default | Critical |
|--------|---------|----------|
| ADRs | 30 days | 60 days |
| Tasks | 14 days | 28 days |
| Notes | 30 days | 60 days |
| Discussions | 7 days | 14 days |

## Status Exceptions

Skip items with terminal statuses:

- **ADRs:** implemented, tested, rejected, canceled
- **Tasks:** done, completed, canceled
- **Notes:** archived
- **Discussions:** archived

## Output Formats

### Summary Only

```
## Freshness Summary

- **Critical:** 3 items need immediate attention
- **Stale:** 18 items should be reviewed
- **Warning:** 13 items approaching staleness

Run with `--detailed` for full breakdown.
```

### Full Report

Complete breakdown with tables and recommendations (default).

### JSON Export

```json
{
  "generated": "2026-01-15T10:30:00",
  "summary": {
    "critical": 3,
    "stale": 18,
    "warning": 13,
    "ok": 62
  },
  "by_entity": {
    "adrs": { "critical": 2, "stale": 5, ... },
    ...
  },
  "items": [...]
}
```

## Tips

1. **Run weekly** — Set calendar reminder for freshness reviews
2. **Address critical first** — Focus on oldest items
3. **Archive liberally** — Better to archive than ignore
4. **Update thresholds** — Adjust based on your workflow pace
5. **Check after sprints** — Good time to clean up stale items
