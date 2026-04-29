---
name: sbdb-review
description: Run a full KB health review — sidecar integrity, broken links, stale index
argument-hint: "[--fix] [--verbose]"
allowed-tools:
  - Bash
---

# sbdb-review

Run a comprehensive knowledge base health review. Checks:
1. **Integrity** — does every `<id>.md` have a sibling `<id>.yaml` sidecar
   whose stored SHAs match the on-disk content?
2. **Validation** — do all records pass schema validation?
3. **Graph health** — broken links, orphan nodes?

## Usage

### Quick check (default scope: working-tree changes only)
```bash
sbdb doctor check --format json
```

### Full audit (every doc under every schema's docs_dir)
```bash
sbdb doctor check --all --format json
```

### Full review with graph
```bash
sbdb doctor check --all --format json \
  && sbdb graph stats --format json \
  && sbdb index stats --format json
```

### Fix drift (rebuilds sidecars from on-disk markdown; key-optional)
```bash
sbdb doctor fix --recompute
```

### After intentional hand-edits (re-sign with HMAC key)
```bash
sbdb doctor sign --force
```

## Interpreting results

| Exit code | Meaning |
|---|---|
| `0` | Clean |
| non-zero | Drift detected; the JSON output enumerates per-doc causes |

Drift causes (in `drifts[].causes`):
- `content_sha mismatch` — markdown body edited outside the ORM (tamper)
- `frontmatter_sha mismatch` — YAML frontmatter edited
- `record_sha mismatch` — derived record shape diverged from sidecar
- `bad_sig` — HMAC signature failed verification (key rotated or tampered)

Drift kinds (in `drifts[].drift`):
- `tamper` — at least one SHA mismatched
- `missing-sidecar` — `<id>.md` has no `<id>.yaml`
- `missing-md` — `<id>.yaml` has no `<id>.md` (orphan sidecar)

## Recommended workflow

1. `sbdb doctor check --format json` — see what changed
2. If only `frontmatter_sha`/`record_sha` drift → `sbdb doctor fix --recompute` is safe
3. If `content_sha mismatch` (real edits) → review the markdown body:
   - Intentional? → `sbdb doctor sign --force` (re-sign)
   - Accidental? → `git checkout <file>`
4. Re-run `sbdb doctor check --all` to confirm clean state across the entire KB
