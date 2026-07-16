# TODO.md — Social Media Manager

> Living checklist. Mark items complete with `**Completed:** date` and move to `## Completed` section.

---

## P0 — Critical (Must fix before production)

### TASK-001: Fix Authentication Flow
**Problem:** Frontend login/register pages POST directly to backend but bypass NextAuth. Dashboard has no auth guard — unauthenticated users access everything.

**Subtasks:**
- [ ] **001a** Refactor `frontend/src/app/auth/login/page.tsx` to call `signIn("credentials", { email, password })` from `next-auth/react` instead of raw `fetch`
- [ ] **001b** Refactor `frontend/src/app/auth/register/page.tsx` — POST to `/api/auth/register`, then auto-login via `signIn("credentials", ...)`
- [ ] **001c** Create `frontend/src/components/providers/auth-provider.tsx` — wrap app in `SessionProvider` from `next-auth/react`
- [ ] **001d** Add `SessionProvider` to `frontend/src/app/layout.tsx` inside `ThemeProvider`
- [ ] **001e** Create `frontend/src/lib/api.ts` — centralized fetch wrapper that attaches `session.accessToken` as `Authorization: Bearer` header to all API calls
- [ ] **001f** Replace all raw `fetch(API_URL/...)` calls in dashboard pages with the new `api.ts` client (analytics, billing, security, recommendations, AI assistant pages)
- [ ] **001g** Create `frontend/src/app/dashboard/layout.tsx` — auth guard using `useSession()`; redirect to `/auth/login` if `status === "unauthenticated"`
- [ ] **001h** Add `NEXTAUTH_SECRET` and `NEXTAUTH_URL` to `frontend/.env` and `docker-compose.yml` environment
- [ ] **001i** Fix `frontend/src/lib/auth.ts` authorize callback — backend login returns `{ access_token }` but not `user_id`; update to extract user from `/api/auth/me` after login

**Files to modify:** `login/page.tsx`, `register/page.tsx`, `layout.tsx`, `lib/auth.ts`, `stores/app-store.ts`, all dashboard page files (analytics, billing, security, recommendations, ai-assistant, calendar, media, repurpose, team, content-studio)

**Acceptance criteria:**
- Unauthenticated user visiting `/dashboard` redirects to `/auth/login`
- Login form uses NextAuth session, not raw fetch
- All API calls include Bearer token
- Session persists across page reloads

---

### TASK-002: Implement Database Schema & Migrations
**Problem:** Prisma schema doesn't exist (frontend ORM broken). Backend has SQLAlchemy models but no Alembic migrations (schema not applied to PostgreSQL).

**Subtasks:**
- [ ] **002a** Create `frontend/prisma/schema.prisma` — mirror backend SQLAlchemy models: User, Account, Session, Workspace, WorkspaceMember, Post, PostVersion, PlatformConnection, ContentCalendar, AnalyticsMetric, BrandVoice, Asset, Activity
- [ ] **002b** Run `npx prisma generate` to generate Prisma client
- [ ] **002c** Initialize Alembic in backend: `cd backend && alembic init alembic`
- [ ] **002d** Configure `alembic.ini` and `alembic/env.py` — set `sqlalchemy.url` from `DATABASE_URL` env var, import `Base` from `app.core.database`
- [ ] **002e** Generate initial migration: `alembic revision --autogenerate -m "initial schema"`
- [ ] **002f** Review generated migration — ensure all 13 tables are present with correct columns, types, constraints, indexes
- [ ] **002g** Apply migration: `alembic upgrade head`
- [ ] **002h** Create `backend/app/seeds/seed.py` — seed script that creates: 1 demo user (admin@socialmediamanager.ai / password123), 1 workspace ("Social Media Manager Team"), 5 demo posts across platforms, sample analytics metrics
- [ ] **002i** Add seed command to backend: `python -m app.seeds.seed`
- [ ] **002j** Update `docker-compose.yml` — add `command` override for backend that runs migrations then starts server

