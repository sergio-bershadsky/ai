---
name: secondbrain-init
description: |
  This skill should be used when the user asks to "create a secondbrain", "scaffold knowledge base",
  "init documentation portal", "set up second brain", "create TDA project", or mentions wanting to
  build a personal knowledge management system with VitePress and microdatabases.
---

# Secondbrain Project Scaffolding

Scaffold a complete knowledge management system with microdatabases, VitePress portal, and Claude automation.

## Overview

Initialize a new secondbrain project with:
- **Microdatabase architecture** (YAML + JSON Schema validation)
- **VitePress documentation portal** (custom theme, Vue components)
- **Configurable entity types** (ADRs, Discussions, Notes, Tasks, Custom)
- **Claude automation** (hooks, maximum freedom settings)

## Workflow

### Step 1: Gather Project Information

Ask the user for:

1. **Project name** (kebab-case, e.g., `my-knowledge-base`)
2. **Target directory** (default: `./<project-name>`)
3. **Use case** (optional context for customization):
   - Personal knowledge base
   - Project documentation
   - Team collaboration

### Step 2: Select Entity Types

Present entity selection with checkboxes:

```
## Entity Selection

Which entities would you like to enable?

[x] ADRs (Architecture Decision Records)
    - Numbered decisions with status workflow
    - Category-based numbering ranges

[x] Discussions (Meeting notes, conversations)
    - Monthly partitioned records
    - Participant tracking

[x] Notes (General knowledge capture)
    - Date-based IDs
    - Tag support

[ ] Tasks (Action items, todo tracking)
    - Sequential numbering
    - Priority and due dates

Would you like to define a custom entity type? (y/n)
```

### Step 3: Configure Maximum Freedom Settings

**CRITICAL**: Always propose creating `.claude/settings.local.json` with maximum permissions:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "_comment": "Secondbrain project - maximum freedom for knowledge management",

  "permissions": {
    "allow_web_search": true,
    "allow_web_fetch": ["*"],
    "allow_read": ["~/**", "/tmp/**"],
    "allow_bash": ["*"],
    "auto_approve_write": ["<project_path>/docs/**"]
  }
}
```

Show the settings and ask for confirmation before proceeding.

### Step 4: Generate Scaffolding

Create the following structure:

```
<project-name>/
├── .claude/
│   ├── settings.local.json     # Max freedom permissions + hooks
│   ├── data/
│   │   ├── config.yaml         # Project configuration
│   │   ├── adrs/               # (if enabled)
│   │   │   ├── schema.yaml
│   │   │   └── records.yaml
│   │   ├── discussions/        # (if enabled)
│   │   │   ├── schema.yaml
│   │   │   └── YYYY-MM.yaml    # Current month
│   │   ├── notes/              # (if enabled)
│   │   │   ├── schema.yaml
│   │   │   └── records.yaml
│   │   └── tasks/              # (if enabled)
│   │       ├── schema.yaml
│   │       └── records.yaml
│   ├── lib/
│   │   └── tracking.py         # CRUD library with validation
│   └── hooks/
│       ├── freshness-check.py
│       ├── sidebar-check.py
│       └── session-context.py
├── docs/
│   ├── .vitepress/
│   │   ├── config.ts           # Navigation, sidebar, plugins
│   │   ├── theme/
│   │   │   ├── index.ts
│   │   │   ├── Layout.vue      # Giscus comments
│   │   │   ├── custom.css
│   │   │   └── components/
│   │   │       └── EntityTable.vue
│   │   └── data/
│   │       └── <entity>.data.ts # Per enabled entity
│   ├── index.md                # Home page
│   ├── adrs/                   # (if enabled)
│   │   ├── index.md
│   │   └── TEMPLATE.md
│   ├── discussions/            # (if enabled)
│   │   ├── index.md
│   │   └── TEMPLATE.md
│   ├── notes/                  # (if enabled)
│   │   └── index.md
│   └── tasks/                  # (if enabled)
│       └── index.md
├── package.json                # VitePress dependencies
├── CLAUDE.md                   # Project instructions
└── .gitignore
```

### Step 5: Generate Files

For each enabled entity, generate from templates in `${CLAUDE_PLUGIN_ROOT}/templates/`:

1. **Microdatabase files:**
   - `config.yaml` from `scaffolding/microdatabase/config.yaml.tmpl`
   - Entity `schema.yaml` from `entities/<entity>/schema.yaml`
   - Entity `records.yaml` initialized empty

2. **VitePress files:**
   - `config.ts` from `scaffolding/vitepress/config.ts.tmpl`
   - Theme files from `scaffolding/vitepress/theme/`
   - Data loaders from `scaffolding/vitepress/data/`

3. **Documentation:**
   - Home page from `scaffolding/docs/index.md.tmpl`
   - Entity index pages from `scaffolding/docs/entity-index.md.tmpl`
   - Templates from `entities/<entity>/TEMPLATE.md`

4. **Automation:**
   - `settings.local.json` from `scaffolding/claude/settings.local.json.tmpl`
   - `tracking.py` from `scaffolding/lib/tracking.py.tmpl`
   - Hooks from `hooks/` (copy to project)

### Step 6: Show Summary

```
## Secondbrain Created Successfully!

**Project:** my-knowledge-base
**Location:** /path/to/my-knowledge-base
**Entities:** ADRs, Discussions, Notes

### Structure Created

.claude/
├── settings.local.json    ✓ Maximum freedom permissions
├── data/                  ✓ Microdatabases with schemas
├── lib/tracking.py        ✓ CRUD operations
└── hooks/                 ✓ Automation hooks

docs/
├── .vitepress/            ✓ Custom theme with EntityTable
├── adrs/                  ✓ Decision records
├── discussions/           ✓ Meeting notes
└── notes/                 ✓ Knowledge capture

### Next Steps

1. Navigate to project:
   cd my-knowledge-base

2. Install dependencies:
   npm install

3. Start development server:
   npm run docs:dev

4. Create your first decision:
   /secondbrain-adr infrastructure my-first-decision

5. Add a note:
   /secondbrain-note my-first-note

### Available Commands

- /secondbrain-adr <category> <title>  — Create ADR
- /secondbrain-note <title>            — Create note
- /secondbrain-discussion <who> <topic> — Document discussion
- /secondbrain-freshness               — Check what needs attention
- /secondbrain-entity <name>           — Add custom entity type
```

## Template Variables

When generating files, replace these variables:

| Variable | Description |
|----------|-------------|
| `{{project_name}}` | Project name (kebab-case) |
| `{{project_path}}` | Absolute path to project |
| `{{description}}` | Project description |
| `{{date}}` | Current date (YYYY-MM-DD) |
| `{{timestamp}}` | Current ISO timestamp |
| `{{year_month}}` | Current year-month (YYYY-MM) |
| `{{entities}}` | Array of enabled entity configs |

## Entity Configuration

Each entity has standard configuration:

```yaml
<entity_slug>:
  enabled: true
  label: "Entity Label"
  singular: "Entity"
  doc_path: docs/<entity_slug>
  freshness:
    stale_after_days: 30
```

## Additional Resources

### Reference Files

For detailed entity schemas and templates:

- **`references/entity-schemas.md`** — Predefined entity schema definitions

### Related Skills

- **secondbrain-entity** — Add custom entity types
- **secondbrain-adr** — Create Architecture Decision Records
- **secondbrain-note** — Create notes
- **secondbrain-task** — Create tasks
- **secondbrain-discussion** — Document discussions
- **secondbrain-freshness** — Freshness report
