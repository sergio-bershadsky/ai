# Tracker profile — `.claude/epic-observation.json`

One file per project, describing the user's tracker and code host. It is the only place tool
specifics live; every epic page in the project reuses it, so pages look and behave the same
whichever tool sits behind them. Start from the closest file in `assets/profiles/`
(`linear`, `jira`, `github`, `monday`) and fill in the placeholders (`<workspace>`, `<org>`…).

```json
{
  "tracker":  {"name": "Jira"},
  "codeHost": {"name": "GitLab"},
  "idPattern": "SHOP-\\d+",
  "changePrefix": "!",
  "links": {"item": "…/browse/{id}", "change": "…/merge_requests/{n}", "commit": "…/commit/{sha}", "person": "…/{login}"},
  "statusMap": {
    "item":   {"To Do": "ready", "Code Review": "in_review", "Won't Do": "canceled"},
    "change": {"opened": "open", "merged": "merged"}
  },
  "people":     {"ana-k": {"name": "Ana K.", "url": "…"}},
  "eventLanes": [{"name": "Review", "tone": "accent"}, {"name": "Code", "tone": "ok"}],
  "forecast":   {"wipWeights": {"done": 1, "in_review": 0.75, "in_progress": 0.4, "blocked": 0.25}},
  "notes": "free text for the next person; never published"
}
```

| Key | Published? | Notes |
|---|---|---|
| `tracker`, `idPattern`, `changePrefix`, `links`, `people`, `eventLanes`, `forecast` | yes, into `config/page` | See data-model.md. |
| `statusMap` | no | Tool wording → canonical, per kind. Case-insensitive. Canonical labels pass through. |
| `codeHost`, `notes` | no | Documentation for whoever maintains the profile. |

## Building it the first time

1. List the tracker's real statuses (workflow / board columns / status column labels) — from
   the tool, not memory — and map each one in `statusMap.item`. Ask the user about any status
   whose meaning is unclear (e.g. "QA" — review or in progress?).
2. Take one real item and one real change and check the link templates open them.
3. `people`: only logins you can match with certainty (same person across code host and
   tracker). Leave others out; they fall back to `links.person` or plain text.
4. Never put an email address in `people` or anywhere in the profile — the page is shared.

`observe.py normalize` reports every label the map doesn't cover; extend the map rather than
editing statuses by hand.