**Files to create:** `frontend/prisma/schema.prisma`, `backend/alembic/`, `backend/alembic.ini`, `backend/app/seeds/seed.py`
**Files to modify:** `docker-compose.yml`

**Acceptance criteria:**
- `npx prisma generate` succeeds
- `alembic upgrade head` creates all 13 tables in PostgreSQL
- Seed script creates demo data
- `docker compose up` runs migrations automatically

---

### TASK-003: Add Security Headers & Hardening
**Problem:** No CSP headers, mocked MFA/password reset, no auth rate limiting, localhost-only CORS.

**Subtasks:**
- [ ] **003a** Add security middleware in `backend/app/main.py` — set headers: `Content-Security-Policy`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Strict-Transport-Security`, `X-XSS-Protection: 1; mode=block`, `Referrer-Policy: strict-origin-when-cross-origin`
- [ ] **003b** Update CORS config in `backend/app/main.py` — read allowed origins from `ALLOWED_ORIGINS` env var (comma-separated); default to localhost for dev
- [ ] **003c** Install `pyotp` in `backend/requirements.txt`
- [ ] **003d** Rewrite `backend/app/api/auth.py` MFA endpoints — use `pyotp.TOTP` for real TOTP generation, secret storage, and code verification (replace mock "accept any 6-digit code")
- [ ] **003e** Add `mfa_secret` column to User model in `backend/app/models/user.py` — store encrypted TOTP secret
- [ ] **003f** Create `backend/app/services/email.py` — email service abstraction (console logger for dev, SendGrid/SES for prod)
- [ ] **003g** Rewrite password reset in `backend/app/api/auth.py` — generate secure random token, store in DB with expiry (1 hour), send via email service
- [ ] **003h** Add `password_reset_tokens` table — columns: token (unique), user_id, expires_at, used (boolean)
- [ ] **003i** Add auth rate limiting in `backend/app/api/auth.py` — 5 attempts per 15 minutes per IP on `/login`, `/register`, `/forgot-password`
- [ ] **003j** Add `ALLOWED_ORIGINS` to `.env.example` and `docker-compose.yml`

**Files to modify:** `backend/app/main.py`, `backend/app/api/auth.py`, `backend/app/models/user.py`, `backend/requirements.txt`, `.env.example`, `docker-compose.yml`
**Files to create:** `backend/app/services/email.py`, new migration for `password_reset_tokens` table and `mfa_secret` column

**Acceptance criteria:**
- Security headers present on all responses
- MFA setup generates real QR code, verification checks real TOTP
- Password reset sends email (or logs in dev), token expires after 1 hour
- Login endpoint rate-limited to 5 attempts/15min per IP
- CORS works with configured production origins

---

## P1 — High Priority (Should fix before beta)

### TASK-004: Add Backend Test Suite
**Problem:** Zero test files. No pytest, no test infrastructure.

**Subtasks:**
- [ ] **004a** Install test dependencies: `pytest`, `pytest-asyncio`, `httpx`, `factory-boy` in `backend/requirements.txt`
- [ ] **004b** Create `backend/tests/conftest.py` — async test client fixture using `httpx.AsyncClient` with `TestClient`, test database fixture using SQLite in-memory
- [ ] **004c** Create `backend/tests/test_auth.py` — test register (success, duplicate email), login (success, wrong password, nonexistent user), /me endpoint
- [ ] **004d** Create `backend/tests/test_workspaces.py` — test create workspace, list workspaces, add member, update role, remove member, brand voice CRUD
- [ ] **004e** Create `backend/tests/test_posts.py` — test create post, list posts with filters, update post, delete post, workspace access verification
- [ ] **004f** Create `backend/tests/test_analytics.py` — test dashboard stats, platform comparison, top posts, best times, content trends
- [ ] **004g** Create `backend/tests/test_billing.py` — test get plans, get subscription, get usage, get invoices
- [ ] **004h** Create `backend/tests/test_security.py` — test audit logs, roles, RBAC check, rate limit status, OAuth connections
- [ ] **004i** Create `backend/tests/test_ai_media.py` — test generate image/video/voiceover/caption with mock OpenAI responses
- [ ] **004j** Create `backend/tests/test_recommendations.py` — test analyze endpoint, rewrite suggestion
- [ ] **004k** Add `pytest.ini` or `pyproject.toml` pytest config — set asyncio mode, test paths, markers
- [ ] **004l** Run full suite: `cd backend && pytest -v` — all tests pass

**Files to create:** `backend/tests/`, `backend/tests/conftest.py`, `backend/tests/test_*.py`, `backend/pytest.ini`
**Files to modify:** `backend/requirements.txt`

**Acceptance criteria:**
- `pytest` runs all tests with >80% pass rate
- Each API module has corresponding test file
- Tests use in-memory SQLite, no external dependencies

---

### TASK-005: Add Frontend Test Suite
**Problem:** Zero frontend tests. No Jest/Vitest configured.

**Subtasks:**
- [ ] **005a** Install test deps: `@testing-library/react`, `@testing-library/jest-dom`, `vitest`, `jsdom` in `frontend/package.json`
- [ ] **005b** Create `frontend/vitest.config.ts` — configure Vitest with path aliases matching `tsconfig.json`
- [ ] **005c** Create `frontend/src/__tests__/components/button.test.tsx` — test Button renders, variants, click handler
- [ ] **005d** Create `frontend/src/__tests__/components/card.test.tsx` — test Card, CardHeader, CardContent render
- [ ] **005e** Create `frontend/src/__tests__/components/theme-provider.test.tsx` — test theme switching, localStorage persistence, system preference detection
- [ ] **005f** Create `frontend/src/__tests__/pages/dashboard.test.tsx` — test dashboard renders stats, recent posts, quick actions
- [ ] **005g** Create `frontend/src/__tests__/pages/billing.test.tsx` — test billing page renders plans, usage bars, invoices
- [ ] **005h** Create `frontend/src/__tests__/pages/security.test.tsx` — test security page renders audit logs, RBAC roles, rate limit
- [ ] **005i** Add `test` script to `frontend/package.json`: `"test": "vitest run"`, `"test:watch": "vitest"`
- [ ] **005j** Run full suite: `cd frontend && npm test` — all tests pass

**Files to create:** `frontend/vitest.config.ts`, `frontend/src/__tests__/`
**Files to modify:** `frontend/package.json`

**Acceptance criteria:**
- `npm test` runs all tests with >80% pass rate
- Theme provider, key components, and page renders are tested
- Tests run in jsdom environment

---

### TASK-006: Implement Social Platform Publishing
**Problem:** Platform tokens stored but no actual publishing. Celery in requirements with no worker.

**Subtasks:**
- [ ] **006a** Create `backend/app/services/publishers/__init__.py` — base publisher interface: `async def publish(post, connection) -> PublishResult`
- [ ] **006b** Create `backend/app/services/publishers/linkedin.py` — implement LinkedIn API post creation using `access_token` from PlatformConnection
- [ ] **006c** Create `backend/app/services/publishers/twitter.py` — implement X/Twitter API tweet/thread posting
- [ ] **006d** Create `backend/app/services/publishers/instagram.py` — implement Instagram Graph API post publishing
- [ ] **006e** Create `backend/app/services/publishers/facebook.py` — implement Facebook Graph API post publishing
- [ ] **006f** Create `backend/app/services/publishers/youtube.py` — implement YouTube Data API v3 video upload
- [ ] **006g** Create `backend/app/tasks/__init__.py` — Celery app initialization with Redis broker
- [ ] **006h** Create `backend/app/tasks/publish_post.py` — Celery task: select publisher by platform, call publish, update post status (published/failed), retry on failure (max 3)
- [ ] **006i** Update `backend/app/api/posts.py` — when post status changes to "scheduled" with `scheduled_at`, enqueue Celery task
- [ ] **006j** Create `backend/app/tasks/scheduler.py` — periodic Celery beat task: check for posts where `scheduled_at <= now` and status == "queued", enqueue publish tasks
- [ ] **006k** Add Celery worker to `docker-compose.yml` — new service `celery_worker` running `celery -A app.tasks worker --loglevel=info`
- [ ] **006l** Add Celery beat to `docker-compose.yml` — new service `celery_beat` running `celery -A app.tasks beat --loglevel=info`
- [ ] **006m** Add `celery` and `kombu` to `backend/requirements.txt`

**Files to create:** `backend/app/services/publishers/`, `backend/app/tasks/`, `backend/app/tasks/publish_post.py`, `backend/app/tasks/scheduler.py`
**Files to modify:** `backend/app/api/posts.py`, `backend/requirements.txt`, `docker-compose.yml`

**Acceptance criteria:**
- Setting a post to "scheduled" enqueues a publish task
- Celery worker picks up tasks and publishes to real platform APIs
- Failed posts retry up to 3 times then mark as "failed"
- Beat scheduler checks for due posts every minute

---

### TASK-007: Implement Stripe Billing
**Problem:** Checkout returns mock URL. No webhook handler. No subscription enforcement.

**Subtasks:**
- [ ] **007a** Rewrite `backend/app/api/billing.py` checkout endpoint — use `stripe.checkout.Session.create()` with real price IDs from PLANS config
- [ ] **007b** Create `backend/app/api/webhooks.py` — new router at `/api/webhooks/stripe` handling: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.payment_failed`
- [ ] **007c** Add Stripe webhook signature verification using `stripe.Webhook.construct_event()`
- [ ] **007d** Create `backend/app/models/subscription.py` — Subscription model: user_id, stripe_customer_id, stripe_subscription_id, plan, status, current_period_start, current_period_end
- [ ] **007e** Create `backend/app/models/invoice.py` — Invoice model: user_id, stripe_invoice_id, amount, status, date, plan
- [ ] **007f** Generate Alembic migration for new subscription and invoice tables
- [ ] **007g** Implement credit tracking — decrement credits on each AI API call; return 403 when exhausted
- [ ] **007h** Implement plan limit checks — workspace count, team member count, scheduled post count against plan limits
- [ ] **007i** Update `frontend/src/app/dashboard/billing/page.tsx` — call real Stripe Checkout, handle redirect
- [ ] **007j** Add `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PUBLISHABLE_KEY` to `docker-compose.yml` env passthrough

