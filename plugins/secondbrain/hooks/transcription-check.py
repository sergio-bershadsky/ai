#!/usr/bin/env python3
"""
SessionStart hook: Check for undocumented meetings from transcription provider.

Triggers: When session starts
Action: Check provider for recent meetings not yet documented
Exit: 0 (always — inject context, never block)
"""

import json
import sys
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


def main():
    project_root = find_project_root()
    if not project_root:
        sys.exit(0)

    config_path = project_root / ".claude" / "data" / "config.yaml"
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}
    except Exception:
        sys.exit(0)

    # Check if transcription is configured and enabled
    transcription = config.get("integrations", {}).get("transcription", {})
    if not transcription.get("enabled", False):
        sys.exit(0)

    if not transcription.get("check_on_session_start", True):
        sys.exit(0)

    provider = transcription.get("provider")
    if not provider:
        sys.exit(0)

    lookback_days = transcription.get("lookback_days", 7)

    # Add project lib to path for provider client and tracking
    lib_path = project_root / ".claude" / "lib"
    sys.path.insert(0, str(lib_path))

    try:
        from tracking import is_meeting_processed
    except ImportError:
        sys.exit(0)

    # Load provider client dynamically
    meetings = []
    try:
        if provider == "fireflies":
            from fireflies import FirefliesClient
            client = FirefliesClient()
            meetings = client.list_meetings(limit=20, days=lookback_days)
        else:
            # Unknown provider — skip silently
            sys.exit(0)
    except Exception:
        # API unavailable — don't block session
        sys.exit(0)

    if not meetings:
        sys.exit(0)

    # Filter to undocumented meetings
    undocumented = []
    for meeting in meetings:
        meeting_id = meeting.get("id")
        if meeting_id and not is_meeting_processed(meeting_id):
            undocumented.append(meeting)

    if not undocumented:
        sys.exit(0)

    # Build context message
    lines = [
        f"You have {len(undocumented)} undocumented meeting(s) from {provider}:",
        ""
    ]

    for meeting in undocumented[:5]:
        date_str = meeting.get("date", "")[:10]
        title = meeting.get("title", "Untitled")
        duration = meeting.get("duration", 0)
        meeting_id = meeting.get("id", "")

        lines.append(f"- [{date_str}] {title} ({int(duration)} min)")
        lines.append(f"  ID: {meeting_id}")

    if len(undocumented) > 5:
        lines.append(f"  ... and {len(undocumented) - 5} more")

    lines.append("")
    lines.append(
        "Run `/secondbrain-transcribe list` to see all, "
        "or `/secondbrain-transcribe <id>` to document one."
    )

    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "\n".join(lines)
        }
    }
    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
