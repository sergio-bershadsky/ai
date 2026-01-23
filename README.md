# Claude Code Skills & Hooks

Personal Claude Code plugin marketplace for workflow automation and development toolkits.

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
| [**secondbrain**](plugins/secondbrain/) | Knowledge base scaffolding with microdatabases, VitePress portal, semantic search | 9 skills | freshness, sidebar, search-index |
| [**replit-prompts**](plugins/replit-prompts/) | Optimized prompts, PRDs, and task plans for Replit Agent | 3 skills | — |

### Internal

| Plugin | Description |
|--------|-------------|
| [**marketplace-validator**](plugins/marketplace-validator/) | Validates marketplace.json schema after every edit |

---

## Plugin Details

### git

Git workflow automation with safety features.

```bash
/plugin install git@bershadsky-claude-tools
```

**Skills:**
- `/commit` — Conventional commits with diff preview and confirmation
- `/version` — Semantic version bumping with git tags

**Hooks:**
- `auto-stage` — Auto-stage files after Write/Edit operations
- `pre-stop-commit` — Block session exit if uncommitted changes exist

---

### settings-sync

Sync Claude Code settings across ephemeral VMs.

```bash
/plugin install settings-sync@bershadsky-claude-tools
```

**Bootstrap for Ephemeral VMs:**

```bash
curl -fsSL https://raw.githubusercontent.com/sergio-bershadsky/ai/main/plugins/settings-sync/scripts/bootstrap.sh | bash
```

---

### django-dev

Opinionated Django development patterns enforcing consistency and production-ready code.

```bash
/plugin install django-dev@bershadsky-claude-tools
```

**Skills:**
- `django-dev` — Core patterns: 1-file-per-model, Base*/Virtual*/Proxy* prefixes, UUID PKs, timestamps, soft delete, Dynaconf
- `django-dev-ninja` — Django Ninja API: 1-endpoint-per-file, router organization, Pydantic schemas
- `django-dev-unfold` — Unfold admin with HTMX patterns
- `django-dev-test` — pytest-django + factory_boy patterns

**Agents:**
- `django-review` — Code reviewer for Django convention compliance

---

### frappe-dev

Professional Frappe Framework v15 development toolkit.

```bash
/plugin install frappe-dev@bershadsky-claude-tools
```

**Skills:**
- `frappe-app` — App scaffolding with multi-layer architecture
- `frappe-api` — REST API v2 endpoints
- `frappe-doctype` — DocType with controller, service, repository
- `frappe-service` — Service layer patterns
- `frappe-test` — Testing with pytest and factories

---

### secondbrain

Knowledge base scaffolding with microdatabases and semantic search.

```bash
/plugin install secondbrain@bershadsky-claude-tools
```

**Skills:**
- `secondbrain-init` — Scaffold new knowledge base project
- `secondbrain-search` — Semantic search (qmd + Orama)
- `secondbrain-adr` — Architecture Decision Records
- `secondbrain-note` — Knowledge capture notes
- `secondbrain-task` — Action item tracking
- `secondbrain-discussion` — Meeting/conversation documentation
- `secondbrain-freshness` — Stale content detection
- `secondbrain-entity` — Custom entity types

**Search Options:**
| Engine | For | Technology |
|--------|-----|------------|
| qmd | Claude Code | SQLite + embedding-gemma |
| Orama | VitePress | JSON + gte-small (browser) |

---

### replit-prompts

Generate optimized prompts for Replit Agent based on official Replit documentation.

```bash
/plugin install replit-prompts@bershadsky-claude-tools
```

**Skills:**
- `replit-prompt` — Transform vague ideas into structured prompts
- `replit-prd` — Comprehensive Product Requirements Documents
- `replit-plan` — Phased development plans with checkpoints

---

### marketplace-validator

Internal plugin that validates marketplace.json schema after edits.

Runs automatically via PostToolUse hook on Write/Edit operations.

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
