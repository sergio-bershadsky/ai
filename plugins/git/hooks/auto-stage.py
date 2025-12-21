#!/usr/bin/env python3
"""
PostToolUse hook: Auto-stage files after Write/Edit/Bash operations.

Triggers after: Write, Edit, Bash tools
Action: Run git add on the modified file(s)
"""

import json
import os
import subprocess
import sys
from pathlib import Path

DEBUG = os.environ.get("CLAUDE_HOOK_DEBUG", "").lower() in ("1", "true")

# Bash commands that modify files
FILE_MODIFYING_COMMANDS = [
    "chmod", "chown", "touch", "mv", "cp", "ln",
    "sed", "awk", "truncate", "install"
]

def debug_log(msg):
    """Write debug info to a log file."""
    if not DEBUG:
        return
    log_file = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")) / ".claude" / "hook-debug.log"
    with open(log_file, "a") as f:
        f.write(f"[auto-stage] {msg}\n")


def extract_paths_from_bash(command, project_dir):
    """Extract file paths from a bash command that might modify files."""
    paths = []

    # Check if command starts with a file-modifying command
    cmd_parts = command.strip().split()
    if not cmd_parts:
        return paths

    base_cmd = cmd_parts[0].split("/")[-1]  # Handle full paths like /bin/chmod

    if base_cmd not in FILE_MODIFYING_COMMANDS:
        return paths

    # Extract potential file paths from command
    # Look for absolute paths or paths relative to project
    for part in cmd_parts[1:]:
        # Skip flags
        if part.startswith("-"):
            continue
        # Skip permission modes for chmod (like 755, +x)
        if base_cmd == "chmod" and (part.isdigit() or part.startswith("+") or part.startswith("u") or part.startswith("g") or part.startswith("o") or part.startswith("a")):
            continue

        # Check if it looks like a file path
        if "/" in part or part.endswith(".py") or part.endswith(".sh") or part.endswith(".md") or part.endswith(".json") or part.endswith(".ts") or part.endswith(".js"):
            # Resolve path
            if os.path.isabs(part):
                if project_dir and part.startswith(project_dir):
                    paths.append(part)
            else:
                # Relative path - make absolute
                full_path = os.path.join(project_dir, part) if project_dir else part
                if os.path.exists(full_path):
                    paths.append(full_path)

    return paths


def stage_file(file_path, project_dir):
    """Stage a single file and return success status."""
    try:
        result = subprocess.run(
            ["git", "add", file_path],
            cwd=project_dir or os.path.dirname(file_path),
            capture_output=True,
            text=True,
            timeout=5
        )
        debug_log(f"git add {file_path}: returncode={result.returncode}, stderr={result.stderr}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        debug_log(f"git add {file_path} timed out")
        return False
    except Exception as e:
        debug_log(f"git add {file_path} exception: {e}")
        return False


def main():
    try:
        input_data = json.load(sys.stdin)
        debug_log(f"Input: {json.dumps(input_data)}")
    except json.JSONDecodeError as e:
        debug_log(f"JSON decode error: {e}")
        return

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")

    files_to_stage = []

    if tool_name in ("Write", "Edit"):
        # Get the file path from tool input
        file_path = tool_input.get("file_path", "")
        if file_path:
            files_to_stage.append(file_path)

    elif tool_name == "Bash":
        # Extract paths from bash command
        command = tool_input.get("command", "")
        debug_log(f"Bash command: {command}")
        paths = extract_paths_from_bash(command, project_dir)
        files_to_stage.extend(paths)

    else:
        debug_log(f"Skipping tool: {tool_name}")
        return

    if not files_to_stage:
        debug_log("No files to stage")
        return

    staged_files = []
    for file_path in files_to_stage:
        debug_log(f"Processing file: {file_path}")

        # Skip files outside the project
        if project_dir and not file_path.startswith(project_dir):
            debug_log(f"File outside project: {file_path} not in {project_dir}")
            continue

        # Stage the file
        if stage_file(file_path, project_dir):
            rel_path = os.path.relpath(file_path, project_dir) if project_dir else file_path
            staged_files.append(rel_path)

    if staged_files:
        if len(staged_files) == 1:
            output = {"message": f"Staged: {staged_files[0]}"}
        else:
            output = {"message": f"Staged: {', '.join(staged_files)}"}
        print(json.dumps(output))
        debug_log(f"Output: {json.dumps(output)}")

if __name__ == "__main__":
    main()
