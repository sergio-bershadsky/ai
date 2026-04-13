#!/usr/bin/env python3
"""Stop hook: blocks Claude from finishing if KB integrity is broken.

This is the deterministic guardrail — even if Claude ignores the PostToolUse
warnings, this hook fires before the response is delivered and tells Claude
to fix the issue before stopping.
"""

import json
import os
import subprocess
import sys


def main():
    # Find sbdb project root
    cwd = os.getcwd()
    project_root = find_project_root(cwd)
    if not project_root:
        return  # not an sbdb project

    sbdb = find_sbdb()
    if not sbdb:
        return  # sbdb not installed

    # Run doctor check
    try:
        result = subprocess.run(
            [sbdb, "doctor", "check", "--format", "json", "-b", project_root],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return

    if result.returncode == 0:
        return  # all clean, allow stop

    # Parse issues
    try:
        data = json.loads(result.stdout)
        issues = data.get("data", {})
        drift_count = issues.get("drift_count", 0)
        tamper_count = issues.get("tamper_count", 0)
    except (json.JSONDecodeError, KeyError):
        return

    if drift_count == 0 and tamper_count == 0:
        return

    # Also check untracked files
    untracked_issues = check_untracked(sbdb, project_root)

    # Build the blocking message
    parts = ["[sbdb] INTEGRITY CHECK FAILED — do not stop yet."]

    if drift_count > 0:
        parts.append(f"\n{drift_count} drift issue(s): run `sbdb doctor fix --recompute`")

    if tamper_count > 0:
        parts.append(f"\n{tamper_count} tamper issue(s): run `sbdb doctor sign --force` for files you edited, or revert unintended changes")

    if untracked_issues:
        parts.append(f"\n{untracked_issues} untracked file(s) need signing: run `sbdb untracked sign-all docs/`")

    parts.append("\nFix these issues, re-run `sbdb doctor check`, and verify exit code 0 before finishing.")

    msg = "".join(parts)

    # Output as a blocking hook message
    output = {"message": msg}

    # If there are issues, we want Claude to keep working
    # The "decision" field tells Claude to not stop
    if drift_count > 0 or tamper_count > 0:
        output["decision"] = "block"

    print(json.dumps(output))


def check_untracked(sbdb, project_root):
    """Check if there are unsigned files that should be tracked."""
    try:
        result = subprocess.run(
            [sbdb, "untracked", "sign-all", "docs/", "--dry-run", "--format", "json", "-b", project_root],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get("data", {}).get("discovered", 0)
    except Exception:
        pass
    return 0


def find_project_root(start_dir):
    directory = os.path.abspath(start_dir)
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
    for candidate in [os.path.join(home, "go", "bin", "sbdb"), "/usr/local/bin/sbdb"]:
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


if __name__ == "__main__":
    main()
