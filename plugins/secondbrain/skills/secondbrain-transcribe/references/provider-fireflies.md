# Fireflies.ai Provider Reference

## Overview

Fireflies.ai provides meeting transcript data via a GraphQL API. The Python client (`fireflies.py`) wraps this API with three methods.

## API Configuration

- **API URL:** `https://api.fireflies.ai/graphql`
- **Auth:** Bearer token via `Authorization` header
- **API Key:** Loaded from `FIREFLIES_API_KEY` environment variable or `.env.local` file

## Python Client Usage

The client is scaffolded at `.claude/lib/fireflies.py` during project init.

```python
import sys
sys.path.insert(0, '.claude/lib')
from fireflies import FirefliesClient

client = FirefliesClient()

# List recent meetings (last 7 days, max 20)
meetings = client.list_meetings(limit=20, days=7)

# Get full transcript with sentences and summary
transcript = client.get_transcript("MEETING_ID")

# Get lightweight summary only
summary = client.get_summary("MEETING_ID")
```

## Client Methods

### `list_meetings(limit=20, days=7) -> list[dict]`

Returns list of meeting objects:
```python
{
    "id": "01KCY1N2ZMSVEKK0DJ0D0HM4CE",
    "title": "Team Sync",
    "date": "2026-03-28T14:00:00",  # ISO format
    "duration": 40,                   # minutes
    "organizer": "jane@example.com",
    "participants": ["jane@example.com", "john@example.com"],
    "url": "https://app.fireflies.ai/view/..."
}
```

### `get_transcript(meeting_id) -> dict`

Returns full transcript:
```python
{
    "id": "...",
    "title": "Team Sync",
    "date": 1711627200000,  # Unix ms timestamp
    "duration": 40,
    "organizer": "jane@example.com",
    "participants": ["jane@example.com", "john@example.com"],
    "sentences": [
        {
            "speaker_name": "Jane Smith",
            "text": "Let's discuss the architecture...",
            "start_time": 0.5,
            "end_time": 3.2
        }
    ],
    "summary": {
        "overview": "Meeting covered architecture decisions...",
        "shorthand_bullet": "- Decided on Redis\n- Docker setup",
        "keywords": "redis, docker, architecture",
        "action_items": "- Jane: Set up Redis cluster\n- John: Docker config",
        "outline": "1. Architecture review\n2. Infrastructure"
    }
}
```

### `get_summary(meeting_id) -> dict`

Lightweight version — same as `get_transcript` but without `sentences`. Use when you only need the AI summary.

## Date Handling

Fireflies returns dates as **Unix timestamps in milliseconds** in the raw API. The client normalizes these to ISO format strings in `list_meetings()`, but `get_transcript()` returns raw values. Convert with:

```python
from datetime import datetime
meeting_date = datetime.fromtimestamp(date_val / 1000)
```

## GraphQL Queries

### List Transcripts
```graphql
query RecentTranscripts($limit: Int) {
    transcripts(limit: $limit) {
        id
        title
        date
        duration
        organizer_email
        participants
        transcript_url
    }
}
```

### Get Full Transcript
```graphql
query Transcript($transcriptId: String!) {
    transcript(id: $transcriptId) {
        id
        title
        date
        duration
        organizer_email
        participants
        sentences {
            speaker_name
            text
            start_time
            end_time
        }
        summary {
            overview
            shorthand_bullet
            keywords
            action_items
            outline
        }
    }
}
```

### Get Summary Only
```graphql
query TranscriptSummary($transcriptId: String!) {
    transcript(id: $transcriptId) {
        id
        title
        date
        participants
        summary {
            overview
            shorthand_bullet
            keywords
            action_items
            outline
        }
    }
}
```

## Error Handling

- **Missing API key:** `ValueError` — set `FIREFLIES_API_KEY` env var or add to `.env.local`
- **HTTP errors:** `RuntimeError` with status code and response body
- **Connection errors:** `RuntimeError` with reason
- **Missing transcript:** `ValueError` — invalid meeting ID
