---
name: replit-prompt
description: |
  This skill should be used when the user asks to "create a replit prompt", "write a prompt for replit",
  "optimize for replit agent", "prepare instructions for replit", or mentions building something with
  Replit Agent. Transforms user requirements into optimized, structured prompts that Replit Agent
  understands and executes accurately with minimal iterations.
---

# Replit Prompt Generator

Transform requirements into optimized prompts for Replit Agent that maximize AI understanding and minimize iterations.

## When to Use

- User wants to build something with Replit Agent
- User needs to convert an idea into a Replit-ready prompt
- User wants to improve an existing Replit prompt
- User is preparing to start a new Replit project

## Core Principles (Replit's Official Guidelines)

### 1. Checkpoint — Structure Iteratively
Break large goals into smaller, testable steps. Use checkpoints between phases.

### 2. Debug — Provide Detailed Context
Include exact error messages, relevant code snippets, and steps already attempted.

### 3. Discover — Ask for Suggestions
Request tool/library recommendations when unsure about approach.

### 4. Experiment — Iterate on Prompts
Refine requests by adjusting wording or adding detail.

### 5. Instruct — Use Positive Goals
Frame as "do this" rather than "don't do that".

### 6. Select — Focused Context
Provide relevant context only; avoid overwhelming with unrelated information.

### 7. Show — Concrete Examples
Reduce ambiguity with code snippets, mockups, or reference apps.

### 8. Simplify — Concise Language
Use direct, short sentences. Avoid jargon.

### 9. Specify — Define Outputs
State expected outputs, constraints, data formats, and edge cases.

### 10. Test — Plan First
Outline features, data structures, and user flows before prompting.

## Prompt Structure Template

When generating prompts for Replit, use this structure:

```markdown
## Project Overview
[1-2 sentences: What is being built and its core purpose]

## Tech Stack
- Frontend: [specific framework/library]
- Backend: [specific framework/language]
- Database: [specific database]
- Authentication: [specific method]
- Additional: [any other required tools/APIs]

## Core Features
1. [Feature 1]: [specific description with expected behavior]
2. [Feature 2]: [specific description with expected behavior]
3. [Feature 3]: [specific description with expected behavior]

## UI/UX Requirements
- Design style: [modern/minimal/material/etc.]
- Color scheme: [specific colors or "neutral professional"]
- Layout: [sidebar/top-nav/dashboard/etc.]
- Responsive: [yes/no, breakpoints if specific]

## Data Model
[Describe main entities and their relationships]
- Entity1: field1, field2, field3
- Entity2: field1, field2 (relates to Entity1)

## User Flows
1. [Flow 1]: Step A → Step B → Step C → Result
2. [Flow 2]: Step A → Step B → Result

## Constraints
- [Constraint 1: e.g., "Must work offline"]
- [Constraint 2: e.g., "No external API calls except X"]

## Success Criteria
- [ ] [Specific testable criterion 1]
- [ ] [Specific testable criterion 2]
- [ ] [Specific testable criterion 3]
```

## Procedure

### Step 1: Gather Requirements

Ask the user about:
1. **What** they want to build (core functionality)
2. **Who** will use it (target users)
3. **How** it should work (key user flows)
4. **Why** (problem being solved)

If user provides vague input, ask clarifying questions:
- "What should happen when a user clicks X?"
- "Should data persist between sessions?"
- "Any specific design/framework preferences?"

### Step 2: Extract Technical Details

Determine from user input or ask about:
- Preferred tech stack (or let Replit decide)
- Authentication requirements
- Data storage needs
- Third-party integrations
- Performance requirements

### Step 3: Structure the Prompt

Transform gathered information into the structured template above.

**Bad prompt transformation:**
```
❌ Bad: "Make a website for my business"
✅ Good: "Create a portfolio website for a freelance photographer with:
- Home page with hero image carousel
- Gallery page with filterable photo categories
- Contact form with email integration
- About page with bio and testimonials
- Tech: React, TailwindCSS, EmailJS for form
- Design: Clean, minimal, lots of whitespace"
```

### Step 4: Add Specificity

Enhance the prompt with:
- **Concrete examples**: "Like Stripe's dashboard layout"
- **Specific behaviors**: "Click 'Add' opens modal, not new page"
- **Edge cases**: "If cart is empty, show 'Start shopping' CTA"
- **Validation rules**: "Email must be valid format, password min 8 chars"

### Step 5: Present Draft

Show the optimized prompt to the user:

```
## Replit Agent Prompt

**Optimized for:** [Build Mode / Plan Mode]
**Estimated complexity:** [Low / Medium / High]

---

[Generated prompt content]

---

**Recommendations:**
1. [Tip for using this prompt effectively]
2. [Suggested follow-up prompts after initial build]

Ready to copy to Replit?
```

Wait for user confirmation or modification requests.

### Step 6: Provide Iteration Guidance

After delivering the prompt, advise on:
- Using Plan Mode first for complex features
- Setting up checkpoints between phases
- Follow-up prompts for refinements

## Output Format

```
## Replit Agent Prompt

**Mode:** Build / Plan
**Complexity:** Low / Medium / High

---

[Structured prompt following template]

---

## Next Steps

1. **Initial Build**: Copy prompt to Replit Agent
2. **After MVP**: [Suggested enhancement prompt]
3. **Testing**: [What to verify after build]

## Checkpoint Strategy

Phase 1: [Description] → Checkpoint
Phase 2: [Description] → Checkpoint
Phase 3: [Description] → Checkpoint
```

## Bad vs Good Prompt Examples

| Issue | Bad Prompt | Good Prompt |
|-------|-----------|-------------|
| Vague | "Fix my code" | "The login function in auth.js throws 'undefined user' on line 42 when email contains '+'" |
| No scope | "Make a website" | "Create a 3-page portfolio: Home (hero, skills), Projects (grid with filters), Contact (form)" |
| Negative | "Don't make it slow" | "Implement lazy loading for images, paginate lists to 20 items" |
| No detail | "Add animation" | "Fade in hero text on page load over 0.5s, slide in cards from bottom on scroll" |
| Overwhelming | "Build the entire backend" | "Implement user signup/login with JWT and a /api/profile GET endpoint" |

## Rules

1. **ALWAYS use positive framing** — "Do X" not "Don't do Y"
2. **ALWAYS include tech stack** — Even if "let Replit decide"
3. **ALWAYS define success criteria** — Testable checkboxes
4. **ALWAYS break into phases** — For anything beyond simple apps
5. **NEVER use vague terms** — No "nice", "good", "fast", "modern" without specifics
6. **NEVER assume context** — Replit Agent has no prior knowledge

## Additional Resources

See reference files for detailed patterns:
- **`references/examples.md`** — Full prompt examples for common app types
- **`references/tech-stacks.md`** — Recommended tech stack combinations
