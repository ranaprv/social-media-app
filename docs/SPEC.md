# Specification — Social Media Manager

**Version:** 1.0.0
**Date:** 2026-07-16

---

## 1. Technology Stack

### Frontend
| Component | Version | Purpose |
|-----------|---------|---------|
| Next.js | 16.2.10 | React framework (App Router) |
| React | 19.2.4 | UI library |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 4.x | Utility-first CSS |
| Recharts | 3.9.2 | Chart components |
| Zustand | 5.0.14 | State management |
| Lucide React | 1.24.0 | Icons |
| Radix UI | Various | Accessible primitives |
| class-variance-authority | 0.7.1 | Component variants |
| clsx | 2.1.1 | Conditional classes |
| tailwind-merge | 3.6.0 | Tailwind class merging |
| date-fns | 4.4.0 | Date utilities |
| NextAuth | 4.24.14 | Authentication |
| Prisma | 7.8.0 | ORM (frontend) |

### Backend
| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.12 | Runtime |
| FastAPI | 0.115.0 | API framework |
| Uvicorn | 0.30.0 | ASGI server |
| SQLAlchemy | 2.0.35 | ORM (async) |
| asyncpg | 0.29.0 | PostgreSQL driver |
| Alembic | 1.13.0 | Database migrations |
| Pydantic | 2.9.0 | Data validation |
| pydantic-settings | 2.5.0 | Environment config |
| python-jose | 3.3.0 | JWT tokens |
| passlib | 1.7.4 | Password hashing |
| OpenAI SDK | 1.50.0 | AI content generation |
| Anthropic SDK | 0.34.0 | Alternative AI |
| Google GenAI | 1.0.0 | Alternative AI |
| Stripe SDK | ≥7.0.0 | Payment processing |
| Celery | 5.4.0 | Task queue |
| Redis | 5.1.0 | Cache/queue backend |
| boto3 | 1.35.0 | AWS S3 storage |
| httpx | 0.27.0 | HTTP client |
| tenacity | 9.0.0 | Retry logic |

### Infrastructure
| Component | Version | Purpose |
|-----------|---------|---------|
| PostgreSQL | 16-alpine | Primary database |
| Redis | 7-alpine | Cache, queue, rate limiting |
| Docker | Compose v3.8 | Container orchestration |
| Node.js | 20-alpine | Frontend runtime |

---

## 2. API Contract Specifications

### Authentication
```
POST /api/auth/register
  Body: { email: string, password: string, name?: string }
  Response: 201 { id, email, name, image, created_at }

POST /api/auth/login
  Body: { email: string, password: string }
  Response: 200 { access_token: string, token_type: "bearer" }

GET /api/auth/me
  Headers: Authorization: Bearer <token>
  Response: 200 { id, email, name, image, created_at }
```

### Posts
```
POST /api/posts/{workspace_id}
  Headers: Authorization: Bearer <token>
  Body: { title?, content, media_urls?, platform, status?, scheduled_at?, metadata? }
  Response: 201 { id, workspace_id, author_id, title, content, ... }

GET /api/posts/{workspace_id}?platform=&status=
  Response: 200 [PostResponse, ...]

PUT /api/posts/{workspace_id}/{post_id}
  Body: { title?, content?, platform?, status?, ... }
  Response: 200 PostResponse

DELETE /api/posts/{workspace_id}/{post_id}
  Response: 204 No Content
```

### Analytics
```
GET /api/analytics/dashboard?period=30d
  Response: 200 {
    period: string,
    summary: { reach: {value, change, trend}, ... },
    reachTrend: [{date, value}, ...],
    impressionsTrend: [{date, value}, ...],
    engagementTrend: [{date, value}, ...]
  }

GET /api/analytics/platform-comparison?period=30d
  Response: 200 { platforms: [{ platform, name, color, followers, reach, ... }] }

GET /api/analytics/top-posts?period=30d&limit=10
  Response: 200 { posts: [{ id, title, platform, impressions, ... }] }

GET /api/analytics/best-times
  Response: 200 { bestTimes: [...], heatmap: [...] }

GET /api/analytics/content-trends?period=30d
  Response: 200 { engagementTrend, reachTrend, followerGrowth, topContentTypes, platformPerformance }
```

