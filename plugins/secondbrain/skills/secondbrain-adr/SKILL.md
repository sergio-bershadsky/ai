---
name: secondbrain-adr
description: |
  This skill should be used when the user asks to "create ADR", "document decision",
  "architecture decision", "add decision record", or mentions needing to record a
  technical decision with status tracking and category organization.
---

# Create Architecture Decision Record

Create numbered ADRs with category-based organization and status workflow.

## Prerequisites

Verify ADR entity is enabled in the secondbrain project:
1. Check for `.claude/data/adrs/records.yaml`
2. If not found, suggest running `secondbrain-init` with ADRs enabled

## Workflow

### Step 1: Gather Information

Collect from user or conversation context:

1. **Category** (determines number range):
   - `infrastructure` (0001-0999) — Architecture & infrastructure
   - `feature` (2000-2999) — Feature implementation
   - `process` (3000-3999) — Process & workflow

2. **Title** — Brief decision title (will be slugified for filename)

3. **Context** — What problem prompted this decision?

### Step 2: Determine ADR Number

1. Load `.claude/data/adrs/records.yaml`
2. Find highest number in selected category range
3. Increment to get next number
4. Format: `ADR-XXXX` (zero-padded)

**Number Ranges:**
```
infrastructure: 0001 - 0999
feature:        2000 - 2999
process:        3000 - 3999
```

### Step 3: Generate ADR Document

Use template from `${CLAUDE_PLUGIN_ROOT}/templates/entities/adr/TEMPLATE.md`:

**Filename:** `docs/adrs/ADR-XXXX-<title-slug>.md`

**Frontmatter:**
```yaml
---
id: ADR-XXXX
status: draft
date_created: YYYY-MM-DD
date_updated: YYYY-MM-DD
author: <author>
category: <category>
---
```

### Step 4: Update Records

Add entry to `.claude/data/adrs/records.yaml`:

```yaml
- number: XXXX
  title: "<title>"
  status: draft
  category: <category>
  created: YYYY-MM-DD
  file: docs/adrs/ADR-XXXX-<slug>.md
  author: <author>
```

Update `last_number` if this is the new highest.

### Step 5: Sidebar Note

**DO NOT manually add ADRs to VitePress sidebar.**

ADRs are automatically listed via the `EntityTable` component on `docs/adrs/index.md`, which reads from `.claude/data/adrs/records.yaml`. No sidebar modification needed.

### Step 6: Confirm Creation

```
## ADR Created

**ID:** ADR-0012
**Title:** Kubernetes Migration Strategy
**Category:** infrastructure
**Status:** draft
**File:** docs/adrs/ADR-0012-kubernetes-migration-strategy.md

### Next Steps
1. Edit the ADR to add context, options, and decision
2. Change status to 'proposed' when ready for review
3. Use /secondbrain-adr-status to update status

### Status Workflow
draft → proposed → admitted → applied → implemented → tested
```

## Status Workflow

```
Draft → Proposed → Admitted → Applied → Implemented → Tested
                          ↘ Rejected
                          ↘ Canceled
```

| Status | Description |
|--------|-------------|
| draft | Initial creation, under development |
| proposed | Ready for review |
| admitted | Approved, pending implementation |
| applied | Implementation started |
| implemented | Implementation complete |
| tested | Verified in production |
| rejected | Not approved |
| canceled | Abandoned |

## Additional Resources

- **`references/adr-template.md`** — Full ADR template
