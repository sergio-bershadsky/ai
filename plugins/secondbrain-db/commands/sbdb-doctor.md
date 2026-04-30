---
name: sbdb-doctor
description: Check, repair, sign, or migrate knowledge base integrity
argument-hint: "[schema] [check|fix|sign|migrate]"
allowed-tools:
  - Bash
---

# sbdb-doctor

`sbdb doctor` verifies each `<id>.md` against its sibling `<id>.yaml`
sidecar (content / frontmatter / record SHA + optional HMAC signature).

## Default scope: working-tree only

Without `--all`, doctor only audits files that differ from `HEAD`
(modified, staged, untracked under any schema's `docs_dir`). The premise:
committed history was already verified, so re-scanning thousands of clean
files on every invocation is wasteful. Outside a git repo, doctor falls
back to `--all` with a stderr notice.

Use `--all` for periodic full audits (CI, cron) or recovery scenarios.

## Usage

Check current changes:
```bash
sbdb doctor check -s ${1:-notes} --format json
```

Full audit:
```bash
sbdb doctor check --all -s ${1:-notes} --format json
```

Fix drift (rebuilds sidecar from on-disk markdown, key-optional):
```bash
sbdb doctor fix --recompute -s ${1:-notes}
```

Re-sign after intentional hand-edit (requires HMAC key):
```bash
sbdb doctor sign --force -s ${1:-notes}
```

Migrate v1 (data/) layout to v2 (per-md sidecars), one-shot, idempotent:
```bash
sbdb doctor migrate
```

## Exit codes

- `0` — clean
- non-zero — drift detected; the JSON output lists per-doc causes:
  `content_sha mismatch`, `frontmatter_sha mismatch`,
  `record_sha mismatch`, `bad_sig`, `missing-sidecar`, `missing-md`.

## Output shape

```json
{
  "action": "doctor.check",
  "scope": "uncommitted",
  "drifts": [
    {"file": "docs/notes/x.md", "drift": "tamper",
     "causes": ["content_sha mismatch"]}
  ]
}
```