### Billing
```
GET /api/billing/plans
  Response: 200 { plans: [{ id, name, price, features, limits, ... }] }

GET /api/billing/subscription
  Response: 200 { plan, status, current_period_start, current_period_end, payment_method }

GET /api/billing/usage
  Response: 200 { credits: {used, limit}, workspaces: {used, limit}, ... }

GET /api/billing/invoices
  Response: 200 { invoices: [{ id, date, amount, status, plan, description }] }

POST /api/billing/checkout
  Body: { plan: string }
  Response: 200 { checkout_url, session_id, plan, amount }

POST /api/billing/cancel
  Response: 200 { status, cancels_at }
```

### Security
```
GET /api/security/audit-logs?action=&resource=&limit=50
  Response: 200 { logs: [{ id, user_id, action, resource, details, timestamp, ip_address }], total }

GET /api/security/roles
  Response: 200 { roles: { owner: {level, permissions}, ... } }

GET /api/security/rate-limit/status
  Response: 200 { remaining, limit, window_seconds, reset_at }

GET /api/security/oauth/connections
  Response: 200 { connections: [{ provider, connected, username, scopes }] }

GET /api/security/encryption/status
  Response: 200 { api_keys_encrypted, encryption_algorithm, key_rotation_enabled }

GET /api/security/gdpr/status
  Response: 200 { data_processing_agreement, consent_recorded, right_to_erasure, ... }
```

### AI Endpoints
```
POST /api/ai/generate
  Body: { platform, content_type, topic, tone?, keywords?, length? }
  Response: 200 { content, hashtags, suggestions, engagement_score }

POST /api/ai/media/generate-image
  Body: { asset_type, prompt, style, brand_colors?, text_overlay? }
  Response: 200 { id, status, url, dimensions, ... }

POST /api/ai/media/generate-video
  Body: { asset_type, prompt, duration, style }
  Response: 200 { id, status, url, duration, ... }

POST /api/ai/media/generate-voiceover
  Body: { text, voice, speed }
  Response: 200 { id, status, url, voice, speed, ... }

POST /api/ai/media/generate-caption
  Body: { platform, topic, tone, include_emojis, include_hashtags }
  Response: 200 { caption, hashtags, character_count, platform_optimized }

GET /api/ai/recommendations/analyze
  Response: 200 { overallScore, recommendations[], contentAnalysis }

POST /api/ai/repurpose/generate
  Body: { input_type, input_content, input_url?, output_types[], tone? }
  Response: 200 { results: [{ id, output_type, content, hashtags, platform }], summary }
```

---

## 3. Database Schema Specification

### Tables (13 total)
1. `users` — User accounts
2. `accounts` — OAuth provider links
3. `sessions` — Active sessions
4. `workspaces` — Multi-tenant workspaces
5. `workspace_members` — Workspace membership with roles
6. `posts` — Content posts
7. `post_versions` — Post edit history
8. `platform_connections` — Social platform OAuth tokens
9. `content_calendars` — Scheduled post dates
10. `analytics_metrics` — Post performance data
11. `brand_voices` — Per-workspace brand voice config
12. `assets` — Media library files
13. `activities` — User activity audit trail

### Indexes
- `users.email` (unique)
- `workspaces.slug` (unique)
- `posts.workspace_id` (foreign key)
- `posts.platform` (filter)
- `posts.status` (filter)
- `analytics_metrics.post_id` (foreign key)
- `workspace_members.workspace_id + user_id` (composite)

---

## 4. Configuration Specification

### Environment Variables
```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/socialmediamanager

# Redis
REDIS_URL=redis://localhost:6379/0

# Auth
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Providers
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_AI_API_KEY=

# Social Platforms
LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=
TWITTER_CLIENT_ID=
TWITTER_CLIENT_SECRET=
INSTAGRAM_CLIENT_ID=
INSTAGRAM_CLIENT_SECRET=
FACEBOOK_APP_ID=
FACEBOOK_APP_SECRET=
YOUTUBE_CLIENT_ID=
YOUTUBE_CLIENT_SECRET=

# Billing
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PUBLISHABLE_KEY=

# Storage
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_BUCKET_NAME=
AWS_REGION=us-east-1

# OAuth
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
```

