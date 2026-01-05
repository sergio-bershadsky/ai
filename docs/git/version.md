# version

Bump semantic version for a plugin.

## Usage

```bash
/version [major|minor|patch] [plugin-name]
```

## Examples

```bash
# Patch bump for git plugin (1.0.0 → 1.0.1)
/version patch git

# Minor bump for settings-sync (1.0.0 → 1.1.0)
/version minor settings-sync

# Major bump, auto-detect plugin
/version major
```

## What It Does

1. Reads current version from `plugin.json`
2. Calculates new version based on bump type
3. Updates `plugin.json` and `marketplace.json`
4. Creates git commit and annotated tag
5. Shows summary (does NOT push)

## Semantic Versioning

| Bump | When to Use | Example |
|------|-------------|---------|
| **major** | Breaking changes | 1.2.3 → 2.0.0 |
| **minor** | New features (backward compatible) | 1.2.3 → 1.3.0 |
| **patch** | Bug fixes | 1.2.3 → 1.2.4 |

## Tag Format

Tags use format `v<version>-<plugin>` for multi-plugin repos:

```
v1.0.1-git
v1.1.0-settings-sync
```

## After Bumping

Push with tags:

```bash
git push --follow-tags
```
