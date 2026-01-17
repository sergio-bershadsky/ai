# Replit Prompt Examples

Complete, production-ready prompt examples for common application types.

## Example 1: SaaS Dashboard

```markdown
## Project Overview
Build a subscription analytics dashboard for SaaS businesses to track MRR, churn, and customer metrics.

## Tech Stack
- Frontend: React with TypeScript
- Styling: TailwindCSS with shadcn/ui components
- Backend: Node.js with Express
- Database: PostgreSQL
- Charts: Recharts
- Authentication: Clerk or Auth0

## Core Features
1. **Dashboard Overview**: Display MRR, ARR, churn rate, and customer count as metric cards with sparklines showing 30-day trend
2. **Revenue Chart**: Interactive line chart showing MRR over time with ability to toggle between daily/weekly/monthly views
3. **Customer Table**: Paginated list of customers with columns: Name, Email, Plan, MRR, Status, Joined Date. Sortable and filterable.
4. **Subscription Management**: View individual customer details, upgrade/downgrade plans, cancel subscriptions

## UI/UX Requirements
- Design: Clean, professional dashboard similar to Stripe Dashboard
- Color scheme: Neutral grays with blue accent (#3B82F6) for primary actions
- Layout: Fixed sidebar (240px) with collapsible option, main content area
- Navigation: Dashboard, Customers, Revenue, Settings
- Responsive: Sidebar collapses to icons on tablet, becomes bottom nav on mobile

## Data Model
- Customer: id, email, name, created_at, status (active/churned/trial)
- Subscription: id, customer_id, plan_id, mrr, started_at, cancelled_at
- Plan: id, name, price_monthly, features (JSON)
- Event: id, customer_id, type (signup/upgrade/downgrade/cancel), created_at

## User Flows
1. **View Dashboard**: Login → See overview cards → Click card → See detailed chart
2. **Find Customer**: Dashboard → Customers → Search/filter → Click row → See details
3. **Cancel Subscription**: Customer detail → Actions dropdown → Cancel → Confirm modal → Success toast

## Constraints
- All monetary values in cents (integer) to avoid floating point issues
- Charts must handle up to 10,000 data points without performance issues
- Customer table pagination: 25 items per page

## Success Criteria
- [ ] Dashboard loads in under 2 seconds with 1000 customers
- [ ] All charts render correctly with sample data
- [ ] Customer search returns results within 500ms
- [ ] Mobile layout is fully functional
- [ ] All CRUD operations work without errors
```

## Example 2: E-commerce Product Page

```markdown
## Project Overview
Create a product detail page for an e-commerce store selling electronics, with variant selection and add-to-cart functionality.

## Tech Stack
- Frontend: Next.js 14 with App Router
- Styling: TailwindCSS
- State: Zustand for cart management
- Database: Supabase (or mock data for MVP)
- Images: Next/Image with blur placeholder

## Core Features
1. **Image Gallery**: Main image (500x500) with 4-5 thumbnail strip below. Click thumbnail to change main image. Zoom on hover.
2. **Product Info**: Name, price (with sale price if applicable), rating stars (1-5), review count link
3. **Variant Selector**: Color swatches (circles with border on selected), Size dropdown (S/M/L/XL)
4. **Add to Cart**: Quantity selector (1-10), Add to Cart button, disabled if out of stock
5. **Product Details**: Tabbed section with Description, Specifications (table), Reviews (list)

## UI/UX Requirements
- Design: Modern e-commerce, similar to Apple Store product pages
- Color scheme: White background, black text, accent color from product images
- Layout: Two-column on desktop (images left 60%, info right 40%), stacked on mobile
- Animations: Smooth image transitions (200ms), button hover states, add-to-cart success animation

## Data Model
- Product: id, name, description, base_price, sale_price, rating, review_count
- Variant: id, product_id, color, size, sku, stock_quantity, price_adjustment
- Image: id, product_id, url, alt_text, sort_order, is_primary
- Review: id, product_id, user_name, rating, comment, created_at

## User Flows
1. **View Product**: Load page → See main image and info → Scroll to read details
2. **Select Variant**: Click color swatch → See new images → Select size from dropdown → See updated stock status
3. **Add to Cart**: Set quantity → Click Add to Cart → See success animation → Cart count updates in header

## Constraints
- Images must be optimized (WebP format, lazy loaded)
- Stock check must happen before adding to cart
- Cart persists in localStorage

## Success Criteria
- [ ] Page loads with LCP under 2.5 seconds
- [ ] All variant combinations show correct price and stock
- [ ] Add to cart works and updates cart state
- [ ] Responsive layout works on 320px to 1920px widths
- [ ] Image gallery is accessible with keyboard navigation
```

