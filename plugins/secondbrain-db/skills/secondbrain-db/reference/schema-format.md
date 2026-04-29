# Schema Format Reference

Schemas are YAML files in `schemas/` that define entity types.

## Structure (v2)

```yaml
version: 1
entity: <name>                    # entity name (used in docs_dir paths)
docs_dir: <path>                  # where .md files live
filename: "{field}.md"            # filename template
id_field: <field>                 # primary key (default: "id")
integrity: strict                 # "strict", "warn", "off"

fields:
  <name>: { type: <type>, required: <bool>, default: <value> }

virtuals:
  <name>:
    returns: <type>
    source: |
      def compute(content, fields):
          return ...
```

### Deprecated fields (still parsed; emit a stderr warning, ignored)

These were used by v1 and are no longer relevant in v2. Remove them from
your schemas:

```yaml
records_dir: <path>      # v1 — gone in v2 (no aggregate index)
partition: none|monthly  # v1 — gone in v2
date_field: <field>      # v1 — required only when partition=monthly
```

`sbdb` v2 emits a one-time warning per schema if these fields are present.

## Field types

| Type | Stored in | Example |
|------|-----------|---------|
| `string` | frontmatter | `{ type: string, required: true }` |
| `int` | frontmatter | `{ type: int, default: 0 }` |
| `float` | frontmatter | `{ type: float }` |
| `bool` | frontmatter | `{ type: bool, default: false }` |
| `date` | frontmatter | `{ type: date, required: true }` |
| `datetime` | frontmatter | `{ type: datetime }` |
| `enum` | frontmatter | `{ type: enum, values: [a, b, c] }` |
| `ref` | frontmatter | `{ type: ref, entity: adrs }` |
| `list` | frontmatter | `{ type: list, items: { type: string } }` |
| `object` | frontmatter | `{ type: object, fields: { ... } }` |

In v2 every field lives in YAML frontmatter on the `.md` file. Queries
walk `docs_dir` and parse frontmatter directly (concurrent, bounded by
`SBDB_WALK_WORKERS` env or `WithWalkWorkers` option). There is no
separate aggregate index — that means two parallel PRs adding two
documents touch disjoint files and merge cleanly.

## ref type

Creates edges in the knowledge graph:

```yaml
fields:
  parent: { type: ref, entity: notes }              # single ref
  related: { type: list, items: { type: ref, entity: adrs } }  # list of refs
```

## Virtual fields

Starlark functions computed from content. Sandboxed: no I/O, no imports,
deterministic.

```yaml
virtuals:
  title:
    returns: string
    source: |
      def compute(content, fields):
          for line in content.splitlines():
              if line.startswith("# "):
                  return line.removeprefix("# ").strip()
          return fields["id"]

  ticket_refs:
    returns: list[string]
    edge: true                    # creates KG edges from returned values
    edge_entity: tickets          # target entity
    source: |
      def compute(content, fields):
          return re.findall("[A-Z]+-[0-9]+", content)
```

Available builtins: `re.findall(pattern, text)`, all Python string
methods, `len()`, `max()`, `min()`, `int()`, `str()`, `list()`.

All virtuals (scalar + complex) are materialised into the markdown's
frontmatter on every save. Queries read the materialised values
directly — Starlark only runs at write time.

## Per-doc sidecar (v2)

Every `<id>.md` has a sibling `<id>.yaml` integrity sidecar:

```yaml
version: 1
algo: sha256
hmac: true                       # false if no integrity key configured
file: my-doc.md
content_sha: 9f86d0...           # SHA-256 of the markdown body
frontmatter_sha: ab1c4d...       # SHA-256 of the canonical-yaml frontmatter
record_sha: 7d865e...            # SHA-256 of the projected record shape
sig: 0a3b...                     # HMAC-SHA-256 (present iff hmac=true)
updated_at: 2026-04-28T09:30:12Z
writer: secondbrain-db/2.0.0
```

This file is maintained by the CLI — never edit it by hand. The
plugin's PreToolUse hook blocks direct edits to anything under `docs/`,
including sidecars.
