# Claude Code Skills & Hooks

Personal Claude Code plugin marketplace for workflow automation.

## Installation

```bash
# Add marketplace
/plugin marketplace add bershadsky/ai

# Install git plugin
/plugin install git@bershadsky-claude-tools
```

Done. The plugin includes:
- `/commit` skill — conventional commits with confirmation
- `auto-stage` hook — auto-stage files after edits
- `pre-stop-commit` hook — block exit if uncommitted changes

## Plugins

| Plugin | Skills | Hooks |
|--------|--------|-------|
| git | commit | auto-stage, pre-stop-commit |

## Documentation

Run locally:
```bash
npm install
npm run docs:dev
```

## License

Public domain (Unlicense)
