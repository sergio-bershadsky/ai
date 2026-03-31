# Second Brain

## Why

Your brain is a lousy database. It forgets names minutes after hearing them, rewrites memories every time it recalls them, and drops critical context the moment you switch tasks. Evolution optimized it for pattern-matching and snap decisions on the savanna — not for retaining the specifics of forty concurrent projects, three competing architectural proposals, and last Tuesday's meeting outcomes.

A second brain is the acknowledgment that durable, searchable, structured knowledge does not belong inside a biological organ that was never designed for storage. It belongs in files you control, versioned with git, organized by meaning rather than by the date you happened to write them down.

Most people who set out to build a second brain never get past choosing the tool. They spend weeks evaluating Obsidian vs. Notion vs. Logseq, configuring plugins, designing tag taxonomies — and never write the first useful note. The tool is a trap. The tool is the easiest part. The hard part is the discipline of writing things down, of revisiting what you wrote, of letting knowledge compound over time. A folder of plain markdown files committed to git will outperform any app you never open.

This is why the only real contract a second brain demands is structural:

```
docs/[topic]/[article].md
```

Markdown files. In folders. Under version control. Everything above this — rendering, search, graph views, publishing — is a replaceable presentation layer. You can swap it without losing a single sentence.

## The Beauty of Separation

There is something deeply elegant about a file that will outlive every application used to open it.

A markdown file written today will be readable in thirty years. Not because some company decided to keep its servers running — but because plain text is the cockroach of digital formats. It survives everything. The same cannot be said about your Notion workspace, your Confluence instance, or that Evernote account you forgot the password to.

When you separate what you *think* from how it *looks*, something remarkable happens: you gain the freedom to change your mind about presentation without touching a single idea. Your knowledge base can be a minimalist terminal output on Monday, a polished VitePress portal on Tuesday, and an Obsidian graph on Wednesday — all from the same folder of files. The thoughts don't move. Only the lens changes.

This is not just an architectural pattern. It is a statement about what matters. The rendering layer is cosmetics. The folder of markdown files is *you* — your decisions, your insights, the patterns you noticed, the mistakes you refuse to repeat. Treat the two with appropriate reverence.

And here's the part that tools get wrong: they want to own your expression. They impose their structure, their templates, their way of connecting ideas. But a second brain is personal. The way you organize knowledge reflects the way you think. Some people think in trees. Others in webs. Some in chronological streams. The `docs/[topic]/[article].md` contract gives you a canvas — not a coloring book. Fill the folders with whatever makes sense to *you*. Name them in your language. Nest them as deep or flat as your mind prefers. The structure is yours to shape. The tool just serves it.

## Choosing Your Presentation Layer

This plugin uses VitePress. It is one valid choice. Here are others — all of them consume the same `docs/[folders]/[article].md` structure:

| | VitePress | Plain MD + Git | Obsidian | MkDocs Material | Docusaurus |
|---|---|---|---|---|---|
| **Type** | SSG (Vue) | Workflow | App | SSG (Python) | SSG (React) |
| **`docs/` native** | Yes | Yes | Yes | Yes | Yes |
| **Git-friendly** | Yes | It *is* git | Yes (plugin) | Yes | Yes |
| **Search** | MiniSearch | grep / ripgrep | Built-in | lunr.js | Algolia |
| **Graph / Backlinks** | Custom (Vue) | No | Built-in | Plugin | Custom (React) |
| **Plugin ecosystem** | Moderate | N/A | Massive (1800+) | Good | Moderate |
| **Hosting** | Any static host | GitHub renders | Obsidian Publish | Any static host | Any static host |
| **Best for** | Publishing portal | Zero lock-in | Personal thinking | Technical docs | Project docs |

Pick whatever matches how you think and where you publish. The files underneath don't care.

---

## This Implementation

What follows is one concrete implementation — a Claude Code plugin that scaffolds and automates a second brain using VitePress, YAML microdatabases, and semantic search.

**Version:** 1.1.0

```bash
/plugin install secondbrain@bershadsky-claude-tools
```

## Quick Start

```bash
# Bootstrap a new knowledge base
/secondbrain-init my-knowledge-base

# Search across everything
/secondbrain-search "authentication patterns"
/secondbrain-search --entity=adrs --recent=30d "database"

# Capture knowledge
/secondbrain-adr infrastructure kubernetes-deployment
/secondbrain-note debugging-cors-preflight
/secondbrain-task migrate-auth-to-oauth2
/secondbrain-discussion q1-architecture-review
```

---

## Skills

### secondbrain-init

