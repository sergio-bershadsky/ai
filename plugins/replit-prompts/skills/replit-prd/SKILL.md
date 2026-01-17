---
name: replit-prd
description: |
  This skill should be used when the user asks to "create a PRD for Replit", "write product requirements",
  "document app specifications", "prepare a product spec", or needs a comprehensive specification document
  that Replit Agent can use for complex, multi-feature applications. Creates structured PRDs optimized
  for AI-powered development.
---

# Replit PRD Generator

Create comprehensive Product Requirements Documents optimized for Replit Agent to build complex applications.

## When to Use

- Building complex applications with multiple features
- Need stakeholder alignment before development
- Want one-shot autonomous builds (entire app from single prompt)
- Require clear acceptance criteria and testing plans
- Working on team projects that need documentation

## PRD vs Simple Prompt

| Aspect | Simple Prompt | Full PRD |
|--------|---------------|----------|
| Features | 1-3 | 4+ |
| Pages/Screens | 1-3 | 4+ |
| User Roles | 1 | Multiple |
| Integrations | 0-1 | Multiple |
| Development Time | < 1 hour | Hours to days |
| Iterations Expected | Minimal | Multiple phases |

**Rule of thumb:** If you can describe it in 10 lines, use a prompt. If you need structure, use a PRD.

## PRD Template for Replit

```markdown
# [Product Name] - Product Requirements Document

## 1. Executive Summary

### Product Name
[Name]

### Version
1.0.0

### Last Updated
[Date]

### One-Line Description
[What it is and who it's for in one sentence]

### Problem Statement
[What problem does this solve? Why does it matter?]

### Success Metrics
- [Metric 1: e.g., "User can complete core task in under 2 minutes"]
- [Metric 2: e.g., "Zero critical bugs in core user flows"]
- [Metric 3: e.g., "Page load time under 3 seconds"]

---

## 2. User Personas

### Persona 1: [Name/Role]
- **Description:** [Who they are]
- **Goals:** [What they want to achieve]
- **Pain Points:** [What frustrates them currently]
- **Tech Comfort:** [Low/Medium/High]

### Persona 2: [Name/Role]
- **Description:** [Who they are]
- **Goals:** [What they want to achieve]
- **Pain Points:** [What frustrates them currently]
- **Tech Comfort:** [Low/Medium/High]

---

## 3. Technical Specifications

### Tech Stack
| Layer | Technology | Rationale |
|-------|------------|-----------|
| Frontend | [Framework] | [Why chosen] |
| Styling | [Library] | [Why chosen] |
| Backend | [Framework] | [Why chosen] |
| Database | [System] | [Why chosen] |
| Auth | [Provider] | [Why chosen] |
| Hosting | Replit Deployments | Default |

### Architecture Overview
```
[Text diagram or description of system architecture]
```

### Third-Party Integrations
| Service | Purpose | API Type | Auth Method |
|---------|---------|----------|-------------|
| [Service] | [What for] | REST/GraphQL | API Key/OAuth |

### Environment Variables Required
| Variable | Description | Required |
|----------|-------------|----------|
| DATABASE_URL | PostgreSQL connection string | Yes |
| [VAR_NAME] | [Description] | Yes/No |

---

## 4. Data Model

### Entity: [EntityName]
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| id | UUID | Yes | Primary key | Unique identifier |
| [field] | [type] | Yes/No | [constraints] | [description] |

### Entity Relationships
```
User (1) ----< (many) Posts
Post (1) ----< (many) Comments
User (1) ----< (many) Comments
```

### Database Indexes
- [table].[column] - For [use case]
- [table].[column] - For [use case]

---

## 5. Feature Specifications

### Feature 1: [Feature Name]

#### Description
[What this feature does]

#### User Stories
- As a [role], I want to [action] so that [benefit]
- As a [role], I want to [action] so that [benefit]

#### Functional Requirements
| ID | Requirement | Priority |
|----|-------------|----------|
| F1.1 | [Specific requirement] | Must Have |
| F1.2 | [Specific requirement] | Must Have |
| F1.3 | [Specific requirement] | Nice to Have |

#### UI Components
- [Component 1]: [Description and behavior]
- [Component 2]: [Description and behavior]

#### API Endpoints
| Method | Endpoint | Request Body | Response | Auth |
|--------|----------|--------------|----------|------|
| POST | /api/[resource] | { field: type } | { field: type } | Required |
| GET | /api/[resource]/:id | - | { field: type } | Required |

#### Validation Rules
- [Field]: [Rule, e.g., "Email must be valid format"]
- [Field]: [Rule, e.g., "Password minimum 8 characters"]

#### Error Handling
| Error Condition | Error Code | User Message | System Action |
|-----------------|------------|--------------|---------------|
| [Condition] | 400/401/etc | [Friendly message] | [What happens] |

### Feature 2: [Feature Name]
[Repeat structure above]

---

## 6. UI/UX Specifications

### Design System
- **Primary Color:** [Hex code]
- **Secondary Color:** [Hex code]
- **Background:** [Hex code]
- **Text:** [Hex code]
- **Font Family:** [Font name]
- **Border Radius:** [Value, e.g., 8px]

### Page Layouts

#### Page: [Page Name]
- **Route:** /[path]
- **Layout:** [Description]
- **Components:**
  - [Component 1]
  - [Component 2]
- **State:** [What state this page manages]

### Navigation Structure
```
Home (/)
├── Dashboard (/dashboard)
├── [Section] (/[path])
│   ├── [Subsection] (/[path]/[subpath])
│   └── [Subsection] (/[path]/[subpath])
└── Settings (/settings)
```

### Responsive Breakpoints
| Breakpoint | Width | Layout Changes |
|------------|-------|----------------|
| Mobile | < 640px | [Changes] |
| Tablet | 640-1024px | [Changes] |
| Desktop | > 1024px | [Default layout] |

---

## 7. User Flows

### Flow 1: [Flow Name]
```
Start → [Step 1] → [Step 2] → [Decision Point]
                                    ├── Yes → [Step 3a] → End
                                    └── No → [Step 3b] → End
