# High-Level Design — ContentPilot AI

**Version:** 1.0.0
**Date:** 2026-07-16

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Browser     │  │   Mobile     │  │   API        │          │
│  │   (Next.js)   │  │   (PWA)      │  │   Client     │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         └──────────────────┼──────────────────┘                  │
│                            │                                     │
│                    ┌───────▼───────┐                             │
│                    │   CDN / Edge   │                             │
│                    │   (Vercel)     │                             │
│                    └───────┬───────┘                             │
└────────────────────────────┼─────────────────────────────────────┘
                             │
┌────────────────────────────┼─────────────────────────────────────┐
│                        API LAYER                                  │
│                    ┌───────▼───────┐                             │
│                    │  FastAPI       │                             │
│                    │  (Python 3.12) │                             │
│                    └───────┬───────┘                             │
│                            │                                     │
│         ┌──────────────────┼──────────────────┐                  │
│         │                  │                  │                   │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐            │
│  │  Auth        │  │  Business   │  │  AI          │            │
│  │  Service     │  │  Services   │  │  Services    │            │
│  │              │  │             │  │              │            │
│  │  - JWT       │  │  - Posts    │  │  - Content   │            │
│  │  - OAuth     │  │  - Calendar │  │  - Ideas     │            │
│  │  - MFA       │  │  - Team     │  │  - Media     │            │
│  │  - RBAC      │  │  - Media    │  │  - Recs      │            │
│  │  - Rate Limit│  │  - Billing  │  │  - Repurpose │            │
│  │  - Audit Log │  │  - Security │  │  - Writing   │            │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
│         └──────────────────┼──────────────────┘                  │
└────────────────────────────┼─────────────────────────────────────┘
                             │
┌────────────────────────────┼─────────────────────────────────────┐
│                     DATA LAYER                                    │
│         ┌──────────────────┼──────────────────┐                  │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐            │
│  │  PostgreSQL  │  │  Redis      │  │  AWS S3     │            │
│  │  (Primary)   │  │  (Cache/    │  │  (Storage)  │            │
│  │              │  │   Queue)    │  │              │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   EXTERNAL SERVICES                               │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  OpenAI      │  │  Anthropic   │  │  Google     │            │
│  │  API         │  │  API         │  │  Gemini     │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  Stripe      │  │  Social      │  │  OAuth      │            │
│  │  Billing     │  │  Platforms   │  │  Providers  │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Overview

### 2.1 Frontend (Next.js 16 + React 19)

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | Next.js 16 (App Router) | SSR/SSG, routing, API routes |
| UI Library | React 19 | Component rendering |
| Styling | Tailwind CSS v4 | Utility-first CSS with CSS variables |
| Charts | Recharts | Analytics visualizations |
| State | Zustand | Client-side state management |
| Icons | Lucide React | Icon system |
| UI Primitives | Radix UI | Accessible dropdowns, dialogs, tabs |
| Auth | NextAuth v4 | Next.js authentication |
| ORM | Prisma | Database access (frontend) |

### 2.2 Backend (FastAPI + Python)

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | FastAPI 0.115 | Async REST API |
| ORM | SQLAlchemy 2.0 (async) | Database access |
| Auth | python-jose + passlib | JWT + bcrypt |
| AI | OpenAI SDK, Anthropic SDK, Google GenAI | Content generation |
| Payments | Stripe SDK | Billing |
| Queue | Celery + Redis | Background jobs |
| Storage | boto3 | AWS S3 file storage |
| HTTP | httpx | External API calls |

### 2.3 Data Stores

| Store | Technology | Purpose |
|-------|------------|---------|
| Primary DB | PostgreSQL 16 | User, workspace, post, analytics data |
| Cache | Redis 7 | Session cache, rate limiting, job queue |
| Object Storage | AWS S3 | Media files, generated assets |

---

## 3. Request Flow

```
User Request
    │
    ▼
[Next.js Frontend]
    │
    ├──► Static assets (CDN)
    │
    └──► API call ──► [FastAPI Backend]
                          │
                          ├──► Auth middleware (JWT verify)
                          │       │
                          │       ├──► Rate limiter check
                          │       ├──► RBAC permission check
                          │       └──► Audit log write
                          │
                          ├──► Business logic
                          │       │
                          │       ├──► SQLAlchemy query ──► PostgreSQL
                          │       ├──► Cache check ──► Redis
                          │       └──► Background task ──► Celery
                          │
                          ├──► AI services
                          │       │
                          │       ├──► OpenAI API
                          │       ├──► Anthropic API
                          │       └──► Google Gemini API
                          │
                          └──► External services
                                  │
                                  ├──► Stripe API
                                  ├──► Social platform APIs
                                  └──► AWS S3
```

---

