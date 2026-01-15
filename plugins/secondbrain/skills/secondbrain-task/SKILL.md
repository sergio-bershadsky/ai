---
name: secondbrain-task
description: |
  This skill should be used when the user asks to "create task", "add todo",
  "track action item", "create ticket", "new task", "remind me to", "need to do",
  "add to backlog", or mentions needing to track work items with priority and status
  in their secondbrain.
---

# Create Task

Create tracked tasks with priority, due dates, and status workflow.

## Prerequisites

Verify Tasks entity is enabled:
1. Check for `.claude/data/tasks/records.yaml`
2. If not found, suggest enabling tasks via `secondbrain-init` or `secondbrain-entity`

## Workflow

### Step 1: Gather Information

Collect from user or conversation context:

1. **Title** — Brief task description
2. **Description** (optional) — Detailed description
3. **Priority** — low, medium, high, critical
4. **Due Date** (optional) — Target completion date
5. **Assignee** (optional) — Person responsible

### Step 2: Generate Task Number

Sequential ID format: `TASK-XXXX` (zero-padded)

1. Load `.claude/data/tasks/records.yaml`
2. Get `last_number`, increment by 1
3. Format as `TASK-0042`

### Step 3: Create Task Record

Add to `.claude/data/tasks/records.yaml`:

```yaml
- number: 42
  title: "Implement user authentication"
  description: "Add OAuth2 login flow"
  status: todo
  priority: high
  created: 2026-01-15
  due_date: 2026-01-31
  assignee: sergey
  tags: [auth, security]
```

Update `last_number: 42`

### Step 4: Create Task Document (Optional)

For complex tasks, create a document:

**Filename:** `docs/tasks/TASK-0042-implement-authentication.md`

```markdown
---
id: TASK-0042
title: Implement user authentication
status: todo
priority: high
created: 2026-01-15
due_date: 2026-01-31
assignee: sergey
tags: [auth, security]
---

# TASK-0042: Implement user authentication

## Description

Add OAuth2 login flow for the application.

## Acceptance Criteria

- [ ] OAuth2 provider configuration
- [ ] Login redirect flow
- [ ] Token storage
- [ ] Logout functionality

## Notes

Implementation notes here...
```

### Step 5: Confirm Creation

```
## Task Created

**ID:** TASK-0042
**Title:** Implement user authentication
**Priority:** high
**Due:** 2026-01-31
**Status:** todo

### Next Steps
- Update status as work progresses
- Add notes to the task document
- Mark complete when done
```

## Status Workflow

```
todo → in_progress → done
            ↓
         blocked → in_progress
            ↓
        canceled
```

| Status | Description |
|--------|-------------|
| todo | Not started |
| in_progress | Work in progress |
| blocked | Waiting on dependency |
| done | Completed |
| canceled | Won't be done |

## Priority Levels

| Priority | Use When |
|----------|----------|
| critical | Urgent, blocks other work |
| high | Important, should be done soon |
| medium | Normal priority |
| low | Nice to have, no rush |

## Additional Resources

- **`references/task-workflows.md`** — Detailed task lifecycle, priority guidelines, and workflow patterns

## Tips

1. **Keep titles actionable** — Start with a verb (Implement, Fix, Add)
2. **Set realistic due dates** — Better to underpromise
3. **Update status promptly** — Keeps the backlog accurate
4. **Use tags** — Helps filter and group related tasks
5. **Add acceptance criteria** — Makes "done" unambiguous
