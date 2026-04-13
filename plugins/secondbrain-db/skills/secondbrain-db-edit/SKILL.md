---
name: secondbrain-db-edit
description: |
  Use when creating, updating, or deleting documents in an sbdb-managed knowledge base.
  Triggers on: "create a note", "add a discussion", "update this ADR", "edit the KB",
  "write a new page", "add content", "modify frontmatter", "create template",
  or any operation that writes to docs/ or data/ in a project with .sbdb.toml.
---

# KB Edit Skill — Integrity-First Document Operations

When editing any file in an sbdb-managed knowledge base, you MUST maintain integrity throughout. Every edit must leave the KB in a clean state.

## Before any edit

1. Check if this is an sbdb project:
```bash
test -f .sbdb.toml && echo "sbdb project" || echo "not managed by sbdb"
```

2. Determine if the target file is schema-managed or untracked:
```bash
sbdb schema list --format json
```

## Creating/updating schema-managed documents

**Always use the CLI — never write .md files directly:**

```bash
# Create (preferred — handles records.yaml + integrity automatically)
echo '{"id":"...","field":"value","content":"# Title\n\nBody"}' | sbdb create -s <schema> --input -

# Update
sbdb update -s <schema> --id <id> --field key=value

# Update body
sbdb update -s <schema> --id <id> --content-file body.md
```

If you must use Write/Edit tools directly (e.g. for complex markdown body), follow the **integrity recovery loop** below.

## Creating/updating untracked files

For files that don't belong to a schema (TEMPLATE.md, index.md, custom pages):

```bash
# Create and sign
sbdb untracked create docs/notes/TEMPLATE.md --content-file template.md

# Or sign an existing file after editing it
sbdb untracked sign docs/notes/TEMPLATE.md
```

## Integrity recovery loop (MANDATORY)

After ANY direct file edit (Write or Edit tool) to a .md or .yaml file in docs/ or data/:

```
LOOP (max 5 iterations):
  1. Run: sbdb doctor check --format json
  2. If exit 0 → DONE, integrity is clean
  3. If exit 4 (drift) → Run: sbdb doctor fix --recompute
  4. If exit 6 (tamper) → Run: sbdb doctor sign --force
  5. If exit 7 (both) → Run: sbdb doctor fix --recompute, then sbdb doctor sign --force
  6. Go to step 1
```

**You MUST NOT finish your task with a non-zero doctor check.** If after 5 iterations the KB is still dirty, report the issue to the user and ask for guidance.

## After editing untracked files

```bash
# Re-sign the file you edited
sbdb untracked sign <file-path>
```

## Rules

1. **Never skip the integrity check** — even if the edit seems trivial
2. **Prefer sbdb CLI over direct file writes** — the CLI handles records.yaml + integrity automatically
3. **If the hook reports an error, fix it immediately** — don't continue with other work until integrity is restored
4. **When creating new files in a schema's docs_dir**, always use `sbdb create` — direct Write creates an orphan file that's not in records.yaml
5. **When creating new files outside schemas**, always use `sbdb untracked create` or `sbdb untracked sign`
6. **Never delete the integrity manifest** (data/<entity>/.integrity.yaml or data/.untracked.yaml)
7. **After bulk operations**, run `sbdb doctor check` once at the end, not after every file

## Decision tree: which tool to use?

```
Is the file part of a schema? (check: does docs_dir match?)
├── YES → Use sbdb create/update/delete CLI
│         → integrity handled automatically
│
└── NO → Is the file already tracked?
         ├── YES (in .untracked.yaml) → Edit with Write/Edit, then: sbdb untracked sign <path>
         │
         └── NO → Create with: sbdb untracked create <path> --content-file <file>
                  Or: write file, then: sbdb untracked sign <path>
```

## Example: Adding a new ADR

```bash
# 1. Create via CLI (preferred)
echo '{"id":"ADR-0005","number":5,"title":"New Architecture","status":"draft","category":"arch","created":"2026-04-13","author":"Sergey Bershadsky","content":"# ADR-0005: New Architecture\n\n## Status\n**Current:** Draft\n\n## Context\n..."}' | sbdb create -s decisions --input -

# 2. Verify
sbdb doctor check -s decisions
# → exit 0
```

## Example: Editing an index page

```bash
# 1. Write the file
# (use Write tool to create docs/notes/index.md)

# 2. Sign it as untracked
sbdb untracked sign docs/notes/index.md

# 3. Verify
sbdb doctor check
# → exit 0
```
