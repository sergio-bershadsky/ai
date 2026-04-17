#!/usr/bin/env python3
"""PreToolUse hook: block direct AI edits under docs/ in sbdb-managed repos.

When a repo contains .sbdb.toml at its root, all mutations to docs/ must go
through the `sbdb` CLI. This hook rejects Write/Edit/MultiEdit/NotebookEdit
targeting docs/, and scans Bash commands for file-mutation patterns targeting
docs/ paths. If sbdb is not installed, the block message includes install
instructions.
"""

import json
import os
import re
import sys


BASH_MUTATION_RE = re.compile(
    r"""
    (?:^|[\s;&|`(])                                   # start or shell separator
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
        if not is_under_docs(target, project_root):
            continue
        emit_block(project_root)
        return


def collect_targets(tool_name, tool_input):
    """Return a list of absolute paths that the tool call would mutate."""
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
    """Heuristically extract paths a bash command would mutate.

    Errs on the side of caution: if the command looks like a mutation and
    mentions a docs/ path anywhere in its tokens, block it.
    """
    targets = []
    cwd = os.getcwd()

    is_mutation = bool(BASH_MUTATION_RE.search(cmd))

    # Shell redirects always write to their target, regardless of leading cmd.
    for m in REDIRECT_RE.finditer(cmd):
        targets.append(_resolve(m.group(1), cwd))

    if is_mutation:
        # Scan all tokens that look like paths containing "docs".
        for m in TOKEN_RE.finditer(cmd):
            tok = m.group(1)
            if "docs" in tok and ("/" in tok or tok == "docs"):
                targets.append(_resolve(tok, cwd))

    return targets


def _resolve(path, cwd):
    if os.path.isabs(path):
        return os.path.normpath(path)
    return os.path.normpath(os.path.join(cwd, path))


def is_under_docs(abs_path, project_root):
    try:
        rel = os.path.relpath(abs_path, project_root)
    except ValueError:
        return False
    if rel.startswith(".."):
        return False
    parts = rel.split(os.sep)
    return len(parts) > 0 and parts[0] == "docs"


def find_project_root(file_path):
    """Walk up from the file path looking for .sbdb.toml."""
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
    """Find the sbdb binary in PATH or common locations."""
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


def emit_block(project_root):
    sbdb = find_sbdb()

    if sbdb:
        reason = (
            f"Direct edits to docs/ are not allowed in sbdb-managed repos "
            f"(.sbdb.toml at {project_root}). "
            f"Use the sbdb CLI instead — e.g. `sbdb doc create`, "
            f"`sbdb doc edit <id>`, `sbdb doc delete <id>`. "
            f"Run `sbdb --help` for the full command list."
        )
    else:
        reason = (
            f"Direct edits to docs/ are not allowed in sbdb-managed repos "
            f"(.sbdb.toml at {project_root}), and the `sbdb` CLI was not "
            f"found in PATH or ~/go/bin.\n\n"
            f"Install with:\n"
            f"  go install github.com/bershadsky/sbdb@latest\n"
            f"Then ensure $(go env GOPATH)/bin is on your PATH.\n"
            f"After installing, retry your change via `sbdb` subcommands "
            f"(`sbdb doc create`, `sbdb doc edit <id>`, `sbdb --help`)."
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
