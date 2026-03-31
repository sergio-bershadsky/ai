# Claude Code Plugin Marketplace

Personal plugin marketplace for Claude Code — skills, hooks, and agents for workflow automation and development toolkits.

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
