---
name: sbdb-doctor
description: Check and repair knowledge base consistency (drift + integrity)
argument-hint: "[--fix] [--recompute]"
allowed-tools:
  - Bash
---

# sbdb-doctor

Run `sbdb doctor check` to find drift and integrity issues, or `sbdb doctor fix` to repair drift.

## Usage

Check for issues:
```bash
sbdb doctor check -s ${1:-$(sbdb config show default_schema 2>/dev/null || echo "notes")} --format json
```

Fix drift (does NOT re-sign tampered files):
```bash
sbdb doctor fix -s ${1:-notes} --recompute
```

Re-sign after intentional hand-edit:
```bash
sbdb doctor sign -s ${1:-notes} --force --id <id>
```

## Exit codes
- `0` clean
- `4` drift detected
- `6` tamper detected
- `7` both drift and tamper
