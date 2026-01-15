#!/usr/bin/env python3
"""
Session Context Hook (SessionStart)

Provides Claude with context about the secondbrain project
at the start of each session.

Exit codes:
- 0: Success (message is informational)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit(0)


def find_project_root() -> Path | None:
    """Find the project root by looking for .claude/data/config.yaml"""
    cwd = Path.cwd()

    for path in [cwd] + list(cwd.parents):
        config_path = path / ".claude" / "data" / "config.yaml"
        if config_path.exists():
            return path

    return None


def load_config(project_root: Path) -> dict | None:
    """Load secondbrain configuration"""
    config_path = project_root / ".claude" / "data" / "config.yaml"

    if not config_path.exists():
        return None

    try:
        with open(config_path) as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def count_entity_records(project_root: Path, entity: str, config: dict) -> dict:
    """Count records for an entity"""
    entity_config = config.get("entities", {}).get(entity, {})

    if not entity_config.get("enabled", False):
        return {"total": 0, "active": 0}

    partitioned = entity_config.get("partitioned") == "monthly"
    data_dir = project_root / ".claude" / "data" / entity

    if not data_dir.exists():
        return {"total": 0, "active": 0}

    total = 0
    active = 0

    if partitioned:
        for yaml_file in data_dir.glob("*.yaml"):
            if yaml_file.name == "schema.yaml":
                continue
            try:
                with open(yaml_file) as f:
                    records = yaml.safe_load(f) or []
                total += len(records)
                # For partitioned, count non-archived
                for r in records:
                    status = r.get("status", "").lower()
                    if status not in ["archived", "canceled"]:
                        active += 1
            except Exception:
                continue
    else:
        records_path = data_dir / "records.yaml"
        if records_path.exists():
            try:
                with open(records_path) as f:
                    data = yaml.safe_load(f) or {}
                records = data.get("records", [])
                total = len(records)
                for r in records:
                    status = r.get("status", "").lower()
                    if status not in ["archived", "completed", "done", "canceled", "rejected"]:
                        active += 1
            except Exception:
                pass

    return {"total": total, "active": active}


def get_recent_activity(project_root: Path, config: dict) -> list[str]:
    """Get recent activity summary"""
    activities = []

    for entity, entity_config in config.get("entities", {}).items():
        if not entity_config.get("enabled", False):
            continue

        data_dir = project_root / ".claude" / "data" / entity
        if not data_dir.exists():
            continue

        # Get most recent record
        most_recent = None
        most_recent_date = None

        partitioned = entity_config.get("partitioned") == "monthly"

        if partitioned:
            yaml_files = sorted(data_dir.glob("*.yaml"), reverse=True)
            for yaml_file in yaml_files:
                if yaml_file.name == "schema.yaml":
                    continue
                try:
                    with open(yaml_file) as f:
                        records = yaml.safe_load(f) or []
                    if records:
                        for r in sorted(records, key=lambda x: x.get("date", ""), reverse=True):
                            date_str = r.get("date")
                            if date_str:
                                most_recent = r
                                most_recent_date = date_str
                                break
                    if most_recent:
                        break
                except Exception:
                    continue
        else:
            records_path = data_dir / "records.yaml"
            if records_path.exists():
                try:
                    with open(records_path) as f:
                        data = yaml.safe_load(f) or {}
                    records = data.get("records", [])
                    if records:
                        # Sort by created date descending
                        sorted_records = sorted(
                            records,
                            key=lambda x: x.get("created") or x.get("date_created") or "",
                            reverse=True
                        )
                        if sorted_records:
                            most_recent = sorted_records[0]
                            most_recent_date = (
                                most_recent.get("created") or
                                most_recent.get("date_created")
                            )
                except Exception:
                    pass

        if most_recent and most_recent_date:
            singular = entity_config.get("singular", entity.rstrip("s"))
            title = most_recent.get("title") or most_recent.get("topic") or most_recent.get("id", "")
            activities.append(f"- Last {singular}: \"{title}\" ({most_recent_date})")

    return activities[:5]  # Limit to 5 most recent


def main():
    """Main hook execution"""
    project_root = find_project_root()

    if not project_root:
        sys.exit(0)

    config = load_config(project_root)

    if not config:
        sys.exit(0)

    project_name = config.get("project", {}).get("name", "Secondbrain")

    # Count records per entity
    entity_stats = {}
    for entity in config.get("entities", {}).keys():
        stats = count_entity_records(project_root, entity, config)
        if stats["total"] > 0:
            entity_stats[entity] = stats

    # Build context message
    lines = [
        f"**{project_name} Secondbrain**",
        ""
    ]

    if entity_stats:
        lines.append("**Records:**")
        for entity, stats in entity_stats.items():
            entity_config = config.get("entities", {}).get(entity, {})
            singular = entity_config.get("singular", entity.rstrip("s"))
            if stats["active"] < stats["total"]:
                lines.append(f"- {entity.title()}: {stats['active']} active / {stats['total']} total")
            else:
                lines.append(f"- {entity.title()}: {stats['total']}")
        lines.append("")

    # Recent activity
    activities = get_recent_activity(project_root, config)
    if activities:
        lines.append("**Recent:**")
        lines.extend(activities)
        lines.append("")

    # Available skills
    lines.append("**Available:** `/secondbrain-adr`, `/secondbrain-note`, `/secondbrain-task`, `/secondbrain-discussion`, `/secondbrain-freshness`")

    print(json.dumps({
        "result": "continue",
        "message": "\n".join(lines)
    }))

    sys.exit(0)


if __name__ == "__main__":
    main()
