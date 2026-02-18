# commit

Create conventional commits with branch protection, semantic correlation, and user confirmation.

**Location:** `git/skills/commit/SKILL.md`
**Type:** Skill

## When to Use

- After completing a task or logical unit of work
- When the user requests a commit
- After significant documentation updates
- After implementing a feature or fix
- When saying "done", "finished editing", or "wrap up"

## Installation

```bash
/plugin install git@bershadsky-claude-tools
```

## Usage

```
/commit
```

## Procedure

1. **Gather Changes** - Run `git status`, `git diff --stat`, `git diff --cached --stat`
2. **Branch Safety Check** - Detect current and default branch; warn if on default
3. **Ticket Tracking** - Detect ticket system, ensure changes are associated with a ticket
4. **Semantic Correlation** - Compare branch name tokens against change nature (feature branches only)
5. **Analyze** - Identify type, scope, and breaking changes
6. **Draft Message** - Use conventional commit format (include ticket ref in footer)
7. **Show Diff** - Present changes and message to user
8. **Wait for Confirmation** - Never commit without approval
9. **Verify** - Show `git log -1 --stat`

## Branch Protection

When committing on the default branch (`main`/`master`), the skill:

1. Warns the user about committing directly to the default branch
2. Checks for ticket tracking (see below) before proposing a branch
3. Inspects existing branches to detect naming conventions:
   - Separator style (`/` vs `-` vs `_`)
   - Type prefixes (`feat`, `fix`, `chore`, `docs`)
   - Nested patterns (`user/type/desc`)
   - Issue ID patterns (`PROJ-123-desc`)
4. Proposes a new branch name following the detected convention, incorporating ticket ID if available
5. Asks user to confirm, suggest alternative, or continue on default

## Ticket Tracking

When on the default branch or when the branch name contains no ticket ID, the skill checks for a project ticket system:

1. **GitHub/GitLab Issues** - Detected via remote URL; confirmed with `gh issue list`
2. **Jira** - Detected via `[A-Z]+-\d+` patterns in existing branches or `.jira` config
3. **Linear** - Detected via Linear-style IDs in branches or `linear` references

If a ticket system is detected and no ticket is associated:
- Warns the user and proposes creating a ticket based on the changes
- For GitHub: offers to run `gh issue create`
- For others: shows suggested title/description for manual creation
- User can: create the ticket, provide an existing ticket ID, or skip

## Semantic Correlation

When on a feature branch, the skill checks whether changes match the branch purpose:

1. Parses branch name into tokens (split on `/`, `-`, `_`)
2. Compares tokens against file paths, change type, and scope
3. If zero overlap, warns: "Changes appear to be about **X**, but branch suggests **Y**"
4. Waits for user confirmation before proceeding

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
6. **Branch safety** — Always check for default branch before committing
7. **Ticket alignment** — If project has ticket tracking, ensure changes are associated with a ticket
8. **Semantic alignment** — Warn if changes don't match branch purpose
9. **Proactive suggestion** — After completing edits, suggest committing
