---
name: secondbrain-review
description: |
  This skill should be used when the user asks to "review page", "stamp as reviewed",
  "mark reviewed", "review documentation", "add review stamp", "mark page as checked",
  or mentions wanting to track who has reviewed a documentation page and when.
---

# Review Stamp Skill

Mark a documentation page as reviewed by appending a `{date, name}` entry to the `reviewed_by` list in frontmatter. Multiple reviewers accumulate over time.

## Usage

```
/secondbrain-review <page-path> [reviewer]
```

- `page-path` — path to the markdown file (e.g., `docs/guides/setup.md`)
- `reviewer` — optional full name; defaults to `review.default_reviewer` from `.claude/data/config.yaml`, or prompts user if not configured

## Prerequisites

Verify the project has a `.claude/data/config.yaml` with a `review` section:

```yaml
review:
  default_reviewer: "Jane Smith"
  thresholds:
    fresh_days: 30
    aging_days: 90
```

If the `review` section is missing, ask the user if they want to add it and configure a default reviewer name.

## Frontmatter Format

```yaml
---
reviewed_by:
  - date: 2026-02-13
    name: Jane Smith
  - date: 2026-02-14
    name: John Doe
---
```

Each review is an entry with `date` (YYYY-MM-DD) and `name` (full name). The list grows over time — never remove previous entries.

## Procedure

### Step 1: Parse Arguments

Extract the page path from the first argument. If a second argument is provided, use it as the reviewer name. Otherwise:
1. Read `review.default_reviewer` from `.claude/data/config.yaml`
2. If that is `null` or missing, check the `team` section in config for a single member to use
3. If still unresolved, ask the user for the reviewer name

### Step 2: Read the File

Read the target file. Verify it exists and is a markdown file under the `docs/` directory.

### Step 3: Update Frontmatter

**If the file has `reviewed_by` as a list** — append a new entry with today's date and the reviewer name. Do not add a duplicate if the same person already reviewed on the same date.

**If the file has legacy format** (`reviewed_by: "Name"` + `last_reviewed: date`) — convert to the list format, preserving the existing review as the first entry, then append the new one. Remove the `last_reviewed` field.

**If the file has no `reviewed_by`** — add a `reviewed_by` list to frontmatter containing one entry. If there is no frontmatter at all, add a frontmatter block.

### Step 4: Show Diff and Confirm

Show the user the exact changes that will be made (old vs new frontmatter). Wait for explicit user approval before writing.

### Step 5: Write the File

Apply the frontmatter changes using the Edit tool.

### Step 6: Confirm Completion

Show a summary:
```
Reviewed: docs/guides/setup.md
Reviewer: Jane Smith
Date: 2026-03-30
Total reviews: 3
```

## Examples

```
/secondbrain-review docs/guides/setup.md
# Appends: - date: 2026-03-30
#            name: Jane Smith (from config default)

/secondbrain-review docs/architecture/overview.md "John Doe"
# Appends: - date: 2026-03-30
#            name: John Doe
```

Adding a second review to an already-reviewed page:
```yaml
# Before:
reviewed_by:
  - date: 2026-01-15
    name: Jane Smith

# After /secondbrain-review page.md "John Doe":
reviewed_by:
  - date: 2026-01-15
    name: Jane Smith
  - date: 2026-03-30
    name: John Doe
```

## Mandatory Rules

- **Always use full names** in review entries — never use aliases or first names only. If a `team` section exists in config, resolve aliases to full names.
- **Never remove existing entries** — the review list is append-only.
- **No duplicate same-day reviews** — if the same person already has an entry for today's date, skip adding.

## Notes

- The `ReviewBadge` component in the VitePress theme automatically renders review status from the `reviewed_by` list
- Staleness thresholds are configurable in `config.yaml` under `review.thresholds`:
  - **fresh**: 0 to `fresh_days` (default 30) — green
  - **aging**: `fresh_days` to `aging_days` (default 90) — yellow
  - **stale**: beyond `aging_days` — orange
- Badge shows reviewer count when multiple reviews exist (e.g., "Reviewed Mar 30, 2026 by John Doe (3 reviews)")
- Legacy format (`reviewed_by: string` + `last_reviewed`) is supported for backwards compatibility
- Review stamps are orthogonal to the freshness system — they track human review quality, while `/secondbrain-freshness` tracks entity record currency
