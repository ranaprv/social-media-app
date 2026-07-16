# Architecture — Social Media Manager

**Version:** 1.0.0
**Date:** 2026-07-16

---

## 1. Architectural Style

**Monolithic full-stack application** with clear frontend/backend separation.

- **Frontend:** Next.js 16 App Router (React 19) — SSR/SSG capable, deployed as container
- **Backend:** FastAPI (Python 3.12) — async REST API, deployed as container
- **Database:** PostgreSQL 16 — primary data store
- **Cache:** Redis 7 — session cache, rate limiting, background job queue
- **Orchestration:** Docker Compose — single-command deployment

### Design Principles
1. **Separation of Concerns** — Frontend and backend are independent deployable units
2. **API-First** — Backend exposes RESTful JSON APIs; frontend consumes them
3. **Graceful Degradation** — AI features work with or without API keys (mock fallbacks)
4. **Multi-Tenancy** — Workspace-based isolation with RBAC
5. **Defense in Depth** — Auth → RBAC → Rate Limiting → Audit Logging

---

## 2. System Context Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Social Media Manager                        │
│                                                          │
│  ┌─────────────┐    REST API    ┌─────────────┐         │
│  │   Frontend   │◄─────────────►│   Backend   │         │
│  │   (Next.js)  │               │  (FastAPI)  │         │
│  └─────────────┘               └──────┬──────┘         │
│                                        │                 │
│                              ┌─────────┼─────────┐      │
│                              │         │         │       │
│                        ┌─────▼──┐ ┌────▼───┐ ┌───▼───┐ │
│                        │Postgres│ │ Redis  │ │  S3   │ │
│                        └────────┘ └────────┘ └───────┘  │
└────────────────────────────────────────┬────────────────┘
                                         │
              ┌──────────────────────────┼──────────────────┐
              │                          │                   │
        ┌─────▼──────┐          ┌───────▼──────┐    ┌──────▼──────┐
        │  AI Providers │       │   Payments    │    │   Social    │
        │  (OpenAI,     │       │   (Stripe)    │    │   Platforms │
        │   Anthropic,  │       └──────────────┘    │  (LinkedIn, │
        │   Gemini)     │                           │   X, IG,    │
        └──────────────┘                           │   FB, YT)   │
                                                   └─────────────┘
```

---

## 3. Container Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Docker Compose Stack                           │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  frontend (Node.js 20-alpine)                             │   │
│  │  Port: 3001 → 3000                                        │   │
│  │  Build: Multi-stage (deps → build → runner)               │   │
│  │  User: nextjs (1001)                                      │   │
│  │  Env: NEXT_PUBLIC_API_URL=http://localhost:8001/api       │   │
│  └──────────────────────────┬───────────────────────────────┘   │
│                              │ HTTP                              │
│  ┌──────────────────────────▼───────────────────────────────┐   │
│  │  backend (Python 3.12-slim)                               │   │
│  │  Port: 8001 → 8000                                        │   │
│  │  Build: Multi-stage (builder → runner)                    │   │
│  │  User: appuser (1001)                                     │   │
│  │  Health: /api/health                                      │   │
│  │  Env: DATABASE_URL, REDIS_URL, API keys                   │   │
│  └─────┬────────────────────────┬───────────────────────────┘   │
│        │ SQL                    │ Redis                          │
│  ┌─────▼──────────┐    ┌───────▼──────────┐                    │
│  │  postgres        │    │  redis            │                    │
│  │  (16-alpine)     │    │  (7-alpine)       │                    │
│  │  Port: 5432      │    │  Port: 6380       │                    │
│  │  Volume: pg_data │    │  Volume: redis_data│                    │
│  │  Health: pg_     │    │  Health: ping      │                    │
│  │            ready │    │                    │                    │
│  └─────────────────┘    └──────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Component Architecture

### 4.1 Frontend Components

```
App (layout.tsx)
└── ThemeProvider
    └── Router
        ├── Auth Pages
        │   ├── Login
        │   └── Register
        └── Dashboard Pages (DashboardLayout)
            ├── Sidebar (navigation, collapse)
            ├── Header (search, theme toggle, user menu)
            └── Page Content
                ├── Dashboard (stats, recent posts, quick actions)
                ├── Content Studio (ideas, generate, tools, brand voice)
                ├── Analytics (charts, KPIs, heatmap, tables)
                ├── Recommendations (score, analysis, suggestions)
                ├── AI Assistant (image, video, voiceover, caption)
                ├── Billing (plans, usage, invoices, checkout)
                ├── Security (RBAC, audit, rate limit, OAuth, GDPR)
                ├── Calendar (events, campaigns, views)
                ├── Media (library, folders, search)
                ├── Repurpose (engine, input/output)
                └── Team (members, comments, reviews, notifications)
