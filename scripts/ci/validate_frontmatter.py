#!/usr/bin/env python3
"""Validate YAML frontmatter on every skill / agent / command markdown file.

For each .md file under plugins/<plugin>/{skills,agents,commands}/:
  - If the file starts with ---, parse the frontmatter block as YAML.
  - The block must close with a second --- and parse to a YAML mapping.
  - Warn (non-fatal) if neither 'name' nor 'description' is present.

Files without a leading --- are skipped (frontmatter is optional for some
file types like README.md inside a skill folder).

Exits 0 on success, 1 if any file's frontmatter fails to parse.
"""

from __future__ import annotations

import sys
import typing
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
PLUGINS_DIR = ROOT / "plugins"
SUBDIRS = ("skills", "agents", "commands")


def die(msg: str) -> "typing.NoReturn":
    sys.stderr.write(f"FAIL: {msg}\n")
    sys.exit(1)


def warn(msg: str) -> None:
    sys.stderr.write(f"warn: {msg}\n")


def collect_targets() -> list[Path]:
    out: list[Path] = []
    for sub in SUBDIRS:
        out.extend(PLUGINS_DIR.glob(f"*/{sub}/**/*.md"))
    return sorted(out)


def validate(path: Path) -> bool:
    text = path.read_text()
    if not text.startswith("---"):
        return True

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return True

    try:
        end = lines.index("---", 1)
    except ValueError:
        sys.stderr.write(
            f"FAIL: {path.relative_to(ROOT)}: starts with --- but has no closing ---\n"
        )
        return False

    block = "\n".join(lines[1:end])
    try:
        data = yaml.safe_load(block)
    except yaml.YAMLError as exc:
        sys.stderr.write(
            f"FAIL: {path.relative_to(ROOT)}: invalid YAML frontmatter: {exc}\n"
        )
        return False

    if not isinstance(data, dict):
        sys.stderr.write(
            f"FAIL: {path.relative_to(ROOT)}: frontmatter must be a YAML mapping\n"
        )
        return False

    if "name" not in data and "description" not in data:
        warn(
            f"{path.relative_to(ROOT)}: frontmatter has neither 'name' nor 'description'"
        )

    return True


def main() -> None:
    if not PLUGINS_DIR.is_dir():
        die(f"plugins/ directory not found at {PLUGINS_DIR}")

    targets = collect_targets()
    if not targets:
        print("No skill/agent/command markdown files found — nothing to validate.")
        return

    fail = 0
    checked = 0
    for path in targets:
        checked += 1
        if not validate(path):
            fail += 1

    if fail:
        die(f"{fail} of {checked} markdown file(s) have frontmatter problems")
    print(f"\n{checked} markdown file(s) validated.")


if __name__ == "__main__":
    main()