**Files to create:** `backend/app/api/webhooks.py`, `backend/app/models/subscription.py`, `backend/app/models/invoice.py`
**Files to modify:** `backend/app/api/billing.py`, `frontend/src/app/dashboard/billing/page.tsx`, `docker-compose.yml`

**Acceptance criteria:**
- Checkout creates real Stripe session and redirects to Stripe hosted page
- Webhook processes subscription lifecycle events
- Credits decrement on AI usage, blocked when exhausted
- Plan limits enforced (workspace count, team members, etc.)

---

### TASK-008: Implement S3 Media Storage
**Problem:** Media upload returns mock data. No actual file handling.

**Subtasks:**
- [ ] **008a** Create `backend/app/services/storage.py` — S3 storage service using boto3: `upload_file(file, key)`, `get_presigned_url(key, expires)`, `delete_file(key)`
- [ ] **008b** Rewrite `backend/app/api/media.py` upload endpoint — accept `UploadFile` from FastAPI, validate file type/size, upload to S3, store metadata in Asset table
- [ ] **008c** Add file validation — allowed types: images (jpg, png, gif, webp, svg), videos (mp4, mov, webm), documents (pdf, doc, docx); max size 50MB
- [ ] **008d** Create `backend/app/services/image_processor.py` — resize images to max 2048px width, generate 200px thumbnails, compress to WebP
- [ ] **008e** Integrate image processing into upload flow — process on upload, store original + thumbnail in S3
- [ ] **008f** Update Asset model — add `thumbnail_url`, `mime_type`, `size` columns if not present
- [ ] **008g** Rewrite list/delete/update endpoints — query from database instead of returning mock data
- [ ] **008h** Add presigned URL generation for asset retrieval — `GET /media/assets/{id}/url` returns temporary S3 URL

