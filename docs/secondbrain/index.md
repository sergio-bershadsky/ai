# Secondbrain Plugin

Knowledge base scaffolding with microdatabases, VitePress portal, configurable entities, and semantic search.

## Overview

This plugin scaffolds a complete knowledge management system with:
- **Microdatabase architecture** — YAML-based data storage with JSON Schema validation
- **VitePress documentation portal** — Custom theme with Vue components
- **Configurable entity types** — ADRs, Notes, Tasks, Discussions, or custom
- **Semantic search** — qmd for Claude, Orama for browser
- **Claude automation** — Hooks for freshness tracking and context injection

## Skills

### secondbrain-init

Scaffold a new knowledge base project.

**Triggers:**
- "Create a secondbrain"
- "Scaffold knowledge base"
- "Init documentation portal"
- "Set up second brain"

**Features:**
- Interactive entity selection
- Search configuration (qmd/Orama/both)
- Maximum freedom Claude settings
- Complete project structure

### secondbrain-search

Semantic search across your knowledge base.

**Triggers:**
- "Search secondbrain"
- "Find in knowledge base"
- "Search notes/ADRs/tasks"

**Features:**
- Hybrid search (BM25 + vector + reranking)
- Entity and date filtering
- Multiple output formats

### secondbrain-adr

Create Architecture Decision Records.

**Triggers:**
- "Create ADR"
- "Document decision"
- "Add architecture record"

**Features:**
- Category-based numbering
- 8-step status workflow
- VitePress integration

### secondbrain-note

Capture knowledge as notes.

**Triggers:**
- "Create note"
- "Add to notes"
- "Document knowledge"

**Features:**
- Date-based IDs
- Tag support
- Simple status tracking

### secondbrain-task

Track action items.

**Triggers:**
- "Create task"
- "Add todo"
- "Track action item"

**Features:**
- Sequential numbering
- Priority levels
- Due dates

### secondbrain-discussion

Document meetings and conversations.

**Triggers:**
- "Document discussion"
- "Add meeting notes"
- "Record conversation"

**Features:**
- Monthly partitioned records
- Participant tracking
- Decision capture

### secondbrain-freshness

Check what needs attention.

**Triggers:**
- "Freshness check"
- "What needs attention"
- "Stale items"

**Features:**
- Configurable thresholds per entity
- Urgency categorization
- Remediation recommendations

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

See [Search Documentation](./search) for details.
