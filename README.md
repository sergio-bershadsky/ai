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

This repository uses VitePress. It is one valid choice. Here are others — all of them consume the same `docs/[folders]/[article].md` structure:

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

What follows is one concrete implementation — a Claude Code plugin marketplace that scaffolds and automates a second brain using VitePress, YAML microdatabases, and semantic search.

**Marketplace ID:** `bershadsky-claude-tools`

## Installation

```bash
# Add marketplace
/plugin marketplace add sergio-bershadsky/ai

# Install a plugin (e.g., git)
/plugin install git@bershadsky-claude-tools
```

## Plugins

### Productivity

| Plugin | Description | Skills | Hooks |
|--------|-------------|--------|-------|
| [**git**](plugins/git/) | Git workflow automation: conventional commits, auto-staging, uncommitted changes protection | /commit, /version | auto-stage, pre-stop-commit |
| [**settings-sync**](plugins/settings-sync/) | Sync Claude settings across ephemeral VMs via Git backup | — | backup-settings |

### Development

| Plugin | Description | Skills | Agents |
|--------|-------------|--------|--------|
| [**django-dev**](plugins/django-dev/) | Opinionated Django toolkit with Ninja API, Unfold admin, pytest, Dynaconf | 4 skills | django-review |
| [**frappe-dev**](plugins/frappe-dev/) | Frappe Framework v15 toolkit with multi-layer architecture | 5 skills | — |

### Knowledge Management

| Plugin | Description | Skills | Hooks |
|--------|-------------|--------|-------|
| [**secondbrain**](plugins/secondbrain/) | Knowledge base scaffolding with microdatabases, VitePress portal, semantic search, review stamps, meeting transcription | 11 skills | freshness, sidebar, search-index, session-context, transcription-check |
| [**replit-prompts**](plugins/replit-prompts/) | Optimized prompts, PRDs, and task plans for Replit Agent | 3 skills | — |

### Internal

| Plugin | Description |
|--------|-------------|
| [**marketplace-validator**](plugins/marketplace-validator/) | Validates marketplace.json schema after every edit |

---

## Plugin Details

### secondbrain

The core knowledge management plugin. Scaffolds a complete system with YAML microdatabases, configurable entity types, semantic search, and automation hooks that keep your knowledge base healthy without manual effort.

```bash
/plugin install secondbrain@bershadsky-claude-tools
```

#### Skills

| Skill | Use Case |
|-------|----------|
| `secondbrain-init` | **Bootstrap a new knowledge base.** Creates the full project structure — YAML microdatabases, VitePress portal, entity schemas, automation hooks. Interactive: you choose which entity types to enable (ADRs, Notes, Tasks, Discussions), whether to add semantic search, review stamps, or meeting transcription. This is the starting point. |
| `secondbrain-adr` | **Record a technical decision.** When you choose Kubernetes over ECS, pick Postgres over Mongo, or decide on a deployment strategy — capture the context, options considered, and consequences. Category-based numbering (infra: 0001-0999, feature: 2000-2999, process: 3000-3999). Status workflow from draft through implemented to rejected. |
| `secondbrain-note` | **Capture knowledge that doesn't fit a formal category.** A debugging insight, a pattern you discovered, a summary of a paper you read. Date-based IDs (2026-03-31-slug), tagged for retrieval. The most flexible entity type — use it when nothing else fits. |
| `secondbrain-task` | **Track action items inside the knowledge base.** Sequential IDs (TASK-0001), priority levels (critical/high/medium/low), due dates, status workflow (todo → in_progress → done, with blocked/canceled paths). Keeps tasks colocated with the knowledge they emerged from. |
| `secondbrain-discussion` | **Document a meeting or conversation.** Captures participants, decisions made, action items assigned, and open questions. Monthly-partitioned YAML records. Source tracking (manual entry, meeting, Slack). Use this after any conversation that produced outcomes worth preserving. |
| `secondbrain-freshness` | **Find content that's going stale.** Generates a report categorizing all content by staleness: critical (2x threshold), stale (1x), warning (0.75x). Configurable thresholds per entity type. Terminal statuses (implemented, done, archived) are exempt. Run periodically to keep the knowledge base honest. |
| `secondbrain-entity` | **Define a new entity type.** When ADRs, Notes, Tasks, and Discussions aren't enough — create custom entities with their own schema, ID format (sequential, date-based, UUID), optional status workflow, and VitePress data loaders. Examples: RFCs, runbooks, retrospectives, vendor evaluations. |
| `secondbrain-search` | **Find knowledge by meaning, not keywords.** Semantic search powered by qmd (SQLite + embedding-gemma + reranker). Filters by entity type, date range, status, tags. Output as brief summaries, detailed results, or JSON. Use when you know what you're looking for but not the exact words you used. |
| `secondbrain-search-init` | **Add semantic search to an existing project.** Downloads embedding models (~1.5GB first run), generates qmd config, optionally installs a PostToolUse hook for automatic incremental indexing. One-time setup. |
| `secondbrain-review` | **Stamp a page as reviewed.** Appends your name and date to the page's frontmatter. Multiple reviewers accumulate over time. Visual staleness badges: green (<30 days), yellow (30-90 days), orange (>90 days). Use during periodic review cycles to mark content as still accurate. |
| `secondbrain-transcribe` | **Import a meeting transcript into a Discussion document.** Pulls transcripts from providers (Fireflies.ai), extracts participants, decisions, and action items. Maps speakers to team members via config. Identifies potential ADRs for manual confirmation. Deduplicates to prevent re-processing. |