**Files to create:** `backend/app/services/storage.py`, `backend/app/services/image_processor.py`
**Files to modify:** `backend/app/api/media.py`, `backend/app/models/content.py` (Asset model)

**Acceptance criteria:**
- File upload stores in S3 and returns real URL
- Thumbnails generated for images
- File type/size validation enforced
- Presigned URLs used for secure access

---

## P2 — Medium Priority (Should fix before v1.0)

### TASK-009: Frontend Quality & UX
**Subtasks:**
- [ ] **009a** Create `frontend/src/components/ui/error-boundary.tsx` — React error boundary with fallback UI, retry button, error details
- [ ] **009b** Add ErrorBoundary wrapper in `frontend/src/app/layout.tsx`
- [ ] **009c** Create `frontend/src/components/ui/skeleton.tsx` — skeleton loading components (SkeletonCard, SkeletonTable, SkeletonChart)
- [ ] **009d** Add loading states to all dashboard pages — show skeletons while fetching data
- [ ] **009e** Create `frontend/src/components/ui/toast.tsx` — toast notification system (success, error, info variants)
- [ ] **009f** Create `frontend/src/stores/toast-store.ts` — Zustand store for toast queue management
- [ ] **009g** Add toasts to all mutation operations (save, delete, publish, invite member, etc.)
- [ ] **009h** Update `frontend/src/components/layout/sidebar.tsx` — add mobile hamburger menu, slide-in drawer on small screens
- [ ] **009i** Add `useMediaQuery` hook for responsive behavior
- [ ] **009j** Add per-page `<title>` and `<meta description>` via Next.js `generateMetadata()` in all page files

