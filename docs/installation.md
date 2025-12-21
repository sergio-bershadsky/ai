# Installation

## Add Marketplace

```bash
/plugin marketplace add bershadsky/ai
```

## Install Plugins

```bash
# Install git workflow plugin
/plugin install git@bershadsky-claude-tools
```

## What Gets Installed

### git plugin

**Skills:**
- `commit` — Create conventional commits with user confirmation

**Hooks:**
- `auto-stage` — Auto-stage files after Write/Edit/Bash
- `pre-stop-commit` — Block exit if uncommitted changes

## Managing Plugins

```bash
# List installed plugins
/plugin list

# Update plugins
/plugin update

# Remove plugin
/plugin remove git@bershadsky-claude-tools
```

## Manual Installation (Alternative)

If you prefer manual setup:

```bash
git clone https://github.com/bershadsky/ai.git ~/claude-shared
```

Then symlink skills and reference hooks manually.
