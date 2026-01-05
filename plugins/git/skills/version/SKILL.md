---
name: version
description: |
  This skill should be used when the user wants to bump versions, create releases, or tag versions. Triggers include: "bump version", "bump the version", "version bump", "release version", "tag a release", "create release", "major/minor/patch bump", "update version", "new version", "/version". Updates plugin.json and marketplace.json. Creates git tag and commit.
---

# Version Skill

Bump semantic versions for plugins with git tag and commit.

## When to Use

- After completing a feature (minor bump)
- After fixing bugs (patch bump)
- After breaking changes (major bump)
- Before releasing a new version

## Arguments

```
/version [bump-type] [plugin-name]
```

**bump-type:** `major`, `minor`, or `patch` (default: patch)
**plugin-name:** Plugin to version (default: auto-detect from cwd or prompt)

**Examples:**
```
/version patch git
/version minor settings-sync
/version major
```

## Procedure

### Step 1: Identify Plugin

If plugin name not provided:
1. Check if cwd is inside a plugin directory
2. If not, list available plugins and ask user

```bash
ls plugins/
```

### Step 2: Read Current Version

```bash
cat plugins/<name>/.claude-plugin/plugin.json | grep version
```

Parse the current version (e.g., `1.2.3`).

### Step 3: Calculate New Version

Based on bump type:
- **major**: `1.2.3` → `2.0.0`
- **minor**: `1.2.3` → `1.3.0`
- **patch**: `1.2.3` → `1.2.4`

### Step 4: Show Changes and Confirm

Present to user:
```
## Version Bump

**Plugin:** git
**Current:** 1.2.3
**New:** 1.3.0
**Type:** minor

**Files to update:**
- plugins/git/.claude-plugin/plugin.json
- .claude-plugin/marketplace.json

**Git actions:**
- Commit: "chore(git): bump version to 1.3.0"
- Tag: v1.3.0-git

---
Proceed with version bump?
```

Wait for user confirmation.

### Step 5: Update Files

After approval, update version in:

1. **Plugin manifest:**
   ```
   plugins/<name>/.claude-plugin/plugin.json
   ```
   Update the `"version"` field.

2. **Marketplace catalog:**
   ```
   .claude-plugin/marketplace.json
   ```
   Update the version for this plugin in the `plugins` array.

### Step 6: Create Git Commit and Tag

```bash
git add plugins/<name>/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "chore(<name>): bump version to <new-version>"
git tag -a "v<new-version>-<name>" -m "Release <name> v<new-version>"
```

### Step 7: Verify

```bash
git log -1 --oneline
git tag -l "v*-<name>" | tail -1
```

## Rules

1. **NEVER push** — Only commit and tag locally, never push
2. **ALWAYS confirm** — Never bump without user approval
3. **Semantic versioning** — Follow MAJOR.MINOR.PATCH strictly
4. **Update both files** — plugin.json AND marketplace.json
5. **Tag format** — Use `v<version>-<plugin-name>` for multi-plugin repos

## Output Format

```
## Version Bump Complete

**Plugin:** git
**Version:** 1.2.3 → 1.3.0

**Commit:** abc1234 chore(git): bump version to 1.3.0
**Tag:** v1.3.0-git

Run `git push --follow-tags` to publish.
```
