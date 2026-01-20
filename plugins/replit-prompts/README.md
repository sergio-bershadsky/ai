# Replit Prompts Plugin

Generate optimized prompts, PRDs, and task plans for Replit Agent that maximize AI understanding and minimize iterations.

## Installation

```bash
claude mcp add-from-marketplace bershadsky-claude-tools/replit-prompts
```

## Overview

This plugin helps you create well-structured instructions for Replit Agent based on official Replit documentation and best practices. It transforms vague ideas into detailed, actionable prompts that Replit Agent can execute effectively.

## Skills

### replit-prompt

Transform requirements into optimized prompts for Replit Agent.

**Triggers:**
- "Create a replit prompt"
- "Write a prompt for replit"
- "Optimize for replit agent"
- "Prepare instructions for replit"

**Features:**
- Applies Replit's 10 official prompting principles
- Converts vague ideas into structured prompts
- Includes tech stack recommendations
- Provides bad vs. good prompt examples

### replit-prd

Create comprehensive Product Requirements Documents for complex Replit projects.

**Triggers:**
- "Create a PRD for replit"
- "Write product requirements"
- "Document app specifications"

**Features:**
- Full PRD template with 13 sections
- Data model specifications
- Feature requirements with acceptance criteria
- Development phases with checkpoints

### replit-plan

Break down projects into iterative development phases with checkpoints.

**Triggers:**
- "Create a plan for replit"
- "Break down tasks"
- "Create development phases"
- "Checkpoint strategy"

**Features:**
- Phase-by-phase task breakdown
- Copy-paste ready prompts for each phase
- Verification steps per phase
- Rollback point planning

## Replit's 10 Prompting Principles

Based on [official Replit documentation](https://docs.replit.com/tutorials/effective-prompting):

| Principle | Description |
|-----------|-------------|
| **Checkpoint** | Structure development iteratively with testable steps |
| **Debug** | Provide exact error messages and relevant code |
| **Discover** | Ask for tool/library suggestions |
| **Experiment** | Refine prompts through iteration |
| **Instruct** | Use positive goals, not negative constraints |
| **Select** | Provide focused, relevant context only |
| **Show** | Include concrete examples and mockups |
| **Simplify** | Use direct, concise language |
| **Specify** | Define outputs, constraints, and edge cases |
| **Test** | Plan structure before prompting |

## Quick Start

### Simple Prompt

```
Create a replit prompt for a todo app with categories
```

### Full PRD

```
Create a PRD for an invoice management SaaS
```

### Phased Development Plan

```
Create a development plan for my e-commerce project
```

## Example Output

### Before (Vague)
```
Make a website for my business
```

### After (Optimized)
```
Create a portfolio website for a freelance photographer with:

## Tech Stack
- Frontend: React with Vite
- Styling: TailwindCSS
- Form handling: EmailJS

## Pages
1. Home: Hero image carousel (5 images), tagline, CTA button
2. Gallery: Filterable grid (categories: Portrait, Wedding, Commercial)
3. About: Bio text, profile photo, testimonials carousel
4. Contact: Form with name, email, message, EmailJS integration

## Design
- Style: Clean, minimal, lots of whitespace
- Colors: Black text, white background, accent from photos
- Typography: Serif for headings, sans-serif for body

## Success Criteria
- [ ] All pages load without errors
- [ ] Gallery filter works correctly
- [ ] Contact form sends email successfully
- [ ] Responsive on mobile devices
```

## PRD Structure

Full PRDs include these sections:

1. **Project Overview** — Name, description, goals
2. **Tech Stack** — Framework, database, styling
3. **Data Model** — Entities with fields and relationships
4. **Features** — Grouped with acceptance criteria
5. **UI/UX** — Wireframes or descriptions
6. **API Endpoints** — Routes and payloads
7. **Authentication** — User flows
8. **Error Handling** — Edge cases
9. **Testing** — Test plan
10. **Deployment** — Environment setup
11. **Success Metrics** — KPIs
12. **Timeline** — Development phases
13. **Open Questions** — Decisions needed

## Development Plan Structure

Plans include:

```
## Phase 1: Foundation
### Tasks
1. Set up project structure
2. Configure database
3. Create base models

### Prompt for Replit Agent
[Copy-paste ready prompt]

### Verification
- [ ] Database connection works
- [ ] Models created successfully

---

## Phase 2: Core Features
...
```

## References

- [Replit Docs: Effective Prompting](https://docs.replit.com/tutorials/effective-prompting)
- [Replit Agent Documentation](https://docs.replit.com/replitai/agent)
- [Replit Blog: Plan Mode](https://blog.replit.com/introducing-plan-mode-a-safer-way-to-vibe-code)

## License

[Unlicense](LICENSE) - Public Domain
