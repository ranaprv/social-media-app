# Changelog

All notable changes to Social Media Manager.

## [1.1.0] - 2026-07-16

### Added
- **Autonomous AI Workflow Pipeline:** 5-stage orchestration (Research → Draft → Visual Prompt → Save DB → HITL Staging) with async state machine
- **Multi-Model AI Engine:** Abstract base class `AIContentGenerator` with concrete generators for Claude (LinkedIn), OpenAI (X/Twitter), Gemini (Instagram)
- **UI-Driven Provider Selection:** `platform_provider_configs` table — users pick AI provider per platform via settings UI, no hardcoded mapping
- **Provider Config CRUD:** GET/PUT endpoints for managing workspace-level provider preferences
- **Analytics Feedback Loop:** Normalised performance score `Ps = w1*(eng/imp) + w2*(shares/imp) + w3*(clicks/imp)` with mock vector store for high-performers (score > 7.5)
- **SQLAlchemy Models:** `content_items`, `platform_posts`, `platform_analytics`, `platform_provider_configs` tables
- **Pydantic V2 Schemas:** Request/response models for workflow trigger, post approval, analytics ingestion, provider config
- **Bug Fixes:** Fixed `BrandVoice` import in `ai_content.py`, removed unimplemented tasks from TODO.md

### Fixed
- Orchestrator `_advance` called incorrectly in pipeline loop
- `to_response()` hardcoded topic/platform instead of using actual values
- Unused imports in API router

### Added
- **Authentication:** Email/password login, OAuth (Google, GitHub), JWT sessions, MFA (TOTP)
- **Dashboard:** Real-time stats, recent posts, quick actions, empty states
- **Content Studio:** AI idea generator, content generator, writing tools, brand voice training
- **Multi-LLM Support:** OpenAI, Anthropic, Gemini with model selection and multi-model voting
- **AI Media:** Image, video, voiceover, caption generation
- **AI Recommendations:** Content scoring (0-100), 6-dimension analysis, prioritized suggestions
- **Content Calendar:** Day/week/month views, drag-and-drop, campaigns
- **Publishing Scheduler:** Queue with retry, best posting times per platform
- **Analytics Dashboard:** KPI cards, trend charts, platform comparison, posting heatmap
- **Research:** Trend discovery, competitor analysis, keyword research
- **Billing:** 4 subscription tiers (Free/Pro/Business/Enterprise), Stripe integration, usage tracking
- **Security:** RBAC (4 tiers), audit logs, rate limiting, CSP headers, encryption status, GDPR compliance
- **Team Collaboration:** Members, comments, reviews, version history, notifications
- **Media Library:** Asset management with S3 storage, thumbnails, search
- **Content Repurposing:** Multi-platform content transformation
- **Dark/Light Mode:** Theme toggle with localStorage persistence
- **Google Drive:** Save content and video scripts to Drive
- **Video Pipeline:** Script generation, voiceover text, thumbnail prompts
- **Docker:** Multi-service compose (frontend, backend, PostgreSQL, Redis, Celery)
- **CI/CD:** GitHub Actions lint, type-check, test, build pipeline
- **Tests:** Backend pytest (5 modules), frontend Vitest (3 component tests)

### Fixed
- Authentication flow connected to NextAuth with backend JWT
- Database schema with Alembic migrations
- SQLAlchemy `metadata` reserved attribute conflict
- bcrypt/passlib compatibility (pinned bcrypt==4.0.1)
- Docker `NEXT_PUBLIC_API_URL` build-time vs runtime issue
- NextAuth server-side Docker networking (localhost → service name)
- Dashboard hardcoded mock data → real API data
- Research page 404 (missing page and API)
