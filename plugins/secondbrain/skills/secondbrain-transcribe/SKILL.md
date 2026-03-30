---
name: secondbrain-transcribe
description: |
  This skill should be used when the user asks to "transcribe meeting", "document meeting",
  "process transcript", "import meeting notes", "check for undocumented meetings",
  or mentions Fireflies, Otter, or meeting transcription. Converts meeting transcripts
  from external providers into structured discussion documents.
---

# Transcribe Skill

Process meeting transcripts from external providers into structured discussion documents, with optional ADR extraction from decisions.

## Usage

```
/secondbrain-transcribe <id | list | all>
```

- `id` — specific meeting ID from the provider to process
- `list` — show recent undocumented meetings
- `all` — batch process all undocumented meetings

**Examples:**
```
/secondbrain-transcribe list
/secondbrain-transcribe 01KCY1N2ZMSVEKK0DJ0D0HM4CE
/secondbrain-transcribe all
```

## Prerequisites

Verify the project has transcription configured in `.claude/data/config.yaml`:

```yaml
integrations:
  transcription:
    enabled: true
    provider: fireflies
    check_on_session_start: true
    lookback_days: 7
    fireflies:
      api_key_env: FIREFLIES_API_KEY
```

If not configured, guide the user through setup:
1. Choose a provider (fireflies is currently supported)
2. Configure API key (environment variable or `.env.local`)
3. Add the `integrations` section to config

Also verify that discussions entity is enabled (transcriptions create discussion documents).

## Procedure

### Step 1: Load Configuration

Read `.claude/data/config.yaml` and extract:
- `integrations.transcription.provider` — which provider to use
- `integrations.transcription.lookback_days` — how far back to check (default: 7)
- `team` section — for participant name mapping

Load the provider-specific reference from `references/provider-<name>.md` for API details.

### Step 2: Route by Subcommand

**`list`** — Fetch recent meetings from provider, filter against processed list, display table:
```
## Undocumented Meetings (Last 7 Days)

| ID | Date | Title | Duration | Participants |
|----|------|-------|----------|--------------|
| 01KCY1N2ZM... | 2026-03-28 | Team Sync | 40 min | Jane, John |

Run `/secondbrain-transcribe <id>` to process a specific meeting.
Run `/secondbrain-transcribe all` to process all meetings.
```

**`<id>`** — Process a specific meeting (continue to Step 3).

**`all`** — Iterate through all unprocessed meetings, processing each (continue to Step 3 for each).

### Step 3: Fetch Meeting Data

Use the provider's client library to fetch meeting data. For provider-specific instructions, read the corresponding reference file:

- **Fireflies:** See `references/provider-fireflies.md`

The client should be available at `.claude/lib/<provider>.py` in the user's project (scaffolded during init).

```python
import sys
sys.path.insert(0, '.claude/lib')

# Provider-specific import
from fireflies import FirefliesClient
client = FirefliesClient()
transcript = client.get_transcript("<meeting-id>")
```

### Step 4: Check Processed Status

Use the tracking library to check if this meeting was already documented:

```python
from tracking import is_meeting_processed
if is_meeting_processed("<meeting-id>"):
    # Already processed — show existing doc location
```

If already processed, inform the user and show the existing discussion file path.

### Step 5: Extract Structured Data

From the transcript, extract:

1. **Participants** — Map to team aliases using the `team` config section. Match email patterns and name patterns to resolve full names.
2. **Date** — Meeting date
3. **Duration** — Meeting length
4. **Key Discussion Points** — Main topics covered
5. **Decisions Made** — Any conclusions or agreements
6. **Action Items** — Tasks assigned with owners
7. **Open Questions** — Unresolved items

Use the provider's AI summary if available (e.g., Fireflies `summary.overview`, `summary.action_items`, `summary.keywords`).

### Step 6: Generate Discussion Document

Create a discussion document following the existing `secondbrain-discussion` patterns:

