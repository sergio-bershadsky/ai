# Claude Code Skills & Hooks

Personal Claude Code plugin marketplace for workflow automation and development toolkits.

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
| **git** | Git workflow automation: conventional commits, auto-staging, uncommitted changes protection | commit, version | auto-stage, pre-stop-commit |
| **settings-sync** | Sync Claude settings across ephemeral VMs via Git backup | — | backup-settings |

### Development

| Plugin | Description | Skills | Agents |
|--------|-------------|--------|--------|
| **django-dev** | Opinionated Django toolkit with Ninja API, Unfold admin, pytest, Dynaconf, uv, Docker | django-dev, django-dev-ninja, django-dev-unfold, django-dev-test | django-review |
| **frappe-dev** | Frappe Framework v15 toolkit with multi-layer architecture, DocType scaffolding, REST API v2 | frappe-app, frappe-api, frappe-doctype, frappe-service, frappe-test | — |
| **marketplace-validator** | Validates marketplace.json schema after every edit | — | — (hook only) |

---

## Plugin Details

### git

Git workflow automation with safety features.

```bash
/plugin install git@bershadsky-claude-tools
```

**Skills:**
- `commit` — Conventional commits with diff preview and confirmation
- `version` — Semantic version bumping with git tags

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

Restore Claude settings on a new VM:

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
- `django-dev` — Core patterns: 1-file-per-model, Base*/Virtual*/Proxy* prefixes, UUID PKs, timestamps, soft delete, Dynaconf, uv+pyproject.toml, Docker
- `django-dev-ninja` — Django Ninja API: 1-endpoint-per-file, router organization, Pydantic schemas
- `django-dev-unfold` — Unfold admin with HTMX patterns
- `django-dev-test` — pytest-django + factory_boy patterns

**Agents:**
- `django-review` — Autonomous code reviewer for Django convention compliance

---

### frappe-dev

Professional Frappe Framework v15 development toolkit.

```bash
/plugin install frappe-dev@bershadsky-claude-tools
```

**Skills:**
- `frappe-app` — App scaffolding and project structure
- `frappe-api` — REST API v2 patterns
- `frappe-doctype` — DocType design and scaffolding
- `frappe-service` — Service layer architecture
- `frappe-test` — Testing patterns

---

### marketplace-validator

Internal plugin that validates marketplace.json schema after edits.

```bash
/plugin install marketplace-validator@bershadsky-claude-tools
```

Runs automatically via PostToolUse hook on Write/Edit operations.

---

## Documentation

Run documentation site locally:

```bash
npm install
npm run docs:dev
```

## License

Public domain (Unlicense)
