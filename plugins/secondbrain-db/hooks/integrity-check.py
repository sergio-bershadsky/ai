#!/usr/bin/env python3
"""PostToolUse hook: runs sbdb doctor check after Write/Edit on .md or .yaml files.

Only triggers when the edited file is inside a docs/ or data/ directory and
a .sbdb.toml exists in the project root (indicating an sbdb-managed project).
"""

import json
import os
import subprocess
import sys


def main():
    # Read the hook input from stdin
    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        return

    # Get the tool name and file path
    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})

    if tool_name not in ("Write", "Edit"):
        return

    file_path = tool_input.get("file_path", "")
    if not file_path:
        return

    # Only check .md and .yaml files
    if not file_path.endswith((".md", ".yaml", ".yml")):
        return

    # Only check files in docs/ or data/ directories
    if "/docs/" not in file_path and "/data/" not in file_path:
        return

    # Find the project root (walk up looking for .sbdb.toml)
    project_root = find_project_root(file_path)
    if not project_root:
        return

    # Check if sbdb is available
    sbdb_path = find_sbdb()
    if not sbdb_path:
        return

    # Run doctor check
    try:
        result = subprocess.run(
            [sbdb_path, "doctor", "check", "--format", "json", "-b", project_root],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return

    if result.returncode == 0:
        return  # all clean

    # Parse the result
    try:
        data = json.loads(result.stdout)
        issues = data.get("data", {})
        drift_count = issues.get("drift_count", 0)
        tamper_count = issues.get("tamper_count", 0)
    except (json.JSONDecodeError, KeyError):
        drift_count = 0
        tamper_count = 0

    # Build warning message
    warnings = []
    if drift_count > 0:
        warnings.append(f"{drift_count} drift issue(s)")
    if tamper_count > 0:
        warnings.append(f"{tamper_count} tamper issue(s)")

    if warnings:
        parts = [f"[sbdb] KB integrity: {', '.join(warnings)} detected after editing {os.path.basename(file_path)}."]

        if drift_count > 0 and tamper_count == 0:
            # Pure drift (likely caused by AI editing frontmatter/content) — safe to auto-fix
            parts.append(
                "This is drift caused by direct file edits. "
                "Run `sbdb doctor fix --recompute` to sync frontmatter with records and re-sign."
            )
        elif tamper_count > 0:
            # Tamper — file was edited outside the ORM
            parts.append(
                "Files were modified outside sbdb. "
                "Review the changes, then either:\n"
                "  - `sbdb doctor sign --force` to accept the edits\n"
                "  - `git checkout <file>` to revert"
            )

        msg = " ".join(parts)
        print(json.dumps({"message": msg}))


def find_project_root(file_path):
    """Walk up from the file path looking for .sbdb.toml."""
    directory = os.path.dirname(os.path.abspath(file_path))
    for _ in range(10):  # max 10 levels up
        if os.path.exists(os.path.join(directory, ".sbdb.toml")):
            return directory
        parent = os.path.dirname(directory)
        if parent == directory:
            break
        directory = parent
    return None


def find_sbdb():
    """Find the sbdb binary in PATH or common locations."""
    # Check PATH
    for path_dir in os.environ.get("PATH", "").split(os.pathsep):
        candidate = os.path.join(path_dir, "sbdb")
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate

    # Check common Go bin locations
    home = os.path.expanduser("~")
    for candidate in [
        os.path.join(home, "go", "bin", "sbdb"),
        "/usr/local/bin/sbdb",
    ]:
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate

    return None


if __name__ == "__main__":
    main()