```

### 4.2 Backend Components

```
FastAPI App (main.py)
├── Middleware
│   └── CORS (localhost:3000, localhost:3001)
├── Routers (20 total)
│   ├── Auth (8 endpoints)
│   ├── Workspaces (11 endpoints)
│   ├── Posts (5 endpoints)
│   ├── Dashboard (1 endpoint)
│   ├── Connections (3 endpoints)
│   ├── AI Content (3 endpoints)
│   ├── AI Ideas (1 endpoint)
│   ├── AI Writing Tools (1 endpoint)
│   ├── AI Brand Voice (2 endpoints)
│   ├── AI Media (5 endpoints)
│   ├── AI Recommendations (2 endpoints)
│   ├── Analytics (5 endpoints)
│   ├── Billing (6 endpoints)
│   ├── Security (7 endpoints)
│   ├── Calendar (6 endpoints)
│   ├── Scheduler (6 endpoints)
│   ├── Team (10 endpoints)
│   ├── Media (3 endpoints)
│   └── Repurpose (1 endpoint)
├── Core
│   ├── Config (Pydantic Settings, 30+ env vars)
│   ├── Database (SQLAlchemy async engine, session factory)
│   └── Security (JWT, bcrypt, OAuth2, get_current_user)
├── Models (13 tables)
│   ├── User, Account, Session
│   ├── Workspace, WorkspaceMember
│   ├── Post, PostVersion
│   ├── PlatformConnection
│   ├── ContentCalendar
│   ├── AnalyticsMetric
│   ├── BrandVoice
│   ├── Asset
│   └── Activity
└── Schemas (30+ Pydantic models)
```

---

## 5. Data Architecture

### 5.1 Entity Relationships

```
User 1──N WorkspaceMember N──1 Workspace
User 1──N Post
User 1──N Activity
User 1──N Account
User 1──N Session

Workspace 1──N Post
Workspace 1──N PlatformConnection
Workspace 1──N ContentCalendar
Workspace 1──1 BrandVoice
Workspace 1──N Asset

Post 1──1 ContentCalendar
Post 1──N AnalyticsMetric
Post 1──N PostVersion
```

### 5.2 Data Flow

```
User Action (Frontend)
    │
    ▼
API Request (JSON + JWT)
    │
    ▼
Auth Middleware (verify JWT → load User)
    │
    ▼
RBAC Check (workspace membership + role → permission)
    │
    ▼
Business Logic (SQLAlchemy queries)
    │
    ▼
Database (PostgreSQL async queries)
    │
    ▼
Response (JSON)
    │
    ▼
Frontend State Update (Zustand)
    │
    ▼