```

**Detailed Steps:**
1. User [action] on [page/component]
2. System [response/validation]
3. User sees [feedback/result]
4. [Continue...]

### Flow 2: [Flow Name]
[Repeat structure]

---

## 8. Non-Functional Requirements

### Performance
- Page load time: < [X] seconds
- API response time: < [X] ms
- Support [X] concurrent users

### Security
- [ ] Input sanitization on all forms
- [ ] HTTPS only
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention
- [ ] CSRF tokens on forms
- [ ] Rate limiting on auth endpoints

### Accessibility
- [ ] Keyboard navigable
- [ ] Screen reader compatible
- [ ] Color contrast ratio 4.5:1 minimum
- [ ] Focus indicators visible

### Browser Support
- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)

---

## 9. Scope Boundaries

### In Scope (MVP)
- [Feature/capability 1]
- [Feature/capability 2]
- [Feature/capability 3]

### Out of Scope (Future)
- [Feature/capability 1] - Reason: [why deferred]
- [Feature/capability 2] - Reason: [why deferred]

### Explicit Non-Goals
- [Thing this product will NOT do]
- [Thing this product will NOT do]

---

## 10. Acceptance Criteria

### Feature 1: [Name]
- [ ] [Testable criterion 1]
- [ ] [Testable criterion 2]
- [ ] [Testable criterion 3]

### Feature 2: [Name]
- [ ] [Testable criterion 1]
- [ ] [Testable criterion 2]

### Overall Application
- [ ] All pages load without errors
- [ ] All forms validate correctly
- [ ] All API endpoints return expected responses
- [ ] Mobile layout is functional
- [ ] No console errors in production

---

## 11. Development Phases

### Phase 1: Foundation (Checkpoint 1)
**Goal:** Basic structure and auth
- [ ] Project setup with tech stack
- [ ] Database schema and migrations
- [ ] Authentication flow
- [ ] Basic navigation/layout

### Phase 2: Core Features (Checkpoint 2)
**Goal:** Primary functionality
- [ ] [Core feature 1]
- [ ] [Core feature 2]

### Phase 3: Polish (Checkpoint 3)
**Goal:** UX and edge cases
- [ ] Error handling
- [ ] Loading states
- [ ] Responsive design
- [ ] Form validations

### Phase 4: Launch (Checkpoint 4)
**Goal:** Production ready
- [ ] Final testing
- [ ] Performance optimization
- [ ] Security review
- [ ] Documentation

---

## 12. Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| [Risk 1] | High/Med/Low | High/Med/Low | [How to address] |
| [Risk 2] | High/Med/Low | High/Med/Low | [How to address] |

---

## 13. Appendix

### Wireframes/Mockups
[Links or embedded images]

### Reference Applications
- [App name](URL) - Similar [feature/design]
- [App name](URL) - Similar [feature/design]

### API Documentation Links
- [Service]: [URL]

### Glossary
| Term | Definition |
|------|------------|
| [Term] | [Definition] |
```

