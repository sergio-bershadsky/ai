---
name: sbdb-review
description: Run a full KB health review — drift, tamper, broken links, stale index
argument-hint: "[--fix] [--verbose]"
allowed-tools:
  - Bash
---

# sbdb-review

Run a comprehensive knowledge base health review. Checks:
1. **Integrity** — are all files signed by the ORM? Any hand-edits detected?
2. **Drift** — do frontmatter values match records.yaml?
3. **Validation** — do all records pass schema validation?
4. **Graph health** — are there broken links or orphan nodes?

## Usage

### Quick check (default)
```bash
sbdb doctor check --format json
```

### Full review with graph
```bash
sbdb doctor check --format json && sbdb graph stats --format json && sbdb index stats --format json
```

### Fix drift issues (does NOT re-sign tampered files)
```bash
sbdb doctor fix --recompute
```

### After intentional hand-edits
```bash
sbdb doctor sign --force
```

## Interpreting results

| Exit code | Meaning | Action |
|---|---|---|
| 0 | Clean | Nothing to do |
| 4 | Drift detected | Run `sbdb doctor fix` |
| 6 | Tamper detected | Review the file, then `sbdb doctor sign --force` or `git checkout` |
| 7 | Both drift + tamper | Fix drift first, then review tampered files |

## Recommended workflow

1. Run `sbdb doctor check` to see all issues
2. If drift only → `sbdb doctor fix --recompute` (safe, automatic)
3. If tamper → manually review each tampered file:
   - Was the edit intentional? → `sbdb doctor sign --force --id <id>`
   - Was it accidental? → `git checkout <file>`
4. Re-run `sbdb doctor check` to confirm clean state
