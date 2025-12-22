---
layout: home

hero:
  name: Claude Skills & Hooks
  text: Plugin marketplace for Claude Code
  tagline: Install with one command
  actions:
    - theme: brand
      text: Get Started
      link: /installation
    - theme: alt
      text: View on GitHub
      link: https://github.com/sergio-bershadsky/ai

features:
  - title: One Command Install
    details: /plugin install git@bershadsky-claude-tools
  - title: Git Workflow
    details: Conventional commits, auto-staging, uncommitted changes protection
  - title: Settings Sync
    details: Backup and restore Claude settings across ephemeral VMs
---

## Quick Start

```bash
# Add marketplace
/plugin marketplace add sergio-bershadsky/ai

# Install plugin
/plugin install git@bershadsky-claude-tools
```

## Plugins

| Plugin | Skills | Hooks |
|--------|--------|-------|
| [git](/git/) | commit | auto-stage, pre-stop-commit |
| [settings-sync](/settings-sync/) | — | backup-settings |
