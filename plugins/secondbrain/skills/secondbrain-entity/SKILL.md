---
name: secondbrain-entity
description: |
  This skill should be used when the user asks to "add entity", "create custom entity",
  "new entity type", "define entity", or mentions wanting to add a new trackable data type
  to their secondbrain project beyond the predefined ADR, Note, Task, and Discussion types.
---

# Add Custom Entity

Create custom entity types with schema validation and VitePress integration.

## Prerequisites

Verify secondbrain is initialized:
1. Check for `.claude/data/config.yaml`
2. If not found, suggest running `secondbrain-init` first

## Workflow

### Step 1: Gather Entity Information

Collect from user:

1. **Entity Name** — Plural name (e.g., "contacts", "projects", "bookmarks")
2. **Singular Name** — For display (e.g., "contact", "project", "bookmark")
3. **Fields** — Custom fields for the entity:
   - Field name (snake_case)
   - Field type (string, integer, boolean, date, array, enum)
   - Required or optional
   - For enums: allowed values
4. **ID Format** — How records are numbered/identified:
   - Sequential (`PREFIX-XXXX`)
   - Date-based (`YYYY-MM-DD-slug`)
   - UUID
5. **Status Workflow** (optional) — If entity has status tracking

### Step 2: Generate Schema

Create `.claude/data/<entity>/schema.yaml`:

```yaml
type: object
required: [records]
properties:
  last_number:
    type: integer
    description: Last assigned sequential number
  records:
    type: array
    items:
      type: object
      required: [id, title, created, file]
      properties:
        id:
          type: string
          description: Unique identifier
        title:
          type: string
          description: Display title
        created:
          type: string
          format: date
        file:
          type: string
          description: Path to markdown file
        status:
          type: string
          enum: [active, archived]
        # ... custom fields
```

### Step 3: Initialize Records File

Create `.claude/data/<entity>/records.yaml`:

```yaml
last_number: 0
records: []
```

### Step 4: Create Document Template

Create `templates/entities/<entity>/TEMPLATE.md`:

```markdown
---
id: {{id}}
title: {{title}}
created: {{date}}
status: active
# ... custom fields
---

# {{title}}

## Overview

[Description]

## Details

[Content]
```

### Step 5: Create VitePress Data Loader

Create `docs/.vitepress/data/<entity>.data.ts`:

```typescript
import { defineLoader } from 'vitepress'
import fs from 'fs'
import yaml from 'js-yaml'

interface Record {
  id: string
  title: string
  created: string
  file: string
  status: string
  // ... custom fields
}

export interface Data {
  records: Record[]
  lastNumber: number
}

declare const data: Data
export { data }

export default defineLoader({
  watch: ['.claude/data/<entity>/*.yaml'],
  async load(): Promise<Data> {
    const recordsPath = '.claude/data/<entity>/records.yaml'

    if (!fs.existsSync(recordsPath)) {
      return { records: [], lastNumber: 0 }
    }

    const content = fs.readFileSync(recordsPath, 'utf-8')
    const parsed = yaml.load(content) as any

    return {
      records: parsed.records || [],
      lastNumber: parsed.last_number || 0
    }
  }
})
```

### Step 6: Create Documentation Index

Create `docs/<entity>/index.md`:

```markdown
---
title: <Entity> Index
---

# <Entity>

<script setup>
import { data } from '../.vitepress/data/<entity>.data'
import EntityTable from '../.vitepress/theme/components/EntityTable.vue'

const columns = [
  { key: 'id', label: 'ID', sortable: true },
  { key: 'title', label: 'Title', sortable: true },
  { key: 'created', label: 'Created', sortable: true },
  { key: 'status', label: 'Status', sortable: true }
]
</script>

<EntityTable :data="data.records" :columns="columns" />
```

### Step 7: Update Configuration

Add entity to `.claude/data/config.yaml`:

```yaml
entities:
  <entity>:
    enabled: true
    singular: <singular>
    id_format: sequential  # or date-based, uuid
    prefix: PREFIX         # for sequential IDs
    freshness:
      stale_after_days: 30
    fields:
      - name: field_name
        type: string
        required: true
```

### Step 8: Update Sidebar

Add to `docs/.vitepress/config.ts` sidebar:

```typescript
{
  text: '<Entity>',
  collapsed: true,
  items: [
    { text: 'Overview', link: '/<entity>/' }
  ]
}
```

### Step 9: Confirm Creation

```
## Entity Created

**Name:** <entity>
**Singular:** <singular>
**ID Format:** sequential (PREFIX-XXXX)
**Status Tracking:** Yes

### Fields
| Field | Type | Required |
|-------|------|----------|
| title | string | Yes |
| description | string | No |
| priority | enum (low, medium, high) | No |

### Files Created
- `.claude/data/<entity>/schema.yaml`
- `.claude/data/<entity>/records.yaml`
- `docs/.vitepress/data/<entity>.data.ts`
- `docs/<entity>/index.md`

### Next Steps
1. Create records using the new entity type
2. Add entity-specific skills if needed
3. Customize the index page layout
```

## Field Types

| Type | YAML Schema | Example |
|------|-------------|---------|
| string | `type: string` | "Hello world" |
| integer | `type: integer` | 42 |
| number | `type: number` | 3.14 |
| boolean | `type: boolean` | true/false |
| date | `type: string, format: date` | 2026-01-15 |
| datetime | `type: string, format: date-time` | 2026-01-15T10:30:00Z |
| array | `type: array, items: {...}` | [tag1, tag2] |
| enum | `type: string, enum: [...]` | "active" |

## ID Formats

### Sequential
Best for: Tasks, tickets, numbered records
```
PREFIX-0001, PREFIX-0002, PREFIX-0003
```

### Date-based
Best for: Notes, journal entries, time-sensitive content
```
2026-01-15-meeting-notes
2026-01-15-architecture-review
```

### UUID
Best for: Globally unique, import/export scenarios
```
550e8400-e29b-41d4-a716-446655440000
```

## Tips

1. **Keep fields minimal** — Start with essential fields, add more later
2. **Use enums for fixed values** — Better than free-form strings
3. **Consider status workflow** — Most entities benefit from status tracking
4. **Plan ID format carefully** — Hard to change after records exist
5. **Reuse existing patterns** — Look at ADR, Task, Note for inspiration
