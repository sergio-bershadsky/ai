#!/usr/bin/env python3
"""
Search Index Update Hook (PostToolUse Write|Edit)

Incrementally updates qmd search index when docs/ files change.
Runs qmd in background to avoid blocking the session.

Exit codes:
- 0: Success (continue session)
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def find_project_root() -> Path | None:
    """Find the project root by looking for .claude/data/config.yaml"""
    cwd = Path.cwd()

    for path in [cwd] + list(cwd.parents):
        config_path = path / ".claude" / "data" / "config.yaml"
        if config_path.exists():
            return path

    return None


def is_search_initialized(project_root: Path) -> bool:
    """Check if search index exists"""
    search_dir = project_root / ".claude" / "search"
    return search_dir.exists() and any(search_dir.iterdir())


def is_qmd_installed() -> bool:
    """Check if qmd is available"""
    try:
        result = subprocess.run(
            ["which", "qmd"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def is_docs_file(file_path: str, project_root: Path) -> bool:
    """Check if file is a markdown file in docs directory"""
    try:
        full_path = Path(file_path)
        docs_dir = project_root / "docs"

        # Check if file is under docs/
        if docs_dir in full_path.parents or full_path.parent == docs_dir:
            # Only care about .md files
            return full_path.suffix == ".md"
    except Exception:
        pass

    return False


def should_skip_file(file_path: str) -> bool:
    """Check if file should be skipped from indexing"""
    path = Path(file_path)

    # Skip template files
    if path.name == "TEMPLATE.md":
        return True

    # Skip vitepress internal files
    if ".vitepress" in str(path):
        return True

    return False


def update_index_background(project_root: Path, file_path: str) -> None:
    """Trigger incremental qmd index update in background"""
    try:
        # Run qmd update in background
        # Using Popen to not block
        subprocess.Popen(
            ["qmd", "index", "--incremental"],
            cwd=str(project_root),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True  # Detach from parent process
        )
    except Exception:
        # Silently fail - search index update is non-critical
        pass


def main():
    """Main hook execution"""
    # Read hook input from stdin
    try:
        hook_input = json.loads(sys.stdin.read())
    except Exception:
        hook_input = {}

    project_root = find_project_root()

    if not project_root:
        sys.exit(0)

    # Check if search is initialized
    if not is_search_initialized(project_root):
        sys.exit(0)

    # Check if qmd is installed
    if not is_qmd_installed():
        sys.exit(0)

    # Get the file that was written/edited
    tool_input = hook_input.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path:
        sys.exit(0)

    # Check if this is a docs file
    if not is_docs_file(file_path, project_root):
        sys.exit(0)

    # Skip certain files
    if should_skip_file(file_path):
        sys.exit(0)

    # Trigger background index update
    update_index_background(project_root, file_path)

    # No output needed - silent background update
    sys.exit(0)


if __name__ == "__main__":
    main()
