# Data model — the neutral contract

The page reads three collections (artifact database) or three keys of a static seed. Nothing
here names a tracker: every tool maps onto these shapes. All writes go through the publisher;
viewers only read.

## `config/page` — one document

Built by `observe.py config PROFILE SEED`: profile fields (tool) merged with the seed's
`config` (epic). Epic fields win; nested maps (`links`, `tracker`, `people`, `forecast`)
merge key by key.

| Field | Source | Purpose |
|---|---|---|
| `title` | epic | Page name, browser tab, header. A real name ("Checkout Redesign"). |
| `subtitle` | epic | One line: epic id + what it delivers. IDs in it auto-link. |
| `lanes` | epic | Cascade rows, upstream → downstream. Omit to derive from items. |
| `matrix` | epic, optional | Evidence grid: `title`, `rowLabel`, `rows[]`, `cols[]`, `colLabels{}`. Omit to hide. |
| `tracker.name` | profile | Shown in "Cascade: dependencies in …" and on every event's "… ↗" link. |
| `idPattern` | profile | Regex for item ids to auto-link. Default `[A-Z][A-Z0-9]+-\d+`. `($^)` disables (numeric ids). |
| `changePrefix` | profile | Change-number marker: `#` (PRs), `!` (GitLab MRs), `""` to disable. |
| `links.item` | profile | `{id}` → item URL, when an item has no explicit `url`. |
| `links.change` | profile | `{n}` → PR/MR URL. |
| `links.commit` | profile | `{sha}` → commit URL. Empty → hashes stay plain text. |
| `links.person` | profile | `{login}` → profile URL for people not in `people`. |
| `people` | profile (+epic) | `{login: {name, url?}}` — display names for `by` / `reviewer`. Only mappings you are sure of. |
| `eventLanes` | profile, optional | `[{name, tone}]`, tone ∈ `accent warn idle ok bad`. Scrubber colours + stack order. Unlisted lanes get a tone by first appearance. |
| `forecast.wipWeights` | profile, optional | Credit per status when "Count work in progress" is on. Default `done 1, in_review .75, in_progress .4, blocked .25`. Shown on the page. |
| `forecast.maxAheadDays` | profile, optional | Caps the forecast axis (default 180). |

## `items/<ID>` — one document per work item

| Field | Type | Purpose |
|---|---|---|
| `title` | string | Short, human title. |
| `lane` | string | One of `config.lanes`. Items without a listed lane stay off the cascade. |
| `blockedBy` | ID[] | Exactly the tracker's blocked-by relations. Never inferred from prose. |
| `inScope` | bool | `true` for the epic's own children (counted in % and burn-up). `false` for related items. |
| `owner` | string | Assignee display name (or "Triage"). |
| `url` | string, optional | Direct link; overrides `links.item`. Required when ids don't match `idPattern`. |

## `events/<id>` — one document per moment

| Field | Type | Purpose |
|---|---|---|
| `at` | ISO-8601 UTC (`…Z`) | When it happened, from a system of record. |
| `approx` | bool, optional | `true` only when the time is estimated; the page labels it. |
| `lane` | string | Kind of source: Planning, Tracker, Review, Code, Design, Live, Other… |
| `kind` | `decision` \| `review`, optional | Badge for an event with no state change. Falls back to lane name (Design/Decision → decision, Review → review). |
| `title` | string | One line, what happened. IDs / change numbers / hashes auto-link. |
| `detail` | string, optional | One or two sentences of why / what it means. |
| `by` | login, optional | Who did it; resolved through `people`. |
| `link` | URL, optional | Tracker page for this event (comment, decision). Default: first item it changes. |
| `effects` | Effect[] | State changes this event causes (may be empty). |

Doc ids only need to be unique; the page orders by `at`. Use sortable ids (`e001`, `e002`…).

### Effects

```json
{"type": "item",   "id": "SHOP-12", "status": "in_progress", "label": "In Progress"}
{"type": "change", "id": "!42", "status": "approved", "reviewer": "di-qa", "title": "Card vault API (SHOP-102)"}
{"type": "check",  "row": "stripe", "col": "card", "result": "pass", "note": "3DS passed"}
```

State at the scrubbed moment is the replay of effects up to it: later effects for the same id
merge over earlier ones, so an effect carries only the fields that change. `reviewer` is shown
only while the change's status is the verdict it gave. Badges (scope +/−, started, done,
opened, approved, changes requested, merged) are derived from the replay — never write them.

Legacy types `ticket` / `pr` / `cell` (`backend` / `case`) and legacy item fields `layer` /
`epic` are still read.

## Canonical statuses

| Kind | Values |
|---|---|
| item | `triage` `backlog` `ready` `in_progress` `in_review` `blocked` `done` `duplicate` `canceled` |
| change | `open` `changes_requested` `approved` `merged` `closed` |
| check | `pass` `fail` `blocked` `pending` `untested` `dropped` |

Progress: `done` counts as done; `in_progress` / `in_review` / `blocked` as active;
`duplicate` / `canceled` leave the denominator. Write the tool's wording in `label` and let
`observe.py normalize` set `status` from the profile's `statusMap`.