## 4. Authentication Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Login Form  │────►│  POST /api   │────►│  Validate    │
│  (Frontend)  │     │  auth/login  │     │  Credentials │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                           ┌──────▼───────┐
                                           │  Generate     │
                                           │  JWT Token    │
                                           │  (30min TTL)  │
                                           └──────┬───────┘
                                                  │
┌──────────────┐     ┌──────────────┐     ┌──────▼───────┐
│  Auth Header │────►│  OAuth2      │────►│  Decode &    │
│  Bearer JWT  │     │  Bearer      │     │  Verify      │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                           ┌──────▼───────┐
                                           │  Load User    │
                                           │  from DB      │
                                           └──────┬───────┘
                                                  │
                                           ┌──────▼───────┐
                                           │  Attach to    │
                                           │  Request      │
                                           └──────────────┘
```

---

## 5. RBAC Model

```
Owner (Level 4)
  └── Permissions: ["*"] (all)
      │
      ├── Admin (Level 3)
      │     └── Permissions: [manage_team, manage_billing, manage_content,
      │                       manage_settings, view_analytics]
      │
      ├── Editor (Level 2)
      │     └── Permissions: [create_content, edit_content, schedule_content,
      │                       view_analytics, comment]
      │
      └── Viewer (Level 1)
            └── Permissions: [view_content, view_analytics]
```

---

## 6. Database Schema (High-Level ERD)

```
┌─────────┐     ┌──────────────┐     ┌──────────┐
│  Users   │────<│  Workspace   │>────│ Workspaces│
│          │     │  Members     │     │           │
└────┬─────┘     └──────────────┘     └─────┬─────┘
     │                                      │
     ├────── Posts ──────────────────────────┤
     │         │                            │
     │    ┌────┴────┐                 ┌─────┴─────┐
     │    │Analytics│                 │ Platform   │
     │    │ Metrics │                 │ Connections│
     │    └─────────┘                 └───────────┘
     │
     ├────── Activities
     │
     ├────── Accounts (OAuth)
     │
     └────── Sessions

Posts ──┬── PostVersions
        ├── ContentCalendar
        └── AnalyticsMetric

Workspaces ──┬── BrandVoice
             ├── Assets
             └── WorkspaceMember
```

---

## 7. Deployment Architecture

```
┌─────────────────────────────────────────────┐
│              Docker Compose                  │
│                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
│  │ Frontend │  │ Backend │  │ Postgres│    │
│  │ :3001    │──│ :8001   │──│ :5432   │    │
│  └─────────┘  └─────────┘  └─────────┘    │
│                     │                       │
│                ┌────▼────┐                  │
│                │  Redis  │                  │
│                │  :6380  │                  │
│                └─────────┘                  │
└─────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  External APIs   │
│  - OpenAI        │
│  - Stripe        │
│  - Social APIs   │
│  - AWS S3        │
└─────────────────┘
```

---

## 8. Security Architecture

| Layer | Mechanism |
|-------|-----------|
| Transport | HTTPS / TLS 1.3 |
| Authentication | JWT Bearer tokens (30-min expiry) |
| Authorization | RBAC (4 roles, permission-based) |
| Rate Limiting | 100 req/60s per user (in-memory, Redis-backed planned) |
| Password Storage | bcrypt (12 rounds) |
| API Key Storage | AES-256-GCM encryption |
| OAuth Tokens | Encrypted at rest, key rotation enabled |
| Audit | Full action logging with user, resource, timestamp, IP |
| GDPR | DPA, consent, right to erasure, data portability |
| CORS | localhost:3000, localhost:3001 |
| Input Validation | Pydantic schemas on all endpoints |

---

## 9. Scalability Considerations

| Component | Current | Scale Path |
|-----------|---------|------------|
| Frontend | Single Next.js instance | Vercel edge functions, CDN |
| Backend | Single FastAPI process | Horizontal scaling, load balancer |
| Database | Single PostgreSQL | Read replicas, connection pooling |
| Cache | Single Redis instance | Redis Cluster |
| AI | Synchronous API calls | Celery task queue, async processing |
| Storage | Local/placeholder | AWS S3 with CDN |
| Queue | In-memory rate limiter | Redis-backed rate limiting |

---

## 10. Environment Configuration

| Variable | Purpose | Required |
|----------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection | Yes |
| `REDIS_URL` | Redis connection | Yes |
| `SECRET_KEY` | JWT signing key | Yes |
| `OPENAI_API_KEY` | OpenAI API access | For AI features |
| `ANTHROPIC_API_KEY` | Anthropic API access | Optional |
| `GOOGLE_AI_API_KEY` | Google Gemini access | Optional |
| `STRIPE_SECRET_KEY` | Stripe billing | For billing |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhooks | For billing |
| `AWS_ACCESS_KEY_ID` | S3 storage | For media |
| `AWS_SECRET_ACCESS_KEY` | S3 storage | For media |
| `AWS_BUCKET_NAME` | S3 bucket | For media |
| Social platform keys | OAuth connections | For publishing |
