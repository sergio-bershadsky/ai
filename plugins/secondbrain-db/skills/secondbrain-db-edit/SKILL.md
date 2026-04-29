---
name: secondbrain-db-edit
description: |
  Use when creating, updating, or deleting documents in an sbdb-managed
  knowledge base. Triggers on: "create a note", "add a discussion",
  "update this ADR", "edit the KB", "write a new page", "add content",
  "modify frontmatter", "create template", or any operation that writes
  to docs/ in a project with .sbdb.toml.
---

# KB Edit Skill — Integrity-First Document Operations

When editing any file in an sbdb-managed knowledge base you MUST maintain
integrity throughout. Every edit must leave the KB in a clean state.

In v2 each document is a **pair**: `<id>.md` (content + frontmatter) and a
sibling `<id>.yaml` integrity sidecar. Both are committed to git. There
is no `data/` directory and no aggregate index.

## Before any edit

1. Check this is an sbdb project:
```bash
test -f .sbdb.toml && echo "sbdb project" || echo "not managed by sbdb"
```

2. Determine if the target file is schema-managed:
```bash
sbdb schema list --format json
# Compare the path prefix against each schema's docs_dir.
```

## Creating/updating schema-managed documents

**Always use the CLI — never write `<id>.md` files directly.** The CLI
keeps the `.md` and its `<id>.yaml` sidecar in lockstep; direct writes
leave them out of sync.

```bash
# Create (preferred — handles sidecar + integrity automatically)
echo '{"id":"...","field":"value","content":"# Title\n\nBody"}' \
  | sbdb create -s <schema> --input -

# Update fields
sbdb update -s <schema> --id <id> --field key=value

# Replace body from a file
sbdb update -s <schema> --id <id> --content-file body.md

# Delete
sbdb delete -s <schema> --id <id> --yes
```

If you must use Write/Edit tools directly (e.g. for a complex markdown body
that's hard to express as a JSON string), follow the **integrity recovery
loop** below — but the plugin's PreToolUse hook will block direct writes
under `docs/` anyway, so this path rarely succeeds.

## Creating/updating untracked files

For files that don't belong to a schema (TEMPLATE.md, index.md, custom
pages outside any schema's `docs_dir`):

```bash
# Create and sign
sbdb untracked create docs/notes/TEMPLATE.md --content-file template.md

# Or sign an existing file after editing it
sbdb untracked sign docs/notes/TEMPLATE.md
```

## Integrity recovery loop (MANDATORY)

After ANY direct file edit (Write or Edit tool) to a `.md` file inside
`docs/`:

```
LOOP (max 5 iterations):
  1. Run: sbdb doctor check --format json
     (default scope = working-tree only — sees just what you edited)
  2. If exit 0 → DONE, integrity is clean
  3. If output shows ONLY frontmatter_sha / record_sha drift (no
     content_sha mismatch and no bad_sig) →
       Run: sbdb doctor fix --recompute
  4. If output shows content_sha mismatch (real content tamper) →
       The user edited the markdown body. Ask whether the change is
       intentional. If yes: sbdb doctor sign --force.
       If no: git checkout the file.
  5. If output shows bad_sig →
       The HMAC key changed or the sidecar was tampered. Ask the user.
  6. Go to step 1
```

**You MUST NOT finish your task with a non-zero doctor check.** If after
5 iterations the KB is still dirty, report the issue to the user and
ask for guidance.

## After editing untracked files

```bash
sbdb untracked sign <file-path>
```

## Rules

1. **Never skip the integrity check** — even if the edit seems trivial.
2. **Prefer sbdb CLI over direct file writes** — the CLI keeps `<id>.md`
   and `<id>.yaml` synchronised.
3. **Never edit `<id>.yaml` sidecars directly.** They're integrity
   artefacts, not user-editable.
4. **If the post-edit hook reports drift, fix it immediately** — don't
   continue with other work until integrity is restored.
5. **When creating new files in a schema's `docs_dir`**, always use
   `sbdb create` — direct Write creates an orphan `.md` with no sidecar.
6. **When creating new files outside schemas**, always use
   `sbdb untracked create` or `sbdb untracked sign`.
7. **After bulk operations**, run `sbdb doctor check --all` once at the
   end (not after every file).

## Decision tree: which tool to use?

```
Is the file part of a schema? (check: does docs_dir match?)
├── YES → Use `sbdb create / update / delete` CLI
│         → md + sidecar handled automatically
│
└── NO → Is the file already in the untracked registry?
         ├── YES → Edit via Write/Edit, then: sbdb untracked sign <path>
         │
         └── NO → Create with: sbdb untracked create <path> --content-file <file>
                  Or: write file, then: sbdb untracked sign <path>
```

## Example: Adding a new ADR

```bash
# 1. Create via CLI
echo '{"id":"ADR-0005","number":5,"title":"New Architecture","status":"draft","category":"arch","created":"2026-04-13","author":"Sergey","content":"# ADR-0005\n\n## Context\n..."}' \
  | sbdb create -s adr --input -

# 2. Verify (default scope finds your new file)
sbdb doctor check -s adr
# → exit 0
```

## Example: Editing an index page (untracked)

```bash
# 1. Write the file with the Write tool — for index pages outside any
#    schema's docs_dir, the guard hook permits this.
# 2. Sign it as untracked
sbdb untracked sign docs/index.md

# 3. Verify
sbdb doctor check
# → exit 0
```
