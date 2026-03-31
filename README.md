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

### [secondbrain](plugins/secondbrain/)

Knowledge base scaffolding with YAML microdatabases, configurable entity types (ADRs, Notes, Tasks, Discussions, custom), dual semantic search (qmd for CLI, Orama for browser), review stamps with staleness badges, and meeting transcription. 11 skills, 2 agents, 5 automation hooks. See the [full documentation](plugins/secondbrain/README.md).

```bash
/plugin install secondbrain@bershadsky-claude-tools
```

---

### [git](plugins/git/)

Conventional commits with branch safety checks and ticket detection (GitHub, GitLab, Jira, Linear). Semantic version bumping with git tags. Auto-stages files after edits. Blocks session exit if uncommitted changes exist.

```bash
/plugin install git@bershadsky-claude-tools
```

**Skills:** `/commit`, `/version` | **Hooks:** auto-stage, pre-stop-commit

---

### [settings-sync](plugins/settings-sync/)

Backs up `~/.claude/` to the repo before session ends, excluding sensitive files. Bootstrap script restores settings on new VMs (Codespaces, Gitpod, cloud).

```bash
/plugin install settings-sync@bershadsky-claude-tools
```

Bootstrap: `curl -fsSL https://raw.githubusercontent.com/sergio-bershadsky/ai/main/plugins/settings-sync/scripts/bootstrap.sh | bash`

---

### [django-dev](plugins/django-dev/)

Opinionated Django patterns: 1-file-per-model, UUID PKs, soft delete, Dynaconf config, Django Ninja APIs (1-endpoint-per-file, Pydantic schemas), Unfold admin with HTMX, pytest + factory_boy testing. Code review agent for convention compliance.

```bash
/plugin install django-dev@bershadsky-claude-tools
```

**Skills:** django-dev, django-dev-ninja, django-dev-unfold, django-dev-test | **Agent:** django-review

---

### [frappe-dev](plugins/frappe-dev/)

Frappe Framework v15 with multi-layer architecture (Controller → Service → Repository → DB). DocType scaffolding, REST API endpoints, service layer patterns, app bootstrapping, pytest integration tests.

```bash
/plugin install frappe-dev@bershadsky-claude-tools
```

**Skills:** frappe-doctype, frappe-api, frappe-service, frappe-app, frappe-test

---

### [replit-prompts](plugins/replit-prompts/)

Structured prompts for Replit Agent based on Replit's 10 official guidelines. Generates optimized prompts, PRDs, and phased development plans that minimize iteration.

```bash
/plugin install replit-prompts@bershadsky-claude-tools
```

**Skills:** replit-prompt, replit-prd, replit-plan

---

### [marketplace-validator](plugins/marketplace-validator/)

Internal. Validates marketplace.json schema after every Write/Edit. Blocks the session if validation fails.

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
