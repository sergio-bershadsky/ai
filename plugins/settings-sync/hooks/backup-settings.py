#!/usr/bin/env python3
"""
Stop hook: Backup Claude settings to repo before session ends.

Triggers: When Claude attempts to stop
Action: Copy ~/.claude settings to .claude-backup/ in the repo
"""

import json
import os
import shutil
import sys
from pathlib import Path

# Files/dirs to backup (relative to ~/.claude)
BACKUP_ITEMS = [
    "settings.json",
    "plugins",
    "projects",
    "ide",
    "commands",
]

# Files to exclude from backup (contain sensitive data)
EXCLUDE_PATTERNS = [
    "*.log",
    "*.jsonl",
    "credentials*",
    "auth*",
    "token*",
    "secret*",
]


def get_backup_dir():
    """Get the .claude-backup directory in the repo."""
    # CLAUDE_PROJECT_DIR points to the repo root
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if not project_dir:
        return None
    return Path(project_dir) / ".claude-backup"


def get_claude_dir():
    """Get the ~/.claude directory."""
    return Path.home() / ".claude"


def should_exclude(path: Path) -> bool:
    """Check if a file should be excluded from backup."""
    name = path.name.lower()
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith("*"):
            if name.endswith(pattern[1:]):
                return True
        elif pattern.endswith("*"):
            if name.startswith(pattern[:-1]):
                return True
        elif name == pattern:
            return True
    return False


def backup_item(source: Path, dest: Path):
    """Backup a single file or directory."""
    if not source.exists():
        return False

    if source.is_file():
        if should_exclude(source):
            return False
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        return True

    elif source.is_dir():
        # Remove existing backup dir
        if dest.exists():
            shutil.rmtree(dest)

        # Copy directory, excluding sensitive files
        def ignore_func(directory, files):
            ignored = []
            for f in files:
                if should_exclude(Path(directory) / f):
                    ignored.append(f)
            return ignored

        shutil.copytree(source, dest, ignore=ignore_func)
        return True

    return False


def main():
    """Main hook entry point."""
    try:
        # Read input (required for hook protocol)
        json.load(sys.stdin)
    except json.JSONDecodeError:
        pass

    backup_dir = get_backup_dir()
    claude_dir = get_claude_dir()

    if not backup_dir:
        # Not in a project context, skip backup
        sys.exit(0)

    if not claude_dir.exists():
        # No Claude settings to backup
        sys.exit(0)

    # Create backup directory
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Backup each item
    backed_up = []
    for item in BACKUP_ITEMS:
        source = claude_dir / item
        dest = backup_dir / item
        if backup_item(source, dest):
            backed_up.append(item)

    if backed_up:
        # Create a .gitignore in backup dir to exclude sensitive patterns
        gitignore_path = backup_dir / ".gitignore"
        gitignore_content = """# Exclude sensitive files
*.log
*.jsonl
credentials*
auth*
token*
secret*
"""
        gitignore_path.write_text(gitignore_content)

        output = {"message": f"Backed up settings: {', '.join(backed_up)}"}
        print(json.dumps(output))

    # Always allow stopping (don't block)
    sys.exit(0)


if __name__ == "__main__":
    main()
