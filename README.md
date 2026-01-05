# Claude Code Skills & Hooks

Personal Claude Code plugin marketplace for workflow automation.

## Installation

```bash
# Add marketplace
/plugin marketplace add sergio-bershadsky/ai

# Install git plugin
/plugin install git@bershadsky-claude-tools
```

Done. The plugin includes:
- `/commit` skill — conventional commits with confirmation
- `/version` skill — bump semantic version with git tag
- `auto-stage` hook — auto-stage files after edits
- `pre-stop-commit` hook — block exit if uncommitted changes

## Plugins

| Plugin | Skills | Hooks |
|--------|--------|-------|
| git | commit, version | auto-stage, pre-stop-commit |
| settings-sync | — | backup-settings |

### Bootstrap for Ephemeral VMs

Restore Claude settings on a new VM:

```bash
curl -fsSL https://raw.githubusercontent.com/sergio-bershadsky/ai/main/plugins/settings-sync/scripts/bootstrap.sh | bash
```

## Documentation

Run locally:
```bash
npm install
npm run docs:dev
```

## License

Public domain (Unlicense)
