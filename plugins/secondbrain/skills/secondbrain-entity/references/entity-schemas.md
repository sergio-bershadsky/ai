# Entity Schema Reference

Complete guide to designing entity schemas for secondbrain.

## Schema Structure

Every entity has a schema file at `.claude/data/<entity>/schema.yaml`:

```yaml
$schema: "http://json-schema.org/draft-07/schema#"
title: Entity Name
type: object
required: [records]
properties:
  last_number:
    type: integer
    description: Last assigned sequential number
    default: 0
  records:
    type: array
    items:
      $ref: "#/definitions/record"

definitions:
  record:
    type: object
    required: [id, title, created, file]
    properties:
      # Define all fields here
```

## Common Field Patterns

### Identity Fields

```yaml
id:
  type: string
  description: Unique identifier
  pattern: "^[A-Z]+-\\d{4}$"  # For PREFIX-0001 format

title:
  type: string
  description: Display title
  minLength: 1
  maxLength: 200
```

### Temporal Fields

```yaml
created:
  type: string
  format: date
  description: Creation date

updated:
  type: string
  format: date
  description: Last modification date

due_date:
  type: string
  format: date
  description: Target completion date
```

### Status Fields

```yaml
status:
  type: string
  enum: [draft, active, archived, deleted]
  default: draft
  description: Current lifecycle status

priority:
  type: string
  enum: [low, medium, high, critical]
  default: medium
```

### Reference Fields

```yaml
file:
  type: string
  description: Path to markdown document

author:
  type: string
  description: Creator username

assignee:
  type: string
  description: Responsible person

tags:
  type: array
  items:
    type: string
  description: Categorization tags
```

### Relationship Fields

```yaml
parent:
  type: string
  description: Parent record ID

children:
  type: array
  items:
    type: string
  description: Child record IDs

related:
  type: array
  items:
    type: string
  description: Related record IDs
```

## Example Entity Schemas

### Contact Entity

```yaml
$schema: "http://json-schema.org/draft-07/schema#"
title: Contacts
type: object
required: [records]
properties:
  last_number:
    type: integer
    default: 0
  records:
    type: array
    items:
      type: object
      required: [id, name, created, file]
      properties:
        id:
          type: string
          pattern: "^CONTACT-\\d{4}$"
        name:
          type: string
        email:
          type: string
          format: email
        company:
          type: string
        role:
          type: string
        created:
          type: string
          format: date
        last_contact:
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
          enum: [active, inactive, archived]
          default: active
```

### Project Entity

```yaml
$schema: "http://json-schema.org/draft-07/schema#"
title: Projects
type: object
required: [records]
properties:
  last_number:
    type: integer
    default: 0
  records:
    type: array
    items:
      type: object
      required: [id, name, created, file, status]
      properties:
        id:
          type: string
          pattern: "^PROJ-\\d{4}$"
        name:
          type: string
        description:
          type: string
        created:
          type: string
          format: date
        start_date:
          type: string
          format: date
        end_date:
          type: string
          format: date
        file:
          type: string
        owner:
          type: string
        team:
          type: array
          items:
            type: string
        status:
          type: string
          enum: [planning, active, on_hold, completed, canceled]
          default: planning
        priority:
          type: string
          enum: [low, medium, high]
          default: medium
        budget:
          type: number
        tags:
          type: array
          items:
            type: string
```

### Bookmark Entity

```yaml
$schema: "http://json-schema.org/draft-07/schema#"
title: Bookmarks
type: object
required: [records]
properties:
  records:
    type: array
    items:
      type: object
      required: [id, title, url, created]
      properties:
        id:
          type: string
          description: Date-based ID (YYYY-MM-DD-slug)
        title:
          type: string
        url:
          type: string
          format: uri
        description:
          type: string
        created:
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
          enum: [unread, read, archived]
          default: unread
```

### Meeting Entity (Monthly Partitioned)

```yaml
$schema: "http://json-schema.org/draft-07/schema#"
title: Meetings
description: Monthly partitioned meeting records
type: array
items:
  type: object
  required: [date, title, file]
  properties:
    date:
      type: string
      format: date
    title:
      type: string
    attendees:
      type: array
      items:
        type: string
    file:
      type: string
    type:
      type: string
      enum: [standup, planning, retrospective, one_on_one, all_hands]
    duration_minutes:
      type: integer
    action_items:
      type: array
      items:
        type: object
        properties:
          task:
            type: string
          assignee:
            type: string
          due_date:
            type: string
            format: date
```

## Validation Patterns

### String Patterns

```yaml
# Uppercase slug
pattern: "^[A-Z][A-Z0-9-]*$"

# Email
format: email

# URL
format: uri

# Date
format: date

# Date-time
format: date-time

# UUID
format: uuid
pattern: "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
```

### Number Constraints

```yaml
amount:
  type: number
  minimum: 0
  maximum: 1000000

percentage:
  type: number
  minimum: 0
  maximum: 100

count:
  type: integer
  minimum: 0
```

### Array Constraints

```yaml
tags:
  type: array
  items:
    type: string
  minItems: 0
  maxItems: 10
  uniqueItems: true
```

## Monthly Partitioning

For high-volume entities, use monthly partitioning:

**File Structure:**
```
.claude/data/meetings/
├── schema.yaml      # Schema definition
├── 2025-12.yaml    # December 2025 records
├── 2026-01.yaml    # January 2026 records
└── 2026-02.yaml    # February 2026 records
```

**Schema for partitioned files:**
```yaml
$schema: "http://json-schema.org/draft-07/schema#"
title: Monthly Records
type: array
items:
  # Record definition
```

**Note:** Partitioned entities don't have `last_number` - each file is a simple array.

## Config Integration

After creating the schema, register in `.claude/data/config.yaml`:

```yaml
entities:
  contacts:
    enabled: true
    singular: contact
    id_format: sequential
    prefix: CONTACT
    freshness:
      stale_after_days: 90
    fields:
      - name: name
        type: string
        required: true
      - name: email
        type: string
        format: email
      - name: company
        type: string
      - name: tags
        type: array

  meetings:
    enabled: true
    singular: meeting
    id_format: date-based
    partitioned: monthly
    freshness:
      stale_after_days: 7
```

## Tips

1. **Start minimal** — Add fields as needed, not speculatively
2. **Use format hints** — `format: date`, `format: email` enable validation
3. **Define defaults** — Reduce required user input
4. **Document fields** — Use `description` for each field
5. **Plan for evolution** — Schema changes require migration
