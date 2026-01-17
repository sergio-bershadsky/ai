# replit-plan

Break down projects into iterative development phases with checkpoints for Replit Agent.

## Usage

```
Create a development plan for [project]
```

```
Break down [project] into phases for replit
```

```
Create checkpoint strategy for [application]
```

## Replit Agent Modes

| Mode | Purpose | Modifies Code | Cost |
|------|---------|---------------|------|
| **Build** | Implementation | Yes | Per checkpoint |
| **Plan** | Discussion, architecture | No | Free |
| **Edit** | Targeted changes | Yes | Per change |

**Strategy:** Start in Plan Mode to review approach, then switch to Build Mode.

## Phase Structure

Each phase includes:

```markdown
## Phase N: [Name]
**Goal:** [One sentence]
**Dependencies:** [Previous phases]

### Tasks
1. [Specific task]
2. [Specific task]
3. [Specific task]

### Deliverables
- [ ] [Testable outcome]
- [ ] [Testable outcome]

### Prompt for Replit Agent
```
[Copy-paste ready prompt]
```

### Verification Steps
- [ ] [How to verify]
```

## Phase Sizing

| Size | Duration | Example |
|------|----------|---------|
| Small | 15-30 min | Single form with validation |
| Medium | 30-60 min | Full CRUD for one entity |
| Large | 60-90 min | Feature with UI + API + data |

**Ideal:** Medium phases (30-60 minutes)

### Too Large Signs
- More than 5 major tasks
- Touches 4+ files
- Multiple unrelated features
- "Build the entire X" language

### Too Small Signs
- Single task < 10 minutes
- No testable deliverable
- Could combine with adjacent phase

## Common Phase Patterns

### Foundation Phase (Always First)
```
1. Project setup with tech stack
2. Database schema and migrations
3. Authentication flow
4. Basic navigation/layout
```

### CRUD Feature Phase
```
1. Database model
2. API endpoints (list, create, read, update, delete)
3. List view with table/cards
4. Create/edit form
5. Delete with confirmation
```

### Dashboard Phase
```
1. Dashboard layout
2. Metric cards with data fetching
3. Recent activity list
4. Quick action buttons
5. Responsive grid
```

### Integration Phase
```
1. Environment variables setup
2. Service wrapper/client
3. Core integration function
4. Error handling
5. UI connection
```

### Polish Phase (Always Last)
```
1. Error handling throughout
2. Loading states
3. Edge cases
4. Responsive design fixes
5. Final testing
```

## Example Output

```markdown
# Todo App - Development Plan

## Summary
| Metric | Value |
|--------|-------|
| Total Phases | 4 |
| Estimated Build Time | 2-3 hours |

---

## Phase 1: Foundation
**Goal:** Project setup with database and auth
...

## Phase 2: Category Management
**Goal:** Full CRUD for categories
...

## Phase 3: Todo Management
**Goal:** Todos with categories and due dates
...

## Phase 4: Search and Polish
**Goal:** Search functionality and UX polish
...

---

## Rollback Points
- After Phase 1: Clean structure
- After Phase 2: Categories work
- After Phase 3: Full functionality
```

## Tips

1. **Always plan rollback points** — Know safe states to return to
2. **Verify before proceeding** — Test each phase's deliverables
3. **Keep prompts specific** — Include technical details
4. **Use checkpoints liberally** — They're your safety net