**File path:** `docs/discussions/YYYY-MM-DD-<participant>-<topic-slug>.md`

**Frontmatter:**
```yaml
---
date: YYYY-MM-DD
participants:
  - Jane Smith
  - John Doe
topic: Meeting Title
status: documented
source: <provider_name>
meeting_id: <provider_meeting_id>
tags: [extracted, keywords]
---
```

**Body template:**
```markdown
# Meeting Title

## Context

<From transcript summary or overview>

## Discussion Points

### Topic 1
<Details from transcript>

### Topic 2
<Details from transcript>

## Decisions

| Decision | Rationale | Owner |
|----------|-----------|-------|
| Decision from transcript | Context | Assignee |

## Action Items

- [ ] Item from transcript — Owner
- [ ] Item from transcript — Owner

## Open Questions

1. Unresolved items from discussion

---

*Source: <provider> transcript*
*Meeting ID: <id>*
*Documented: YYYY-MM-DD*
```

**CRITICAL:** Do NOT add the discussion to the VitePress sidebar. Discussion documents are auto-listed via the EntityTable component.

### Step 7: Identify Potential ADRs

Scan decisions for architectural/technical choices:

**ADR Candidates:**
- Technology choices ("we decided to use X")
- Architecture patterns ("we'll implement Y approach")
- Process changes ("going forward we'll do Z")

Present to user with confirmation for each:
```
## Potential ADRs from Meeting

Found 2 decisions that might warrant ADRs:

1. "Decided to use Docker Compose for local development"
   → Create ADR? [Y/N]

2. "Will implement Redis for caching layer"
   → Create ADR? [Y/N]
```

**Never auto-create ADRs** — always wait for user confirmation on each.

### Step 8: Show Draft and Confirm

Present the full draft before writing:
```
## Meeting Transcript Documentation

**Meeting:** Jane <> John
**Date:** 2026-03-28
**Duration:** 40 minutes
**Provider ID:** 01KCY1N2ZMSVEKK0DJ0D0HM4CE

### Files to Create/Update
1. CREATE: docs/discussions/2026-03-28-john-doe-team-sync.md
2. UPDATE: .claude/data/discussions/2026-03.yaml (add record)

### ADRs to Create (if confirmed)
- ADR-0005: Docker Compose for Local Development

### Draft Document
---
[Document content]
---

Proceed with documentation?
```

### Step 9: Create Files and Update Records

After approval:
1. Create the discussion markdown file
2. Add a record to the monthly discussion partition (`.claude/data/discussions/YYYY-MM.yaml`):
   ```yaml
   - date: 'YYYY-MM-DD'
     member: john
     topic: Team Sync
     file: docs/discussions/2026-03-28-john-doe-team-sync.md
     source: fireflies
     meeting_id: 01KCY1N2ZMSVEKK0DJ0D0HM4CE
   ```
3. Create any confirmed ADRs using the `/secondbrain-adr` skill workflow

## Team Member Mapping

If a `team` section exists in config, map provider participant names/emails to team aliases:

```yaml
team:
  jane:
    full_name: "Jane Smith"
    patterns: ["jane@*", "Jane*"]
  john:
    full_name: "John Doe"
    patterns: ["john@*", "John*"]
```

Match participant names/emails against patterns to resolve full names. Unmatched participants are kept as-is.

## Rules

1. **Always check processed status** — don't re-document meetings
2. **Map participants correctly** — use team config for name resolution
3. **Extract decisions carefully** — only suggest ADRs for technical/architectural decisions
4. **Manual ADR confirmation** — never auto-create ADRs without user approval
5. **Update discussion records** — add to monthly partition YAML
6. **Preserve transcript source** — include `meeting_id` and `source` in frontmatter
7. **Handle API errors gracefully** — report provider API issues clearly
8. **Do NOT add to sidebar** — discussions are auto-listed via EntityTable
