#!/usr/bin/env python3
"""Epic Observation tooling: tracker profile -> page config, status normalization, validation,
static export. Standard library only.

The page never knows which tracker produced its data. Two inputs carry everything tool-specific:

  profile  .claude/epic-observation.json — one per project/tracker: tracker name, link
           templates, id pattern, status map (tool wording -> canonical), people, event lanes.
  seed     {"config": {...}, "items": {...}, "events": [...]} — one per epic. `config` holds
           only epic-level fields (title, subtitle, lanes, matrix); the profile fills the rest.

Usage:
    observe.py config     PROFILE [SEED]       print the merged config/page document
    observe.py normalize  PROFILE SEED [OUT]   set canonical `status` from each effect's `label`
    observe.py validate   SEED [--profile P]   report problems; exit 1 if any
    observe.py export     SEED OUT [--profile P]  embed the seed in the template (static page)

See references/data-model.md and references/profile.md.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "epic-observation.html"

CANONICAL = {
    "item": {"triage", "backlog", "ready", "in_progress", "in_review", "blocked", "done", "duplicate", "canceled"},
    "change": {"open", "changes_requested", "approved", "merged", "closed"},
    "check": {"pass", "fail", "blocked", "pending", "untested", "dropped"},
}
LEGACY_TYPES = {"ticket": "item", "pr": "change", "cell": "check"}
# Profile keys copied into config/page. Everything else in the profile (statusMap, notes) is
# tooling-only and never reaches the published page.
PAGE_KEYS = ("tracker", "idPattern", "changePrefix", "links", "people", "eventLanes", "forecast")
NESTED = ("links", "tracker", "people", "forecast")


class UnmappedStatus(ValueError):
    """A tracker status the profile has no canonical mapping for."""


def load(path: str | Path) -> dict:
    return json.loads(Path(path).read_text())


def effect_type(ef: dict) -> str:
    t = str(ef.get("type", ""))
    return LEGACY_TYPES.get(t, t)


def merge_config(profile: dict, epic_config: dict | None) -> dict:
    """Profile supplies tool settings; the epic's own config wins on conflicts, key by key for
    nested maps (so an epic can add one person without restating the whole people map)."""
    out = {k: profile[k] for k in PAGE_KEYS if k in profile}
    for k, v in (epic_config or {}).items():
        out[k] = {**out.get(k, {}), **v} if k in NESTED and isinstance(v, dict) else v
    return out


def resolve_status(kind: str, label: str, status_map: dict[str, dict[str, str]]) -> str:
    """Canonical status for a tracker label, using profile.statusMap[kind].

    Matching is case-insensitive on the tool's wording. A label that already is a canonical
    value passes through.
    """
    table = {k.casefold(): v for k, v in status_map.get(kind, {}).items()}
    key = label.strip().casefold()
    if key in table:
        return table[key]
    if key.replace(" ", "_") in CANONICAL[kind]:
        return key.replace(" ", "_")
    # WHY strict: a guessed status silently skews % done and the forecast on a page the team
    # trusts; refusing makes the gap visible so the profile's statusMap gets extended instead.
    raise UnmappedStatus(f"{kind} label {label!r} is not in statusMap.{kind} and is not canonical")


def normalize(seed: dict, profile: dict) -> list[str]:
    """Fill `status` on item/change effects from `label`. Returns the problems found."""
    problems: list[str] = []
    status_map = profile.get("statusMap", {})
    for i, ev in enumerate(seed.get("events", [])):
        for ef in ev.get("effects", []):
            kind = effect_type(ef)
            if kind not in ("item", "change") or not ef.get("label"):
                continue
            try:
                ef["status"] = resolve_status(kind, ef["label"], status_map)
            except UnmappedStatus as err:
                problems.append(f"event {i} ({ev.get('at')}): {err}")
    return problems


def validate(seed: dict, profile: dict | None = None) -> list[str]:
    """Problems that would make the page wrong. Empty list means the seed is usable."""
    problems: list[str] = []
    items = seed.get("items", {})
    if not isinstance(items, dict):
        return ["items must be an object keyed by item id"]
    config = merge_config(profile or {}, seed.get("config"))
    try:
        id_re = re.compile(config.get("idPattern", r"[A-Z][A-Z0-9]+-\d+"))
    except re.error as err:
        problems.append(f"idPattern is not a valid regex: {err}")
        id_re = None
    lanes = config.get("lanes")
    for item_id, item in items.items():
        if not item.get("title"):
            problems.append(f"item {item_id} has no title")
        if lanes and item.get("lane") and item["lane"] not in lanes:
            problems.append(f"item {item_id} lane {item['lane']!r} is not in config.lanes")
        for blocker in item.get("blockedBy", []):
            if blocker not in items:
                problems.append(f"{item_id} is blocked by {blocker}, which is not in items")
        if id_re and not item.get("url") and not id_re.fullmatch(item_id):
            problems.append(f"item {item_id} does not match idPattern and has no url")
    for i, ev in enumerate(seed.get("events", [])):
        where = f"event {i}"
        for key in ("at", "title"):
            if not ev.get(key):
                problems.append(f"{where} is missing {key!r}")
        if ev.get("at") and not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d(:\d\d(\.\d+)?)?Z", ev["at"]):
            problems.append(f"{where}: at {ev['at']!r} is not ISO-8601 UTC (…Z)")
        for ef in ev.get("effects", []):
            kind = effect_type(ef)
            if kind not in CANONICAL:
                problems.append(f"{where}: unknown effect type {ef.get('type')!r}")
                continue
            value = ef.get("result") if kind == "check" else ef.get("status")
            if value is not None and value not in CANONICAL[kind]:
                problems.append(f"{where}: {kind} {ef.get('id', '')} status {value!r} is not canonical")
            if kind == "item" and ef.get("id") not in items and not ef.get("title"):
                problems.append(f"{where}: item {ef.get('id')} has no title and no entry in items")
    return problems


def export(seed: dict, profile: dict | None) -> str:
    seed = {**seed, "config": merge_config(profile or {}, seed.get("config"))}
    # WHY escape "</": the seed sits inside a <script> element; a literal "</script>" in any
    # event text would end the element early and break the page.
    payload = json.dumps(seed, ensure_ascii=False).replace("</", "<\\/")
    tag = f'<script type="application/json" id="seed">{payload}</script>\n'
    page = TEMPLATE.read_text()
    # WHY the prefix: the template is an artifact body (the host adds doctype + charset); a
    # standalone file without them renders in quirks mode with mangled non-ASCII text.
    head = '<!doctype html>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n'
    return head + page.replace("<script>\n", tag + "<script>\n", 1)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("config"); c.add_argument("profile"); c.add_argument("seed", nargs="?")
    n = sub.add_parser("normalize"); n.add_argument("profile"); n.add_argument("seed"); n.add_argument("out", nargs="?")
    v = sub.add_parser("validate"); v.add_argument("seed"); v.add_argument("--profile")
    e = sub.add_parser("export"); e.add_argument("seed"); e.add_argument("out"); e.add_argument("--profile")
    a = ap.parse_args(argv)

    if a.cmd == "config":
        seed = load(a.seed) if a.seed else {}
        print(json.dumps(merge_config(load(a.profile), seed.get("config")), indent=2, ensure_ascii=False))
        return 0
    if a.cmd == "normalize":
        seed = load(a.seed)
        problems = normalize(seed, load(a.profile))
        Path(a.out or a.seed).write_text(json.dumps(seed, indent=2, ensure_ascii=False) + "\n")
        return report(problems)
    profile = load(a.profile) if a.profile else None
    seed = load(a.seed)
    problems = validate(seed, profile)
    if a.cmd == "validate" or problems:
        return report(problems)
    Path(a.out).write_text(export(seed, profile))
    print(f"wrote {a.out} ({len(seed.get('events', []))} events, {len(seed.get('items', {}))} items)")
    return 0


def report(problems: list[str]) -> int:
    if problems:
        print("Problems:\n- " + "\n- ".join(problems), file=sys.stderr)
        return 1
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
