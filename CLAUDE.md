# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Plugin marketplace for Claude Code skills and hooks. Marketplace ID: `bershadsky-claude-tools`

## Commands

```bash
npm install           # Install dependencies (run first)
npm run docs:dev      # Dev server at localhost:5173
npm run docs:build    # Production build
npm run docs:preview  # Preview build
```

## Architecture

**Marketplace Registry:**
- `.claude-plugin/marketplace.json` — Lists all available plugins with metadata

**Plugin Structure:** `plugins/<name>/`
- `.claude-plugin/plugin.json` — Plugin manifest (name, version, description)
- `skills/<skill>/SKILL.md` — Skill definitions with YAML frontmatter
- `hooks/hooks.json` — Hook event handlers (maps events to Python scripts)
- `hooks/*.py` — Hook implementation scripts

**Documentation:** `docs/` — VitePress site mirroring plugin features

**Templates:** `templates/SKILL-TEMPLATE.md` — Skill authoring template

## Creating Plugins

1. Create `plugins/<name>/.claude-plugin/plugin.json` with name, version, description
2. Add skills in `skills/<skill>/SKILL.md` using YAML frontmatter for `name` and `description`
3. Add hooks in `hooks/hooks.json` mapping events to Python scripts
4. Register plugin in `.claude-plugin/marketplace.json` under `plugins` array
5. Add documentation in `docs/<name>/` and update `docs/.vitepress/config.ts` sidebar

Use `${CLAUDE_PLUGIN_ROOT}` for paths in hooks.json — resolves to plugin directory at runtime.

## Hook Events

| Event | Trigger | Block Session |
|-------|---------|---------------|
| `Stop` | Before session ends | Exit code 2 |
| `PostToolUse` | After tool execution | — |

**Matcher:** Regex pattern matching tool names (e.g., `Write|Edit|Bash`)

Debug: `CLAUDE_HOOK_DEBUG=1` → `.claude/hook-debug.log`
