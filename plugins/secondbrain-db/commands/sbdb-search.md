---
name: sbdb-search
description: Full-text or semantic search over knowledge base documents
argument-hint: "<phrase> [--semantic] [--k 10] [--expand] [--depth 1]"
allowed-tools:
  - Bash
---

# sbdb-search

Search for content across all documents. Two modes: full-text (grep) and semantic (vector similarity).

## Full-text search (default)

Searches markdown body content using grep. No API key required.

```bash
sbdb search "${1}" --format json
```

Output:
```json
{
  "version": 1,
  "data": [
    {"id": "deploy-guide", "file": "docs/notes/deploy-guide.md", "snippet": "...deployment strategy for production..."}
  ]
}
```

## Semantic search

Searches by meaning using vector embeddings. Requires `SBDB_EMBED_API_KEY`.

```bash
sbdb search "${1}" --semantic --k 10 --format json
```

Output:
```json
{
  "version": 1,
  "data": [
    {"doc_id": "deploy-guide", "entity": "notes", "title": "Deployment Guide", "score": 0.92, "snippet": "..."},
    {"doc_id": "infra-plan", "entity": "notes", "title": "Infrastructure Plan", "score": 0.85, "snippet": "..."}
  ]
}
```

Results are ranked by cosine similarity (1.0 = identical, 0.0 = unrelated).

## Semantic search + graph expansion

Find semantically similar documents, then also return their knowledge graph neighbors:

```bash
sbdb search "${1}" --semantic --expand --depth 1 --format json
```

Output includes both search results and related edges:
```json
{
  "version": 1,
  "data": {
    "results": [
      {"doc_id": "deploy-guide", "score": 0.92, "...": "..."}
    ],
    "related": [
      {"source_id": "deploy-guide", "target_id": "adr-0007", "edge_type": "link", "context": "see also"}
    ]
  }
}
```

## Prerequisites

### Full-text search
No prerequisites — uses grep or pure-Go fallback.

### Semantic search
1. Set API key: `export SBDB_EMBED_API_KEY="sk-..."`
2. Build the index: `sbdb index build`
3. Supported providers: OpenAI, Voyage AI, Mistral, Ollama, any OpenAI-compatible endpoint

Configure in `.sbdb.toml`:
```toml
[knowledge_graph.embeddings]
provider = "openai"
base_url = "https://api.openai.com"
model = "text-embedding-3-small"
```

## When to use which

| Need | Command |
|------|---------|
| Find exact keyword | `sbdb search "keyword"` |
| Find by concept/meaning | `sbdb search "concept" --semantic` |
| Find related documents too | `sbdb search "concept" --semantic --expand` |
| Filter after searching | `sbdb query --filter status=active` (use query for structured filters) |
