---
name: secondbrain-search
description: |
  This skill should be used when the user asks to "search secondbrain", "find in knowledge base",
  "look up documentation", "search notes/ADRs/tasks", "find related content", "semantic search",
  or mentions wanting to find specific content across their secondbrain using natural language.
---

# Semantic Search

Search your secondbrain knowledge base using semantic similarity (meaning-based) and full-text search.

## Prerequisites

1. **qmd installed**: Check with `which qmd`
   - Install: `bun install -g qmd` or `npm install -g qmd`
   - First run downloads ~1.5GB models

2. **Search initialized**: Check for `.claude/search/` directory
   - If not initialized, suggest running `/secondbrain-search-init`

## Usage

```
/secondbrain-search "your natural language query"
/secondbrain-search --entity=adrs "database migration"
/secondbrain-search --recent=30d "authentication"
/secondbrain-search --status=active --tag=kubernetes "deployment"
```

## Workflow

### Step 1: Validate Environment

```bash
# Check qmd is installed
which qmd

# Check search is initialized
ls .claude/search/
```

If qmd not installed:
```
qmd is not installed. Install it with:
  bun install -g qmd
  # or
  npm install -g qmd

Then initialize search with: /secondbrain-search-init
```

If search not initialized:
```
Search not initialized for this project.
Run: /secondbrain-search-init
```

### Step 2: Parse Query and Filters

Extract from user input:

| Filter | Syntax | Example |
|--------|--------|---------|
| Entity | `--entity=<type>` | `--entity=adrs,notes` |
| Recent | `--recent=<period>` | `--recent=7d`, `--recent=2w`, `--recent=1m` |
| Date from | `--from=<date>` | `--from=2025-01-01` |
| Date to | `--to=<date>` | `--to=2025-12-31` |
| Status | `--status=<status>` | `--status=active`, `--status=!archived` |
| Tag | `--tag=<tag>` | `--tag=kubernetes` |
| Limit | `--limit=<n>` | `--limit=10` (default: 5) |
| Format | `--format=<fmt>` | `--format=brief`, `--format=detailed`, `--format=json` |

### Step 3: Execute Search

Run qmd search command:

```bash
cd <project_root>
qmd query "<user_query>" --json --limit=<limit>
```

Parse JSON output:
```json
{
  "results": [
    {
      "id": "docs/adrs/ADR-0012-kubernetes-deployment.md",
      "score": 0.92,
      "title": "Kubernetes Deployment Strategy",
      "excerpt": "We decided to use Blue-Green deployment for stateless services...",
      "metadata": {
        "frontmatter": {
          "status": "implemented",
          "created": "2025-12-15"
        }
      }
    }
  ]
}
```

### Step 4: Enrich with Metadata

Load YAML records to add entity-specific metadata:

For each result:
1. Determine entity type from file path (e.g., `docs/adrs/` → ADRs)
2. Load corresponding records from `.claude/data/<entity>/records.yaml`
3. Match by file path and enrich with status, tags, dates, etc.

### Step 5: Apply Post-Filters

Filter results based on user criteria:

```python
# Pseudocode
for result in results:
    if entity_filter and result.entity not in entity_filter:
        skip
    if status_filter and result.status != status_filter:
        skip
    if tag_filter and tag_filter not in result.tags:
        skip
    if date_filter and not in_date_range(result.date, from_date, to_date):
        skip
```

### Step 6: Format Output

#### Brief Format (default for >3 results)

```
## Search Results

**Query:** "kubernetes deployment"
**Results:** 4 matches

1. **[ADR-0012] Kubernetes Deployment Strategy** (0.92)
   Status: implemented | Updated: 2025-12-15

2. **[Note] Kubernetes Scaling Best Practices** (0.87)
   Tags: kubernetes, scaling | Created: 2025-11-20

3. **[Discussion] Platform Team - Deployment Pipeline** (0.79)
   Date: 2025-10-05 | Participants: Alice, Bob

4. **[Task] Implement Canary Deployments** (0.71)
   Status: in_progress | Priority: high
```

#### Detailed Format (default for ≤3 results)

```
## Search Results

**Query:** "kubernetes deployment"
**Results:** 2 matches

---

### 1. [ADR-0012] Kubernetes Deployment Strategy
**Score:** 0.92 | **Status:** implemented | **Category:** infrastructure

**File:** [ADR-0012-kubernetes-deployment.md](docs/adrs/ADR-0012-kubernetes-deployment.md)

**Excerpt:**
> We decided to use Blue-Green deployment for stateless services
> and Rolling updates for stateful workloads. This approach provides
> zero-downtime deployments while minimizing resource overhead...

**Metadata:**
- Created: 2025-12-15
- Author: sergey
- Category: infrastructure

---

### 2. [Note] Kubernetes Scaling Best Practices
**Score:** 0.87 | **Tags:** kubernetes, scaling

**File:** [2025-11-20-kubernetes-scaling.md](docs/notes/2025-11-20-kubernetes-scaling.md)

**Excerpt:**
> Key considerations for scaling Kubernetes deployments:
> 1. Horizontal Pod Autoscaler configuration
> 2. Resource requests and limits
> 3. Pod disruption budgets...

**Metadata:**
- Created: 2025-11-20
- Status: active
```

#### JSON Format

```json
{
  "query": "kubernetes deployment",
  "total": 4,
  "results": [
    {
      "entity": "adrs",
      "id": "ADR-0012",
      "title": "Kubernetes Deployment Strategy",
      "file": "docs/adrs/ADR-0012-kubernetes-deployment.md",
      "score": 0.92,
      "excerpt": "We decided to use Blue-Green deployment...",
      "metadata": {
        "status": "implemented",
        "category": "infrastructure",
        "created": "2025-12-15",
        "author": "sergey"
      }
    }
  ]
}
```

## Search Tips

Display helpful tips when no results found:

```
## No Results Found

**Query:** "foobar nonexistent"

### Tips

1. **Try broader terms** — Use general concepts instead of specific jargon
2. **Check spelling** — Semantic search handles typos but exact terms may miss
3. **Remove filters** — Try without --entity or --status filters first
4. **Use related concepts** — "authentication" instead of "OAuth2"

### Alternative Actions

- `/secondbrain-freshness` — See all recent content
- Run without filters: `/secondbrain-search "foobar"`
```

## Refine Search

After showing results, offer refinement options:

```
### Refine Search

- `--entity=adrs` — Filter to ADRs only
- `--recent=30d` — Limit to last 30 days
- `--status=active` — Exclude archived items
- `"kubernetes AND deployment"` — Boolean operators
```

## Related Skills

- **secondbrain-search-init** — Initialize search for this project
- **secondbrain-freshness** — View items by freshness/staleness
