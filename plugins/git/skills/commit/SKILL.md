---
name: commit
description: |
  This skill should be used when the user asks to commit changes, wants help writing commit messages, or has finished a task and needs to save their work. Triggers include: "commit this", "commit changes", "save my changes", "write a commit", "help me commit", "create a commit", "conventional commit", "/commit". Always confirms with user before committing. Never pushes to remote.
---

# Commit Skill

Create conventional commits after task completion with user confirmation.

## When to Use

- After completing a task or logical unit of work
- When the user requests a commit
- After significant documentation updates
- After implementing a feature or fix

## Procedure

### Step 1: Gather Changes

```bash
git status
git diff --stat
```

### Step 2: Analyze Changes

Identify:
- Files modified, added, or deleted
- Type of change (feat, fix, docs, refactor, style, test, chore)
- Scope (which module/area affected)
- Breaking changes (if any)

### Step 3: Draft Commit Message

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

**Example:**
```
feat(auth): add password reset flow

- Add forgot password endpoint
- Implement email verification token
- Add password reset form component

Closes #123
```

### Step 4: Show Diff and Confirm

Before committing, ALWAYS:

1. Show the user what will be committed:
```bash
git diff --staged  # or git diff if not staged
```

2. Show the proposed commit message

3. Ask: "Ready to commit these changes? (yes/no)"

4. Wait for explicit user approval

### Step 5: Execute Commit (only after approval)

```bash
git add -A  # or specific files
git commit -m "<message>"
```

### Step 6: Verify

```bash
git log -1 --stat
```

## Rules

1. **NEVER push** — Only commit locally, never run `git push`
2. **ALWAYS confirm** — Never commit without explicit user approval
3. **Show diff first** — User must see changes before approving
4. **One logical unit** — Each commit should represent one complete change
5. **Conventional format** — Always use type(scope): description format

## Output Format

```
## Proposed Commit

**Type:** feat
**Scope:** auth
**Files:**
- src/auth/reset.ts (new)
- src/components/ResetForm.tsx (new)
- src/api/routes.ts (modified)

**Message:**
```
feat(auth): add password reset flow

- Add forgot password endpoint
- Implement email verification token
- Add password reset form component

Closes #123
```

**Diff summary:**
3 files changed, 245 insertions(+)

---
Ready to commit these changes?
```
