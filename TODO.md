# TODO.md — ContentPilot AI

> Living checklist. Mark items complete with `**Completed:** date` and move to `## Completed` section.

---

## P0 — Critical (Must fix before production)

### Authentication & Authorization
- [ ] **Connect login/register forms to NextAuth** — Frontend auth pages exist but don't use NextAuth session; they post to backend directly. Wire up NextAuth signIn/signUp properly.
- [ ] **Implement OAuth login flow** — Google and GitHub providers configured in NextAuth but no callback handling or account linking to backend users.
- [ ] **Add auth middleware to frontend** — Dashboard pages have no auth guard; unauthenticated users can access all routes directly.
- [ ] **Implement refresh token flow** — JWT expires in 30 min with no refresh mechanism; users get logged out silently.

### Database
- [ ] **Create Prisma schema** — `prisma.config.ts` references `prisma/schema.prisma` which doesn't exist. Frontend ORM is non-functional.
- [ ] **Generate Alembic migrations** — Backend has SQLAlchemy models but no migration files; schema isn't applied to PostgreSQL.
- [ ] **Add database seeding** — No seed script for development data (demo users, workspaces, posts).

### Security
- [ ] **Add CSP headers** — No Content-Security-Policy, X-Frame-Options, or X-Content-Type-Options headers.
- [ ] **Implement actual MFA** — TOTP verification is mocked (accepts any 6-digit code). Need real TOTP library (pyotp).
- [ ] **Implement real password reset** — Token generation is mocked. Need email service + secure token storage.
- [ ] **Add CORS restrictions for production** — Currently allows all methods/headers from localhost only; needs production origins.
- [ ] **Add rate limiting to auth endpoints** — Login/register endpoints have no rate limiting (brute force risk).

---

## P1 — High Priority (Should fix before beta)

### Testing
- [ ] **Add pytest for backend** — Zero test files exist. Need unit tests for auth, posts, workspaces, AI endpoints.
- [ ] **Add Jest/Vitest for frontend** — Zero test files exist. Need component tests for key pages.
- [ ] **Add integration tests** — Test full request flow: register → login → create post → get analytics.
- [ ] **Add API contract tests** — Validate all endpoints return expected schemas.

### AI Integration
- [ ] **Connect OpenAI image generation** — `generate-image` endpoint returns placeholder. Need DALL-E 3 integration.
- [ ] **Connect video generation API** — `generate-video` returns placeholder. Need actual video generation service (Runway, Pika, etc.).
- [ ] **Add AI credit tracking** — No usage metering for AI calls; users can make unlimited requests.
- [ ] **Add AI response caching** — Same prompt returns same result; should cache for cost savings.
- [ ] **Add error handling for AI provider failures** — Currently silently falls back to placeholder; should surface errors.

### Social Platform Publishing
- [ ] **Implement LinkedIn posting** — Connection tokens stored but no actual post publishing via API.
- [ ] **Implement X/Twitter posting** — Same gap as LinkedIn.
- [ ] **Implement Instagram posting** — Same gap.
- [ ] **Implement Facebook posting** — Same gap.
- [ ] **Implement YouTube upload** — Same gap.
- [ ] **Add posting queue worker** — Celery in requirements but no worker defined or tasks registered.

### Billing
- [ ] **Implement Stripe checkout session creation** — `POST /billing/checkout` returns mock URL; needs real Stripe SDK call.
- [ ] **Implement Stripe webhook handler** — No webhook endpoint for payment events (subscription created, updated, failed).
- [ ] **Add subscription enforcement** — No logic to block features when credits are exhausted or plan limits hit.
- [ ] **Add invoice PDF generation** — Invoices returned as JSON; need downloadable PDF.

### Media Storage
- [ ] **Implement S3 file upload** — `POST /media/assets` returns mock; needs actual multipart upload to S3.
- [ ] **Add presigned URL generation** — For secure file access without exposing S3 directly.
- [ ] **Add image processing pipeline** — Resize, compress, generate thumbnails on upload.
- [ ] **Add file type validation** — No server-side validation of uploaded file types/sizes.

---

