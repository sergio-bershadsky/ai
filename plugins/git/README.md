# Git Plugin

Git workflow automation with conventional commits, auto-staging, and uncommitted changes protection.

## Installation

```bash
claude mcp add-from-marketplace bershadsky-claude-tools/git
```

## Features

- **Conventional Commits** - Structured commit messages with user confirmation
- **Auto-staging** - Automatically stages files after Write/Edit/Bash operations
- **Protected Exit** - Prevents session exit with uncommitted changes
- **Version Bumping** - Semantic versioning with git tags

## Skills

### /commit

Create conventional commits after completing work.

```
/commit
```

**Workflow:**
1. Analyzes staged/unstaged changes
2. Drafts conventional commit message
3. Shows diff for review
4. Commits after user approval

**Commit Types:** `feat`, `fix`, `docs`, `refactor`, `style`, `test`, `chore`

**Rules:**
- Never pushes to remote
- Always requires user confirmation
- Shows diff before committing

### /version

Bump semantic versions for plugins.

```
/version [bump-type] [plugin-name]
```

**Arguments:**
- `bump-type`: `major`, `minor`, `patch` (default: patch)
- `plugin-name`: Auto-detects or prompts

**Examples:**
```
/version              # Patch bump, auto-detect plugin
/version minor        # Minor bump
/version major git    # Major bump for git plugin
```

**Actions:**
- Updates `plugin.json` version
- Updates `marketplace.json` version
- Creates annotated git tag (`v1.2.3-plugin-name`)

## Hooks

### Auto-Stage (PostToolUse)

Automatically stages modified files after:
- `Write` - Files written by Claude
- `Edit` - Files edited by Claude
- `Bash` - Files modified by shell commands (chmod, mv, cp, etc.)

### Pre-Stop Commit (Stop)

Blocks session exit if uncommitted changes exist:
- Lists staged, modified, and untracked files
- Shows diff summary
- Suggests running `/commit`

**Exit Codes:**
- `0` - No changes, allow exit
- `2` - Changes detected, block exit

## Environment Variables

| Variable | Description |
|----------|-------------|
| `CLAUDE_HOOK_DEBUG=1` | Enable debug logging to `.claude/hook-debug.log` |

## License

[Unlicense](LICENSE) - Public Domain
