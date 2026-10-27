# Epic Observation Plugin

A scrubbable "Epic Observation" page: drag back to any moment and see the epic as it stood then
— % done, burn-up with a forecast band, the blocked-by dependency cascade, open changes with
review verdicts, an optional evidence grid, and a filterable event log linked back to the
tracker and code host.

The same page works for Linear, Jira, monday.com, GitHub Issues/Projects, GitLab, Azure DevOps,
Asana, ClickUp, Shortcut… It looks and behaves identically for each, because the page only
reads a neutral data model; everything tool-specific sits in one per-project **tracker profile**.

![Sample page (Jira + GitLab profile)](https://raw.githubusercontent.com/sergio-bershadsky/ai/main/plugins/epic-observation/examples/sample.png)

## How it fits together

| Layer | File | Owned by |
|---|---|---|
| Template | `skills/epic-observation/assets/epic-observation.html` | plugin — never patched per tool |
| Data model (contract) | `skills/epic-observation/references/data-model.md` | plugin |
| Tracker profile | `.claude/epic-observation.json` in your project | you — status map, link templates, people |
| Epic seed / live db | `config` + `items` + `events` | the agent, from your tracker and code host |
| Tooling | `skills/epic-observation/scripts/observe.py` | plugin — `normalize`, `validate`, `config`, `export` |

**Bring your own tool.** The agent reads your tracker through whatever access you already
have (an MCP connector, a CLI, a REST API). It writes the tool's own wording into `label`, and
`observe.py normalize` converts it to canonical statuses through your profile's `statusMap`.
Example profiles: `assets/profiles/{linear,jira,github,monday}.json`; per-tool notes are in
`references/adapters.md`.

## Usage

Ask for it in plain words: *"make an observation page for epic SHOP-100"*, *"show how this
epic progressed"*, *"burn-up and forecast for the checkout project"*. The first run in a project
builds the profile with you. After that the skill keeps the page current as work lands.

Two ways to publish:

- **Live**: a claude.ai artifact backed by its database. Events are appended without
  republishing, and viewers see updates immediately.
- **Static**: `observe.py export seed.json out.html --profile .claude/epic-observation.json`
  writes a self-contained snapshot.

```bash
K=plugins/epic-observation/skills/epic-observation
python3 $K/scripts/observe.py export $K/assets/sample-seed.json /tmp/sample.html --profile $K/assets/profiles/jira.json
python3 -m unittest discover -s $K/tests
```
