# Settings Sync Plugin

Sync Claude settings across ephemeral VMs via Git backup.

## Installation

```bash
/plugin marketplace add sergio-bershadsky/ai
/plugin install settings-sync@bershadsky-claude-tools
```

## Overview

This plugin copies your Claude settings into the current repository after every Claude turn (the `Stop` hook), and provides a bootstrap script to restore them on a new machine. It does not commit or push — committing `.claude-backup/` is up to you.

## How It Works

```
Claude turn ends → Backup Hook → .claude-backup/ (you commit + push)
                                        ↓
New VM → Bootstrap Script → Restore Settings
```

## Features

### Automatic Backup (after every turn)

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

**Limitation:** `bootstrap.sh` hard-codes `REPO_URL=https://github.com/sergio-bershadsky/ai.git`, so the
one-liner above restores from this marketplace repo. To restore your own backup, download the script and
change `REPO_URL` to your repository first.

## Hooks

### Backup Settings (Stop)

- **Trigger:** `Stop` — every time Claude finishes a turn
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
