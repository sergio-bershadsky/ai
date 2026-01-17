# replit-prd

Create comprehensive Product Requirements Documents for complex Replit Agent builds.

## When to Use PRD vs Simple Prompt

| Aspect | Simple Prompt | Full PRD |
|--------|---------------|----------|
| Features | 1-3 | 4+ |
| Pages/Screens | 1-3 | 4+ |
| User Roles | 1 | Multiple |
| Integrations | 0-1 | Multiple |
| Development Time | < 1 hour | Hours to days |

**Rule:** If describable in 10 lines, use a prompt. Otherwise, use a PRD.

## Usage

```
Create a PRD for [complex application]
```

```
Write product requirements for [multi-feature app]
```

## PRD Sections

The generated PRD includes:

### 1. Executive Summary
- Product name and version
- One-line description
- Problem statement
- Success metrics

### 2. User Personas
- Target user descriptions
- Goals and pain points
- Technical comfort level

### 3. Technical Specifications
- Complete tech stack with rationale
- Architecture overview
- Third-party integrations
- Environment variables

### 4. Data Model
- All entities with fields
- Types and constraints
- Relationships diagram
- Database indexes

### 5. Feature Specifications
For each feature:
- User stories
- Functional requirements (prioritized)
- UI components
- API endpoints
- Validation rules
- Error handling

### 6. UI/UX Specifications
- Design system (colors, fonts, spacing)
- Page layouts
- Navigation structure
- Responsive breakpoints

### 7. User Flows
- Step-by-step flow diagrams
- Decision points
- Success and error paths

### 8. Non-Functional Requirements
- Performance targets
- Security checklist
- Accessibility requirements
- Browser support

### 9. Scope Boundaries
- In scope (MVP)
- Out of scope (future)
- Explicit non-goals

### 10. Acceptance Criteria
- Testable checkboxes per feature
- Overall application criteria

### 11. Development Phases
- Phase breakdown with goals
- Checkpoint deliverables

### 12. Risks and Mitigations
- Identified risks
- Impact and probability
- Mitigation strategies

### 13. Appendix
- Wireframes/mockups
- Reference applications
- API documentation links

## Using PRD with Replit Agent

### Workflow

1. **Plan Mode First**
   ```
   Review this PRD and create a development plan for Phase 1.
   Don't start building - just outline your approach.
   ```

2. **Approve Plan**
   Review Agent's proposed approach

3. **Build Mode**
   ```
   Proceed with Phase 1 implementation. Create checkpoint when complete.
   ```

4. **Verify & Iterate**
   Test deliverables before next phase

5. **Repeat**
   Continue for each phase

### Tips

- Use Plan Mode to review complex features (free, no charges)
- Create checkpoints between phases for safe rollback
- Break phases if Agent struggles with scope
