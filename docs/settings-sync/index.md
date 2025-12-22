# Settings Sync Plugin

Backup and restore Claude settings across ephemeral VMs.

## Installation

```bash
/plugin install settings-sync@bershadsky-claude-tools
```

## Features

### Auto Backup

On every session stop, automatically backs up `~/.claude/` to `.claude-backup/` in your repo:

- `settings.json` — Claude configuration
- `plugins/` — Installed plugins
- `projects/` — Project-specific settings
- `ide/` — IDE integration settings
- `commands/` — Custom slash commands

Sensitive files (credentials, tokens, logs) are excluded.

### Bootstrap Script

Restore settings on a new VM:

```bash
curl -fsSL https://raw.githubusercontent.com/sergio-bershadsky/ai/main/plugins/settings-sync/scripts/bootstrap.sh | bash
```

## Hooks

| Hook | Event | Description |
|------|-------|-------------|
| backup-settings | Stop | Backs up ~/.claude to .claude-backup/ |

## Use Case

Perfect for:

- **Codespaces** — Settings restored on every rebuild
- **GitPod** — Consistent config across workspaces
- **Docker dev containers** — Persistent settings in ephemeral environments
- **CI/CD** — Pre-configured Claude for automation
