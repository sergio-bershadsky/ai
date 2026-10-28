# Secondbrain Plugin

Knowledge base scaffolding with microdatabases, VitePress portal, configurable entities, semantic search, review stamps, and meeting transcription.

**Version:** 1.1.0

## Overview

This plugin scaffolds a complete knowledge management system with:
- **Microdatabase architecture** — YAML-based data storage with JSON Schema validation
- **VitePress documentation portal** — Custom theme with Vue components
- **Configurable entity types** — ADRs, Notes, Tasks, Discussions, or custom
- **Semantic search** — qmd for Claude, Orama for browser
- **Review stamps** — Track who reviewed which page and when, with visual staleness badges
- **Meeting transcription** — Import transcripts from providers (Fireflies.ai) into discussion documents
- **Claude automation** — Hooks for freshness tracking, context injection, and meeting detection

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

### secondbrain-review

Stamp documentation pages as reviewed.

**Triggers:**
- "Review page"
- "Stamp as reviewed"
- "Mark reviewed"

**Features:**
- Append-only `reviewed_by` list in frontmatter
- Configurable staleness thresholds (fresh/aging/stale)
- ReviewBadge Vue component with color-coded indicators

### secondbrain-transcribe

Import meeting transcripts from external providers.

**Triggers:**
- "Transcribe meeting"
- "Document meeting"
- "Process transcript"

**Features:**
- Provider-agnostic design (Fireflies.ai supported)
- Auto-generates discussion documents from transcripts
- Participant mapping via team config
- Decision extraction with optional ADR creation

### secondbrain-entity

Define custom entity types (RFCs, runbooks, postmortems…) with their own schema, ID format and status workflow.

**Triggers:**
- "Add entity"
- "Create custom entity"
- "New entity type"

**Output:** `schema.yaml` + a single `records.yaml` (custom entities are not sharded) + VitePress data loader + index page.

### secondbrain-search-init

One-time qmd setup for an existing project: downloads embedding models (~1.5GB on first run) and writes qmd config. Incremental indexing is already handled by the plugin's `search-index-update` hook — skip the skill's optional step that registers a second copy in `.claude/settings.local.json`.

**Triggers:**
- "Initialize search"
- "Set up semantic search"
- "Enable qmd"

## Agents

### secondbrain-review (agent)

**Assess document quality before publishing.** Evaluates completeness, clarity, and alignment with entity-specific criteria. ADRs need context, options considered, and consequences. Notes need enough context to be useful to your future self. Tasks need clear acceptance criteria. Returns a verdict with prioritized improvement suggestions.

| Verdict | Meaning |
|---------|---------|
| Ready | Ship it |
| Minor revisions | Small gaps, quick fixes |
| Major revisions | Significant content missing |
| Needs rethinking | Structural problems, wrong entity type, or unclear purpose |

### secondbrain-refine (agent)

**Autonomous knowledge base improvement.** Runs in the background, scans the entire knowledge base, and identifies: stale content, broken internal links, missing frontmatter fields, inconsistent formatting, duplicate information. Proposes improvements in batches that require your confirmation before applying anything. Supports notifications (ntfy.sh, macOS sound) so you can let it work while you do something else.

Use when the knowledge base has accumulated enough content that manual cleanup is no longer practical.

## Hooks

| Hook | Event | What It Does |
|------|-------|--------------|
| `freshness-check` | UserPromptSubmit | Reports the 10 most stale items at the start of each session (throttled to once per hour). You see what needs attention before you start working. |
| `session-context` | SessionStart | Injects a project overview — entity counts, search status, recent activity, available skills. Gives Claude full context about your knowledge base without you having to explain it every time. |
| `transcription-check` | SessionStart | Lists undocumented meetings from your transcription provider. Reminds you to run `/secondbrain-transcribe` for meetings that haven't been captured yet. |
| `sidebar-check` | PostToolUse (Write\|Edit) | Warns when a new markdown file isn't linked in the VitePress sidebar. Skips only `index.md`, so it also warns on ADR / note / task / discussion pages — those are listed by `EntityTable` and are intentionally kept out of the sidebar; ignore the warning for them. |
| `search-index-update` | PostToolUse (Write\|Edit) | Runs incremental qmd indexing in the background after any document is created or edited. Keeps search results current without manual rebuilds. |

**Known gap (sharded storage):** `freshness-check` and `session-context` read monthly shards only when an entity's config sets `partitioned: monthly`, which the scaffold does not write yet — so for ADRs, notes, tasks and discussions they currently fall back to `records.yaml` and report nothing. The same applies to the VitePress data loader behind `EntityTable` and to `secondbrain-search` record lookups, which read only `records.yaml`. Fix tracked separately.

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
│   ├── data/                     # Microdatabases (YAML + JSON Schema)
│   │   ├── config.yaml           # Central configuration
│   │   ├── adrs/                 # Monthly-sharded
│   │   │   ├── schema.yaml
│   │   │   ├── meta.yaml         # last_number + shard list
│   │   │   ├── 2025-12.yaml
│   │   │   └── 2026-03.yaml      # Current month
│   │   ├── notes/                # Monthly-sharded
│   │   │   ├── schema.yaml
│   │   │   ├── meta.yaml         # shard list
│   │   │   └── 2026-03.yaml
│   │   ├── tasks/                # Monthly-sharded
│   │   │   ├── schema.yaml
│   │   │   ├── meta.yaml         # last_number + shard list
│   │   │   └── 2026-03.yaml
│   │   └── discussions/          # Monthly-sharded
│   │       ├── schema.yaml
│   │       └── 2026-03.yaml
│   ├── search/                   # qmd index (if enabled)
│   ├── lib/
│   │   ├── tracking.py           # CRUD operations for microdatabases
│   │   └── fireflies.py          # Transcription provider client (if enabled)
│   └── hooks/                    # Automation scripts
├── docs/                         # VitePress portal
│   ├── .vitepress/
│   │   └── theme/
│   │       └── components/
│   │           ├── EntityTable.vue    # Auto-generated tables from records
│   │           ├── SearchBox.vue      # Orama search (if enabled)
│   │           └── ReviewBadge.vue    # Staleness badges (if enabled)
│   ├── adrs/
│   ├── notes/
│   ├── tasks/
│   └── discussions/
└── package.json
```

## Search Options

| Option | For | Technology | Requires |
|--------|-----|------------|----------|
| **qmd** | Claude Code | SQLite + embedding-gemma | `bun install -g qmd` |
| **Orama** | VitePress | JSON + gte-small | npm dependencies |
| **Both** | AI + Humans | Dual index | Both above |

See [Search Documentation](./search) for details.
