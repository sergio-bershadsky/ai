# Secondbrain Plugin

Knowledge base scaffolding with microdatabases, VitePress portal, configurable entities, and semantic search.

## Installation

```bash
claude mcp add-from-marketplace bershadsky-claude-tools/secondbrain
```

## Overview

This plugin scaffolds a complete knowledge management system with:

- **Microdatabase architecture** — YAML-based data storage with JSON Schema validation
- **VitePress documentation portal** — Custom theme with Vue components
- **Configurable entity types** — ADRs, Notes, Tasks, Discussions, or custom
- **Semantic search** — qmd for Claude Code, Orama for browser
- **Claude automation** — Hooks for freshness tracking and context injection

## Quick Start

### Create New Project

```
/secondbrain-init my-knowledge-base
```

### Search Knowledge Base

```
/secondbrain-search "authentication patterns"
/secondbrain-search --entity=adrs "database"
/secondbrain-search --recent=30d "deployment"
```

### Add Content

```
/secondbrain-adr infrastructure kubernetes-deployment
/secondbrain-note meeting-notes-q1-planning
/secondbrain-task implement-authentication
```

## Skills

### secondbrain-init

Scaffold a new knowledge base project.

**Triggers:** "Create a secondbrain", "Scaffold knowledge base", "Init documentation portal"

**Features:**
- Interactive entity selection
- Search configuration (qmd/Orama/both)
- Maximum freedom Claude settings
- Complete project structure

### secondbrain-search

Semantic search across your knowledge base.

**Triggers:** "Search secondbrain", "Find in knowledge base"

**Syntax:**
```
/secondbrain-search [filters] "query"
```

**Filters:**
| Filter | Syntax | Example |
|--------|--------|---------|
| Entity | `--entity=<type>` | `--entity=adrs,notes` |
| Recent | `--recent=<period>` | `--recent=7d` |
| Status | `--status=<status>` | `--status=active` |
| Tag | `--tag=<tag>` | `--tag=kubernetes` |
| Limit | `--limit=<n>` | `--limit=10` |

### secondbrain-search-init

Initialize semantic search on an existing project.

**Triggers:** "Enable search", "Add qmd", "Add semantic search"

### secondbrain-adr

Create Architecture Decision Records.

**Triggers:** "Create ADR", "Document decision", "Add architecture record"

**Features:**
- Category-based numbering (infrastructure: 1-99, feature: 100-199, process: 200-299)
- 8-step status workflow (draft → proposed → admitted → applied → implemented → tested → rejected → canceled)
- VitePress integration

### secondbrain-note

Capture knowledge as notes.

**Triggers:** "Create note", "Add to notes", "Document knowledge"

**Features:**
- Date-based IDs
- Tag support
- Simple status tracking

### secondbrain-task

Track action items.

**Triggers:** "Create task", "Add todo", "Track action item"

**Features:**
- Sequential numbering
- Priority levels
- Due dates

### secondbrain-discussion

Document meetings and conversations.

**Triggers:** "Document discussion", "Add meeting notes", "Record conversation"

**Features:**
- Monthly partitioned records
- Participant tracking
- Decision capture

### secondbrain-freshness

Check what needs attention.

**Triggers:** "Freshness check", "What needs attention", "Stale items"

### secondbrain-entity

Add custom entity types to your project.

## Architecture

```
my-knowledge-base/
├── .claude/
│   ├── data/                  # Microdatabases
│   │   ├── config.yaml
│   │   ├── adrs/records.yaml
│   │   ├── notes/records.yaml
│   │   └── tasks/records.yaml
│   ├── search/                # qmd index (if enabled)
│   └── hooks/                 # Automation
├── docs/                      # VitePress portal
│   ├── .vitepress/
│   │   └── theme/
│   │       └── components/
│   │           └── SearchBox.vue  # Orama (if enabled)
│   ├── adrs/
│   ├── notes/
│   └── tasks/
└── package.json
```

## Search Options

| Option | For | Technology | Requires |
|--------|-----|------------|----------|
| **qmd** | Claude Code | SQLite + embedding-gemma | `bun install -g qmd` |
| **Orama** | VitePress | JSON + gte-small | npm dependencies |
| **Both** | AI + Humans | Dual index | Both above |

### qmd (Claude Code Search)

```
Query → qmd
         ↓
    ┌────┴────┐
    │         │
   BM25    Vector
(keyword) (semantic)
    │         │
    └────┬────┘
         ↓
     Reranker
   (LLM scoring)
         ↓
    Top Results
```

First run downloads ~1.5GB of models:
- embedding-gemma-300M (embeddings)
- qwen3-reranker (result ranking)

### Orama (Browser Search)

- Client-side semantic search
- ~30MB model (on-demand loading)
- Offline-capable
- Press `Cmd+K` to search

## Hooks

| Hook | Event | Action |
|------|-------|--------|
| freshness-check | Stop | Report stale items |
| sidebar-check | Stop | Verify sidebar consistency |
| session-context | SessionStart | Inject recent items |
| search-index-update | PostToolUse | Update qmd index |

## Entity Types

### Built-in

| Entity | ID Format | Features |
|--------|-----------|----------|
| ADRs | `ADR-NNNN` | Category numbering, status workflow |
| Notes | `NOTE-YYYYMMDD-N` | Date-based, tags |
| Tasks | `TASK-NNNN` | Priority, due dates |
| Discussions | `DISC-YYYYMM-N` | Monthly, participants |

### Custom

Add custom entities via `/secondbrain-entity`:

```
/secondbrain-entity research
```

## Microdatabase Schema

Each entity uses YAML with JSON Schema validation:

```yaml
# .claude/data/adrs/records.yaml
last_number: 5
records:
  - number: 1
    title: "Use PostgreSQL for primary storage"
    status: implemented
    category: infrastructure
    created: 2025-01-15
    file: docs/adrs/ADR-0001-use-postgresql.md
```

## VitePress Components

### EntityTable

Auto-generated tables from microdatabase records:

```vue
<EntityTable entity="adrs" />
```

### SearchBox (Orama)

Client-side semantic search:

```vue
<SearchBox />
```

## Use Cases

- **Personal Knowledge Base** — Capture learnings and decisions
- **Project Documentation** — ADRs, meeting notes, technical specs
- **Team Collaboration** — Shared knowledge with search

## License

[Unlicense](LICENSE) - Public Domain
