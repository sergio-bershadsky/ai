#!/usr/bin/env python3
"""Validate every plugins/*/hooks/hooks.json file.

Checks:
  - Valid JSON.
  - Top-level shape: { "hooks": { <event>: [...] } }.
  - Event names are recognized: PreToolUse, PostToolUse, Stop, SubagentStop,
    SessionStart, SessionEnd, UserPromptSubmit, PreCompact, Notification.
  - Each entry has matcher (regex string) and a hooks[] array.
  - Each command references a script via ${CLAUDE_PLUGIN_ROOT}/<path>;
    resolves the path under plugins/<plugin>/ and confirms the file exists
    AND is executable.
  - Timeout is positive integer when present.

Exits 0 on success, 1 on any error.
"""

from __future__ import annotations

import json
import os
import re
import sys
import typing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLUGINS_DIR = ROOT / "plugins"

VALID_EVENTS = {
    "PreToolUse",
    "PostToolUse",
    "Stop",
    "SubagentStop",
    "SessionStart",
    "SessionEnd",
    "UserPromptSubmit",
    "PreCompact",
    "Notification",
}


def die(msg: str) -> "typing.NoReturn":
    sys.stderr.write(f"FAIL: {msg}\n")
    sys.exit(1)


def warn(msg: str) -> None:
    sys.stderr.write(f"warn: {msg}\n")


INTERPRETERS = ("python3", "python", "sh", "bash", "node", "deno", "ruby", "perl")


def validate_command(command: str, plugin_dir: Path, source: Path) -> None:
    if "${CLAUDE_PLUGIN_ROOT}" not in command:
        warn(
            f"{source.relative_to(ROOT)}: command does not reference "
            f"${{CLAUDE_PLUGIN_ROOT}} — paths may break when installed: {command!r}"
        )
        return

    # Pull out anything that follows ${CLAUDE_PLUGIN_ROOT}/ up to the next quote/space.
    matches = re.findall(r'\$\{CLAUDE_PLUGIN_ROOT\}([^"\s]+)', command)
    if not matches:
        die(
            f"{source.relative_to(ROOT)}: cannot extract script path from command: {command!r}"
        )

    # If the command starts with a known interpreter, the script doesn't need
    # to be executable — the interpreter reads it.
    leading = command.strip().split(maxsplit=1)[0]
    invoked_via_interpreter = any(leading.endswith(i) for i in INTERPRETERS)

    for relative in matches:
        relative = relative.lstrip("/")
        target = plugin_dir / relative
        if not target.exists():
            die(
                f"{source.relative_to(ROOT)}: command references "
                f"missing file: {target.relative_to(ROOT)}"
            )
        if not invoked_via_interpreter and not os.access(target, os.X_OK):
            die(
                f"{source.relative_to(ROOT)}: hook script is invoked directly "
                f"but is not executable: {target.relative_to(ROOT)} — "
                f"run `chmod +x` and commit"
            )


def validate_hooks_file(plugin_dir: Path, hooks_json: Path) -> int:
    try:
        data = json.loads(hooks_json.read_text())
    except json.JSONDecodeError as exc:
        die(f"{hooks_json.relative_to(ROOT)}: invalid JSON: {exc}")

    if not isinstance(data, dict):
        die(f"{hooks_json.relative_to(ROOT)}: top-level must be an object")

    # Accept both wrapped form {"hooks": {...}} and flat form {"PreToolUse": [...]}.
    if "hooks" in data and isinstance(data["hooks"], dict):
        events = data["hooks"]
    elif any(k in VALID_EVENTS for k in data.keys()):
        events = data
    else:
        die(
            f"{hooks_json.relative_to(ROOT)}: top-level must be either "
            f'{{"hooks": {{...}}}} or {{"<EventName>": [...]}}'
        )

    hook_count = 0
    for event_name, entries in events.items():
        if event_name not in VALID_EVENTS:
            die(
                f"{hooks_json.relative_to(ROOT)}: unknown event {event_name!r}. "
                f"Valid: {sorted(VALID_EVENTS)}"
            )
        if not isinstance(entries, list):
            die(f"{hooks_json.relative_to(ROOT)}: '{event_name}' must be an array")

        for i, entry in enumerate(entries):
            if not isinstance(entry, dict):
                die(
                    f"{hooks_json.relative_to(ROOT)}: {event_name}[{i}] must be an object"
                )
            matcher = entry.get("matcher")
            if matcher is None:
                die(
                    f"{hooks_json.relative_to(ROOT)}: {event_name}[{i}] missing 'matcher'"
                )
            try:
                re.compile(matcher)
            except re.error as exc:
                die(
                    f"{hooks_json.relative_to(ROOT)}: {event_name}[{i}] matcher "
                    f"{matcher!r} is not a valid regex: {exc}"
                )

            for h in entry.get("hooks", []):
                if not isinstance(h, dict):
                    die(
                        f"{hooks_json.relative_to(ROOT)}: {event_name}[{i}].hooks[] must be objects"
                    )
                if h.get("type") != "command":
                    die(
                        f"{hooks_json.relative_to(ROOT)}: {event_name}[{i}].hooks[] "
                        f"only 'command' type is supported, got {h.get('type')!r}"
                    )
                command = h.get("command")
                if not command:
                    die(
                        f"{hooks_json.relative_to(ROOT)}: {event_name}[{i}].hooks[] missing 'command'"
                    )
                timeout = h.get("timeout")
                if timeout is not None and (
                    not isinstance(timeout, int) or timeout <= 0
                ):
                    die(
                        f"{hooks_json.relative_to(ROOT)}: {event_name}[{i}].hooks[] "
                        f"timeout must be a positive integer, got {timeout!r}"
                    )
                validate_command(command, plugin_dir, hooks_json)
                hook_count += 1

    return hook_count


def main() -> None:
    if not PLUGINS_DIR.is_dir():
        die(f"plugins/ directory not found at {PLUGINS_DIR}")

    total_hooks = 0
    plugins_with_hooks = 0
    for plugin_dir in sorted(PLUGINS_DIR.iterdir()):
        if not plugin_dir.is_dir():
            continue
        hooks_json = plugin_dir / "hooks" / "hooks.json"
        if not hooks_json.exists():
            continue
        n = validate_hooks_file(plugin_dir, hooks_json)
        total_hooks += n
        plugins_with_hooks += 1
        print(f"  ok  {plugin_dir.name:30s} {n} hook(s)")

    print(
        f"\n{plugins_with_hooks} plugin(s) with hooks; {total_hooks} hook entr(ies) validated."
    )


if __name__ == "__main__":
    main()