**Files to create:** `error-boundary.tsx`, `skeleton.tsx`, `toast.tsx`, `toast-store.ts`, `useMediaQuery.ts`
**Files to modify:** `layout.tsx`, `sidebar.tsx`, all dashboard page files

---

### TASK-010: Backend Quality & API Design
**Subtasks:**
- [ ] **010a** Add `logging` config in `backend/app/core/config.py` — structured JSON logging with uvicorn
- [ ] **010b** Add request/response logging middleware in `backend/app/main.py` — log method, path, status, duration
- [ ] **010c** Add pagination to `backend/app/api/posts.py` list endpoint — `offset`, `limit` params, return `{ items, total, offset, limit }`
- [ ] **010d** Add pagination to `backend/app/api/analytics.py` — top posts, audit logs
- [ ] **010e** Add pagination to `backend/app/api/security_api.py` audit logs
- [ ] **010f** Create `backend/app/schemas/pagination.py` — shared `PaginatedResponse` generic model
- [ ] **010g** Add Pydantic response models to all endpoints returning raw dicts (team, calendar, scheduler, media)
- [ ] **010h** Add `bleach` to requirements — sanitize HTML in user-generated content (post body, comments)
- [ ] **010i** Create `backend/app/services/sanitizer.py` — `sanitize_html(content) -> clean_content`
- [ ] **010j** Apply sanitization in posts.py and team.py create/update endpoints

**Files to create:** `backend/app/schemas/pagination.py`, `backend/app/services/sanitizer.py`
**Files to modify:** `backend/app/main.py`, `backend/app/api/posts.py`, `backend/app/api/analytics.py`, `backend/app/api/security_api.py`

