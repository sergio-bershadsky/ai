# Git Plugin

Git workflow automation.

## Installation

```bash
/plugin install git@bershadsky-claude-tools
```

## Skills

| Name | Description |
|------|-------------|
| [commit](/git/commit) | Create conventional commits with user confirmation |
| [version](/git/version) | Bump semantic version with git tag |

## Hooks

| Name | Trigger | Description |
|------|---------|-------------|
| [auto-stage](/git/auto-stage) | PostToolUse | Auto-stage files after Write/Edit |
| [pre-stop-commit](/git/pre-stop-commit) | Stop | Block exit if uncommitted changes |
