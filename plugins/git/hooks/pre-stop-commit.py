#!/usr/bin/env python3
"""
Stop hook: Check for uncommitted changes before stopping.

Triggers: When Claude attempts to stop
Action: Block if there are staged or unstaged changes, prompt for commit
Exit codes:
  0 = allow stopping (no changes or just committed)
  2 = block stopping (uncommitted changes)
"""

import json
import os
import subprocess
import sys


def get_project_dir():
    """Get project directory from environment or current dir."""
    return os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())


def get_git_status():
    """Get git status information."""
    project_dir = get_project_dir()

    try:
        # Check for staged changes
        staged = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=5
        )
        staged_files = [f for f in staged.stdout.strip().split("\n") if f]

        # Check for unstaged changes
        unstaged = subprocess.run(
            ["git", "diff", "--name-only"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=5
        )
        unstaged_files = [f for f in unstaged.stdout.strip().split("\n") if f]

        # Check for untracked files
        untracked = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=5
        )
        untracked_files = [f for f in untracked.stdout.strip().split("\n") if f]

        return staged_files, unstaged_files, untracked_files

    except subprocess.TimeoutExpired:
        return [], [], []
    except Exception:
        return [], [], []


def get_diff_stat():
    """Get diff stat for staged changes."""
    project_dir = get_project_dir()

    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--stat"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip()
    except Exception:
        return ""


def main():
    """Main hook entry point."""
    try:
        # Read input (not used but required for hook protocol)
        json.load(sys.stdin)
    except json.JSONDecodeError:
        pass

    staged, unstaged, untracked = get_git_status()

    # If no changes, allow stopping
    if not staged and not unstaged and not untracked:
        sys.exit(0)

    # Build message about uncommitted changes
    lines = ["Uncommitted changes detected. Please commit before stopping.", ""]

    if staged:
        lines.append(f"**Staged ({len(staged)} files):**")
        for f in staged[:10]:  # Limit to first 10
            lines.append(f"  - {f}")
        if len(staged) > 10:
            lines.append(f"  ... and {len(staged) - 10} more")
        lines.append("")

    if unstaged:
        lines.append(f"**Modified ({len(unstaged)} files):**")
        for f in unstaged[:10]:
            lines.append(f"  - {f}")
        if len(unstaged) > 10:
            lines.append(f"  ... and {len(unstaged) - 10} more")
        lines.append("")

    if untracked:
        lines.append(f"**Untracked ({len(untracked)} files):**")
        for f in untracked[:5]:
            lines.append(f"  - {f}")
        if len(untracked) > 5:
            lines.append(f"  ... and {len(untracked) - 5} more")
        lines.append("")

    # Add diff stat if there are staged changes
    if staged:
        diff_stat = get_diff_stat()
        if diff_stat:
            lines.append("**Diff summary:**")
            lines.append(f"```\n{diff_stat}\n```")
            lines.append("")

    lines.append("Run `/commit` to review and commit these changes.")

    # Block with message
    output = {
        "decision": "block",
        "reason": "\n".join(lines)
    }
    print(json.dumps(output))
    sys.exit(2)


if __name__ == "__main__":
    main()
