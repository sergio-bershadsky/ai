---
name: commit
description: |
  Create a git commit after completing a task. Use this skill after finishing a logical unit of work to commit changes with a detailed conventional commit message. Always confirms with user before applying the commit. Never pushes to remote. Triggers include: "commit this", "commit changes", "save my changes", "write a commit", "help me commit", "create a commit", "conventional commit", "/commit", "done with changes", "finished editing", "wrap up", "save work".
---

# Commit Skill

Create conventional commits with branch protection, semantic correlation, and user confirmation.

## When to Use

- After completing a task or logical unit of work
- When the user requests a commit
- After significant documentation updates
- After implementing a feature or fix
- When the user says they're "done", "finished editing", or wants to "wrap up"

## Procedure

### Step 1: Gather Changes

```bash
git status
git diff --stat
git diff --cached --stat
```

If there are no changes (nothing staged, modified, or untracked), inform the user and stop.

### Step 2: Branch Safety Check (mandatory)

Detect the current branch and the default branch:

```bash
git symbolic-ref --short HEAD
git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null || echo ""
```

If `refs/remotes/origin/HEAD` is not set, check whether `main` or `master` exists as fallback.

**If on the default branch:**

1. Warn the user: "You're committing directly to `<default-branch>`. Consider creating a feature branch."
2. Run Step 3 (Ticket Tracking) to check for an associated ticket before proposing a branch.
3. Detect the repo's branch naming convention by inspecting existing branches:
   ```bash
   git branch -a --format='%(refname:short)'
   ```
4. Analyze naming patterns:
   - Separator style: `/` vs `-` vs `_`
   - Type prefixes: `feat`, `fix`, `chore`, `docs`, etc.
   - Nested patterns: `user/type/desc`, `type/desc`
   - Issue ID patterns: `PROJ-123-desc`
   - Default to `type/short-description` if no clear pattern found
5. Propose a new branch name following the detected convention. If a ticket was found/created in Step 3, incorporate the ticket ID into the branch name (e.g., `feat/PROJ-123-add-auth`).
6. Ask user to: confirm the proposed name, suggest an alternative, or continue on the default branch

If the user chooses to create a branch, run:
```bash
git checkout -b <branch-name>
```

### Step 3: Ticket Tracking (when on default branch or no ticket in branch name)

Detect whether the project uses a ticket tracking system and ensure changes are associated with a ticket.

**Detection — check for ticket system indicators (in order):**

1. **GitHub/GitLab Issues** — Check if remote is GitHub/GitLab:
   ```bash
   git remote get-url origin
   ```
   If GitHub: use `gh issue list --limit 5 --state open` to confirm issues are enabled.
   If GitLab: note that GitLab issues are likely available.

2. **Jira** — Look for Jira-style ticket IDs in existing branch names (`[A-Z]+-\d+` pattern like `PROJ-123`). Check for `.jira` config or Jira URL references in the repo.

3. **Linear** — Check for Linear-style IDs in branches (`[A-Z]+-\d+` with short prefixes like `ENG-123`). Check for `linear` references in the repo.

4. **No ticket system detected** — Skip this step entirely and proceed.

**If a ticket system is detected:**

1. Check if the current changes are already associated with a ticket:
   - Parse the current branch name for a ticket ID
   - If on default branch, there is no ticket association
2. If **no ticket is associated**, analyze the changes (from Step 1) to understand their nature, then:
   - Warn: "This project uses **[system]** for tracking. No ticket is associated with these changes."
   - Propose creating a ticket first:
     - Draft a ticket title and description based on the changes
     - For GitHub: offer to run `gh issue create --title "..." --body "..."`
     - For other systems: show the suggested title/description and ask user to create it manually
   - Ask user to: **create the ticket**, **provide an existing ticket ID**, or **skip** (commit without ticket)
3. If user provides or creates a ticket, use the ticket ID when constructing the branch name in Step 2.

### Step 4: Semantic Correlation (feature branches only)

Only when on a feature branch (not the default branch):

1. Parse the branch name into tokens (split on `/`, `-`, `_`)
2. Compare tokens against the nature of the changes (file paths, change type, scope)
3. If there is **zero semantic overlap** between branch name and changes, warn:
   > "Changes appear to be about **X**, but branch `branch-name` suggests **Y**. Continue?"
4. Wait for user confirmation before proceeding

### Step 5: Analyze Changes

Identify:
- Files modified, added, or deleted
- Type of change (`feat`, `fix`, `docs`, `refactor`, `style`, `test`, `chore`)
- Scope (which module/area affected)
- Breaking changes (if any)

### Step 6: Draft Commit Message

Use conventional commits format:

```
<type>(<scope>): <short description>

<body with details>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `style`: Formatting, missing semicolons, etc.
- `test`: Adding or updating tests
- `chore`: Maintenance tasks, dependencies

If a ticket was associated in Step 3, include it in the footer (e.g., `Closes #123` or `Refs: PROJ-123`).

### Step 7: Show Diff and Confirm

Before committing, ALWAYS:

1. Show the staged diff (or unstaged diff if nothing is staged yet):
```bash
git diff --staged
```

2. Show the proposed commit message

3. Ask: "Ready to commit these changes? (yes/no)"

4. Wait for explicit user approval

### Step 8: Execute Commit (only after approval)

Stage files — prefer specific files over `git add -A`:
```bash
git add <specific-files>
git commit -m "<message>"
```

### Step 9: Verify

```bash
git log -1 --stat
```

## Rules

1. **NEVER push** — Only commit locally, never run `git push`
2. **ALWAYS confirm** — Never commit without explicit user approval
3. **Show diff first** — User must see changes before approving
4. **One logical unit** — Each commit should represent one complete change
5. **Conventional format** — Always use type(scope): description format
6. **Branch safety** — Always check if on default branch before committing
7. **Ticket alignment** — If project has ticket tracking, ensure changes are associated with a ticket
8. **Semantic alignment** — Warn if changes don't match branch purpose
9. **Proactive suggestion** — After completing edits, suggest committing

## Output Format

```
## Proposed Commit

**Branch:** feat/add-auth
**Type:** feat
**Scope:** auth
**Files:**
- src/auth/reset.ts (new)
- src/components/ResetForm.tsx (new)
- src/api/routes.ts (modified)

**Message:**
feat(auth): add password reset flow

- Add forgot password endpoint
- Implement email verification token
- Add password reset form component

Closes #123

**Diff summary:**
3 files changed, 245 insertions(+)

---
Ready to commit these changes?
```
