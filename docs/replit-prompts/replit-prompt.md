# replit-prompt

Transform requirements into optimized prompts for Replit Agent.

## Usage

This skill activates when you mention Replit prompting:

```
Create a replit prompt for [your idea]
```

```
Write a prompt for replit to build [application]
```

```
Optimize this for replit agent: [vague description]
```

## Prompt Structure

The skill generates prompts following this structure:

```markdown
## Project Overview
[What is being built and its core purpose]

## Tech Stack
- Frontend: [specific framework]
- Styling: [specific library]
- Backend: [specific framework]
- Database: [specific database]

## Core Features
1. [Feature with specific behavior]
2. [Feature with specific behavior]
3. [Feature with specific behavior]

## UI/UX Requirements
- Design style: [specific style]
- Color scheme: [specific colors]
- Layout: [specific layout]

## Data Model
- Entity1: field1, field2, field3
- Entity2: field1, field2

## User Flows
1. [Flow]: Step A → Step B → Result

## Success Criteria
- [ ] [Testable criterion]
- [ ] [Testable criterion]
```

## Bad vs Good Examples

| Issue | Bad | Good |
|-------|-----|------|
| Vague | "Fix my code" | "Login fails with 'undefined user' error on line 42 when email contains '+'" |
| No scope | "Make a website" | "Create 3-page portfolio: Home (hero), Projects (grid), Contact (form)" |
| Negative | "Don't make it slow" | "Implement lazy loading, paginate to 20 items" |
| No detail | "Add animation" | "Fade in hero text over 0.5s on page load" |
| Too broad | "Build the backend" | "Implement user signup/login with JWT and /api/profile endpoint" |

## Recommended Tech Stacks

### Modern React (Most Projects)
```
Frontend: React 18 + TypeScript + Vite
Styling: TailwindCSS + shadcn/ui
Backend: Node.js + Express
Database: PostgreSQL (Supabase)
```

### Next.js Full-Stack
```
Framework: Next.js 14 (App Router)
Styling: TailwindCSS
Database: Supabase
Auth: NextAuth.js
```

### Python Backend
```
Backend: Python + FastAPI
Frontend: React or HTML/CSS
Database: PostgreSQL + SQLAlchemy
```

### Lightweight MVP
```
Backend: Flask or Express
Frontend: HTMX + TailwindCSS (CDN)
Database: SQLite
```

## Output

The skill provides:

1. **Optimized prompt** ready to paste into Replit
2. **Complexity assessment** (Low/Medium/High)
3. **Next steps** after initial build
4. **Follow-up prompts** for refinements
