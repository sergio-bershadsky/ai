---
name: epic-observation
description: Build and keep current a live "Epic Observation" page — a scrubbable timeline of an epic (or project, milestone, initiative) that replays its history and shows, at any moment, % of work items done, a burn-up with a forecast band, the dependency cascade from the tracker's blocked-by links, open changes (PRs/MRs) with review verdicts, an optional evidence grid, and a filterable event log linked back to the tracker and code host. Tool-agnostic — Linear, Jira, monday.com, GitHub Issues/Projects, GitLab, Azure DevOps, Asana, ClickUp, Shortcut… — through a per-project tracker profile; the page looks and behaves the same for every tool. Use it whenever someone wants a progress timeline, status page or burn-up for an epic, a visual of ticket dependencies, "show how this epic progressed", a shareable project progress page, a delivery forecast, or asks to keep such a page updated as work lands — even if they don't say "observation" or "timeline".
---

# Epic Observation

A live page that answers "where is this epic, how did it get here, what is it waiting on, and
when will it land?" — scrubbable, so a reader can drag back to any moment and see the epic as
it stood then.

**Architecture (keep it this way):**

```
tracker / code host ──(agent reads via the user's MCP / CLI / API)──▶ neutral data
  profile  .claude/epic-observation.json   tool specifics, once per project
  seed     config + items + events          one epic, canonical statuses
            │  observe.py normalize / validate / config / export
            ▼
  assets/epic-observation.html              one template, never edited per tool
```

The template knows nothing about any tracker. Tool specifics live in the **profile**; the
**data model** is the contract. Never patch the template for one tool — if a tool needs
something the model can't express, extend the model (data-model.md) for everyone.

Scripts: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/epic-observation/scripts/observe.py <cmd>`
(below: `observe.py`). Standard library only.

| Part of the page | Driven by |
|---|---|
| Header, links, id auto-linking, "<Tracker> ↗" | `config/page` (profile + epic) |
| Burn-up + forecast (opt / exp / pes, WIP credit toggle) | item effects replayed; `forecast` config |
| Scrubber: day columns stacked by event lane, zoom row | `events`; `eventLanes` |
| % complete + bar | in-scope items' statuses at the scrubbed moment |
| Work items / Changes boards (+ reviewer on verdicts) | `item` / `change` effects |
| Evidence grid (optional) | `check` effects; `config.matrix` |
| Cascade (dependency graph) | `items`: `lane` + `blockedBy`; status from events |
| Event log: badges, filters, people, links | `events`; badges derived, never written |

Read `references/data-model.md` before writing any data.

## Workflow

### 1. Profile — once per project

Look for `.claude/epic-observation.json` in the project. Missing → build it with the user
(`references/profile.md`): copy the closest `assets/profiles/*.json`, then fill it from the
real tracker — its actual status list, one real item URL, one real change URL. Ask about any
status whose meaning is unclear rather than guessing. Read `references/adapters.md` for the
tool's section (how to list children, where history and relations live). Unknown tool → the
"others" checklist there.

### 2. Gather facts with real timestamps

Build the seed from source systems, not memory:
- tracker: item created / started / review / completed / canceled times (changelog, activity
  log, history), relation changes, decisive comments (`kind: "decision"`, `link` to it);
- code host: change opened, review verdicts (with `reviewer`), merged / closed; key commits;
- checks you actually ran (evidence grid).

**Every `at` comes from a system of record.** If you genuinely can't pin a time (a meeting, a
manual check), estimate it and set `approx: true` — the page labels it. Never move an event to
another date to make the timeline look busier or gap-free: the page is shared with the team and
linked from the tracker, so a backdated event misreports when work happened. Quiet days are
normal; the scrubber collapses them and marks weekends.

Write the tool's wording in each effect's `label`, then:

```bash
observe.py normalize .claude/epic-observation.json seed.json   # label → canonical status
observe.py validate seed.json --profile .claude/epic-observation.json
```

Fix every reported problem at the source (extend `statusMap`, add the missing item) — don't
hand-edit statuses around the profile.

### 3. Publish

**Live (preferred):** publish `assets/epic-observation.html` as an artifact with the `db`
capability and read-only rules for viewers (load the artifact skills the environment requires
first):
`{"db": {"rules": [{"path": "config", "read": "view", "write": "admin"}, {"path": "items", "read": "view", "write": "admin"}, {"path": "events", "read": "view", "write": "admin"}]}}`.
Seed it with batch writes: `config/page` = output of `observe.py config PROFILE seed.json`,
every item into `items`, then the events. Verify once: read the collections back.

**Static (no artifact db):** `observe.py export seed.json out.html --profile PROFILE` embeds
the data; the page shows "snapshot" instead of "live".

### 4. Link both ways

Add the page URL to the epic and every child item in the tracker (a link / attachment, not a
comment), so readers can jump from any ticket to the timeline. New children get it when they
appear.

### 5. Keep it current — at every milestone, unprompted

A stale progress page is worse than none: people trust it. Append events (no republish) when a
change opens / merges / gets a verdict, an item changes status, a blocked-by relation changes,
the epic is restructured (children added or removed → `inScope`), or a check produces
evidence. Re-sync `items` when relations or owners change; re-write `config/page` when the
profile changes.

**The cascade mirrors the tracker's relations exactly.** A dependency drawn in a diagram or
comment but absent from the tracker gets no arrow — say so and suggest adding the relation.

### 6. Report

One or two lines: what changed on the page, plus anything you could not verify (approximate
times, unreachable sources, unmapped statuses).

## Judgment calls

- **What counts toward %, burn-up and forecast.** Only `inScope` items, minus `duplicate` /
  `canceled`. Related bugs show on the boards but never count. The page says "counts items,
  not effort" — keep it so; don't invent story-point weights.
- **Forecast.** Off by default; a band (±1 standard error), never a single promised date, and
  "no end date at this pace" when the pessimistic slope is ≤ 0. WIP credit weights are
  assumptions printed on the page; the done-only forecast is always shown next to them.
- **Lanes.** Cascade lanes: 3–6, matching how the team splits work, upstream → downstream.
  Event lanes: the kind of source (Tracker, Code, Review, Design, Live, Planning, Other).
- **People.** Map a login to a name only when certain. Never publish email addresses.
- **Evidence grid** only for a real matrix of checks; omit `config.matrix` otherwise.
- **Security-relevant findings** go on the timeline as factual events, without exploit detail.

## Migrating an older page

Pages built by the earlier `epic-observation-tool` skill or by hand (collections `tickets`,
effects `ticket` / `pr` / `cell`, fields `layer` / `epic`, tool wording as `status`) still
render. To move one onto this template: read its collections, write a profile, run
`normalize` over the events, republish the template to the same URL, and re-seed `config/page`.
