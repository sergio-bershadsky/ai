# Marketplace Validator Plugin

Validates marketplace.json schema after every edit in this repository.

## Installation

```bash
claude mcp add-from-marketplace bershadsky-claude-tools/marketplace-validator
```

## Overview

This plugin automatically validates the `.claude-plugin/marketplace.json` file after any Write or Edit operation, ensuring the marketplace registry maintains a consistent schema.

## How It Works

```
Write/Edit Tool → PostToolUse Hook → Validate Schema
                                           ↓
                               Pass: Continue silently
                               Fail: Block with error details
```

## Hooks

### Validate Marketplace (PostToolUse)

- **Trigger:** After Write|Edit tool use
- **Action:** Validates marketplace.json against required schema
- **Behavior:** Blocks operation if validation fails

**Exit Codes:**
- `0` — Validation passed or file doesn't exist
- `2` — Validation failed, operation blocked

## Validation Rules

### Required Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Marketplace name |
| `owner` | object | Owner information |
| `owner.name` | string | Owner name (required) |
| `owner.email` | string | Owner email (optional) |
| `plugins` | array | List of plugins |

### Required Plugin Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Plugin name |
| `source` | string | Path to plugin directory |
| `description` | string | Plugin description |
| `version` | string | Plugin version |

### Invalid/Deprecated Fields

| Field | Error |
|-------|-------|
| `path` | Use `source` instead |
| `keywords` | Not allowed in marketplace plugins |

## Example marketplace.json

```json
{
  "name": "my-marketplace",
  "owner": {
    "name": "John Doe",
    "email": "john@example.com"
  },
  "plugins": [
    {
      "name": "my-plugin",
      "source": "plugins/my-plugin",
      "description": "A useful plugin",
      "version": "1.0.0"
    }
  ]
}
```

## Error Messages

### Missing Field
```
marketplace.json validation failed:
  - plugins[0]: missing required field 'source' (did you use 'path' instead?)
```

### Invalid JSON
```
marketplace.json is not valid JSON: Expecting ',' delimiter: line 5 column 3
```

### Type Errors
```
marketplace.json validation failed:
  - Field 'name' must be a string
  - owner.name must be a string
```

## Use Cases

- **Plugin Development** — Validate changes while developing new plugins
- **CI Integration** — Ensure marketplace consistency before commits
- **Multi-developer Repos** — Catch schema errors early

## License

[Unlicense](LICENSE) - Public Domain
