# Settings Sync Plugin

Backup and restore Claude settings across ephemeral VMs.

## Installation

```bash
/plugin marketplace add sergio-bershadsky/ai
/plugin install settings-sync@bershadsky-claude-tools
```

## Features

### Auto Backup

After every Claude turn (`Stop` hook), copies `~/.claude/` into `.claude-backup/` in the current repo. Committing and pushing it is up to you:

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

`bootstrap.sh` hard-codes `REPO_URL` to this marketplace repo; to restore your own backup, download it and set `REPO_URL` to your repository.

## Hooks

| Hook | Event | Description |
|------|-------|-------------|
| backup-settings | Stop (every turn) | Copies ~/.claude to .claude-backup/ (no commit) |

## Use Case

Perfect for:

- **Codespaces** — Settings restored on every rebuild
- **GitPod** — Consistent config across workspaces
- **Docker dev containers** — Persistent settings in ephemeral environments
- **CI/CD** — Pre-configured Claude for automation
