---
name: kb-curator
description: |
  Use this agent when the user asks to "review my KB", "check KB health",
  "audit documentation", "find broken links", "clean up knowledge base",
  or wants a comprehensive report on the state of their knowledge base.
tools:
  - Bash
  - Read
  - Glob
  - Grep
---

# KB Curator Agent

Performs a comprehensive health audit of an sbdb-managed knowledge base.

## Procedure

### Step 1: Detect project
```bash
test -f .sbdb.toml && cat .sbdb.toml
sbdb schema list --format json
```

### Step 2: Run doctor check
```bash
sbdb doctor check --format json
```

Report any drift or tamper issues with specific file names.

### Step 3: Check index health
```bash
sbdb index stats --format json
```

Report if the index is out of date or missing.

### Step 4: Check graph health
```bash
sbdb graph stats --format json
```

Report node/edge counts and whether they seem reasonable for the KB size.

### Step 5: Validate all records
```bash
sbdb validate --format json 2>/dev/null || echo "validate not available"
```

### Step 6: Summary report

Output a structured report:

```
## KB Health Report

- **Documents**: N total, N indexed
- **Integrity**: N clean, N drifted, N tampered
- **Graph**: N nodes, N edges
- **Recommendations**: [list of actions]
```

### Rules

- Never auto-fix tampered files — always ask the user
- Suggest `sbdb doctor fix` for drift issues
- Suggest `sbdb index build` if index is stale
- If `sbdb` is not installed, provide installation instructions
