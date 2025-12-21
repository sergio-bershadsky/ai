# auto-stage

Auto-stage files after Write/Edit/Bash operations.

**Location:** `git/hooks/auto-stage.py`
**Type:** Hook
**Trigger:** PostToolUse (Write, Edit, Bash)

## What It Does

Automatically runs `git add` on files modified by Claude Code, so you don't have to manually stage changes before committing.

## Behavior

| Tool | Action |
|------|--------|
| Write | Stage the created/modified file |
| Edit | Stage the edited file |
| Bash | Stage files if command modifies files (chmod, mv, cp, etc.) |

## Installation

```bash
/plugin install git@bershadsky-claude-tools
```

Hook is automatically configured when plugin is installed.

## Debug Mode

Enable debug logging:

```bash
export CLAUDE_HOOK_DEBUG=1
```

Logs are written to `.claude/hook-debug.log`.

## Supported Bash Commands

The hook detects these file-modifying commands:

- `chmod`, `chown`
- `touch`, `mv`, `cp`, `ln`
- `sed`, `awk`
- `truncate`, `install`
