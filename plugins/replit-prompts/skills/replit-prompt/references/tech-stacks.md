# Recommended Tech Stacks for Replit

Pre-configured tech stack combinations optimized for Replit Agent.

## Full-Stack Web Applications

### Stack 1: Modern React (Recommended for Most Projects)

```
Frontend: React 18 + TypeScript + Vite
Styling: TailwindCSS + shadcn/ui
Backend: Node.js + Express
Database: PostgreSQL (via Supabase or Neon)
Auth: Clerk or Supabase Auth
State: React Query (server), Zustand (client)
```

**Best for:** Dashboards, SaaS apps, admin panels, data-heavy applications

**Prompt snippet:**
```
Tech Stack:
- Frontend: React 18 with TypeScript, Vite for bundling
- Styling: TailwindCSS with shadcn/ui component library
- Backend: Express.js REST API
- Database: PostgreSQL with Prisma ORM
- Authentication: Clerk
```

---

### Stack 2: Next.js Full-Stack

```
Framework: Next.js 14 (App Router)
Styling: TailwindCSS
Database: Supabase or PlanetScale
Auth: NextAuth.js or Supabase Auth
State: React Query + Context
Deployment: Vercel (from Replit)
```

**Best for:** SEO-critical apps, marketing sites, blogs, e-commerce

**Prompt snippet:**
```
Tech Stack:
- Framework: Next.js 14 with App Router and TypeScript
- Styling: TailwindCSS
- Database: Supabase (PostgreSQL + Auth + Storage)
- API: Next.js API routes with server actions
```

---

### Stack 3: Python Backend

```
Backend: Python + FastAPI
Frontend: React or plain HTML/CSS/JS
Database: PostgreSQL or SQLite
ORM: SQLAlchemy or Tortoise ORM
Auth: JWT tokens
```

**Best for:** ML/AI integrations, data processing, Python-heavy logic

**Prompt snippet:**
```
Tech Stack:
- Backend: Python 3.11 with FastAPI
- Frontend: React with Vite (or Jinja2 templates for simple UI)
- Database: PostgreSQL with SQLAlchemy
- Authentication: JWT with python-jose
```

---

### Stack 4: Lightweight/MVP

```
Framework: Flask or Express
Frontend: HTMX + TailwindCSS (no build step)
Database: SQLite
Templates: Jinja2 or EJS
```

**Best for:** Quick prototypes, internal tools, simple CRUD apps

**Prompt snippet:**
```
Tech Stack:
- Backend: Flask with Jinja2 templates
- Styling: TailwindCSS via CDN (no build step)
- Interactivity: HTMX for dynamic updates without JavaScript
- Database: SQLite (single file, no setup)
```

---

## Mobile-First / PWA

### Stack 5: React Native Web

```
Framework: React Native + Expo
Web: React Native Web for browser
Styling: NativeWind (Tailwind for RN)
Backend: Supabase or Firebase
```

**Best for:** Apps that need web + mobile from same codebase

**Prompt snippet:**
```
Tech Stack:
- Framework: React Native with Expo (SDK 50+)
- Web support: React Native Web for browser deployment
- Styling: NativeWind (TailwindCSS for React Native)
- Backend: Supabase for auth, database, and storage
```

---

## Real-Time Applications

### Stack 6: Real-Time Collaboration

```
Frontend: React
Backend: Node.js + Socket.io
Database: PostgreSQL + Redis (for pub/sub)
State: Zustand with socket sync
```

**Best for:** Chat apps, collaborative editors, live dashboards

**Prompt snippet:**
```
Tech Stack:
- Frontend: React with TypeScript
- Backend: Express.js with Socket.io for WebSocket connections
- Database: PostgreSQL for persistence, Redis for pub/sub
- Real-time sync: Socket.io rooms for multi-user collaboration
```

---

## AI/ML Applications

### Stack 7: AI-Powered App

```
Backend: Python + FastAPI
AI: OpenAI API or Anthropic Claude API
Frontend: React or Streamlit
Database: PostgreSQL + pgvector (for embeddings)
```

**Best for:** Chatbots, RAG apps, AI assistants, content generation

**Prompt snippet:**
```
Tech Stack:
- Backend: Python FastAPI
- AI: OpenAI API (GPT-4) for generation, text-embedding-3-small for embeddings
- Vector DB: PostgreSQL with pgvector extension
- Frontend: React with streaming response handling
- Note: User must provide OPENAI_API_KEY in Replit Secrets
```

---

## Database Selection Guide

| Use Case | Recommended | Notes |
|----------|-------------|-------|
| General purpose | PostgreSQL | Most versatile, use Supabase/Neon for managed |
| Quick prototype | SQLite | Zero setup, single file, no server needed |
| Document-heavy | MongoDB | Flexible schema, use MongoDB Atlas |
| Real-time sync | Firebase Firestore | Built-in real-time listeners |
| Key-value/Cache | Redis | Use for sessions, rate limiting, pub/sub |
| Vector search | PostgreSQL + pgvector | For AI/embeddings applications |

---

## Authentication Options

| Provider | Best For | Complexity |
|----------|----------|------------|
| Supabase Auth | Full-stack Supabase projects | Low |
| Clerk | Beautiful UI, social logins | Low |
| NextAuth.js | Next.js projects, flexible | Medium |
| Firebase Auth | Mobile-first, Google ecosystem | Low |
| Custom JWT | Full control, learning | High |

**Prompt snippet for auth:**
```
Authentication: Clerk (handles signup, login, password reset, social auth)
- Protected routes redirect to /sign-in
- User data available via useUser() hook
- Session tokens automatically attached to API requests
```

---

## Styling Framework Comparison

| Framework | Pros | Cons | Best For |
|-----------|------|------|----------|
| TailwindCSS | Utility-first, fast | Verbose HTML | Any project |
| shadcn/ui | Pre-built components | Tailwind required | Dashboards, SaaS |
| Chakra UI | Good defaults, accessible | Larger bundle | Quick prototypes |
| Material UI | Google design, comprehensive | Opinionated, heavy | Enterprise apps |
| Vanilla CSS | Full control | Time consuming | Learning, small projects |

---

## Replit-Specific Considerations

### Environment Variables
```
Always mention that sensitive keys should be stored in Replit Secrets:
- DATABASE_URL
- API keys (OPENAI_API_KEY, STRIPE_KEY, etc.)
- Auth secrets

Prompt snippet:
"Store all API keys in Replit Secrets (Environment Variables).
Access via process.env.VARIABLE_NAME in Node.js or os.environ in Python."
```

### Database Connections
```
For persistent databases, use external services:
- Supabase (PostgreSQL) - Free tier available
- PlanetScale (MySQL) - Free tier available
- MongoDB Atlas - Free tier available
- Neon (PostgreSQL) - Free tier available

SQLite works for prototypes but data may not persist across Repl restarts
on free tier.
```

### Deployment
```
Replit offers:
- Always-on Repls (paid) - Keep app running
- Deployments - Production hosting with custom domains
- Autoscaling - For high-traffic apps

For MVP/testing, regular Repl is sufficient.
```
