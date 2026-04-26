#!/usr/bin/env python3
"""PreToolUse hook: block direct AI edits under .sbdb/events/ in sbdb-managed repos.

The events log is append-only and immutable. All writes must go through
`sbdb event append` (or the doctor archival path for archive/). This hook
rejects any direct Write/Edit/MultiEdit/NotebookEdit and any Bash mutation
targeting .sbdb/events/**.
"""

import json
import os
import re
import sys


BASH_MUTATION_RE = re.compile(
    r"""
    (?:^|[\s;&|`(])
    (?:
        (?:rm|mv|cp|tee|touch|mkdir|rmdir|chmod|chown|ln)\b
      | (?:sed|gsed|perl)\s+[^|;&]*?-i\b
      | awk\s+[^|;&]*?-i\s+inplace\b
    )
    """,
    re.VERBOSE,
)

REDIRECT_RE = re.compile(r"(?:>>?|\|\s*tee(?:\s+-a)?)\s+[\"']?([^\s\"';&|]+)")
TOKEN_RE = re.compile(r"[\"']?([^\s\"';&|<>]+)")


def main():
    try:
        event = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        return

    tool_name = event.get("tool_name", "")
    tool_input = event.get("tool_input", {}) or {}

    targets = collect_targets(tool_name, tool_input)
    if not targets:
        return

    for target in targets:
        project_root = find_project_root(target)
        if not project_root:
            continue
        if not is_under_events(target, project_root):
            continue
        emit_block(project_root, target)
        return


def collect_targets(tool_name, tool_input):
    if tool_name in ("Write", "Edit", "MultiEdit"):
        p = tool_input.get("file_path")
        return [os.path.abspath(p)] if p else []

    if tool_name == "NotebookEdit":
        p = tool_input.get("notebook_path") or tool_input.get("file_path")
        return [os.path.abspath(p)] if p else []

    if tool_name == "Bash":
        cmd = tool_input.get("command", "") or ""
        return bash_targets(cmd)

    return []


def bash_targets(cmd):
    targets = []
    cwd = os.getcwd()

    is_mutation = bool(BASH_MUTATION_RE.search(cmd))

    for m in REDIRECT_RE.finditer(cmd):
        targets.append(_resolve(m.group(1), cwd))

    if is_mutation:
        for m in TOKEN_RE.finditer(cmd):
            tok = m.group(1)
            if ".sbdb/events" in tok or tok.startswith(".sbdb/events"):
                targets.append(_resolve(tok, cwd))

    return targets


def _resolve(path, cwd):
    if os.path.isabs(path):
        return os.path.normpath(path)
    return os.path.normpath(os.path.join(cwd, path))


def is_under_events(abs_path, project_root):
    try:
        rel = os.path.relpath(abs_path, project_root)
    except ValueError:
        return False
    if rel.startswith(".."):
        return False
    parts = rel.split(os.sep)
    return len(parts) >= 2 and parts[0] == ".sbdb" and parts[1] == "events"


def find_project_root(file_path):
    directory = os.path.dirname(os.path.abspath(file_path))
    if not directory:
        directory = os.getcwd()
    for _ in range(10):
        if os.path.exists(os.path.join(directory, ".sbdb.toml")):
            return directory
        parent = os.path.dirname(directory)
        if parent == directory:
            break
        directory = parent
    return None


def find_sbdb():
    for path_dir in os.environ.get("PATH", "").split(os.pathsep):
        candidate = os.path.join(path_dir, "sbdb")
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate

    home = os.path.expanduser("~")
    for candidate in [
        os.path.join(home, "go", "bin", "sbdb"),
        "/usr/local/bin/sbdb",
    ]:
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate

    return None


def emit_block(project_root, target):
    sbdb = find_sbdb()
    rel = os.path.relpath(target, project_root)
    is_archive = rel.startswith(os.path.join(".sbdb", "events", "archive"))

    if is_archive:
        path_kind = "archive"
        guidance = (
            "Archive files under .sbdb/events/archive/ are sealed and immutable. "
            "Only `sbdb doctor fix` may write here, and only during scheduled monthly archival."
        )
    else:
        path_kind = "live event log"
        guidance = (
            "Event files under .sbdb/events/ are append-only and immutable. "
            "Use `sbdb event append --type <type> --id <id>` to record an event. "
            "Never edit existing event files."
        )

    if sbdb:
        reason = (
            f"Direct edits to the {path_kind} are not allowed in sbdb-managed repos "
            f"(.sbdb.toml at {project_root}). {guidance}"
        )
    else:
        reason = (
            f"Direct edits to the {path_kind} are not allowed in sbdb-managed repos "
            f"(.sbdb.toml at {project_root}), and the `sbdb` CLI was not found in PATH "
            f"or ~/go/bin.\n\n"
            f"Install with:\n"
            f"  go install github.com/bershadsky/sbdb@latest\n"
            f"Then ensure $(go env GOPATH)/bin is on your PATH.\n\n"
            f"{guidance}"
        )

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        },
        "decision": "block",
        "reason": reason,
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