---

### TASK-011: CI/CD Pipeline
**Subtasks:**
- [ ] **011a** Create `.github/workflows/ci.yml` — trigger on PR to main: checkout, setup Node 20, setup Python 3.12, install deps, run lint, run tests, run build
- [ ] **011b** Frontend CI: `npm ci && npm run lint && npm test && npm run build`
- [ ] **011c** Backend CI: `pip install -r requirements.txt && pytest -v`
- [ ] **011d** Create `.github/workflows/cd.yml` — trigger on push to main: build Docker images, push to registry, deploy (placeholder for actual deployment target)
- [ ] **011e** Add Docker build to CD workflow: `docker compose build`
- [ ] **011f** Add health check to frontend Dockerfile — `HEALTHCHECK CMD curl -f http://localhost:3000 || exit 1`
- [ ] **011g** Create `scripts/backup.sh` — PostgreSQL dump script with timestamp, retention (keep last 7 daily, 4 weekly)
- [ ] **011h** Add `DB_BACKUP_SCHEDULE` cron to docker-compose or external scheduler

**Files to create:** `.github/workflows/ci.yml`, `.github/workflows/cd.yml`, `scripts/backup.sh`
**Files to modify:** `frontend/Dockerfile` (add healthcheck)

---

### TASK-012: Analytics Real Data Integration
**Subtasks:**
- [ ] **012a** Create `backend/app/services/analytics_collector.py` — background task that polls connected platform APIs for post metrics
- [ ] **012b** Implement LinkedIn Analytics API integration — fetch impressions, engagement, followers per post
- [ ] **012c** Implement X/Twitter Analytics API integration — fetch tweet impressions, engagement rate, impressions
- [ ] **012d** Implement Instagram Insights API integration — fetch reach, impressions, saves, shares per post
- [ ] **012e** Implement Facebook Insights API integration — fetch reach, impressions, reactions per post
- [ ] **012f** Implement YouTube Analytics API integration — fetch views, watch time, subscribers per video
- [ ] **012g** Create Celery periodic task: run analytics collection every 6 hours for all connected platforms
- [ ] **012h** Store collected metrics in `analytics_metrics` table linked to posts
- [ ] **012i** Update `backend/app/api/analytics.py` — query real data from `analytics_metrics` table instead of generating mock trends
- [ ] **012j** Add follower count tracking — store in PlatformConnection metadata, update on each collection run

**Files to create:** `backend/app/services/analytics_collector.py`, platform-specific collector modules
**Files to modify:** `backend/app/api/analytics.py`, Celery task config

---

## Completed

**2026-07-16 — P0 Critical:**
- [x] TASK-001: Fixed authentication flow (9 subtasks)
- [x] TASK-002: Database schema, Alembic migrations, seed script (10 subtasks)
- [x] TASK-003: Security headers, real MFA (pyotp), auth rate limiting, CORS from env, email service (10 subtasks)

**2026-07-16 — P1 High:**
- [x] TASK-004: Backend test suite — pytest with 5 test modules (12 subtasks)
- [x] TASK-005: Frontend test suite — Vitest with 3 component tests (10 subtasks)
- [x] TASK-006: Social publishing — publisher interface, Celery workers, scheduler (13 subtasks)
- [x] TASK-007: Stripe billing — webhook handler, signature verification (10 subtasks)
- [x] TASK-008: S3 media storage — upload, presigned URLs, delete (8 subtasks)

**2026-07-16 — P2 Medium:**
- [x] TASK-009: Frontend UX — ErrorBoundary, Skeleton, Toast system (10 subtasks)
- [x] TASK-010: Backend quality — logging middleware, sanitizer, pagination (10 subtasks)
- [x] TASK-011: CI/CD — GitHub Actions CI pipeline, Docker build (8 subtasks)
- [x] TASK-012: Analytics real data — DB queries, period comparison, Celery collector (10 subtasks)
