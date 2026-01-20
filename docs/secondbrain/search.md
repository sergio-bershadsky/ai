# Semantic Search

Add meaning-based search to your secondbrain knowledge base.

## Overview

Secondbrain supports two complementary search engines:

| Engine | Purpose | Technology | Runtime |
|--------|---------|------------|---------|
| **qmd** | Claude Code search | SQLite + embedding-gemma | CLI |
| **Orama** | VitePress browser | JSON + gte-small | Client-side |

Both provide semantic search — finding content by meaning, not just keywords.

## qmd (Claude Code Search)

### Installation

```bash
# Using Bun (recommended)
bun install -g qmd

# Using npm
npm install -g qmd
```

First run downloads ~1.5GB of models:
- embedding-gemma-300M (embeddings)
- qwen3-reranker (result ranking)

### Initialize Search

For new projects, select search during `/secondbrain-init`.

For existing projects:

```
/secondbrain-search-init
```

### Usage

```
/secondbrain-search "kubernetes deployment strategies"
```

#### Filters

| Filter | Syntax | Example |
|--------|--------|---------|
| Entity | `--entity=<type>` | `--entity=adrs,notes` |
| Recent | `--recent=<period>` | `--recent=7d` |
| Date from | `--from=<date>` | `--from=2025-01-01` |
| Date to | `--to=<date>` | `--to=2025-12-31` |
| Status | `--status=<status>` | `--status=active` |
| Tag | `--tag=<tag>` | `--tag=kubernetes` |
| Limit | `--limit=<n>` | `--limit=10` |

#### Examples

```
# Search ADRs only
/secondbrain-search --entity=adrs "database"

# Recent content
/secondbrain-search --recent=30d "authentication"

# Exclude archived
/secondbrain-search --status=active "deployment"

# Combined filters
/secondbrain-search --entity=notes --tag=kubernetes --recent=60d "scaling"
```

### How It Works

```
Query → qmd
         ↓
    ┌────┴────┐
    │         │
   BM25    Vector
(keyword) (semantic)
    │         │
    └────┬────┘
         ↓
     Reranker
   (LLM scoring)
         ↓
    Top Results
```

1. **BM25**: Traditional keyword matching
2. **Vector**: Semantic similarity using embeddings
3. **Reranker**: LLM-based relevance scoring
4. **Results**: Merged and ranked

### Index Management

```bash
# Rebuild entire index
qmd index --rebuild

# Check status
qmd status

# Incremental update (automatic via hook)
qmd index --incremental
```

## Orama (VitePress Browser Search)

### Setup

During `/secondbrain-init`, select "Orama" or "Both" for search configuration.

This adds:
- `@orama/orama` dependency
- `@orama/plugin-embeddings` for client-side embeddings
- `SearchBox.vue` component
- `build-search-index.ts` script

### How It Works

**Build time:**
```
docs/*.md → build-search-index.ts → search-index.json
```

**Runtime (browser):**
```
User query → Orama + gte-small → Semantic results
```

The search index is generated during `npm run docs:build` and served as a static JSON file.

### Usage

1. Press `Cmd+K` (or `Ctrl+K`)
2. Type your query
3. Navigate with arrow keys
4. Press Enter to open

### Features

- **Hybrid search**: Full-text + semantic
- **Client-side**: No server required
- **Offline**: Works after initial load
- **Fast**: Sub-100ms response

### Customization

Edit `docs/.vitepress/theme/components/SearchBox.vue`:

```vue
// Adjust result limit
limit: 10

// Change embedding model
model: 'gte-small'

// Modify search mode
mode: 'hybrid' // or 'fulltext' or 'vector'
```

## Dual Index Architecture

When both qmd and Orama are enabled:

```
                    docs/*.md
                        │
          ┌─────────────┼─────────────┐
          ↓                           ↓
    ┌─────────────┐           ┌─────────────┐
    │     qmd     │           │    Orama    │
    │  (Claude)   │           │  (Browser)  │
    ├─────────────┤           ├─────────────┤
    │ SQLite      │           │ JSON        │
    │ sqlite-vec  │           │ gte-small   │
    │ ~2MB/100doc │           │ ~30MB model │
    └─────────────┘           └─────────────┘
          ↓                           ↓
    /secondbrain-search       VitePress search bar
```

Benefits:
- Same content, same quality
- Optimized for each runtime
- AI and humans use same search

## Troubleshooting

### qmd: Models download stuck

```bash
rm -rf ~/.cache/qmd/models/
qmd index
```

### qmd: Index corruption

```bash
rm -rf .claude/search/
qmd index
```

### Orama: Search not working

1. Check `search-index.json` exists in build output
2. Verify `npm run search:build` runs before build
3. Check browser console for errors

### Search returns no results

- Try broader terms
- Remove filters
- Check if content is indexed
- Run `qmd status` (for qmd)

## Performance

### qmd

| Documents | Index Size | Search Time |
|-----------|------------|-------------|
| 100 | ~2 MB | <100ms |
| 500 | ~10 MB | <200ms |
| 1000 | ~20 MB | <500ms |

### Orama

| Documents | Index Size | Model Load | Search |
|-----------|------------|------------|--------|
| 100 | ~500 KB | ~2s | <50ms |
| 500 | ~2 MB | ~2s | <100ms |
| 1000 | ~4 MB | ~2s | <150ms |

Model loads once, then cached.
