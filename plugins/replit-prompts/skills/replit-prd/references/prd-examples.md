# PRD Examples for Replit Agent

Complete PRD examples ready to use with Replit Agent.

## Example 1: Invoice Management SaaS

```markdown
# InvoiceFlow - Product Requirements Document

## 1. Executive Summary

### Product Name
InvoiceFlow

### Version
1.0.0

### Last Updated
2026-01-17

### One-Line Description
A simple invoicing application for freelancers to create, send, and track invoices.

### Problem Statement
Freelancers spend too much time creating invoices manually and tracking payments.
They need a simple tool that handles professional invoicing without the complexity
of enterprise solutions.

### Success Metrics
- User can create and send an invoice in under 3 minutes
- Dashboard shows payment status at a glance
- PDF export produces professional, print-ready documents

---

## 2. User Personas

### Persona 1: Solo Freelancer
- **Description:** Individual contractor (designer, developer, writer)
- **Goals:** Create professional invoices quickly, track who owes money
- **Pain Points:** Spreadsheets are messy, enterprise tools are overkill
- **Tech Comfort:** Medium

### Persona 2: Small Agency Owner
- **Description:** Runs 2-5 person creative agency
- **Goals:** Track multiple client invoices, see cash flow overview
- **Pain Points:** Losing track of unpaid invoices, manual reminders
- **Tech Comfort:** Medium-High

---

## 3. Technical Specifications

### Tech Stack
| Layer | Technology | Rationale |
|-------|------------|-----------|
| Frontend | React + TypeScript | Type safety, component reuse |
| Styling | TailwindCSS + shadcn/ui | Consistent, professional UI |
| Backend | Node.js + Express | JavaScript throughout |
| Database | PostgreSQL (Supabase) | Relational data, free tier |
| Auth | Supabase Auth | Integrated with database |
| PDF | @react-pdf/renderer | Client-side PDF generation |
| Email | Resend | Transactional emails |

### Architecture Overview
```
Browser → React SPA → Express API → Supabase (Auth + DB)
                    ↘ Resend (Email)
                    ↘ PDF Generation (client-side)
