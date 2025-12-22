#!/bin/bash
# Bootstrap Claude settings from backup
# Usage: curl -fsSL https://raw.githubusercontent.com/sergio-bershadsky/ai/main/plugins/settings-sync/scripts/bootstrap.sh | bash

set -e

REPO_URL="https://github.com/sergio-bershadsky/ai.git"
BACKUP_DIR=".claude-backup"
CLAUDE_DIR="$HOME/.claude"
TEMP_DIR=$(mktemp -d)

cleanup() {
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

echo "==> Bootstrapping Claude settings..."

# Clone repo (shallow, just backup dir)
git clone --depth 1 --filter=blob:none --sparse "$REPO_URL" "$TEMP_DIR" 2>/dev/null
cd "$TEMP_DIR"
git sparse-checkout set "$BACKUP_DIR" 2>/dev/null

# Check if backup exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo "No backup found in repo. Skipping restore."
    exit 0
fi

# Create ~/.claude if needed
mkdir -p "$CLAUDE_DIR"

# Restore settings
echo "==> Restoring settings..."

# settings.json
if [ -f "$BACKUP_DIR/settings.json" ]; then
    cp "$BACKUP_DIR/settings.json" "$CLAUDE_DIR/"
    echo "    Restored: settings.json"
fi

# plugins/
if [ -d "$BACKUP_DIR/plugins" ]; then
    cp -r "$BACKUP_DIR/plugins" "$CLAUDE_DIR/"
    echo "    Restored: plugins/"
fi

# projects/
if [ -d "$BACKUP_DIR/projects" ]; then
    cp -r "$BACKUP_DIR/projects" "$CLAUDE_DIR/"
    echo "    Restored: projects/"
fi

# ide/
if [ -d "$BACKUP_DIR/ide" ]; then
    cp -r "$BACKUP_DIR/ide" "$CLAUDE_DIR/"
    echo "    Restored: ide/"
fi

# commands/ (custom slash commands)
if [ -d "$BACKUP_DIR/commands" ]; then
    cp -r "$BACKUP_DIR/commands" "$CLAUDE_DIR/"
    echo "    Restored: commands/"
fi

echo "==> Done! Claude settings restored to $CLAUDE_DIR"