**Bootstrap a new knowledge base.** Creates the full project structure — YAML microdatabases, VitePress portal, entity schemas, automation hooks. Interactive: you choose which entity types to enable (ADRs, Notes, Tasks, Discussions), whether to add semantic search, review stamps, or meeting transcription. This is the starting point.

**Triggers:** "Create a secondbrain", "Scaffold knowledge base", "Init documentation portal"

### secondbrain-adr

**Record a technical decision.** When you choose Kubernetes over ECS, pick Postgres over Mongo, or decide on a deployment strategy — capture the context, options considered, and consequences. Without this, six months from now nobody remembers *why* that choice was made, and someone re-opens the debate.

**Triggers:** "Create ADR", "Document decision", "Add architecture record"

| Feature | Details |
|---------|---------|
| Numbering | Category-based ranges: infrastructure (0001-0999), feature (2000-2999), process (3000-3999) |
| Status workflow | draft → proposed → admitted → applied → implemented → tested → rejected → canceled |
| Output | Markdown page in `docs/adrs/` + YAML record in `.claude/data/adrs/records.yaml` |

### secondbrain-note

**Capture knowledge that doesn't fit a formal category.** A debugging insight you don't want to rediscover the hard way. A pattern you noticed across three different projects. A summary of a paper or talk. The most flexible entity type — use it when nothing else fits.

**Triggers:** "Create note", "Add to notes", "Document knowledge"

| Feature | Details |
|---------|---------|
| ID format | Date-based: `2026-03-31-cors-preflight-gotchas` |
| Organization | Tags for cross-cutting retrieval |
| Status | active / archived |

### secondbrain-task

**Track action items inside the knowledge base.** Keeps tasks colocated with the knowledge they emerged from — an ADR that requires implementation, a meeting that produced follow-ups, a note that surfaced a bug.

**Triggers:** "Create task", "Add todo", "Track action item"

| Feature | Details |
|---------|---------|
| ID format | Sequential: TASK-0001, TASK-0002 |
| Priority | critical / high / medium / low |
| Status workflow | todo → in_progress → done (with blocked / canceled paths) |
| Tracking | Due dates, assignee |

### secondbrain-discussion

**Document a meeting or conversation.** After any discussion that produced outcomes — decisions made, action items assigned, open questions raised — capture it before the details evaporate. Monthly-partitioned records prevent any single YAML file from growing unwieldy.

**Triggers:** "Document discussion", "Add meeting notes", "Record conversation"

| Feature | Details |
|---------|---------|
| ID format | Monthly: DISC-202603-1, DISC-202603-2 |
| Captures | Participants, topics, decisions, action items, open questions |
| Source tracking | manual / meeting / slack |

### secondbrain-freshness

**Find content that's going stale.** Knowledge rots. An ADR written 18 months ago about a service that's been rewritten twice is worse than no ADR — it's actively misleading. This skill generates a report categorizing all content by staleness with configurable thresholds per entity type. Terminal statuses (implemented, done, archived) are exempt.

**Triggers:** "Freshness check", "What needs attention", "Stale items"

| Staleness level | Threshold | Meaning |
|-----------------|-----------|---------|
| Critical | 2x configured days | Actively dangerous — likely outdated |
| Stale | 1x configured days | Needs review |
| Warning | 0.75x configured days | Approaching staleness |

### secondbrain-entity

**Define a new entity type.** When ADRs, Notes, Tasks, and Discussions aren't enough — create custom entities with their own schema, ID format, optional status workflow, and VitePress data loaders. Examples: RFCs, runbooks, retrospectives, vendor evaluations, incident postmortems.

**Triggers:** "Add entity type", "Create custom entity"

| Feature | Details |
|---------|---------|
| Field types | string, integer, date, boolean, enum, array |
| ID formats | sequential, date-based, UUID |
| Output | schema.yaml + records.yaml + VitePress data loader + index page |

### secondbrain-search

**Find knowledge by meaning, not keywords.** You remember the concept but not the exact words you used six months ago. Semantic search powered by qmd finds it anyway — combining BM25 keyword matching, vector similarity, and LLM reranking.

**Triggers:** "Search secondbrain", "Find in knowledge base"

```
/secondbrain-search [filters] "query"
```

| Filter | Syntax | Example |
|--------|--------|---------|
| Entity | `--entity=<type>` | `--entity=adrs,notes` |
| Recent | `--recent=<period>` | `--recent=7d` |
| Date range | `--from=<date> --to=<date>` | `--from=2026-01-01` |
| Status | `--status=<status>` | `--status=active` |
| Tag | `--tag=<tag>` | `--tag=kubernetes` |
| Limit | `--limit=<n>` | `--limit=10` |
| Format | `--format=<fmt>` | `--format=json` |

