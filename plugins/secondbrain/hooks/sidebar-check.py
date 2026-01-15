#!/usr/bin/env python3
"""
Sidebar Check Hook (PostToolUse Write|Edit)

Checks if newly created/edited doc files are properly linked
in the VitePress sidebar configuration.

Exit codes:
- 0: Success (warning message if orphan found)
"""

import json
import os
import re
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


def get_tool_output(hook_input: dict) -> dict | None:
    """Extract tool output from hook input"""
    return hook_input.get("tool_output", {})


def is_docs_file(file_path: str, project_root: Path) -> bool:
    """Check if file is in docs directory"""
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


def get_relative_docs_path(file_path: str, project_root: Path) -> str | None:
    """Get path relative to docs directory"""
    try:
        full_path = Path(file_path)
        docs_dir = project_root / "docs"

        if docs_dir in full_path.parents or full_path.parent == docs_dir:
            rel_path = full_path.relative_to(docs_dir)
            # Convert to VitePress link format (without .md extension)
            link = "/" + str(rel_path).replace(".md", "")
            if link.endswith("/index"):
                link = link[:-6] + "/"
            return link
    except Exception:
        pass

    return None


def check_sidebar_contains_link(config_path: Path, link: str) -> bool:
    """Check if sidebar configuration contains the link"""
    if not config_path.exists():
        return True  # No config, can't check

    try:
        content = config_path.read_text()

        # Simple check: look for the link in the config
        # Handle both with and without trailing slash
        link_patterns = [
            f"'{link}'",
            f'"{link}"',
            f"'{link}/'",
            f'"{link}/"',
        ]

        for pattern in link_patterns:
            if pattern in content:
                return True

        # Also check for the path without leading slash
        link_no_slash = link.lstrip("/")
        additional_patterns = [
            f"'{link_no_slash}'",
            f'"{link_no_slash}"',
        ]

        for pattern in additional_patterns:
            if pattern in content:
                return True

    except Exception:
        return True  # Can't read, assume OK

    return False


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

    # Get the file that was written
    tool_input = hook_input.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path:
        sys.exit(0)

    # Check if this is a docs file
    if not is_docs_file(file_path, project_root):
        sys.exit(0)

    # Skip index files, theme files, and data files
    path_obj = Path(file_path)
    if (path_obj.name == "index.md" or
        ".vitepress" in str(path_obj) or
        path_obj.name.endswith(".data.ts")):
        sys.exit(0)

    # Get the relative link path
    link = get_relative_docs_path(file_path, project_root)

    if not link:
        sys.exit(0)

    # Check if it's in the sidebar
    config_path = project_root / "docs" / ".vitepress" / "config.ts"

    if not check_sidebar_contains_link(config_path, link):
        # File not in sidebar - warn
        print(json.dumps({
            "result": "continue",
            "message": f"**Sidebar Warning:** New document `{link}` is not linked in the VitePress sidebar. Consider adding it to `docs/.vitepress/config.ts`."
        }))

    sys.exit(0)


if __name__ == "__main__":
    main()