```

### Third-Party Integrations
| Service | Purpose | API Type | Auth Method |
|---------|---------|----------|-------------|
| Supabase | Database + Auth | REST | API Key |
| Resend | Sending invoices via email | REST | API Key |

### Environment Variables Required
| Variable | Description | Required |
|----------|-------------|----------|
| SUPABASE_URL | Supabase project URL | Yes |
| SUPABASE_ANON_KEY | Supabase anonymous key | Yes |
| RESEND_API_KEY | Resend API key for emails | Yes |

---

## 4. Data Model

### Entity: User
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| id | UUID | Yes | Primary key | Supabase auth user ID |
| email | String | Yes | Unique, email format | Login email |
| business_name | String | No | Max 200 chars | Displayed on invoices |
| business_address | Text | No | - | Displayed on invoices |
| created_at | Timestamp | Yes | Auto-generated | Account creation |

### Entity: Client
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| id | UUID | Yes | Primary key | Unique identifier |
| user_id | UUID | Yes | FK to User | Owner of this client |
| name | String | Yes | Max 200 chars | Client/company name |
| email | String | Yes | Email format | For sending invoices |
| address | Text | No | - | Client address |
| created_at | Timestamp | Yes | Auto-generated | When added |

### Entity: Invoice
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| id | UUID | Yes | Primary key | Unique identifier |
| user_id | UUID | Yes | FK to User | Invoice owner |
| client_id | UUID | Yes | FK to Client | Who to bill |
| invoice_number | String | Yes | Unique per user | e.g., "INV-001" |
| status | Enum | Yes | draft/sent/paid/overdue | Current state |
| issue_date | Date | Yes | - | When issued |
| due_date | Date | Yes | >= issue_date | Payment deadline |
| subtotal | Integer | Yes | >= 0 | Total in cents |
| tax_rate | Decimal | No | 0-100 | Tax percentage |
| total | Integer | Yes | Computed | subtotal + tax |
| notes | Text | No | - | Additional notes |
| created_at | Timestamp | Yes | Auto-generated | Creation time |

### Entity: InvoiceItem
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| id | UUID | Yes | Primary key | Unique identifier |
| invoice_id | UUID | Yes | FK to Invoice | Parent invoice |
| description | String | Yes | Max 500 chars | Line item description |
| quantity | Decimal | Yes | > 0 | Number of units |
| unit_price | Integer | Yes | >= 0 | Price per unit in cents |
| total | Integer | Yes | Computed | quantity * unit_price |

### Entity Relationships
```
User (1) ----< (many) Clients
User (1) ----< (many) Invoices
Client (1) ----< (many) Invoices
Invoice (1) ----< (many) InvoiceItems
```

---

## 5. Feature Specifications

### Feature 1: User Authentication

#### Description
Email/password signup, login, and session management via Supabase Auth.

#### User Stories
- As a new user, I want to sign up with my email so I can start creating invoices
- As a returning user, I want to log in quickly so I can access my invoices

#### Functional Requirements
| ID | Requirement | Priority |
|----|-------------|----------|
| A1.1 | Sign up with email and password | Must Have |
| A1.2 | Log in with email and password | Must Have |
| A1.3 | Password reset via email link | Must Have |
| A1.4 | Persistent session (7 days) | Must Have |
| A1.5 | Log out from all devices | Nice to Have |

#### UI Components
- SignupForm: email, password, confirm password, submit button
- LoginForm: email, password, "Forgot password" link, submit button
- PasswordResetForm: email input, submit button

#### API Endpoints
Handled by Supabase Auth SDK - no custom endpoints needed.

#### Validation Rules
- Email: valid email format, required
- Password: minimum 8 characters, at least one number

#### Error Handling
| Error Condition | Error Code | User Message | System Action |
|-----------------|------------|--------------|---------------|
| Email exists | 400 | "An account with this email already exists" | Show login link |
| Invalid credentials | 401 | "Invalid email or password" | Clear password field |
| Network error | 500 | "Connection error. Please try again." | Retry button |

---

### Feature 2: Client Management

#### Description
Add, edit, and delete clients who will receive invoices.

#### User Stories
- As a user, I want to add new clients so I can invoice them
- As a user, I want to edit client details when they change
- As a user, I want to delete clients I no longer work with

#### Functional Requirements
| ID | Requirement | Priority |
|----|-------------|----------|
| C2.1 | List all clients with search | Must Have |
| C2.2 | Add new client | Must Have |
| C2.3 | Edit existing client | Must Have |
| C2.4 | Delete client (soft delete) | Must Have |
| C2.5 | View client's invoice history | Must Have |

#### UI Components
- ClientList: searchable table with name, email, invoice count, actions
- ClientForm: modal with name, email, address fields
- ClientDetail: client info + list of their invoices

#### API Endpoints
| Method | Endpoint | Request Body | Response | Auth |
|--------|----------|--------------|----------|------|
| GET | /api/clients | - | { clients: Client[] } | Required |
| POST | /api/clients | { name, email, address } | { client: Client } | Required |
| PUT | /api/clients/:id | { name, email, address } | { client: Client } | Required |
| DELETE | /api/clients/:id | - | { success: true } | Required |

#### Validation Rules
- Name: required, max 200 characters
- Email: required, valid email format

---

### Feature 3: Invoice Creation & Management

#### Description
Create, edit, and manage invoices with line items.

#### User Stories
- As a user, I want to create invoices with multiple line items
- As a user, I want to save drafts and edit before sending
- As a user, I want to duplicate past invoices as templates

#### Functional Requirements
| ID | Requirement | Priority |
|----|-------------|----------|
| I3.1 | Create new invoice with line items | Must Have |
| I3.2 | Auto-generate invoice number (INV-001, INV-002...) | Must Have |
| I3.3 | Save as draft | Must Have |
| I3.4 | Edit draft invoices | Must Have |
| I3.5 | Delete draft invoices | Must Have |
| I3.6 | Add tax rate calculation | Must Have |
| I3.7 | Duplicate invoice as new draft | Nice to Have |

#### UI Components
- InvoiceList: table with number, client, amount, status, date, actions
- InvoiceForm: client selector, date pickers, line items editor, tax input, notes
- LineItemRow: description, quantity, unit price, total (computed), delete button
- InvoiceSummary: subtotal, tax, total display

#### API Endpoints
| Method | Endpoint | Request Body | Response | Auth |
|--------|----------|--------------|----------|------|
| GET | /api/invoices | ?status=draft&client_id=x | { invoices: Invoice[] } | Required |
| GET | /api/invoices/:id | - | { invoice: Invoice, items: InvoiceItem[] } | Required |
| POST | /api/invoices | { client_id, dates, items[], tax_rate, notes } | { invoice: Invoice } | Required |
| PUT | /api/invoices/:id | { ...fields } | { invoice: Invoice } | Required |
| DELETE | /api/invoices/:id | - | { success: true } | Required |
| POST | /api/invoices/:id/duplicate | - | { invoice: Invoice } | Required |

---

### Feature 4: Invoice Sending & PDF Export

#### Description
Send invoices via email and download as PDF.

#### User Stories
- As a user, I want to send invoices directly to clients via email
- As a user, I want to download a professional PDF of any invoice

#### Functional Requirements
| ID | Requirement | Priority |
|----|-------------|----------|
| S4.1 | Generate professional PDF from invoice | Must Have |
| S4.2 | Download PDF to device | Must Have |
| S4.3 | Send invoice via email with PDF attachment | Must Have |
| S4.4 | Update status to "sent" after sending | Must Have |
| S4.5 | Preview PDF before sending | Must Have |

#### API Endpoints
| Method | Endpoint | Request Body | Response | Auth |
|--------|----------|--------------|----------|------|
| POST | /api/invoices/:id/send | { message?: string } | { success: true } | Required |

#### PDF Template Contents
- Business name and address (from user profile)
- Client name and address
- Invoice number and dates
- Line items table
- Subtotal, tax, total
- Payment terms/notes

---

### Feature 5: Payment Tracking

#### Description
Mark invoices as paid and track payment status.

#### User Stories
- As a user, I want to mark invoices as paid when I receive payment
- As a user, I want to see which invoices are overdue

#### Functional Requirements
| ID | Requirement | Priority |
|----|-------------|----------|
| P5.1 | Mark invoice as paid | Must Have |
| P5.2 | Auto-mark as overdue when past due date | Must Have |
| P5.3 | Show payment status badges (draft/sent/paid/overdue) | Must Have |
| P5.4 | Filter invoices by status | Must Have |

---

### Feature 6: Dashboard

#### Description
Overview of invoicing activity and outstanding amounts.

#### User Stories
- As a user, I want to see total outstanding amounts at a glance
- As a user, I want to see recent invoicing activity

#### Functional Requirements
| ID | Requirement | Priority |
|----|-------------|----------|
| D6.1 | Show total outstanding (sent + overdue) | Must Have |
| D6.2 | Show total paid this month | Must Have |
| D6.3 | Show overdue invoices count with quick action | Must Have |
| D6.4 | Show recent invoices (last 5) | Must Have |

#### UI Components
- MetricCard: value, label, trend indicator
- RecentInvoicesTable: last 5 invoices with quick actions
- OverdueBanner: alert showing overdue count with "View" link

---

## 6. UI/UX Specifications

### Design System
- **Primary Color:** #2563EB (Blue)
- **Success Color:** #16A34A (Green)
- **Warning Color:** #F59E0B (Amber)
- **Danger Color:** #DC2626 (Red)
- **Background:** #F9FAFB
- **Card Background:** #FFFFFF
- **Text Primary:** #111827
- **Text Secondary:** #6B7280
- **Font Family:** Inter
- **Border Radius:** 8px

### Navigation Structure
```
Dashboard (/)
├── Invoices (/invoices)
│   ├── New Invoice (/invoices/new)
│   └── Invoice Detail (/invoices/:id)
├── Clients (/clients)
│   └── Client Detail (/clients/:id)
└── Settings (/settings)
```

### Responsive Breakpoints
| Breakpoint | Width | Layout Changes |
|------------|-------|----------------|
| Mobile | < 640px | Stack cards, hide sidebar, bottom nav |
| Tablet | 640-1024px | Collapsible sidebar, 2-column grids |
| Desktop | > 1024px | Fixed sidebar, full tables |

---

## 7. User Flows

### Flow 1: Create and Send First Invoice
```
Login → Dashboard → Click "New Invoice"
→ Select/Add Client → Add Line Items → Set Dates
→ Preview → Send → Confirm → Success (status: sent)
```

### Flow 2: Mark Invoice as Paid
```
Dashboard → Click overdue invoice → Invoice Detail
→ Click "Mark as Paid" → Confirm → Status updates → Dashboard metrics update
```

---

## 8. Non-Functional Requirements

### Performance
- Dashboard loads in < 2 seconds
- Invoice list paginates at 25 items
- PDF generates in < 3 seconds

### Security
- [x] All routes require authentication except /login, /signup
- [x] Users can only access their own data (RLS in Supabase)
- [x] API keys stored in environment variables
- [x] HTTPS only

---

## 9. Scope Boundaries

### In Scope (MVP)
- Email/password authentication
- Client CRUD
- Invoice CRUD with line items
- PDF generation and download
- Email sending via Resend
- Dashboard with metrics
- Status tracking (draft/sent/paid/overdue)

### Out of Scope (Future)
- Online payment integration (Stripe) - Phase 2
- Recurring invoices - Phase 2
- Multiple currencies - Phase 2
- Team/multi-user accounts - Phase 3

---

## 10. Acceptance Criteria

### Authentication
- [ ] User can sign up with email/password
- [ ] User can log in and session persists
- [ ] User can reset password via email

### Clients
- [ ] User can add, edit, delete clients
- [ ] Client list is searchable
- [ ] Deleting client doesn't delete invoices

### Invoices
- [ ] User can create invoice with multiple line items
- [ ] Invoice numbers auto-increment correctly
- [ ] Tax calculates correctly
- [ ] Total = subtotal + tax

### PDF & Email
- [ ] PDF renders all invoice data correctly
- [ ] PDF downloads successfully
- [ ] Email sends with correct content
- [ ] Invoice status updates after sending

### Dashboard
- [ ] Metrics show correct totals
- [ ] Overdue invoices flagged correctly
- [ ] Recent invoices list updates

---

## 11. Development Phases

### Phase 1: Foundation (Checkpoint 1)
- [ ] Supabase project setup
- [ ] Database schema + migrations
- [ ] Auth flow (signup, login, logout)
- [ ] Basic layout with navigation

### Phase 2: Core CRUD (Checkpoint 2)
- [ ] Client management (list, add, edit, delete)
- [ ] Invoice creation with line items
- [ ] Invoice list with filtering

### Phase 3: PDF & Email (Checkpoint 3)
- [ ] PDF generation component
- [ ] PDF download functionality
- [ ] Email sending integration
- [ ] Status transitions

### Phase 4: Dashboard & Polish (Checkpoint 4)
- [ ] Dashboard metrics
- [ ] Overdue auto-marking
- [ ] Responsive design fixes
- [ ] Error handling throughout

---

## 12. Reference Applications

- [Invoice Ninja](https://invoiceninja.com) - Feature reference
- [Stripe Dashboard](https://dashboard.stripe.com) - UI/UX reference
```

