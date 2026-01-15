# Note Formats Reference

Comprehensive guide to note types and formatting patterns.

## Note Categories

### Knowledge Notes

Capture learned information for future reference.

**Template:**
```markdown
---
id: 2026-01-15-topic-slug
title: Topic Title
created: 2026-01-15
tags: [category, technology]
status: active
---

# Topic Title

## Summary

Brief overview of the key concept.

## Key Points

- Point 1
- Point 2
- Point 3

## Details

In-depth explanation...

## Examples

```code
// Example implementation
```

## References

- [External Resource](url)
- Related: [[other-note]]
```

### Meeting Notes

Capture discussions and outcomes.

**Template:**
```markdown
---
id: 2026-01-15-meeting-topic
title: Meeting Topic
created: 2026-01-15
tags: [meeting, team]
status: active
---

# Meeting: Topic

**Date:** 2026-01-15
**Attendees:** Alice, Bob, Charlie

## Agenda

1. Item 1
2. Item 2

## Discussion

### Topic 1
- Discussion points...

### Topic 2
- Discussion points...

## Decisions

- Decision 1
- Decision 2

## Action Items

- [ ] Task 1 — @alice
- [ ] Task 2 — @bob

## Next Steps

Follow-up items...
```

### Research Notes

Document research findings.

**Template:**
```markdown
---
id: 2026-01-15-research-topic
title: Research Topic
created: 2026-01-15
tags: [research, domain]
status: active
---

# Research: Topic

## Objective

What are we trying to learn?

## Methodology

How we gathered information.

## Findings

### Finding 1

Details...

### Finding 2

Details...

## Analysis

Interpretation of findings.

## Conclusions

Summary of insights.

## Sources

1. Source 1
2. Source 2
```

### How-To Notes

Step-by-step procedures.

**Template:**
```markdown
---
id: 2026-01-15-how-to-topic
title: How to Topic
created: 2026-01-15
tags: [howto, procedure]
status: active
---

# How to Topic

## Prerequisites

- Requirement 1
- Requirement 2

## Steps

### Step 1: First Action

Description of what to do.

```bash
# Command example
```

### Step 2: Second Action

Description...

### Step 3: Third Action

Description...

## Verification

How to confirm success.

## Troubleshooting

### Issue 1
Solution...

### Issue 2
Solution...
```

### Quick Notes

Brief captures for later processing.

**Template:**
```markdown
---
id: 2026-01-15-quick-thought
title: Quick Thought
created: 2026-01-15
tags: [quick, inbox]
status: active
---

# Quick Thought

Brief capture of an idea or observation.

---
*TODO: Process this note into proper format.*
```

## Tag Conventions

### Category Tags

| Tag | Use For |
|-----|---------|
| `howto` | Step-by-step procedures |
| `reference` | Information to look up |
| `research` | Research and analysis |
| `meeting` | Meeting notes |
| `quick` | Unprocessed captures |

### Technology Tags

| Tag | Use For |
|-----|---------|
| `python` | Python-related |
| `kubernetes` | K8s topics |
| `database` | Database topics |
| `api` | API-related |

### Domain Tags

| Tag | Use For |
|-----|---------|
| `architecture` | System design |
| `security` | Security topics |
| `performance` | Optimization |
| `devops` | Operations |

## Status Values

| Status | Meaning |
|--------|---------|
| `active` | Current, relevant note |
| `archived` | No longer current |

## Linking Patterns

### Internal Links

```markdown
See [[note-id]] for details.
Related: [[2026-01-15-related-note]]
```

### External Links

```markdown
[Link Text](https://example.com)
```

### ADR References

```markdown
See [ADR-0012](../adrs/ADR-0012-decision.md).
```

## Tips

1. **Date prefix IDs** — Makes notes sortable
2. **Tag consistently** — Reuse existing tags
3. **Link liberally** — Connect related notes
4. **Review regularly** — Archive stale notes
5. **Process quick notes** — Don't let inbox grow