UI Re-render (React)
```

---

## 6. Security Architecture

### 6.1 Authentication Flow

```
Register: email + password → bcrypt hash → store → 201
Login: email + password → verify hash → JWT (30min) → 200
Request: Bearer JWT → decode → load user → attach to request
```

### 6.2 Authorization Layers

```
Layer 1: JWT Validity (token not expired, signature valid)
Layer 2: User Exists (user_id in token matches DB record)
Layer 3: Workspace Membership (user is member of requested workspace)
Layer 4: Role Permission (user's role grants required permission)
```

### 6.3 Security Controls

| Control | Implementation |
|---------|---------------|
| Password Hashing | bcrypt (passlib, 12 rounds) |
| Token Signing | HS256 (python-jose) |
| Token Expiry | 30 minutes |
| CORS | localhost:3000, localhost:3001 |
| Rate Limiting | 100 req/60s per user (in-memory) |
| Input Validation | Pydantic schemas (all endpoints) |
| Audit Logging | Action, resource, user, timestamp, IP |
| API Key Encryption | AES-256-GCM (planned) |
| OAuth Token Storage | Encrypted at rest (planned) |
| GDPR | DPA, consent, erasure, portability |

---

## 7. AI Integration Architecture

### 7.1 Provider Selection

```
AI Request
    │
    ├──► provider_override from request body
    │       └── Present → Use specified provider
    │
    ├──► platform_provider_configs table (UI settings)
    │       └── Row exists for (workspace, platform) → Use configured provider
    │
    ├──► Check OPENAI_API_KEY
    │       ├── Present → Call OpenAI (GPT-4o / DALL-E / TTS-1)
    │       └── Absent → Skip
    │
    ├──► Check ANTHROPIC_API_KEY
    │       ├── Present → Call Anthropic (Claude)
    │       └── Absent → Skip
    │
    └──► All absent → Return placeholder/mock response
```

### 7.2 Autonomous AI Workflow

```
POST /content/trigger-workflow
    │
    ▼
ContentOrchestrator.run_workflow()
    ├── Stage 1: Research (context gathering)
    ├── Stage 2: Draft ──► PlatformWorkflowFactory.create(platform)
    │                       └──► ClaudeLinkedInGenerator / OpenAIXGenerator / GeminiInstagramGenerator
    ├── Stage 3: Visual Prompt Generation (via same generator)
    ├── Stage 4: Save to DB (ContentItem model)
    └── Stage 5: HITL Staging (pending_approval)

POST /content/approve-post/{post_id}
    └── pending_approval → scheduled

POST /analytics/ingest
    ├── Store raw metrics (PlatformAnalytics model)
    ├── Calculate Ps = w1*(eng/imp) + w2*(shares/imp) + w3*(clicks/imp)
    └── If Ps > 7.5 → mock embedding → MockVectorStore (RAG context)
```

**Provider Resolution (no hardcoded platform→provider mapping):**
1. `provider_override` from API request body (optional per-request)
2. `platform_provider_configs` table (set via UI settings page)
3. First available provider with a configured API key (fallback)

### 7.3 AI Feature Mapping

| Feature | Primary Provider | Model | Fallback |
|---------|-----------------|-------|----------|
| Content Generation | OpenAI | GPT-4o | Placeholder |
| Idea Generation | OpenAI | GPT-4o | Template-based |
| Writing Tools | OpenAI | GPT-4o | Placeholder |
| Recommendations | OpenAI | GPT-4o | Mock scores |
| Repurposing | OpenAI | GPT-4o | Template-based |
| Image Generation | OpenAI | DALL-E | Placeholder |
| Video Generation | External API | — | Placeholder |
| Voiceover (TTS) | OpenAI | TTS-1 | Placeholder |
| Caption Generation | OpenAI | GPT-4o | Template-based |
| Brand Voice Analysis | OpenAI | GPT-4o | Placeholder |

---

## 8. Deployment Architecture

### 8.1 Development

```
docker compose up --build
├── Frontend: http://localhost:3001 (hot reload)
├── Backend: http://localhost:8001 (hot reload)
├── PostgreSQL: localhost:5432
├── Redis: localhost:6380
└── API Docs: http://localhost:8001/api/docs
```

### 8.2 Production

```
docker compose -f docker-compose.yml up -d
├── All services with restart: unless-stopped
├── Memory limits per service
├── Health checks for PostgreSQL, Redis, Backend
├── Volume persistence for data
└── Environment variables from .env
```

### 8.3 Scaling Path

```
Current: Single-host Docker Compose
    │
    ├──► Horizontal: Docker Swarm / Kubernetes
    ├──► Database: Read replicas, connection pooling
    ├──► Cache: Redis Cluster
    ├──► Frontend: Vercel edge + CDN
    ├──► Backend: Multiple FastAPI instances + load balancer
    └──► Queue: Dedicated Celery workers
```

---

## 9. Error Handling Architecture

### Backend Error Responses

```json
// Validation Error (422)
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email",
      "type": "value_error.email"
    }
  ]
}

// Authentication Error (401)
{
  "detail": "Could not validate credentials"
}

// Authorization Error (403)
{
  "detail": "Only owners and admins can invite members"
}

// Not Found (404)
{
  "detail": "Workspace not found or access denied"
}

// Business Logic Error (400)
{
  "detail": "Email already registered"
}
```

### Frontend Error Handling

```
API Fetch Error → try/catch → fall back to mock data
AI Generation Error → catch → show placeholder response
Auth Error → redirect to /auth/login
404 → Next.js not-found page
```

---

## 10. Quality Attributes

| Attribute | Strategy | Current State |
|-----------|----------|---------------|
| **Performance** | Async I/O, connection pooling, Redis caching | FastAPI async, PostgreSQL async |
| **Scalability** | Stateless API, horizontal scaling ready | Docker Compose (single host) |
| **Security** | JWT + RBAC + rate limiting + audit | Implemented |
| **Availability** | Health checks, restart policies | Docker health checks |
| **Maintainability** | Clean separation, typed schemas | TypeScript + Pydantic |
| **Testability** | Dependency injection, mockable services | FastAPI DI (no tests yet) |
| **Observability** | Audit logs, health endpoints | Partially implemented |
| **Portability** | Docker containers, env-based config | Fully containerized |