## Example 3: Task Management App

```markdown
## Project Overview
Build a Kanban-style task management app for personal productivity with drag-and-drop boards.

## Tech Stack
- Frontend: React with Vite
- Styling: TailwindCSS
- Drag & Drop: @dnd-kit/core
- Backend: Express.js
- Database: SQLite (for simplicity, can migrate to PostgreSQL)
- State: React Query for server state

## Core Features
1. **Board View**: Three columns (To Do, In Progress, Done) with draggable task cards
2. **Task Cards**: Title (required), description (optional), due date badge, priority indicator (color dot)
3. **Task CRUD**: Click card to open modal for edit, delete button with confirmation, quick-add at bottom of each column
4. **Filters**: Filter by priority (all/high/medium/low), search by title
5. **Persistence**: All changes auto-save, optimistic updates with error rollback

## UI/UX Requirements
- Design: Clean and minimal, similar to Trello but simpler
- Color scheme: Light gray background (#F3F4F6), white cards, colored priority dots (red=high, yellow=medium, green=low)
- Layout: Full-width board, columns equal width, horizontal scroll if needed
- Animations: Smooth drag (200ms), card entrance animation, success/error toasts

## Data Model
- Task: id, title, description, status (todo/in_progress/done), priority (high/medium/low), due_date, created_at, sort_order
- No user model for MVP (single user)

## User Flows
1. **Add Task**: Click "+" at column bottom → Type title → Press Enter → Card appears
2. **Move Task**: Drag card → Drop on different column → Status updates → Sort order preserved
3. **Edit Task**: Click card → Modal opens → Edit fields → Click Save or press Escape to cancel
4. **Delete Task**: In edit modal → Click Delete → Confirm → Card removed with animation

## Constraints
- Max 100 tasks per column for performance
- Drag must work on touch devices
- Auto-save within 500ms of change

## Success Criteria
- [ ] Drag and drop works smoothly without layout jumps
- [ ] Tasks persist after page refresh
- [ ] Filter and search respond in under 100ms
- [ ] Touch drag works on mobile
- [ ] Error states handled gracefully (show toast, rollback optimistic update)
```

## Example 4: API Integration App

```markdown
## Project Overview
Build a weather dashboard that fetches data from OpenWeatherMap API and displays current conditions and 5-day forecast.

## Tech Stack
- Frontend: React with TypeScript
- Styling: TailwindCSS
- API: OpenWeatherMap API (free tier)
- HTTP Client: Axios
- Icons: React Icons (weather icons)

## Core Features
1. **Location Search**: Search input with autocomplete for city names, recent searches dropdown (last 5)
2. **Current Weather**: Large temperature display, weather icon, condition text (Sunny, Cloudy, etc.), feels like, humidity, wind speed
3. **5-Day Forecast**: Horizontal scrollable cards showing day name, high/low temps, weather icon
4. **Unit Toggle**: Switch between Celsius and Fahrenheit, persists in localStorage

## UI/UX Requirements
- Design: Modern weather app, gradient backgrounds based on conditions (blue for clear, gray for cloudy, etc.)
- Color scheme: Dynamic based on weather, white text with shadows for readability
- Layout: Centered card (max-width 600px), search at top, current weather middle, forecast bottom
- Animations: Fade transition when location changes, smooth temperature number animation

## Data Model
- CurrentWeather: temp, feels_like, humidity, wind_speed, condition, icon_code
- Forecast: date, temp_high, temp_low, condition, icon_code
- UserPreferences: unit (celsius/fahrenheit), recent_searches[]

## User Flows
1. **Initial Load**: Check localStorage for last searched city → Fetch weather → Display
2. **Search City**: Type in search → See autocomplete suggestions → Select → Fetch new data → Update display
3. **Toggle Unit**: Click C/F toggle → All temperatures convert instantly → Preference saved

## API Integration
- Endpoint: api.openweathermap.org/data/2.5/weather (current)
- Endpoint: api.openweathermap.org/data/2.5/forecast (5-day)
- API Key: User must provide (show input if missing, store in localStorage)
- Rate limiting: Cache responses for 10 minutes

## Constraints
- Handle API errors gracefully (show friendly message, not raw error)
- Support offline viewing of last fetched data
- API key stored securely in localStorage (not in code)

## Success Criteria
- [ ] Weather displays correctly for any valid city
- [ ] Unit conversion is accurate
- [ ] Recent searches persist and work
- [ ] Graceful handling when API is down
- [ ] Responsive design works on mobile
```

