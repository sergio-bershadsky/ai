# Predefined Entity Schemas

Reference documentation for built-in entity types and their schemas.

## ADRs (Architecture Decision Records)

### Schema

```yaml
type: object
required:
  - last_number
  - records
properties:
  last_number:
    type: integer
    description: Highest ADR number across all categories
  records:
    type: array
    items:
      type: object
      required:
        - number
        - title
        - status
        - created
        - file
      properties:
        number:
          type: integer
        title:
          type: string
        status:
          type: string
          enum:
            - draft
            - proposed
            - admitted
            - applied
            - implemented
            - tested
            - rejected
            - canceled
        category:
          type: string
          enum:
            - infrastructure
            - feature
            - process
        created:
          type: string
          format: date
        updated:
          type: string
          format: date
        file:
          type: string
        author:
          type: string
```

### Number Ranges

| Category | Range | Description |
|----------|-------|-------------|
| infrastructure | 0001-0999 | Architecture & infrastructure decisions |
| feature | 2000-2999 | Feature implementation decisions |
| process | 3000-3999 | Process & workflow decisions |

### Status Workflow

```
Draft → Proposed → Admitted → Applied → Implemented → Tested
                          ↘ Rejected
                          ↘ Canceled
```

---

## Discussions

### Schema

```yaml
type: array
items:
  type: object
  required:
    - date
    - member
    - topic
    - file
  properties:
    date:
      type: string
      format: date
    member:
      type: string
      description: Team member identifier
    topic:
      type: string
    file:
      type: string
      description: Path to discussion markdown
    source:
      type: string
      enum:
        - manual
        - meeting
        - slack
    participants:
      type: array
      items:
        type: string
```

### File Naming

`YYYY-MM-DD-<participant>-<topic-slug>.md`

### Monthly Partitioning

Discussion records are partitioned by month:
- `discussions/2025-12.yaml`
- `discussions/2026-01.yaml`

Past months become immutable after the month ends.

---

## Notes

### Schema

```yaml
type: object
required:
  - records
properties:
  last_number:
    type: integer
  records:
    type: array
    items:
      type: object
      required:
        - id
        - title
        - created
        - file
      properties:
        id:
          type: string
          description: Date-based ID (YYYY-MM-DD-slug)
        title:
          type: string
        created:
          type: string
          format: date
        updated:
          type: string
          format: date
        file:
          type: string
        tags:
          type: array
          items:
            type: string
        status:
          type: string
          enum:
            - active
            - archived
```

### File Naming

`YYYY-MM-DD-<title-slug>.md`

---

## Tasks

### Schema

```yaml
type: object
required:
  - last_number
  - records
properties:
  last_number:
    type: integer
    description: Highest task number
  records:
    type: array
    items:
      type: object
      required:
        - number
        - title
        - status
        - created
      properties:
        number:
          type: integer
        title:
          type: string
        description:
          type: string
        status:
          type: string
          enum:
            - todo
            - in_progress
            - blocked
            - done
            - canceled
        priority:
          type: string
          enum:
            - low
            - medium
            - high
            - critical
        created:
          type: string
          format: date
        due_date:
          type: string
          format: date
        completed_date:
          type: string
          format: date
        assignee:
          type: string
        tags:
          type: array
          items:
            type: string
```

### ID Format

`TASK-XXXX` (sequential, zero-padded)

---

## Custom Entity Template

When creating custom entities, use this schema template:

```yaml
type: object
required:
  - records
properties:
  last_number:
    type: integer
    description: Optional - for numbered entities
  records:
    type: array
    items:
      type: object
      required:
        - id
        - title
        - created
        - file
      properties:
        id:
          type: string
        title:
          type: string
        created:
          type: string
          format: date
        file:
          type: string
        # Add custom properties below
```

## Validation

All schemas use JSON Schema draft-07 format. Validation is performed:

1. **On load** — Before returning data to caller
2. **On save** — Before writing to file
3. **Graceful degradation** — Continues without validation if jsonschema not installed
