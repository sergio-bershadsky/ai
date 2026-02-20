# Git Plugin

Git workflow automation with conventional commits, branch protection, semantic correlation.

## Installation

```bash
claude mcp add-from-marketplace bershadsky-claude-tools/git
```

## Features

- **Conventional Commits** - Structured commit messages with user confirmation
- **Branch Protection** - Warns when committing to default branch, proposes feature branches using repo naming conventions
- **Ticket Tracking** - Detects project ticket system (GitHub Issues, Jira, Linear), ensures changes are associated with a ticket, proposes creating tickets when missing
- **Semantic Correlation** - Detects mismatches between branch name and change content

## Skills

### /commit

Create conventional commits with branch safety and semantic awareness.

```
/commit
```

**Workflow:**
1. Gathers staged/unstaged changes
2. Checks if on default branch — warns and proposes feature branch
3. Detects ticket tracking system — ensures changes have an associated ticket
4. Validates semantic alignment between branch name and changes
5. Analyzes changes and drafts conventional commit message
6. Shows diff for review
7. Commits after user approval
8. Verifies with `git log`

**Branch Protection:**
- Detects default branch (`main`/`master`)
- Inspects existing branches to detect naming conventions
- Proposes new branch name following repo patterns, incorporating ticket ID if available
- User can confirm, suggest alternative, or continue on default

**Ticket Tracking:**
- Detects GitHub Issues, Jira, or Linear from remote URL and branch patterns
- Warns if no ticket is associated with the changes
- Proposes creating a ticket (auto-creates for GitHub via `gh issue create`)
- Incorporates ticket ID into branch name and commit footer

**Semantic Correlation:**
- Parses feature branch name into tokens
- Compares against change nature (file paths, commit type)
- Warns if changes don't match branch purpose

**Commit Types:** `feat`, `fix`, `docs`, `refactor`, `style`, `test`, `chore`

**Rules:**
- Never pushes to remote
- Always requires user confirmation
- Shows diff before committing

## License

[Unlicense](LICENSE) - Public Domain
