# pre-stop-commit

Block Claude from stopping if there are uncommitted changes.

**Location:** `git/hooks/pre-stop-commit.py`
**Type:** Hook
**Trigger:** Stop

## What It Does

Prevents Claude from ending a session with uncommitted work. Checks for:

- Staged changes
- Unstaged modifications
- Untracked files

If any exist, blocks stopping and prompts to run `/commit`.

## Behavior

| Condition | Action |
|-----------|--------|
| No changes | Allow stop (exit 0) |
| Any changes | Block stop (exit 2), show summary |

## Output Example

```
Uncommitted changes detected. Please commit before stopping.

**Staged (2 files):**
  - src/main.ts
  - README.md

**Modified (1 files):**
  - package.json

**Diff summary:**
 2 files changed, 45 insertions(+), 3 deletions(-)

Run `/commit` to review and commit these changes.
```

## Installation

```bash
/plugin install git@bershadsky-claude-tools
```

Hook is automatically configured when plugin is installed.
