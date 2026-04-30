---
name: sbdb-query
description: Query knowledge base records with filters, ordering, and aggregation
argument-hint: "[--filter key=value] [--order -field] [--limit N] [--count] [--exists]"
allowed-tools:
  - Bash
---

# sbdb-query

Query records from the knowledge base using filters and ordering. Walks `docs_dir` and parses each `.md` frontmatter directly (concurrent, bounded by `SBDB_WALK_WORKERS`). Comparable speed to v1 for typical KBs (<10k docs); larger bases get the same scaling cost as a `find` + parse.

## Usage

```bash
sbdb query --filter ${1:-status=active} --format json
```

## Filter lookups

| Suffix | Meaning | Example |
|--------|---------|---------|
| (none) | Exact match | `--filter status=active` |
| `__gte` | Greater or equal | `--filter created__gte=2026-01-01` |
| `__lte` | Less or equal | `--filter priority__lte=3` |
| `__gt` | Greater than | `--filter count__gt=0` |
| `__lt` | Less than | `--filter count__lt=100` |
| `__in` | In list (CSV) | `--filter status__in=active,draft` |
| `__contains` | Substring | `--filter title__contains=deploy` |
| `__icontains` | Case-insensitive substring | `--filter title__icontains=Deploy` |
| `__startswith` | Prefix | `--filter id__startswith=adr-` |

## Examples

### Filter by field value
```bash
sbdb query --filter status=active --format json
```

### Multiple filters (AND logic)
```bash
sbdb query --filter status=active --filter created__gte=2026-04-01 --format json
```

### Exclude records
```bash
sbdb query --filter status=active --exclude difficulty=hard --format json
```

### Order and paginate
```bash
sbdb query --order -created --limit 10 --offset 20 --format json
```

### Count matching records
```bash
sbdb query --filter status=active --count --format json
# → {"version": 1, "data": {"count": 42}}
```

### Check existence
```bash
sbdb query --filter slug=my-note --exists --format json
# → {"version": 1, "data": {"exists": true}}
```

### Load full content (expensive — opens every .md file)
```bash
sbdb query --filter status=active --load-content --format json
```

## Output format

Default JSON output:
```json
{
  "version": 1,
  "data": [
    {"id": "note-1", "status": "active", "created": "2026-04-08", "title": "My Note", "file": "docs/notes/note-1.md"},
    ...
  ]
}
```

Records contain only scalar fields (fast). Complex fields (lists, objects) require `--load-content`.