---

## Example 2: Simple Habit Tracker

A shorter PRD for a simpler application:

```markdown
# HabitPulse - Product Requirements Document

## 1. Executive Summary

### Product Name
HabitPulse

### One-Line Description
A minimalist daily habit tracker to build consistency through simple check-ins.

### Problem Statement
Complex habit apps overwhelm users. Most people just need a simple way to mark
habits complete each day and see their streaks.

---

## 2. User Persona

### Target User: Casual Self-Improver
- **Description:** Someone wanting to build 2-5 simple habits
- **Goals:** Track daily habits, see progress, maintain streaks
- **Pain Points:** Other apps are too complex, require too much setup

---

## 3. Technical Specifications

### Tech Stack
| Layer | Technology |
|-------|------------|
| Frontend | React + Vite |
| Styling | TailwindCSS |
| Backend | Express.js |
| Database | SQLite |
| Auth | Simple email magic link |

---

## 4. Data Model

### Habit
| Field | Type | Required |
|-------|------|----------|
| id | UUID | Yes |
| user_id | UUID | Yes |
| name | String | Yes |
| color | String | Yes |
| created_at | Timestamp | Yes |

### Completion
| Field | Type | Required |
|-------|------|----------|
| id | UUID | Yes |
| habit_id | UUID | Yes |
| date | Date | Yes |
| completed_at | Timestamp | Yes |

---

## 5. Features

### Feature 1: Habit Management
- Add habit with name and color
- Edit habit name/color
- Delete habit (with confirmation)
- Max 10 habits per user

### Feature 2: Daily Check-in
- Today view shows all habits
- Tap to mark complete (checkbox animation)
- Tap again to unmark
- Visual feedback on completion

### Feature 3: Streak Display
- Current streak shown per habit
- Longest streak badge
- Calendar heatmap for past 30 days

### Feature 4: Simple Auth
- Magic link email login (no passwords)
- Session persists 30 days

---

## 6. UI/UX

### Design
- Minimal, card-based UI
- Each habit is a large tappable card
- Colors: user-selected accent per habit
- Animation: satisfying check animation on complete

### Layout
- Single page: Today's habits
- Settings accessible via gear icon
- Calendar view in modal/drawer

---

## 7. Acceptance Criteria

- [ ] User can add up to 10 habits
- [ ] Tapping habit marks it complete for today
- [ ] Streak counts correctly (resets on missed day)
- [ ] Calendar shows past 30 days accurately
- [ ] Works on mobile and desktop

---

## 8. Development Phases

### Phase 1: Core
- [ ] Auth with magic link
- [ ] Add/edit/delete habits
- [ ] Today view with check-in

### Phase 2: Streaks
- [ ] Streak calculation
- [ ] Calendar heatmap
- [ ] Longest streak display

### Phase 3: Polish
- [ ] Animations
- [ ] Responsive design
- [ ] Error handling
```

---

## PRD Checklist

Before using a PRD with Replit Agent, verify:

- [ ] **Executive summary** is clear and concise
- [ ] **Tech stack** is explicitly specified
- [ ] **Data model** includes all fields with types
- [ ] **Features** have specific requirements, not vague descriptions
- [ ] **API endpoints** are defined for backend features
- [ ] **Validation rules** specified for all inputs
- [ ] **Error handling** documented
- [ ] **UI/UX** includes colors, layout, and component descriptions
- [ ] **User flows** map the complete journey
- [ ] **Acceptance criteria** are testable checkboxes
- [ ] **Development phases** break work into checkpoints
- [ ] **Scope boundaries** clearly state what's NOT included