### CSS Variables (Light Mode)
```css
:root {
  --background: #ffffff;
  --foreground: #0f172a;
  --primary: #3b82f6;
  --secondary: #8b5cf6;
  --accent: #06b6d4;
  --muted: #f1f5f9;
  --card: #ffffff;
  --border: #e2e8f0;
  --destructive: #ef4444;
  --success: #22c55e;
  --warning: #f59e0b;
}
```

### CSS Variables (Dark Mode)
```css
.dark {
  --background: #0f172a;
  --foreground: #f8fafc;
  --muted: #1e293b;
  --card: #1e293b;
  --border: #334155;
}
```

---

## 5. Subscription Plan Specification

| Feature | Free | Pro ($29) | Business ($99) | Enterprise ($299) |
|---------|------|-----------|----------------|-------------------|
| AI Credits/month | 50 | 500 | 2,000 | Unlimited |
| Platform Connections | 3 | 5 | 5 | Unlimited |
| Workspaces | 1 | 5 | Unlimited | Unlimited |
| Team Members | 1 | 5 | 20 | Unlimited |
| Media Storage | 100 MB | 5 GB | 50 GB | Unlimited |
| Scheduled Posts | 10 | 100 | Unlimited | Unlimited |
| Analytics | Basic | Advanced | Full Suite | Enterprise |
| Brand Voice | No | Yes | Yes | Yes |
| Content Calendar | No | Yes | Yes | Yes |
| AI Repurposing | No | Yes | Yes | Yes |
| Team Collaboration | No | No | Yes | Yes |
| Media Library | No | No | Yes | Yes |
| Custom Integrations | No | No | Yes | Yes |
| SSO/SAML | No | No | No | Yes |
| SLA | No | No | No | Yes |
| Custom AI Models | No | No | No | Yes |
| API Access | No | No | No | Yes |
| Support | Email | Priority | Dedicated | Account Manager |

---

## 6. RBAC Permission Matrix

| Permission | Owner | Admin | Editor | Viewer |
|------------|-------|-------|--------|--------|
| `*` (all) | ✅ | — | — | — |
| `manage_team` | ✅ | ✅ | — | — |
| `manage_billing` | ✅ | ✅ | — | — |
| `manage_content` | ✅ | ✅ | — | — |
| `manage_settings` | ✅ | ✅ | — | — |
| `create_content` | ✅ | ✅ | ✅ | — |
| `edit_content` | ✅ | ✅ | ✅ | — |
| `schedule_content` | ✅ | ✅ | ✅ | — |
| `comment` | ✅ | ✅ | ✅ | — |
| `view_analytics` | ✅ | ✅ | ✅ | ✅ |
| `view_content` | ✅ | ✅ | ✅ | ✅ |

---

## 7. Rate Limiting Specification

| Parameter | Value |
|-----------|-------|
| Window | 60 seconds |
| Max Requests | 100 per window |
| Storage | In-memory (dict), Redis planned |
| Key | User ID (from JWT) |
| Response Headers | X-RateLimit-Remaining, X-RateLimit-Limit |
| Exceeded Response | 429 Too Many Requests |

---

## 8. Build & Deployment Specification

### Frontend Build
```bash
npm ci                    # Install dependencies
npm run build             # Next.js production build
npm start                 # Start production server (port 3000)
```

### Backend Build
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker Compose
```bash
docker compose up --build          # Development
docker compose up -d               # Production (detached)
docker compose down                # Stop all services
docker compose logs -f backend     # Stream backend logs
```

### Port Mapping
| Service | Internal | External |
|---------|----------|----------|
| Frontend | 3000 | 3001 |
| Backend | 8000 | 8001 |
| PostgreSQL | 5432 | 5432 |
| Redis | 6379 | 6380 |
