#!/usr/bin/env python3
"""Stop hook: blocks Claude from finishing if KB integrity is broken.

Deterministic guardrail — even if Claude ignores the PostToolUse warnings,
this hook fires before the response is delivered and tells Claude to fix
the issue before stopping.

Updated for sbdb v2 layout:
- doctor check returns exit 0 / non-zero with a `drifts` array (no more
  drift_count / tamper_count keys).
- Stop-time scope is `--all` because we want a complete final state, not
  just uncommitted changes — the agent may have committed mid-conversation.
"""

import json
import os
import subprocess


def main():
    cwd = os.getcwd()
    project_root = find_project_root(cwd)
    if not project_root:
        return  # not an sbdb project

    sbdb = find_sbdb()
    if not sbdb:
        return  # sbdb not installed

    # Final check uses --all (audit everything, not just working-tree diff)
    try:
        result = subprocess.run(
            [sbdb, "doctor", "check", "--all", "--format", "json", "-b", project_root],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return

    if result.returncode == 0:
        return  # clean — allow stop

    drifts = parse_drifts(result.stdout)
    if not drifts:
        return  # exit was non-zero but unparseable; bail

    untracked_count = check_untracked(sbdb, project_root)

    parts = ["[sbdb] INTEGRITY CHECK FAILED — do not stop yet."]

    counts = classify(drifts)
    if counts["pure_drift"]:
        parts.append(
            f"\n• {counts['pure_drift']} pure drift: run `sbdb doctor fix --recompute --all`"
        )
    if counts["tamper"]:
        parts.append(
            f"\n• {counts['tamper']} content tamper: run `sbdb doctor sign --force --all` for "
            "files you intentionally edited, or revert via git"
        )
    if counts["bad_sig"]:
        parts.append(
            f"\n• {counts['bad_sig']} HMAC signature mismatch: re-sign with "
            "`sbdb doctor sign --force --all` or revert"
        )
    if counts["missing"]:
        parts.append(
            f"\n• {counts['missing']} missing md-or-sidecar pair: "
            "run `sbdb doctor fix --recompute --all` to rebuild missing sidecars"
        )

    if untracked_count:
        parts.append(
            f"\n• {untracked_count} untracked file(s) need signing: "
            "run `sbdb untracked sign-all docs/`"
        )

    parts.append(
        "\n\nFix these issues, re-run `sbdb doctor check --all`, and verify exit code 0 "
        "before finishing."
    )

    print(json.dumps({"message": "".join(parts), "decision": "block"}))


def parse_drifts(stdout):
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


def classify(drifts):
    out = {"pure_drift": 0, "tamper": 0, "bad_sig": 0, "missing": 0}
    for d in drifts:
        causes = d.get("causes", [])
        kind = d.get("drift", "")
        if kind in ("missing-md", "missing-sidecar"):
            out["missing"] += 1
        elif "bad_sig" in causes:
            out["bad_sig"] += 1
        elif "content_sha mismatch" in causes:
            out["tamper"] += 1
        elif causes:
            out["pure_drift"] += 1
    return out


def check_untracked(sbdb, project_root):
    try:
        result = subprocess.run(
            [sbdb, "untracked", "sign-all", "docs/", "--dry-run", "--format", "json", "-b", project_root],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if isinstance(data, dict):
                inner = data.get("data") if isinstance(data.get("data"), dict) else data
                return inner.get("discovered", 0) if isinstance(inner, dict) else 0
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
