# Task Workflows Reference

Comprehensive guide to task management patterns and workflows.

## Task Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  todo ──────► in_progress ──────► done                     │
│                    │                                        │
│                    ▼                                        │
│               blocked ──────► in_progress                   │
│                    │                                        │
│                    ▼                                        │
│               canceled                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Status Definitions

| Status | Description | Next Actions |
|--------|-------------|--------------|
| `todo` | Not started | Start work, cancel |
| `in_progress` | Actively working | Complete, block, cancel |
| `blocked` | Waiting on dependency | Unblock, cancel |
| `done` | Completed successfully | Archive |
| `canceled` | Won't be done | — |

## Priority Guidelines

### Critical

**Use when:**
- Production is down
- Security vulnerability
- Blocking multiple team members
- Deadline is imminent

**Expected response:** Same day

### High

**Use when:**
- Important feature work
- Significant bug affecting users
- Blocking one team member
- Due within the week

**Expected response:** Within 2-3 days

### Medium

**Use when:**
- Normal feature work
- Non-critical bugs
- Improvements and enhancements
- Due within 2 weeks

**Expected response:** Within 1 week

### Low

**Use when:**
- Nice-to-have features
- Cosmetic issues
- Technical debt
- No specific deadline

**Expected response:** When capacity allows

## Task Types

### Feature Tasks

Implement new functionality.

```markdown
---
id: TASK-0042
title: Implement user authentication
status: todo
priority: high
created: 2026-01-15
due_date: 2026-01-31
assignee: sergey
tags: [feature, auth]
---

# TASK-0042: Implement user authentication

## Description

Add OAuth2 login flow for the application.

## Acceptance Criteria

- [ ] OAuth2 provider configuration
- [ ] Login redirect flow
- [ ] Token storage
- [ ] Logout functionality

## Technical Notes

Use existing auth library...
```

### Bug Tasks

Fix defects.

```markdown
---
id: TASK-0043
title: Fix login redirect loop
status: in_progress
priority: critical
created: 2026-01-15
assignee: sergey
tags: [bug, auth]
---

# TASK-0043: Fix login redirect loop

## Problem

Users stuck in redirect loop when session expires.

## Steps to Reproduce

1. Login
2. Wait for session timeout
3. Click any link

## Root Cause

[To be determined]

## Solution

[Document fix here]
```

### Chore Tasks

Maintenance and housekeeping.

```markdown
---
id: TASK-0044
title: Update dependencies
status: todo
priority: low
created: 2026-01-15
tags: [chore, maintenance]
---

# TASK-0044: Update dependencies

## Description

Monthly dependency update.

## Tasks

- [ ] npm audit
- [ ] Update minor versions
- [ ] Test suite passes
- [ ] Deploy to staging
```

## Estimation Guidelines

### T-Shirt Sizing

| Size | Time | Complexity |
|------|------|------------|
| XS | < 2 hours | Trivial change |
| S | 2-4 hours | Simple, well-defined |
| M | 1-2 days | Moderate complexity |
| L | 3-5 days | Complex, some unknowns |
| XL | 1-2 weeks | Very complex, research needed |

### Story Points (Fibonacci)

| Points | Meaning |
|--------|---------|
| 1 | Trivial |
| 2 | Small |
| 3 | Medium |
| 5 | Large |
| 8 | Very large |
| 13 | Epic-level, should split |

## Workflow Patterns

### Daily Review

1. Review in_progress tasks
2. Update status if completed
3. Identify blockers
4. Prioritize todo queue

### Weekly Planning

1. Review completed tasks
2. Archive done tasks
3. Review upcoming due dates
4. Reprioritize as needed

### Task Breakdown

For large tasks:

1. Create parent task
2. Create subtasks with references
3. Track completion in parent

```yaml
- id: TASK-0050
  title: "Implement search feature"
  subtasks:
    - TASK-0051
    - TASK-0052
    - TASK-0053
```

## Blocking and Dependencies

### Marking Blocked

```yaml
status: blocked
blocked_by: "Waiting for API specification"
blocked_since: 2026-01-15
```

### Unblocking

1. Resolve dependency
2. Update status to `in_progress`
3. Clear blocked fields

### Dependencies

```yaml
depends_on:
  - TASK-0030
  - TASK-0031
blocks:
  - TASK-0055
```

## Tags Best Practices

### Standard Tags

| Tag | Use For |
|-----|---------|
| `feature` | New functionality |
| `bug` | Defect fix |
| `chore` | Maintenance |
| `docs` | Documentation |
| `test` | Testing |
| `refactor` | Code improvement |

### Component Tags

| Tag | Use For |
|-----|---------|
| `frontend` | UI work |
| `backend` | API work |
| `database` | Data layer |
| `infra` | Infrastructure |

## Tips

1. **Start with verb** — "Implement", "Fix", "Update"
2. **Be specific** — Include context in title
3. **Set due dates** — Even estimates help
4. **Update promptly** — Keep status current
5. **Split large tasks** — Break into subtasks
6. **Link context** — Reference ADRs, notes, PRs