#### Agents

| Agent | Use Case |
|-------|----------|
| `secondbrain-review` | **Assess document quality before publishing.** Evaluates completeness, clarity, and alignment with entity-specific criteria (ADRs need context + options + consequences, Notes need actionability). Returns a verdict: ready, minor revisions, major revisions, or needs rethinking. Use before sharing a document with the team. |
| `secondbrain-refine` | **Autonomous knowledge base improvement.** Runs in the background, identifies stale content, broken links, missing metadata, and inconsistencies. Proposes improvements in batches that require your confirmation before applying. Supports notifications (ntfy.sh, macOS sound). Use when you want the knowledge base cleaned up without doing the grunt work yourself. |

#### Hooks

| Hook | Event | What It Does |
|------|-------|--------------|
| `freshness-check` | UserPromptSubmit | Reports the 10 most stale items at the start of each session (throttled to once per hour). You see what needs attention before you start working. |
| `session-context` | SessionStart | Injects a project overview — entity counts, search status, recent activity, available skills. Gives Claude full context about your knowledge base without you having to explain it. |
| `transcription-check` | SessionStart | Lists undocumented meetings from your transcription provider. Reminds you to run `/secondbrain-transcribe` for meetings that haven't been captured yet. |
| `sidebar-check` | PostToolUse | Warns when a new markdown file isn't linked in the VitePress sidebar. Prevents orphaned documents that exist but are invisible in the portal. |
| `search-index-update` | PostToolUse | Runs incremental qmd indexing in the background after any document is created or edited. Keeps search results current without manual rebuilds. |

#### Search Engines

| Engine | Environment | Technology | Use Case |
|--------|-------------|------------|----------|
| qmd | Claude Code (CLI) | SQLite + embedding-gemma + qwen3-reranker | BM25 keyword + vector semantic + LLM reranking. For when you're working in the terminal. |
| Orama | VitePress (browser) | JSON + gte-small client-side embeddings | Offline-capable semantic search. Press Cmd+K in the published site. |

---

### git

Standardized git workflow that prevents sloppy commits and protects against leaving uncommitted work behind.

```bash
/plugin install git@bershadsky-claude-tools
```

#### Skills

| Skill | Use Case |
|-------|----------|
| `/commit` | **Create a conventional commit with guardrails.** Analyzes your diff, detects the branch naming convention and linked tickets (GitHub, GitLab, Jira, Linear), drafts a conventional commit message (type(scope): description), warns if you're committing to the default branch, and always asks for confirmation before committing. Never pushes. |
| `/version` | **Bump a plugin's semantic version.** Choose major, minor, or patch. Updates plugin.json and marketplace.json, creates a commit and a git tag (v1.2.0-plugin-name). Auto-detects the plugin from your working directory. Never pushes — you run `git push --follow-tags` when ready. |

#### Hooks

| Hook | Event | What It Does |
|------|-------|--------------|
| `auto-stage` | PostToolUse | Automatically stages files after Write/Edit operations. No more forgotten `git add`. |
| `pre-stop-commit` | Stop | Blocks session exit if uncommitted changes exist. Forces you to either commit or consciously discard before leaving. Exit code 2 prevents session close. |

---

### settings-sync

Preserves your Claude Code configuration across ephemeral environments (cloud VMs, Codespaces, Gitpod).

```bash
/plugin install settings-sync@bershadsky-claude-tools
```

#### Hook

| Hook | Event | What It Does |
|------|-------|--------------|
| `backup-settings` | Stop | Copies `~/.claude/` to `.claude-backup/` in the repo before session ends. Excludes sensitive files (logs, credentials, tokens). On next VM, bootstrap restores them. |

**Bootstrap for new VMs:**

