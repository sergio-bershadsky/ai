# Settings Sync Plugin

Sync Claude settings across ephemeral VMs via Git backup.

## Installation

```bash
claude mcp add-from-marketplace bershadsky-claude-tools/settings-sync
```

## Overview

This plugin automatically backs up your Claude settings to Git when sessions end, and provides a bootstrap script to restore them on new machines.

## How It Works

```
Session End → Backup Hook → Git Commit
                    ↓
New VM → Bootstrap Script → Restore Settings
```

## Features

### Automatic Backup (on session end)

Backs up from `~/.claude/`:
- `settings.json`
- `plugins/`
- `projects/`
- `ide/`
- `commands/`

**Backup Location:** `.claude-backup/` in your repository

**Excluded (security):**
- `*.log`
- `*.jsonl`
- `credentials*`
- `auth*`
- `token*`
- `secret*`

### One-Command Restore

Restore settings on a new VM:

```bash
curl -fsSL https://raw.githubusercontent.com/sergio-bershadsky/ai/main/plugins/settings-sync/scripts/bootstrap.sh | bash
```

This will:
1. Clone the repository (shallow, sparse checkout)
2. Restore backed-up settings to `~/.claude/`

## Hooks

### Backup Settings (Stop)

- **Trigger:** Session end
- **Action:** Copies settings to `.claude-backup/`
- **Behavior:** Non-blocking (always allows exit)

## Use Cases

- **Ephemeral Development Environments** - Codespaces, Gitpod, Cloud IDEs
- **Multiple Machines** - Keep settings consistent across devices
- **Team Onboarding** - Share project-specific settings

## Security

- Credentials, tokens, and secrets are automatically excluded
- `.gitignore` is created in backup directory
- Only configuration files are synced

## License

[Unlicense](LICENSE) - Public Domain
