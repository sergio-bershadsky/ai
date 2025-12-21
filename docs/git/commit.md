# commit

Create conventional commits after task completion with user confirmation.

**Location:** `git/skills/commit/SKILL.md`
**Type:** Skill

## When to Use

- After completing a task or logical unit of work
- When the user requests a commit
- After significant documentation updates
- After implementing a feature or fix

## Installation

```bash
/plugin install git@bershadsky-claude-tools
```

## Usage

```
/commit
```

## Procedure

1. **Gather Changes** - Run `git status` and `git diff --stat`
2. **Analyze** - Identify type, scope, and breaking changes
3. **Draft Message** - Use conventional commit format
4. **Show Diff** - Present changes and message to user
5. **Wait for Confirmation** - Never commit without approval
6. **Execute** - Run `git add` and `git commit`
7. **Verify** - Show `git log -1 --stat`

## Commit Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `style` | Formatting, missing semicolons, etc. |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks, dependencies |

## Message Format

```
<type>(<scope>): <short description>

<body with details>

<footer>
```

## Rules

1. **NEVER push** — Only commit locally, never run `git push`
2. **ALWAYS confirm** — Never commit without explicit user approval
3. **Show diff first** — User must see changes before approving
4. **One logical unit** — Each commit should represent one complete change
5. **Conventional format** — Always use type(scope): description format
