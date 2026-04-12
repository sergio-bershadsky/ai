---
name: sbdb-init
description: Initialize a new secondbrain-db project
argument-hint: "[--template notes|blog|adr]"
allowed-tools:
  - Bash
---

# sbdb-init

Scaffold a new knowledge base with schemas, directories, and configuration.

## Usage

```bash
sbdb init --template ${1:-notes}
```

Creates `schemas/`, `docs/`, `data/`, `.sbdb.toml` with the chosen template.
