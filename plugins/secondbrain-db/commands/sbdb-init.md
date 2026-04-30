---
name: sbdb-init
description: Initialize a new secondbrain-db project (bare scaffold)
allowed-tools:
  - Bash
---

# sbdb-init

Scaffold a new knowledge base. v2 produces a bare scaffold — no starter
schema, no `data/` directory.

## Usage

```bash
sbdb init
```

Creates `.sbdb.toml` plus empty `schemas/` and `docs/` directories.

## Adding your first schema

After init, drop a YAML file into `schemas/<entity>.yaml`. Reference
schemas for common entity types (notes, ADRs, discussions, tasks) ship
with this plugin under
`${CLAUDE_PLUGIN_ROOT}/skills/secondbrain-db/reference/schemas/`. Copy
one to start, or write your own.

## Interactive wizard

For a guided setup that also adds GitHub Actions / VitePress / KG config:

```bash
sbdb init -i
```

The wizard asks for project name and four toggles (GitHub CI, VitePress,
integrity signing, knowledge graph). It does NOT ask which entity types
you want — schemas are content the user defines, not opinions the CLI
ships with.