```bash
curl -fsSL https://raw.githubusercontent.com/sergio-bershadsky/ai/main/plugins/settings-sync/scripts/bootstrap.sh | bash
```

---

### django-dev

Opinionated Django patterns that enforce consistency across models, APIs, admin, and tests. Install once, and every Django project follows the same structure.

```bash
/plugin install django-dev@bershadsky-claude-tools
```

#### Skills

| Skill | Use Case |
|-------|----------|
| `django-dev` | **Establish project structure and model conventions.** 1-file-per-model in a `models/` package. UUID primary keys, timestamps, soft delete via BaseModel. Naming conventions: Base* (abstract), Virtual* (in-memory), Proxy* (proxy models). Dynaconf for configuration. uv + pyproject.toml for dependencies. Strict class member ordering enforced. |
| `django-dev-ninja` | **Build REST APIs with Django Ninja.** 1-endpoint-per-file in `api/<group>/` subpackages. Pydantic schemas in `schemas/`. Router-per-group. Business logic stays in services, not endpoints. Includes patterns for pagination, error handling, file uploads, JWT/API key/session auth. |
| `django-dev-unfold` | **Configure Unfold admin dashboards.** 1-admin-per-file in `admin/` package. Unfold decorators for styled displays (@display with label coloring). Range filters, inline support, dashboard customization, Tailwind styling. |
| `django-dev-test` | **Write tests with pytest and factory_boy.** Never Django TestCase. Factories for all test data. Mirror app structure in tests/unit/, tests/integration/, tests/e2e/. Conftest patterns for shared fixtures. Mock/patch for service isolation. |

#### Agent

| Agent | Use Case |
|-------|----------|
| `django-review` | **Review code for convention compliance.** Checks model organization, naming prefixes, class member ordering, API structure, admin setup, security (no hardcoded secrets, parameterized SQL), and configuration (Dynaconf, Docker). Issues categorized as critical, convention violation, or suggestion. |

---

### frappe-dev

Frappe Framework v15 development with multi-layer architecture: Controller → Service → Repository → DB.

```bash
/plugin install frappe-dev@bershadsky-claude-tools
```

#### Skills

| Skill | Use Case |
|-------|----------|
| `frappe-doctype` | **Create a complete DocType implementation.** Generates controller with lifecycle hooks (before_validate through on_trash), service layer for business logic, repository for data access, and integration tests. v15 type annotations with TYPE_CHECKING blocks. DocStatus helpers for readable status checks. |
| `frappe-api` | **Build REST API endpoints.** Standard CRUD (GET, GET list, POST, PUT, DELETE) plus bulk operations. Permission checks on every endpoint, input validation via v15 type hints, standardized error responses, transaction handling (auto-commit/rollback). Includes cURL examples. |
| `frappe-service` | **Implement business logic in the service layer.** Decorators for permissions, transactions, and logging. CRUD with business rules, workflow processing, bulk operations, dashboard query methods. Integration service pattern for external APIs with retry logic. |
| `frappe-app` | **Scaffold a new Frappe application.** Multi-layer architecture, proper module organization, v15 best practices out of the box. |
| `frappe-test` | **Write tests with pytest and factories.** Fixtures, factory patterns, integration tests that exercise the full Controller → Service → Repository stack. |

---

### replit-prompts

Generate structured prompts that maximize Replit Agent's effectiveness and minimize back-and-forth iterations.

```bash
/plugin install replit-prompts@bershadsky-claude-tools
```

#### Skills

| Skill | Use Case |
|-------|----------|
| `replit-prompt` | **Turn a vague idea into a structured prompt.** Applies Replit's 10 official guidelines (Checkpoint, Debug, Discover, Experiment, Instruct, Select, Show, Simplify, Specify, Test). Outputs a template covering project overview, tech stack, core features, UI/UX, data model, user flows, constraints, and success criteria. |
| `replit-prd` | **Write a Product Requirements Document.** Comprehensive PRD formatted for Replit Agent consumption. Covers scope, user stories, technical requirements, and acceptance criteria. |
| `replit-plan` | **Create a phased development plan.** Breaks work into phases with checkpoints, dependencies, and deliverables. Designed for iterative Replit Agent sessions. |

---

### marketplace-validator

Internal plugin. Validates marketplace.json schema automatically after every edit.

Runs as a PostToolUse hook on Write/Edit operations. Checks required fields (name, owner, plugins array), plugin fields (name, source, description, version), and blocks the session (exit code 2) if validation fails.

---

## Documentation

Run documentation site locally:

```bash
npm install
npm run docs:dev
```

Visit: http://localhost:5173

## License

Public domain ([Unlicense](LICENSE))
