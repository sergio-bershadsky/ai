# ADR Template Reference

Complete template for Architecture Decision Records.

## Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | ADR identifier (ADR-XXXX) |
| status | enum | Yes | Current status |
| date_created | date | Yes | Creation date |
| date_updated | date | Yes | Last update date |
| author | string | Yes | Primary author |
| category | enum | No | infrastructure/feature/process |
| reviewers | array | No | List of reviewers |
| supersedes | integer | No | ADR number this supersedes |
| superseded_by | integer | No | ADR number that supersedes this |

## Status Values

- `draft` — Under development
- `proposed` — Ready for review
- `admitted` — Approved
- `applied` — Implementation started
- `implemented` — Implementation complete
- `tested` — Verified
- `rejected` — Not approved
- `canceled` — Abandoned

## Full Template

```markdown
---
id: ADR-{{number}}
status: draft
date_created: {{date}}
date_updated: {{date}}
author: {{author}}
category: {{category}}
reviewers: []
supersedes: null
superseded_by: null
---

# ADR-{{number}}: {{title}}

## Status

**Draft** — Under consideration

## Context

What is the issue that we're seeing that is motivating this decision or change?

- Background information
- Current pain points
- Business drivers
- Technical constraints

## Decision

What is the change that we're proposing and/or doing?

Be specific and actionable. Include:
- The approach chosen
- Key implementation details
- Timeline if relevant

## Options Considered

### Option 1: [Name]

**Description:**

**Pros:**
-

**Cons:**
-

**Effort:** Low/Medium/High

### Option 2: [Name]

**Description:**

**Pros:**
-

**Cons:**
-

**Effort:** Low/Medium/High

### Option 3: [Name] (if applicable)

...

## Consequences

What becomes easier or more difficult to do because of this change?

### Positive

-

### Negative

-

### Neutral

-

### Risks

-

## Implementation

### Phase 1
- [ ] Task 1
- [ ] Task 2

### Phase 2
- [ ] Task 3
- [ ] Task 4

## Related

- [ADR-XXXX](./ADR-XXXX-related-decision.md) — Related decision
- [Issue #123](https://github.com/org/repo/issues/123) — Related issue
- [Documentation](../guides/related-guide.md) — Related docs

## Notes

Additional context, meeting notes, or implementation details that don't fit elsewhere.

## Changelog

| Date | Author | Change |
|------|--------|--------|
| {{date}} | {{author}} | Initial draft |
```

## Tips

1. **Keep it concise** — Decisions should be understandable in 5 minutes
2. **Focus on "why"** — The reasoning is more valuable than the decision
3. **Document alternatives** — Show what was considered and rejected
4. **Link related content** — Connect to issues, docs, and other ADRs
5. **Update status** — Keep the status current as implementation progresses
