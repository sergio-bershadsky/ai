# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Code plugin marketplace with reusable skills and hooks for workflow automation.

## Commands

```bash
npm run docs:dev      # Run docs locally (http://localhost:5173)
npm run docs:build    # Build docs for production
npm run docs:preview  # Preview production build
```

## Adding a New Plugin

1. Create `plugins/<name>/.claude-plugin/plugin.json` with name, version, description, skills path, hooks path
2. Add skills in `plugins/<name>/skills/<skill>/SKILL.md` (use `templates/SKILL-TEMPLATE.md` as reference)
3. Add hooks in `plugins/<name>/hooks/hooks.json`
4. Register plugin in `.claude-plugin/marketplace.json` under the `plugins` array

## Plugin Conventions

**Paths:** Use `${CLAUDE_PLUGIN_ROOT}` variable in hooks.json for portable paths

**Skills:** SKILL.md files with YAML frontmatter (name, description) followed by procedure steps

**Hooks:** Python scripts with JSON I/O. Available hook events:
- `Stop` - Triggers when Claude attempts to stop (can block with exit code 2)
- `PostToolUse` - Triggers after tool execution, matcher pattern filters by tool name

**Debugging hooks:** Set `CLAUDE_HOOK_DEBUG=1` to write logs to `.claude/hook-debug.log`

## License

Public domain (Unlicense)
