# Adapters — mapping a tracker onto the data model

Each section answers the same five questions: how to list the epic's children, where status
and its history live, where blocked-by relations live, how statuses map to the canonical set,
and what the link templates are. The answers go into the project's profile
(`references/profile.md`) once; after that, every run only gathers facts. Use whatever access
the user has — official MCP connector, CLI, or REST API; read-only calls are enough to build the
page. Put the tool's own wording into `label`; `observe.py normalize` sets `status` from the
profile's `statusMap`. Example profiles: `assets/profiles/`.

Verify every API detail below against the tool's current docs or the user's instance before
relying on it — trackers rename fields and endpoints.

## Linear
- Children: issues with `parentId = <epic>` (MCP `list_issues {parentId}`).
- Timestamps: `createdAt`, `startedAt`, `completedAt`, `canceledAt`; comments for decisions.
- Relations: `get_issue {includeRelations: true}` → `relations.blockedBy`.
- Status map: Triage→`triage`, Backlog→`backlog`, Todo / "Pick Immediately"→`ready`,
  In Progress→`in_progress`, In Review→`in_review`, Done→`done`, Duplicate→`duplicate`,
  Canceled→`canceled`. A `blocked` label usually means `blocked` only if the team uses it so.
- Links: `links.item = "https://linear.app/<workspace>/issue/{id}"`. Attach the page with the
  issue `links` field (an attachment), on the epic and each child.

## Jira (Cloud / Data Center)
- Children: JQL `parent = EPIC-1` (next-gen) or `"Epic Link" = EPIC-1` (classic).
- Timestamps: `created`, `resolutiondate`; status changes from the changelog
  (`expand=changelog`) give exact start/review times.
- Relations: issue links of type "Blocks" (inward "is blocked by").
- Status map by status *category* first: To Do→`backlog`/`ready`, In Progress→`in_progress`,
  Done→`done`; refine by name (In Review→`in_review`, Won't Do→`canceled`, Duplicate→`duplicate`).
- Links: `links.item = "https://<site>.atlassian.net/browse/{id}"`. Attach via a remote link.

## GitHub Issues / Projects
- Children: sub-issues of the parent issue, or items of a Project filtered by an Epic field.
- Timestamps: issue `created_at`, `closed_at`; timeline events (labeled, project status
  field changes) for in-progress/review moments.
- Relations: "blocked by" issue dependencies where enabled; otherwise only a convention —
  don't invent arrows from prose.
- Status map: open → `backlog`/`ready`/`in_progress` (use the Project status field),
  closed as completed → `done`, closed as not planned → `canceled`, duplicate → `duplicate`.
- IDs: `idPattern` like `"[a-z-]+#\\d+"` or plain issue numbers; `changePrefix: "#"` is usually
  the PR number — if issues and PRs share `#`, give items an explicit `url` and keep `#` for changes.
- Links: `links.change = "https://github.com/<org>/<repo>/pull/{n}"`,
  `links.commit = "https://github.com/<org>/<repo>/commit/{sha}"`.

## GitLab
- Children: epic issues (`/groups/:id/epics/:iid/issues`) or a parent issue's child items.
- Relations: issue links with `link_type = is_blocked_by`.
- Status: state + workflow labels / board lists; closed → `done`.
- Changes: merge requests, `changePrefix: "!"`,
  `links.change = "https://<host>/<group>/<project>/-/merge_requests/{n}"`.

## Azure DevOps
- Children: work items with a Parent link to the Epic/Feature (WIQL tree query).
- Relations: `System.LinkTypes.Dependency-Reverse` (predecessor) as blocked-by.
- Status map by state category: Proposed→`backlog`, In Progress→`in_progress`,
  Resolved→`in_review`, Completed→`done`, Removed→`canceled`.
- Links: `links.item = "https://dev.azure.com/<org>/<project>/_workitems/edit/{id}"`.

## Asana
- Children: subtasks of the epic task, or tasks in a project/section.
- Relations: task dependencies ("waiting on").
- Status: completed → `done`; otherwise a custom "Status" field or the section name.
- Links: tasks have `permalink_url` — store it as each item's `url`.

## monday.com
- Children: the epic is usually an item whose **subitems** are the work, or a board / group
  that holds the epic's items. Ask which convention the team uses.
- Timestamps: item `created_at`; status-change times from the board's activity log
  (GraphQL `boards { activity_logs }`, filter by the status column) — the item's
  `updated_at` alone is not a status-change time.
- Relations: the board's **Dependency** column (item → items it depends on) is blocked-by. No
  dependency column → empty `blockedBy` and say so in the subtitle.
- Status: Status columns have per-board labels (defaults like "Working on it", "Stuck",
  "Done"); map each board label in `statusMap.item` (Stuck → `blocked`).
- IDs: numeric — set `idPattern` to `($^)` so plain numbers never auto-link, and store each
  item's URL in `url` (`https://<account>.monday.com/boards/<board>/pulses/<item>`). Use a short
  human id in titles if the team has one (an "ID" column).

## ClickUp
- Children: subtasks of the epic task, or tasks in a List/Folder.
- Timestamps: `date_created`, `date_closed`; status history via the time-in-status endpoint.
- Relations: task dependencies ("waiting on" = blocked-by).
- Status: per-List custom statuses with a type (open / custom / closed) — map by name.
- Links: tasks carry a `url`; store it per item.

## Shortcut / Notion / others
Answer the five questions from the tool's API docs:
1. How do I list the children of the epic (parent link, epic field, project/section)?
2. Where are status and status-change timestamps (history/changelog/activity)?
3. Where are blocked-by (or "depends on") relations?
4. What maps onto each canonical status (use the tool's status categories when it has them)?
5. What URL shape opens an item, a change, a commit?

If the tool has no relations at all, leave `blockedBy` empty and say on the page (subtitle)
that the cascade has no dependency data — don't infer dependencies from text.

## Code hosts (changes and commits)
Changes come from the code host, not the tracker: opened, review verdicts, merged/closed, with
their timestamps. Connect a change to items through the ticket id in its title, body or branch
name, and record it as a `change` effect.
