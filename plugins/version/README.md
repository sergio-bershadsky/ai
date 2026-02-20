# Version Plugin

Semantic version bumping for plugins with git tags and commits.

## Installation

```bash
claude mcp add-from-marketplace bershadsky-claude-tools/version
```

## Features

- **Semantic Versioning** - Follows MAJOR.MINOR.PATCH strictly
- **Git Integration** - Creates annotated git tags and commits
- **Multi-plugin Support** - Tag format `v<version>-<plugin>` for multi-plugin repos
- **Marketplace Sync** - Updates both plugin.json and marketplace.json

## Skills

### /version

Bump semantic versions for plugins.

```
/version [bump-type] [plugin-name]
```

**Arguments:**
- `bump-type`: `major`, `minor`, `patch` (default: patch)
- `plugin-name`: Auto-detects or prompts

**Examples:**
```
/version              # Patch bump, auto-detect plugin
/version minor        # Minor bump
/version major git    # Major bump for git plugin
```

**Actions:**
- Updates `plugin.json` version
- Updates `marketplace.json` version
- Creates annotated git tag (`v1.2.3-plugin-name`)

## License

[Unlicense](LICENSE) - Public Domain