### secondbrain-search-init

**Add semantic search to an existing project.** One-time setup. Downloads embedding models (~1.5GB on first run), generates qmd config, optionally installs a PostToolUse hook for automatic incremental indexing after every document edit.

**Triggers:** "Enable search", "Add qmd", "Add semantic search"

### secondbrain-review

**Stamp a page as reviewed.** During periodic review cycles, mark content as "I read this and it's still accurate." Appends your name and date to the page's frontmatter — multiple reviewers accumulate over time. Visual staleness badges render automatically in VitePress.

**Triggers:** "Review page", "Stamp as reviewed", "Mark reviewed"

| Badge | Age | Color |
|-------|-----|-------|
| Fresh | < 30 days | Green |
| Aging | 30–90 days | Yellow |
| Stale | > 90 days | Orange |

### secondbrain-transcribe

**Import a meeting transcript into a Discussion document.** Pulls transcripts from external providers, extracts the signal (participants, decisions, action items) from the noise (small talk, filler). Maps speakers to team members via config. Identifies statements that sound like architectural decisions and flags them as potential ADRs for your confirmation. Deduplicates to prevent re-processing the same meeting.

**Triggers:** "Transcribe meeting", "Document meeting", "Process transcript"

| Feature | Details |
|---------|---------|
| Providers | Fireflies.ai (extensible) |
| Extraction | Participants, decisions, action items, open questions |
| ADR detection | Flags potential decisions for manual ADR creation |
| Deduplication | Tracks processed transcripts to prevent duplicates |

---

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

---

## Hooks

| Hook | Event | What It Does |
|------|-------|--------------|
| `freshness-check` | UserPromptSubmit | Reports the 10 most stale items at the start of each session (throttled to once per hour). You see what needs attention before you start working. |
| `session-context` | SessionStart | Injects a project overview — entity counts, search status, recent activity, available skills. Gives Claude full context about your knowledge base without you having to explain it every time. |
| `transcription-check` | SessionStart | Lists undocumented meetings from your transcription provider. Reminds you to run `/secondbrain-transcribe` for meetings that haven't been captured yet. |
| `sidebar-check` | PostToolUse (Write\|Edit) | Warns when a new markdown file isn't linked in the VitePress sidebar. Prevents orphaned documents that exist but are invisible in the portal. |
| `search-index-update` | PostToolUse (Write\|Edit) | Runs incremental qmd indexing in the background after any document is created or edited. Keeps search results current without manual rebuilds. |

---

## Architecture

```
my-knowledge-base/
├── .claude/
│   ├── data/                  # Microdatabases (YAML + JSON Schema)
│   │   ├── config.yaml        # Central configuration
│   │   ├── adrs/records.yaml
│   │   ├── notes/records.yaml
│   │   ├── tasks/records.yaml
│   │   └── discussions/       # Monthly-partitioned
│   │       └── 2026-03.yaml
│   ├── search/                # qmd index (if enabled)
│   ├── lib/
│   │   ├── tracking.py        # CRUD operations for microdatabases
│   │   └── fireflies.py       # Transcription provider client (if enabled)
│   └── hooks/                 # Automation scripts
├── docs/                      # VitePress portal
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

## Search Engines

### qmd (Claude Code — terminal)

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

| | Details |
|---|---|
| Technology | SQLite + embedding-gemma-300M + qwen3-reranker |
| First run | Downloads ~1.5GB of models |
| Index size | ~2MB per 100 documents |
| Use case | Searching from Claude Code sessions |

### Orama (VitePress — browser)

| | Details |
|---|---|
| Technology | JSON + gte-small client-side embeddings |
| Model size | ~30MB (loaded on demand) |
| Index size | ~500KB per 100 documents |
| Offline | Yes — works without a server |
| Use case | Press Cmd+K in the published site |

## Entity Types

### Built-in

| Entity | ID Format | Key Features |
|--------|-----------|--------------|
| ADRs | `ADR-NNNN` | Category-based numbering, 8-step status workflow |
| Notes | `YYYY-MM-DD-slug` | Date-based, tags, active/archived |
| Tasks | `TASK-NNNN` | Sequential, priority levels, due dates |
| Discussions | `DISC-YYYYMM-N` | Monthly-partitioned, participants, decisions |

### Custom

Define new entity types with `/secondbrain-entity`:

```
/secondbrain-entity research
/secondbrain-entity incident-postmortem
```

## Microdatabase Schema

Each entity stores records in YAML with JSON Schema validation:

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

## License

[Unlicense](LICENSE) — Public Domain
