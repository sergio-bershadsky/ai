# Changelog

All notable changes to the Secondbrain plugin will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.1.0] - 2026-03-30

### Added

- **Review Stamps** (`/secondbrain-review`) — Track who reviewed which documentation pages and when, with an append-only audit trail in frontmatter. Configurable staleness thresholds (fresh/aging/stale) with visual ReviewBadge component that renders automatically on every VitePress page.

- **Meeting Transcription** (`/secondbrain-transcribe`) — Import meeting transcripts from external providers (Fireflies.ai supported out of the box) and automatically generate structured discussion documents. Includes participant mapping, decision extraction with optional ADR creation, and deduplication to prevent re-processing.

- **SessionStart hook for transcription** — Automatically detects undocumented meetings when a session starts and prompts you to process them.

- **ReviewBadge Vue component** — Color-coded staleness indicator (green/yellow/orange) with review count, rendered above every documentation page via VitePress theme.

- **Team configuration** — Project-level `team` section in config.yaml for mapping aliases to full names and email patterns, shared across review stamps and transcription.

- **`is_meeting_processed()` tracking function** — Query discussion microdatabase partitions to check if a meeting has already been documented.

### Changed

- Discussion entity schema now supports optional `meeting_id` and `provider` fields for transcription source tracking.
- Discussion `source` enum extended with `fireflies` and `otter` provider values.
- Init scaffolding (`/secondbrain-init`) now offers Review Stamps and Meeting Transcription as optional features during project setup.
- Session context hook lists new available commands when features are configured.

## [1.0.0] - 2026-03-28

### Added

- Initial release with core knowledge management system.
- Configurable entity types: ADRs, Discussions, Notes, Tasks, and custom entities.
- Microdatabase architecture with YAML records and JSON Schema validation.
- VitePress documentation portal with EntityTable component.
- Semantic search via qmd (CLI) and Orama (browser).
- Freshness tracking with configurable staleness thresholds.
- Automation hooks: freshness check, session context, sidebar validation, search index updates.
- Background refinement and review agents.
- Interactive scaffolding via `/secondbrain-init`.
