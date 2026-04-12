---
name: sbdb-graph
description: Query and export the knowledge graph — find relationships between documents
argument-hint: "<subcommand> [--id X] [--depth N] [--export-format json|mermaid|dot]"
allowed-tools:
  - Bash
---

# sbdb-graph

Navigate the knowledge graph to find relationships between documents. The graph is built from markdown links, `ref` fields, and virtual field edges.

## Subcommands

### Show what links TO a document (incoming)
```bash
sbdb graph incoming --id ${1} --format json
```

Output:
```json
{
  "version": 1,
  "data": [
    {"source_id": "deploy-guide", "source_entity": "notes", "target_id": "adr-0007", "target_entity": "adrs", "edge_type": "link", "context": "references"}
  ]
}
```

### Show what a document links TO (outgoing)
```bash
sbdb graph outgoing --id ${1} --format json
```

### Find neighbors within N hops (BFS traversal)
```bash
sbdb graph neighbors --id ${1} --depth ${2:-2} --format json
```

Useful for: "show me everything related to this document within 2 degrees of separation."

### Export the full graph

For visualization in D3.js, Cytoscape.js, React Flow, or any graph visualization library:
```bash
sbdb graph export --export-format json
```

Output:
```json
{
  "version": 1,
  "data": {
    "nodes": [
      {"id": "deploy-guide", "entity": "notes", "title": "Deployment Guide", "file": "docs/notes/deploy-guide.md"},
      {"id": "adr-0007", "entity": "adrs", "title": "ADR-0007: Terraform IaC"}
    ],
    "edges": [
      {"source": "deploy-guide", "target": "adr-0007", "type": "link", "label": "see ADR-0007"}
    ]
  }
}
```

For embedding in markdown (GitHub, Obsidian, GitLab):
```bash
sbdb graph export --export-format mermaid
```

For rendering with Graphviz:
```bash
sbdb graph export --export-format dot
```

### Graph statistics
```bash
sbdb graph stats --format json
# → {"nodes": 142, "edges": 387, "model_id": "text-embedding-3-small", "db_size_bytes": 12582912}
```

## Building the graph

The graph must be built before querying:

```bash
# Index schema-backed documents only
sbdb index build

# Index ALL .md files (including unstructured pages, guides, index pages)
sbdb index build --crawl

# Force re-index everything
sbdb index build --crawl --force
```

## Edge types

| Type | Source | Example |
|------|--------|---------|
| `link` | Markdown `[text](path.md)` links | Auto-extracted from content |
| `ref` | Schema `ref` field values | `parent: { type: ref, entity: notes }` |
| `virtual` | Virtual fields with `edge: true` | Ticket refs, tag links |
| `frontmatter_ref` | Frontmatter values that look like doc IDs | Crawl-mode heuristic |

## Common workflows

### "What documents reference this ADR?"
```bash
sbdb graph incoming --id adr-0007 --format json
```

### "Show me the full context around a document"
```bash
sbdb graph neighbors --id deploy-guide --depth 2 --format json
```

### "Find documents by meaning AND their relationships"
```bash
sbdb search "deployment strategy" --semantic --expand --depth 1 --format json
```

### "Generate a diagram of my KB for documentation"
```bash
sbdb graph export --export-format mermaid > docs/graph.md
```