## P2 — Medium Priority (Should fix before v1.0)

### Frontend
- [ ] **Add error boundaries** — No React error boundaries; unhandled errors crash the entire app.
- [ ] **Add loading skeletons** — Pages show nothing while data loads; need skeleton UI.
- [ ] **Add toast notifications** — No user feedback for success/error actions (save, delete, publish).
- [ ] **Add mobile responsive sidebar** — Sidebar is fixed-width; needs hamburger menu on mobile.
- [ ] **Add SEO meta tags** — No title, description, or Open Graph tags per page.
- [ ] **Add page transitions** — Hard jumps between routes; add smooth transitions.
- [ ] **Connect frontend auth to backend JWT** — Frontend stores NextAuth session but doesn't pass backend JWT to API calls.

### Backend
- [ ] **Add API versioning** — All endpoints under `/api/`; should be `/api/v1/` for future compatibility.
- [ ] **Add request/response logging** — No structured logging for API requests.
- [ ] **Add OpenAPI response models** — Many endpoints return raw dicts instead of typed Pydantic responses.
- [ ] **Add pagination to list endpoints** — Posts, analytics, audit logs return all results; need cursor/offset pagination.
- [ ] **Add WebSocket for real-time notifications** — Notifications page polls; should use WebSocket for live updates.
- [ ] **Refactor mock data endpoints** — Team, calendar, scheduler, media endpoints return hardcoded data; need database-backed implementations.
- [ ] **Add input sanitization** — No XSS prevention on user-generated content (post content, comments).

### DevOps
- [ ] **Add GitHub Actions CI** — No CI pipeline; need lint, type-check, test, build on PR.
- [ ] **Add GitHub Actions CD** — No deployment pipeline; need auto-deploy on merge to main.
- [ ] **Add Docker health check for frontend** — Backend has healthcheck; frontend doesn't.
- [ ] **Add production environment config** — `.env.example` missing Stripe keys; no production `.env` template.
- [ ] **Add database backup strategy** — No automated PostgreSQL backups configured.

### Analytics
- [ ] **Connect real analytics data** — Dashboard returns mock/generated data; needs actual platform API integration.
- [ ] **Add analytics data collection worker** — Background job to fetch metrics from connected platforms.
- [ ] **Add funnel visualization** — Current charts are basic; need conversion funnel analysis.

---

## P3 — Low Priority (Nice to have)

### Features
- [ ] **Add content A/B testing** — Test different versions of posts and measure performance.
- [ ] **Add competitor tracking** — Monitor competitor content and engagement.
- [ ] **Add hashtag performance analytics** — Track which hashtags drive the most engagement.
- [ ] **Add content scoring before publish** — Pre-publish quality check using AI.
- [ ] **Add multi-language content generation** — AI content in different languages.
- [ ] **Add email newsletter integration** — Send content as email campaigns.
- [ ] **Add RSS feed ingestion** — Pull content from RSS feeds for repurposing.
- [ ] **Add browser extension** — Quick content capture from any webpage.
- [ ] **Add mobile app** — React Native or Expo companion app.

### Platform
- [ ] **Add TikTok integration** — Platform not currently supported.
- [ ] **Add Pinterest integration** — Platform not currently supported.
- [ ] **Add threads.net integration** — Platform not currently supported.
- [ ] **Add Bluesky integration** — Platform not currently supported.

### Quality
- [ ] **Add accessibility audit** — WCAG 2.1 AA compliance check.
- [ ] **Add performance monitoring** — Lighthouse CI, Core Web Vitals tracking.
- [ ] **Add Sentry error tracking** — Frontend and backend error reporting.
- [ ] **Add analytics tracking** — PostHog or Mixpanel for product analytics.
- [ ] **Add A/B testing for UI** — Test different layouts and flows.

### Documentation
- [ ] **Add API developer guide** — Guide for third-party API consumers.
- [ ] **Add deployment guide** — Step-by-step production deployment instructions.
- [ ] **Add contribution guidelines** — CONTRIBUTING.md with code standards.
- [ ] **Add changelog** — Track feature releases and breaking changes.

---

## Completed

_(None yet)_
