#!/usr/bin/env python3
"""
Freshness Check Hook (UserPromptSubmit)

Checks for stale records in the secondbrain and provides context
to Claude about items needing attention.

Exit codes:
- 0: Success (message is informational)
- 2: Block session (not used here)
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    import yaml
except ImportError:
    # yaml not available, skip check
    sys.exit(0)


def find_project_root() -> Path | None:
    """Find the project root by looking for .claude/data/config.yaml"""
    cwd = Path.cwd()

    # Check current directory and parents
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


def check_entity_freshness(project_root: Path, entity: str, config: dict) -> list[dict]:
    """Check freshness for a specific entity"""
    stale_items = []

    entity_config = config.get("entities", {}).get(entity, {})
    if not entity_config.get("enabled", False):
        return stale_items

    freshness_config = entity_config.get("freshness", {})
    stale_days = freshness_config.get("stale_after_days", 30)
    stale_threshold = datetime.now() - timedelta(days=stale_days)

    # Check if entity uses monthly partitioning
    partitioned = entity_config.get("partitioned") == "monthly"

    data_dir = project_root / ".claude" / "data" / entity

    if not data_dir.exists():
        return stale_items

    if partitioned:
        # Check monthly files
        for yaml_file in data_dir.glob("*.yaml"):
            if yaml_file.name == "schema.yaml":
                continue

            try:
                with open(yaml_file) as f:
                    records = yaml.safe_load(f) or []

                for record in records:
                    date_str = record.get("date")
                    if date_str:
                        record_date = datetime.strptime(date_str, "%Y-%m-%d")
                        if record_date < stale_threshold:
                            status = record.get("status", "unknown")
                            if status not in ["archived", "completed", "done", "canceled"]:
                                stale_items.append({
                                    "entity": entity,
                                    "id": record.get("id", record.get("topic", "Unknown")),
                                    "date": date_str,
                                    "days_old": (datetime.now() - record_date).days
                                })
            except Exception:
                continue
    else:
        # Check records.yaml
        records_path = data_dir / "records.yaml"

        if not records_path.exists():
            return stale_items

        try:
            with open(records_path) as f:
                data = yaml.safe_load(f) or {}

            records = data.get("records", [])

            for record in records:
                # Get date field (could be created, date, date_created, etc.)
                date_str = (
                    record.get("created") or
                    record.get("date") or
                    record.get("date_created") or
                    record.get("date_updated")
                )

                if not date_str:
                    continue

                try:
                    record_date = datetime.strptime(str(date_str), "%Y-%m-%d")
                except ValueError:
                    continue

                # Skip completed/archived/canceled items
                status = record.get("status", "").lower()
                if status in ["archived", "completed", "done", "canceled", "rejected", "tested", "implemented"]:
                    continue

                if record_date < stale_threshold:
                    stale_items.append({
                        "entity": entity,
                        "id": record.get("id") or record.get("number") or record.get("title", "Unknown"),
                        "title": record.get("title", ""),
                        "status": status,
                        "date": str(date_str),
                        "days_old": (datetime.now() - record_date).days
                    })
        except Exception:
            pass

    return stale_items


def main():
    """Main hook execution"""
    # Read hook input from stdin
    try:
        hook_input = json.loads(sys.stdin.read())
    except Exception:
        hook_input = {}

    # Find project root
    project_root = find_project_root()

    if not project_root:
        # Not a secondbrain project, exit silently
        sys.exit(0)

    # Load config
    config = load_config(project_root)

    if not config:
        sys.exit(0)

    # Check last freshness check time
    meta = config.get("meta", {})
    last_check = meta.get("last_freshness_check")

    if last_check:
        try:
            last_check_time = datetime.fromisoformat(last_check)
            # Only run full check once per hour
            if datetime.now() - last_check_time < timedelta(hours=1):
                sys.exit(0)
        except Exception:
            pass

    # Collect stale items from all entities
    all_stale = []

    for entity in config.get("entities", {}).keys():
        stale_items = check_entity_freshness(project_root, entity, config)
        all_stale.extend(stale_items)

    # Sort by days_old descending
    all_stale.sort(key=lambda x: x.get("days_old", 0), reverse=True)

    # Output result if there are stale items
    if all_stale:
        # Limit to top 10 most stale
        top_stale = all_stale[:10]

        output = {
            "message": f"Secondbrain Freshness Alert: {len(all_stale)} item(s) need attention",
            "details": top_stale,
            "total_stale": len(all_stale)
        }

        # Format as context message
        context_lines = [
            f"**Secondbrain Freshness:** {len(all_stale)} item(s) may need review:",
            ""
        ]

        for item in top_stale[:5]:
            entity = item["entity"]
            item_id = item["id"]
            days = item["days_old"]
            title = item.get("title", "")
            status = item.get("status", "")

            line = f"- [{entity}] {item_id}"
            if title:
                line += f": {title}"
            if status:
                line += f" (status: {status})"
            line += f" — {days} days old"

            context_lines.append(line)

        if len(all_stale) > 5:
            context_lines.append(f"- ... and {len(all_stale) - 5} more")

        context_lines.append("")
        context_lines.append("Run `/secondbrain-freshness` for full report.")

        print(json.dumps({
            "result": "continue",
            "message": "\n".join(context_lines)
        }))

    sys.exit(0)


if __name__ == "__main__":
    main()
