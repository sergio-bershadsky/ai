---
name: secondbrain-db
description: |
  Use when the user works with a markdown knowledge base (VitePress, Docusaurus, Obsidian, Jekyll)
  backed by YAML frontmatter and YAML record indexes, or asks to query, search, verify integrity,
  or repair drift between frontmatter and records. Also applies when a .sbdb.toml or schemas/*.yaml
  file is present in the project, or when the user mentions "sbdb", "knowledge base", "knowledge graph",
  "doctor check", "drift", "tamper", or "semantic search" in the context of their documentation.
---

# secondbrain-db

A CLI tool (`sbdb`) for managing markdown knowledge bases with YAML schemas, Starlark virtual fields, integrity signing, and a SQLite-backed knowledge graph.

## Prerequisites

Check if `sbdb` is installed:

```bash
which sbdb || echo "NOT INSTALLED"
```

If not installed, guide the user:
- **macOS/Linux**: `go install github.com/sergio-bershadsky/secondbrain-db@latest`
- **From source**: `git clone ... && cd secondbrain-db && make install`

Check if the project is an sbdb project:
```bash
test -f .sbdb.toml && echo "sbdb project" || echo "not an sbdb project"
```

## Core commands

| Task | Command |
|------|---------|
| Initialize project | `sbdb init --template notes` |
| List schemas | `sbdb schema list` |
| Show schema | `sbdb schema show --format json` |
| Create document | `sbdb create --input -` (JSON on stdin) |
| Get document | `sbdb get --id <id> --format json` |
| List documents | `sbdb list --format json` |
| Query documents | `sbdb query --filter key=value --format json` |
| Search (grep) | `sbdb search "phrase"` |
| Search (semantic) | `sbdb search "phrase" --semantic --k 10` |
| Update document | `sbdb update --id <id> --field key=value` |
| Delete document | `sbdb delete --id <id> --yes` |
| Check health | `sbdb doctor check` |
| Fix drift | `sbdb doctor fix --recompute` |
| Re-sign after edit | `sbdb doctor sign --force` |
| Build index | `sbdb index build` |
| Build index (crawl) | `sbdb index build --crawl` |
| Graph neighbors | `sbdb graph neighbors --id <id> --depth 2` |
| Graph export | `sbdb graph export --export-format json` |

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 2 | Not found |
| 3 | Validation error |
| 4 | Drift detected |
| 6 | Tamper detected |
| 7 | Drift + tamper |

## When creating documents

Always use `--format json` for structured output. Build the JSON payload using the schema:

```bash
# Discover the schema first
sbdb schema show --format json

# Then create
echo '{"id":"my-doc","created":"2026-04-08","content":"# Title\n\nBody."}' | sbdb create --input -
```

## When the user edits files manually

After any hand-edit to `.md` or `.yaml` files in the KB:
1. Run `sbdb doctor check` to detect issues
2. If exit code 6 (tamper): ask the user whether to `sbdb doctor sign --force` or revert
3. Never auto-sign without asking — tamper detection is a safety feature

## Detailed reference

For schema format, field types, virtual fields, and advanced usage, see the files in `reference/`:
- [CLI Reference](reference/cli-reference.md)
- [Schema Format](reference/schema-format.md)
