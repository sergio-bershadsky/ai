#!/usr/bin/env python3
"""PostToolUse hook: runs sbdb doctor check after Write/Edit on .md or .yaml files.

Only triggers when the edited file is inside a docs/ directory and a
.sbdb.toml exists in the project root (indicating an sbdb-managed project).

Updated for sbdb v2 layout:
- v2 has no data/ directory; per-doc <id>.yaml sidecars sit next to <id>.md
  under docs_dir.
- doctor check returns exit 0 (clean) or non-zero with `{"action":
  "doctor.check", "scope": ..., "drifts": [{"file": ..., "drift": ...,
  "causes": [...]}, ...]}`. Older keys drift_count / tamper_count are gone.
- doctor check defaults to working-tree-only scope; that's exactly what we
  want here (only audit what just changed), so we omit --all.
"""

import json
import os
import subprocess
import sys


def main():
    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        return

    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})

    if tool_name not in ("Write", "Edit"):
        return

    file_path = tool_input.get("file_path", "")
    if not file_path:
        return

    # Only check .md and .yaml files inside docs/
    if not file_path.endswith((".md", ".yaml", ".yml")):
        return
    if "/docs/" not in file_path:
        return

    project_root = find_project_root(file_path)
    if not project_root:
        return

    sbdb_path = find_sbdb()
    if not sbdb_path:
        return

    # Default scope (uncommitted-only) is precisely what we want: only
    # audit changes that haven't been committed yet.
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
        return  # clean

    drifts = parse_drifts(result.stdout)
    if not drifts:
        return

    msg = build_message(drifts, file_path)
    if msg:
        print(json.dumps({"message": msg}))


def parse_drifts(stdout):
    """Return the list of drift entries from a doctor.check JSON payload.

    Tolerates both wire shapes:
      {"action":"doctor.check","scope":"uncommitted","drifts":[...]}
      {"data":{"drifts":[...]}}
    """
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return []
    if isinstance(data, dict):
        if isinstance(data.get("drifts"), list):
            return data["drifts"]
        inner = data.get("data")
        if isinstance(inner, dict) and isinstance(inner.get("drifts"), list):
            return inner["drifts"]
    return []


def build_message(drifts, edited_file):
    pure_drift = []
    tamper = []
    bad_sig = []
    missing = []

    for d in drifts:
        causes = d.get("causes", [])
        kind = d.get("drift", "")
        if kind in ("missing-md", "missing-sidecar"):
            missing.append(d.get("file", ""))
        elif "bad_sig" in causes:
            bad_sig.append(d.get("file", ""))
        elif "content_sha mismatch" in causes:
            tamper.append(d.get("file", ""))
        elif causes:
            pure_drift.append(d.get("file", ""))

    parts = [f"[sbdb] integrity check found drift after editing {os.path.basename(edited_file)}:"]

    if pure_drift:
        parts.append(
            f"\n  • {len(pure_drift)} pure drift (frontmatter/record vs. sidecar) — "
            "auto-fixable: `sbdb doctor fix --recompute`"
        )
    if tamper:
        parts.append(
            f"\n  • {len(tamper)} content tamper — review the markdown body, then either "
            "`sbdb doctor sign --force` (accept the edit) or revert via git"
        )
    if bad_sig:
        parts.append(
            f"\n  • {len(bad_sig)} HMAC signature mismatch — file edited outside the ORM "
            "with an active integrity key; re-sign or revert"
        )
    if missing:
        parts.append(
            f"\n  • {len(missing)} missing pair (md or sidecar) — run "
            "`sbdb doctor fix --recompute` to rebuild the sidecar"
        )

    return "".join(parts) if len(parts) > 1 else ""


def find_project_root(file_path):
    directory = os.path.dirname(os.path.abspath(file_path))
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
