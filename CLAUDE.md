# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Plugin marketplace for Claude Code skills and hooks.

## Commands

```bash
npm run docs:dev      # Dev server at localhost:5173
npm run docs:build    # Production build
npm run docs:preview  # Preview build
```

## Architecture

- `.claude-plugin/marketplace.json` - Plugin registry
- `plugins/<name>/.claude-plugin/plugin.json` - Plugin manifest
- `plugins/<name>/skills/<skill>/SKILL.md` - Skill definitions
- `plugins/<name>/hooks/hooks.json` - Hook configurations
- `templates/SKILL-TEMPLATE.md` - Skill authoring template

## Creating Plugins

1. Create `plugins/<name>/.claude-plugin/plugin.json`
2. Add skills in `skills/<skill>/SKILL.md` (see `templates/SKILL-TEMPLATE.md`)
3. Add hooks in `hooks/hooks.json` with Python scripts
4. Register in `.claude-plugin/marketplace.json`

Use `${CLAUDE_PLUGIN_ROOT}` for paths in hooks.json.

## Hook Events

- `Stop` - Before session ends (exit 2 to block)
- `PostToolUse` - After tool execution (matcher: regex for tool names)

Debug: `CLAUDE_HOOK_DEBUG=1` → `.claude/hook-debug.log`