## Procedure

### Step 1: Gather High-Level Requirements

Ask the user:
1. What is the product and who is it for?
2. What are the 3-5 most important features?
3. Any specific tech requirements or preferences?
4. Any reference apps or designs to emulate?

### Step 2: Define User Personas

For each user type:
- Who are they?
- What do they need to accomplish?
- What's their technical skill level?

### Step 3: Detail Features

For each feature, extract:
- User stories
- UI components needed
- Data required
- API endpoints
- Validation rules
- Error scenarios

### Step 4: Design Data Model

- List all entities
- Define all fields with types and constraints
- Map relationships
- Identify required indexes

### Step 5: Specify UI/UX

- Color palette
- Page layouts
- Navigation structure
- Responsive behavior
- Key interactions

### Step 6: Define User Flows

Document step-by-step:
- Happy path
- Error paths
- Edge cases

### Step 7: Set Acceptance Criteria

Create testable checkboxes for:
- Each feature
- Overall functionality
- Performance requirements

### Step 8: Plan Development Phases

Break into 3-4 phases with:
- Clear goals
- Specific deliverables
- Checkpoint criteria

### Step 9: Present Draft PRD

```
## PRD Draft: [Product Name]

**Complexity:** [Low/Medium/High]
**Estimated Phases:** [Number]
**Primary Persona:** [Name]

---

[Full PRD content]

---

## Usage Instructions

1. Copy entire PRD to Replit Agent
2. Use Plan Mode first to review Agent's approach
3. Approve plan and start Phase 1
4. Create checkpoint after each phase
5. Review and iterate before next phase

Ready to proceed?
```

### Step 10: Provide Iteration Guidance

After PRD delivery:
- How to use Plan Mode effectively
- When to create checkpoints
- How to handle deviations

## Output Format

```
# [Product Name] PRD

## Quick Reference

| Attribute | Value |
|-----------|-------|
| Complexity | [Low/Medium/High] |
| Features | [Count] |
| Pages | [Count] |
| API Endpoints | [Count] |
| Phases | [Count] |

---

[Full PRD following template]

---

## Replit Agent Instructions

**Mode:** Start in Plan Mode

**Phase 1 Prompt:**
"Review this PRD and create a development plan for Phase 1: [Phase 1 Goal].
Don't start building yet - just outline your approach."

**Build Prompt (after plan approval):**
"Proceed with Phase 1 implementation. Create a checkpoint when complete."

**Subsequent Phases:**
Repeat plan → build → checkpoint cycle for each phase.
```

## Rules

1. **ALWAYS include acceptance criteria** — Every feature needs testable conditions
2. **ALWAYS define data model** — Schema before code
3. **ALWAYS specify error handling** — Every feature's error scenarios
4. **ALWAYS break into phases** — 3-4 phases with clear checkpoints
5. **NEVER leave fields vague** — Every input has type, constraints, validation
6. **NEVER skip security requirements** — Always include security section
7. **PREFER reference apps** — Concrete examples over abstract descriptions

## Additional Resources

See reference files:
- **`references/prd-examples.md`** — Complete PRD examples for different app types
