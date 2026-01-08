#!/usr/bin/env python3
"""
PostToolUse hook: Validate marketplace.json schema after edits.

Triggers: After Write|Edit tool use
Action: Validate marketplace.json schema and report errors
"""

import json
import os
import sys
from typing import Any


def get_project_dir() -> str:
    """Get project directory from environment or current dir."""
    return os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())


def validate_marketplace(data: dict[str, Any]) -> list[str]:
    """Validate marketplace.json against required schema."""
    errors = []

    # Required top-level fields
    if "name" not in data:
        errors.append("Missing required field: name")
    elif not isinstance(data["name"], str):
        errors.append("Field 'name' must be a string")

    if "owner" not in data:
        errors.append("Missing required field: owner")
    elif isinstance(data["owner"], dict):
        if "name" not in data["owner"]:
            errors.append("owner.name is required")
        elif not isinstance(data["owner"]["name"], str):
            errors.append("owner.name must be a string")
        if "email" in data["owner"] and not isinstance(data["owner"]["email"], str):
            errors.append("owner.email must be a string")
    else:
        errors.append("Field 'owner' must be an object")

    if "plugins" not in data:
        errors.append("Missing required field: plugins")
    elif not isinstance(data["plugins"], list):
        errors.append("Field 'plugins' must be an array")
    else:
        for i, plugin in enumerate(data["plugins"]):
            prefix = f"plugins[{i}]"
            if not isinstance(plugin, dict):
                errors.append(f"{prefix}: must be an object")
                continue

            # Required plugin fields
            if "name" not in plugin:
                errors.append(f"{prefix}: missing required field 'name'")
            elif not isinstance(plugin["name"], str):
                errors.append(f"{prefix}.name: must be a string")

            if "source" not in plugin:
                errors.append(f"{prefix}: missing required field 'source' (did you use 'path' instead?)")
            elif not isinstance(plugin["source"], str):
                errors.append(f"{prefix}.source: must be a string")

            if "description" not in plugin:
                errors.append(f"{prefix}: missing required field 'description'")

            if "version" not in plugin:
                errors.append(f"{prefix}: missing required field 'version'")

            # Warn about deprecated/invalid fields
            if "path" in plugin:
                errors.append(f"{prefix}: 'path' is invalid, use 'source' instead")

            if "keywords" in plugin:
                errors.append(f"{prefix}: 'keywords' is not allowed in marketplace plugins")

    return errors


def main():
    """Main hook entry point."""
    project_dir = get_project_dir()
    marketplace_path = os.path.join(project_dir, ".claude-plugin", "marketplace.json")

    # Check if marketplace.json exists
    if not os.path.exists(marketplace_path):
        # Not a marketplace repo, skip validation
        sys.exit(0)

    try:
        with open(marketplace_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        output = {
            "decision": "block",
            "reason": f"marketplace.json is not valid JSON: {e}"
        }
        print(json.dumps(output))
        sys.exit(2)
    except Exception:
        # Can't read file, skip
        sys.exit(0)

    errors = validate_marketplace(data)

    if errors:
        error_list = "\n".join(f"  - {e}" for e in errors)
        output = {
            "decision": "block",
            "reason": f"marketplace.json validation failed:\n{error_list}\n\nPlease fix these issues before continuing."
        }
        print(json.dumps(output))
        sys.exit(2)

    # Validation passed
    sys.exit(0)


if __name__ == "__main__":
    main()
