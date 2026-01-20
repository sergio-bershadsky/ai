---
name: secondbrain-search-init
description: |
  This skill should be used when the user asks to "initialize search", "set up semantic search",
  "enable qmd", "add search to secondbrain", or mentions wanting to enable semantic search
  capabilities for an existing secondbrain project.
---

# Initialize Semantic Search

Set up qmd semantic search for an existing secondbrain project.

## Prerequisites

1. **Secondbrain project exists**: Check for `.claude/data/config.yaml`
2. **qmd installed**: Check with `which qmd`

## Workflow

### Step 1: Validate Environment

```bash
# Check secondbrain exists
ls .claude/data/config.yaml

# Check qmd installation
which qmd
```

If secondbrain not found:
```
No secondbrain project found in current directory.
Run `/secondbrain-init` to create a new project first.
```

If qmd not installed:
```
## qmd Not Installed

qmd is required for semantic search. Install it:

### Using Bun (Recommended)
bun install -g qmd

### Using npm
npm install -g qmd

After installation, run this skill again.

**Note:** First run will download ~1.5GB of embedding models.
```

### Step 2: Check Existing Search

```bash
ls .claude/search/ 2>/dev/null
```

If search already initialized:
```
## Search Already Initialized

Search is already configured for this project.

**Index location:** .claude/search/
**Last indexed:** 2026-01-15 10:30

### Options

1. **Rebuild index** — Re-index all documents
   `/secondbrain-search-init --rebuild`

2. **Search now** — Start searching
   `/secondbrain-search "your query"`

3. **Check status** — View index statistics
   `qmd status`
```

### Step 3: Create Search Configuration

Create `.claude/search/` directory and qmd config:

```bash
mkdir -p .claude/search
```

Generate `qmd.config.json` in project root:

```json
{
  "name": "{{project_name}}-secondbrain",
  "paths": ["docs"],
  "ignore": [
    "**/node_modules/**",
    "**/.vitepress/cache/**",
    "**/.vitepress/dist/**",
    "**/TEMPLATE.md"
  ],
  "indexDir": ".claude/search",
  "chunk": {
    "size": 800,
    "overlap": 0.15
  },
  "metadata": {
    "extractFrontmatter": true,
    "includeFileMetadata": true
  }
}
```

### Step 4: Update .gitignore

Add search index to `.gitignore` (index should not be committed):

```
# Semantic search index (regenerate with /secondbrain-search-init)
.claude/search/
qmd.config.json
```

### Step 5: Build Initial Index

Run initial indexing:

```bash
qmd index
```

Show progress:
```
## Building Search Index

Scanning docs/...
Found 47 documents

Indexing:
[████████████████████░░░░░░░░░░] 35/47 documents

Downloading models (first run only):
- embedding-gemma-300M... done
- qwen3-reranker... done

Building embeddings:
[██████████████████████████████] 47/47 documents

Index built successfully!
- Documents: 47
- Chunks: 312
- Index size: 2.4 MB
- Location: .claude/search/
```

### Step 6: Register Hook (Optional)

Ask user if they want automatic index updates:

```
## Automatic Index Updates

Would you like to automatically update the search index
when documents are modified?

[x] Yes, add PostToolUse hook (Recommended)
    - Updates index incrementally on file changes
    - Adds ~0.5s to Write/Edit operations

[ ] No, I'll rebuild manually
    - Run `qmd index` or `/secondbrain-search-init --rebuild`
```

If yes, add hook to `.claude/settings.local.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/search-index-update.py\"",
            "timeout": 30000
          }
        ]
      }
    ]
  }
}
```

Copy hook script:
```bash
cp "${CLAUDE_PLUGIN_ROOT}/hooks/search-index-update.py" .claude/hooks/
```

### Step 7: Show Summary

```
## Search Initialized Successfully!

**Project:** my-knowledge-base
**Documents indexed:** 47
**Index location:** .claude/search/

### Quick Start

Search your knowledge base:
/secondbrain-search "kubernetes deployment strategies"

Search with filters:
/secondbrain-search --entity=adrs "database"
/secondbrain-search --recent=30d "authentication"

### Index Management

Rebuild index:
qmd index --rebuild

Check status:
qmd status

View recent searches:
qmd history

### Automatic Updates

Index updates: Enabled (PostToolUse hook)
Documents in docs/ will be re-indexed on save.
```

## Options

### --rebuild

Force rebuild of entire index:

```bash
qmd index --rebuild
```

### --no-hook

Skip adding the automatic update hook:

```
/secondbrain-search-init --no-hook
```

## Troubleshooting

### Models Download Stuck

If model download hangs:
```bash
# Clear cache and retry
rm -rf ~/.cache/qmd/models/
qmd index
```

### Index Corruption

If search returns errors:
```bash
# Remove and rebuild
rm -rf .claude/search/
qmd index
```

### Slow Indexing

For large document sets (>500 docs):
- Initial indexing may take several minutes
- Consider using `--batch-size=50` for progress visibility

## Related Skills

- **secondbrain-search** — Search your knowledge base
- **secondbrain-init** — Create new secondbrain project
