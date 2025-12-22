# Claude Settings Backup

This directory contains backed up Claude settings from `~/.claude/`.

## Backed up items

- `settings.json` - Claude configuration
- `plugins/` - Installed plugins
- `projects/` - Project-specific settings
- `ide/` - IDE integration settings
- `commands/` - Custom slash commands

## Excluded (sensitive)

- `*.log`, `*.jsonl` - Logs and history
- `credentials*`, `auth*`, `token*`, `secret*` - Sensitive data

## Restore on new VM

```bash
curl -fsSL https://raw.githubusercontent.com/sergio-bershadsky/ai/main/plugins/settings-sync/scripts/bootstrap.sh | bash
```
