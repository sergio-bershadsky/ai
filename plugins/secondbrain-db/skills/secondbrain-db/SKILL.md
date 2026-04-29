---
name: secondbrain-db
description: |
  Use when the user works with a markdown knowledge base (VitePress, Docusaurus, Obsidian, Jekyll)
  backed by YAML frontmatter and per-doc sidecar integrity files. Applies when a .sbdb.toml or
  schemas/*.yaml file is present in the project, or when the user mentions "sbdb",
  "knowledge base", "knowledge graph", "doctor check", "drift", "tamper", "sidecar", or
  "semantic search". Also covers embedding sbdb as a Go library via the public pkg/sbdb API.
---

# secondbrain-db

`sbdb` v2 is a file-backed knowledge base ORM with per-md sidecar integrity, YAML schemas,
Starlark virtual fields, HMAC signing, and a SQLite-backed knowledge graph.

It ships as **two products from the same codebase**:
- The `sbdb` CLI (a single static binary).
- An embeddable Go library at `github.com/sergio-bershadsky/secondbrain-db/pkg/sbdb`.

## Storage layout (v2, important)

For each document there are exactly two files, sibling to each other:

```
docs/<entity>/<id>.md      ← markdown body + YAML frontmatter
docs/<entity>/<id>.yaml    ← per-doc integrity sidecar (SHAs + optional HMAC)
```

There is **no `data/` directory** — that was v1. v2 has no aggregate
`records.yaml` or `.integrity.yaml`. The frontmatter is the source of
truth; queries walk `docs_dir` and parse it concurrently.

Two parallel PRs adding two different documents touch disjoint files —
they merge with zero git conflict. This is the central reason v2 exists.

## Prerequisites

```bash
which sbdb || echo "NOT INSTALLED"
test -f .sbdb.toml && echo "sbdb project" || echo "not an sbdb project"
```

If sbdb is missing:
- macOS/Linux: `go install github.com/sergio-bershadsky/secondbrain-db@latest`
- Or download from https://github.com/sergio-bershadsky/secondbrain-db/releases (v2.0.0+)

If the project is on the v1 layout (has a `data/` directory), run:
```bash
sbdb doctor migrate
```
The migration is idempotent — safe to re-run.

## Core commands

| Task | Command |
|------|---------|
| Initialize project (bare scaffold) | `sbdb init` |
| List schemas | `sbdb schema list` |
| Show schema | `sbdb schema show -s <name> --format json` |
| Create document | `sbdb create -s <schema> --input -` (JSON on stdin) |
| Get document | `sbdb get -s <schema> --id <id> --format json` |
| List documents | `sbdb list -s <schema> --format json` |
| Query documents | `sbdb query -s <schema> --filter key=value --format json` |
| Search (grep) | `sbdb search "phrase"` |
| Search (semantic) | `sbdb search "phrase" --semantic --k 10` |
| Update document | `sbdb update -s <schema> --id <id> --field key=value` |
| Delete document | `sbdb delete -s <schema> --id <id> --yes` |
| Check integrity (uncommitted) | `sbdb doctor check` |
| Check integrity (full audit) | `sbdb doctor check --all` |
| Fix drift | `sbdb doctor fix --recompute` |
| Re-sign after intentional edit | `sbdb doctor sign --force` |
| Migrate v1 → v2 layout | `sbdb doctor migrate` |
| Build KG index | `sbdb index build` |
| Build KG (crawl mode) | `sbdb index build --crawl` |
| Graph neighbors | `sbdb graph neighbors --id <id> --depth 2` |
| Graph export | `sbdb graph export --export-format json` |
| Emit events from git | `sbdb events emit <commit-from> [<commit-to>]` |

## Doctor scope (default: working-tree only)

`sbdb doctor check` and `fix` and `sign` default to scanning ONLY files
that differ from `HEAD` — modified, staged, untracked under any
schema's `docs_dir`. Pass `--all` for a full audit.

Premise: committed history was already verified, so re-scanning thousands
of clean files on every invocation is wasteful. `--all` is for periodic
audits (CI cron) or recovery scenarios.

Outside a git repo, doctor falls back to `--all` automatically with a
stderr notice.

## Exit codes

- `0` — success / clean
- non-zero — error (drift detected, validation failed, etc.); the JSON
  output enumerates per-doc causes

For doctor check specifically, drift causes are:
`content_sha mismatch`, `frontmatter_sha mismatch`, `record_sha mismatch`,
`bad_sig`, `missing-sidecar`, `missing-md`.

## When creating documents

Always use `--format json` for structured output. Build the JSON payload
using the schema:

```bash
# Discover the schema first
sbdb schema show -s notes --format json

# Then create
echo '{"id":"my-doc","created":"2026-04-08","content":"# Title\n\nBody."}' \
  | sbdb create -s notes --input -
```

## When the user edits files manually

After any hand-edit to `.md` files inside `docs/`:
1. Run `sbdb doctor check` (default scope finds it).
2. If `content_sha mismatch`: ask the user whether to `sbdb doctor sign --force`
   (accept the edit) or revert via `git checkout`.
3. If only `frontmatter_sha`/`record_sha` drift: `sbdb doctor fix --recompute`
   is safe — it rebuilds the sidecar from the current on-disk state.
4. Never auto-sign without asking — content tamper detection is a safety feature.

**Never edit `<id>.yaml` sidecars directly.** They are integrity artefacts
maintained by the CLI. If you need to change a document's metadata, edit
the `.md` frontmatter through `sbdb update` (or write the `.md` directly
and follow the post-edit doctor flow above).

## Reference schemas

This plugin ships starter schemas for common entity types. Copy any of
them into a fresh project's `schemas/` directory after `sbdb init`:

```bash
cp "${CLAUDE_PLUGIN_ROOT}/skills/secondbrain-db/reference/schemas/notes.yaml" \
   schemas/notes.yaml
```

Available references (under `reference/schemas/`):
- `notes.yaml` — personal notes with status, tags, source links
- `adr.yaml` — Architecture Decision Records with status lifecycle
- `discussion.yaml` — meeting notes with participants, monthly partition
- `task.yaml` — task tracking with priority, assignee, checklists, due dates

These are examples — modify freely or write your own from scratch.

## Embedding sbdb as a Go library

Other Go applications can embed sbdb directly:

```go
import "github.com/sergio-bershadsky/secondbrain-db/pkg/sbdb"

ctx := context.Background()
db, err := sbdb.Open(ctx, sbdb.Config{Root: "."},
    sbdb.WithLogger(slog.Default()),
    sbdb.WithIntegrityKey(myKey))
defer db.Close()

doc, err := db.Repo("notes").Create(ctx, sbdb.Doc{
    Frontmatter: map[string]any{"id": "hello", "created": "2026-04-28"},
    Content:     "# Hello",
})

records, err := db.Repo("notes").Query().
    Filter(map[string]any{"status": "active"}).
    OrderBy("-created").
    Limit(10).
    Records()
```

Public types: `Open`, `DB`, `Repo`, `Doc`, sentinel errors
(`ErrNotFound`, `ErrConflict`, `ErrUnknownEntity`, …), functional options
(`WithLogger`, `WithClock`, `WithIntegrityKey`, `WithIntegrityKeyLoader`,
`WithWalkWorkers`).

`pkg/sbdb/...` follows strict semver post-1.0. Sub-packages:
- `pkg/sbdb/schema` — parsed YAML schemas
- `pkg/sbdb/query` — Query builder
- `pkg/sbdb/integrity` — Sidecar, hash helpers, GitScope
- `pkg/sbdb/events` — git → JSONL projection
- `pkg/sbdb/kg` — knowledge graph with optional Embedder

## Detailed reference

- [CLI Reference](reference/cli-reference.md)
- [Schema Format](reference/schema-format.md)
- [Reference Schemas](reference/schemas/)