## Example 5: Form Builder

```markdown
## Project Overview
Create a simple form builder where users can drag-and-drop form fields to create custom forms and view submissions.

## Tech Stack
- Frontend: React
- Styling: TailwindCSS
- Drag & Drop: react-beautiful-dnd
- Backend: Express.js
- Database: MongoDB (flexible schema for form submissions)
- Validation: Zod

## Core Features
1. **Field Palette**: Sidebar with draggable field types (Text, Email, Number, Textarea, Checkbox, Select, Date)
2. **Form Canvas**: Drop zone where fields are arranged vertically, reorderable by drag
3. **Field Configuration**: Click field to open config panel (label, placeholder, required toggle, validation rules)
4. **Form Preview**: Toggle to preview mode showing form as end-user would see it
5. **Submissions View**: Table of all submissions for a form with export to CSV

## UI/UX Requirements
- Design: Clean builder interface similar to Typeform admin
- Color scheme: Light mode, blue primary (#2563EB), gray secondary
- Layout: Three-column (field palette 200px | canvas flex | config panel 300px), collapsible panels
- States: Clear visual feedback for drag operations, hover states, selected field highlight

## Data Model
- Form: id, name, fields[], created_at, updated_at
- Field: id, type, label, placeholder, required, validation{}, options[] (for select)
- Submission: id, form_id, data{}, submitted_at

## User Flows
1. **Create Form**: Click "New Form" → Name it → Drag fields to canvas → Configure each → Save
2. **Edit Field**: Click field on canvas → Config panel shows → Edit properties → Auto-saves
3. **Reorder Fields**: Drag field up/down within canvas → Order updates immediately
4. **View Submissions**: Click form → Submissions tab → See table → Click row for detail → Export CSV

## Constraints
- Max 20 fields per form
- Form name max 100 characters
- Validation runs client-side before submit

## Success Criteria
- [ ] All 7 field types can be added and configured
- [ ] Drag and drop is smooth and intuitive
- [ ] Form preview matches final render exactly
- [ ] Submissions are stored and retrievable
- [ ] CSV export includes all submission data
```

## Prompt Iteration Examples

### Starting Broad, Then Refining

**Initial prompt:**
```
Build a blog platform
```

**First refinement:**
```
Build a blog platform where users can write and publish articles. Include user authentication, markdown editor, and public article pages.
```

**Final optimized prompt:**
```
Build a minimalist blog platform for individual writers.

Tech Stack: Next.js 14, TailwindCSS, Supabase (auth + database), MDX for content

Core Features:
1. Authentication: Email/password signup and login via Supabase Auth
2. Dashboard: List of user's drafts and published posts, sorted by updated_at
3. Editor: Full-screen markdown editor with live preview side-by-side, auto-save every 30s
4. Publishing: Publish/unpublish toggle, URL slug auto-generated from title (editable)
5. Public Pages: /blog listing all published posts, /blog/[slug] for individual posts

UI: Clean, typography-focused design. White background, serif font for article text, sans-serif for UI.

Success Criteria:
- [ ] User can sign up, log in, and log out
- [ ] Markdown renders correctly including code blocks, images, and links
- [ ] Published articles are visible without authentication
- [ ] SEO meta tags work on article pages
```

### Debugging Prompt

**Bad:**
```
My app is broken, fix it
```

**Good:**
```
The login form throws "TypeError: Cannot read property 'email' of undefined" when I click Submit.

Context:
- Using React with useState for form
- handleSubmit function on line 24 of LoginForm.jsx
- Console shows the error points to line 28

Already tried:
- Checking that useState initializes with {email: '', password: ''}
- Adding console.log before the error line (values print correctly)

Expected: Form submits and calls /api/login
Actual: Error thrown, no API call made
```
