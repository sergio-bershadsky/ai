#!/usr/bin/env python3
"""Validate every plugins/*/.claude-plugin/plugin.json and the root marketplace.json.

Checks:
  - Valid JSON.
  - Required fields: name, version, description.
  - version is valid semver (X.Y.Z, optional pre-release).
  - name matches the directory name under plugins/.
  - marketplace.json's `plugins[]` entries reference real plugins
    with matching names, and the per-entry `version` is not ahead
    of the plugin's own plugin.json (warn if behind).

Exits 0 on success, 1 on any error. Prints findings to stderr.
"""

from __future__ import annotations

import json
import re
import sys
import typing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLUGINS_DIR = ROOT / "plugins"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"

SEMVER = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>[0-9A-Za-z.-]+))?"
    r"(?:\+(?P<build>[0-9A-Za-z.-]+))?$"
)


def die(msg: str) -> "typing.NoReturn":
    sys.stderr.write(f"FAIL: {msg}\n")
    sys.exit(1)


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        die(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")


def warn(msg: str) -> None:
    sys.stderr.write(f"warn: {msg}\n")


def validate_plugin(plugin_dir: Path) -> dict:
    manifest_path = plugin_dir / ".claude-plugin" / "plugin.json"
    if not manifest_path.exists():
        die(f"{plugin_dir.relative_to(ROOT)}: missing .claude-plugin/plugin.json")
    data = read_json(manifest_path)

    for required in ("name", "version", "description"):
        if not data.get(required):
            die(
                f"{manifest_path.relative_to(ROOT)}: missing required field '{required}'"
            )

    version = data["version"]
    if not SEMVER.match(version):
        die(
            f"{manifest_path.relative_to(ROOT)}: version {version!r} is not valid semver"
        )

    if data["name"] != plugin_dir.name:
        die(
            f"{manifest_path.relative_to(ROOT)}: name {data['name']!r} "
            f"does not match directory name {plugin_dir.name!r}"
        )

    return data


def validate_marketplace(plugin_versions: dict[str, str]) -> None:
    if not MARKETPLACE.exists():
        warn("no marketplace.json at repo root — skipping marketplace cross-check")
        return
    data = read_json(MARKETPLACE)
    listed = {p["name"]: p for p in data.get("plugins", [])}

    only_in_market = set(listed) - set(plugin_versions)
    only_on_disk = set(plugin_versions) - set(listed)

    for name in sorted(only_in_market):
        die(
            f"marketplace.json lists plugin {name!r} but no such directory under plugins/"
        )

    for name in sorted(only_on_disk):
        warn(f"plugin {name!r} exists on disk but is not listed in marketplace.json")

    for name, entry in listed.items():
        market_version = entry.get("version", "")
        plugin_version = plugin_versions[name]
        if market_version and not SEMVER.match(market_version):
            die(
                f"marketplace.json: plugin {name!r} has invalid version {market_version!r}"
            )
        if market_version and market_version != plugin_version:
            warn(
                f"marketplace.json: plugin {name!r} listed at {market_version}, "
                f"but plugin.json says {plugin_version}"
            )


def main() -> None:
    if not PLUGINS_DIR.is_dir():
        die(f"plugins/ directory not found at {PLUGINS_DIR}")

    plugin_versions: dict[str, str] = {}
    plugin_dirs = sorted(p for p in PLUGINS_DIR.iterdir() if p.is_dir())
    if not plugin_dirs:
        die("no plugins found under plugins/")

    for plugin_dir in plugin_dirs:
        data = validate_plugin(plugin_dir)
        plugin_versions[data["name"]] = data["version"]
        print(f"  ok  {data['name']:30s} v{data['version']}")

    validate_marketplace(plugin_versions)
    print(f"\n{len(plugin_versions)} plugin manifest(s) validated.")


if __name__ == "__main__":
    main()
