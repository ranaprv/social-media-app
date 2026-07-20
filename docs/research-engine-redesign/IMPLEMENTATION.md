# Research Engine Redesign — Implementation Plan

## Overview

Transform the Research Engine from a generic LLM trend tool into a Video SEO-focused research platform with database persistence, 5 capability tabs, and integration with the Strategy, Scheduling, and Repurpose engines.

**Approach:** LLM + YouTube Data API hybrid. LLM for analysis/insights, YouTube API for structured data (search volume, competitor metrics). Database persistence via PostgreSQL JSONB.

## Prerequisites

- PostgreSQL running (already configured)
- Alembic migrations working
- Frontend build passing (0 lint errors)
- YouTube Data API credentials (optional — LLM fallback works without it)

## Phase Summary

| Phase | Title | Est. Time | Delivers |
|-------|-------|-----------|----------|
| 1 | Database & Migration | 1-2h | `research_items` table |
| 2 | Backend API | 3-4h | 5 endpoints + persistence |
| 3 | Frontend Redesign | 3-4h | 5 tabs + sidebar + charts |
| 4 | Engine Integration | 2-3h | Strategy/Scheduling/Repurpose hooks |
| 5 | Polish & Testing | 1-2h | Error handling, loading states, edge cases |

---

## Phase 1: Database & Migration

### Objective
Create the `research_items` table with all required columns and indexes.

### Rationale
Database is the foundation — everything else depends on it. Must exist before API or frontend work begins.

### Tasks
- [ ] Create Alembic migration for `research_items` table
- [ ] Add `ResearchItem` SQLAlchemy model in `backend/app/models/`
- [ ] Add Pydantic schema in `backend/app/schemas/`
- [ ] Verify migration runs cleanly: `alembic upgrade head`

### Success Criteria
- `research_items` table exists with all columns from RESEARCH.md schema
- Model imports work in existing codebase
- Migration is reversible (`alembic downgrade` works)

### Files Likely Affected
- `backend/alembic/versions/` (new migration file)
- `backend/app/models/research.py` (new)
- `backend/app/schemas/research.py` (new)

---

## Phase 2: Backend API

### Objective
Build 5 research endpoints with database persistence and LLM-powered analysis.

### Rationale
Backend must exist before frontend can consume it. Each endpoint follows the same pattern: accept request → LLM analysis → persist to DB → return result.

### Tasks
- [ ] Refactor `backend/app/api/research.py` into 5 endpoint groups
- [ ] Implement `POST /research/keywords` — keyword research with Video SEO scoring
- [ ] Implement `POST /research/competitors` — competitor analysis with gap detection
- [ ] Implement `POST /research/trends` — trend analysis with direction tracking
- [ ] Implement `POST /research/thumbnails` — thumbnail & title A/B testing
- [ ] Implement `POST /research/audience` — audience analytics
- [ ] Implement `GET /research/saved` — list saved research items
- [ ] Implement `DELETE /research/saved/{id}` — delete research item
- [ ] Add persistence layer: save all results to `research_items` table
- [ ] Add Video SEO scoring algorithm (composite of difficulty, volume, competition)

### Success Criteria
- All 5 POST endpoints return structured JSON with Video SEO scores
- Results persist to `research_items` table
- `GET /research/saved` returns paginated list
- Each endpoint handles errors gracefully (LLM failure, DB failure)

### Files Likely Affected
- `backend/app/api/research.py` (major refactor)
- `backend/app/services/research_service.py` (new — business logic)
- `backend/app/services/video_seo_scorer.py` (new — scoring algorithm)

---

## Phase 3: Frontend Redesign

### Objective
Redesign the Research page with 5 tabs, persistent sidebar, and visual scoring.

### Rationale
Frontend redesign makes the new capabilities accessible. Each tab maps to one backend endpoint.

### Tasks
- [ ] Create `ResearchSidebar` component (saved items list with delete)
- [ ] Create `KeywordResearchTab` with search volume gauges and difficulty scores
- [ ] Create `CompetitorAnalysisTab` with gap analysis and top content tables
- [ ] Create `TrendAnalysisTab` with direction charts and opportunity scoring
- [ ] Create `ThumbnailTitleTab` with A/B variant scoring and CTR prediction
- [ ] Create `AudienceAnalyticsTab` with demographics and peak hours
- [ ] Refactor `research/page.tsx` to use new tab components
- [ ] Add `VideoSEOGauge` component (0-100 score with color coding)
- [ ] Add `TrendChart` component (line chart for direction over time)
- [ ] Add save-to-strategy button on each research item

### Success Criteria
- All 5 tabs render with real data from backend
- Saved items persist across page reloads
- Video SEO scores display with visual gauges
- "Save to strategy" links research items to content pillars

### Files Likely Affected
- `frontend/src/app/dashboard/research/page.tsx` (major refactor)
- `frontend/src/components/research/` (new directory, 7+ components)
- `frontend/src/components/ui/video-seo-gauge.tsx` (new)
- `frontend/src/components/ui/trend-chart.tsx` (new)

---

## Phase 4: Engine Integration

### Objective
Connect research data to Strategy, Scheduling, and Repurpose engines.

### Rationale
This is the core value proposition — research feeds content creation. Without this, research is isolated.

### Tasks
- [ ] Add `GET /research/by-pillar/{pillar_id}` endpoint for Strategy engine
- [ ] Add `GET /research/rising?platform={platform}` for Scheduling engine
- [ ] Add `GET /research/top-scoring?limit={n}` for content slot generation
- [ ] Update Strategy wizard "Content Pillars" step to pre-populate from research
- [ ] Update Scheduling engine to pull topics from `research_items` by pillar
- [ ] Update Repurpose engine to suggest platform-specific repurposing based on research
- [ ] Add "Research-backed" badge on calendar items that use researched topics

### Success Criteria
- Strategy wizard shows researched topic suggestions in pillar step
- Scheduling engine generates calendar slots from high-scoring research items
- Repurpose engine suggests optimal platform for each researched topic
- Calendar items show which research informed them

### Files Likely Affected
- `backend/app/api/research.py` (new endpoints)
- `backend/app/services/content_pillar_manager.py` (research integration)
- `backend/app/services/calendar_analytics.py` (research integration)
- `frontend/src/app/dashboard/strategy/wizard/page.tsx` (research pre-population)
- `frontend/src/app/dashboard/calendar/page.tsx` (research-backed badges)

---

## Phase 5: Polish & Testing

### Objective
Handle edge cases, loading states, error recovery, and verify everything works end-to-end.

### Rationale
Production readiness — users will hit API failures, empty states, and edge cases.

### Tasks
- [ ] Add loading skeletons for all 5 tabs
- [ ] Add empty states with call-to-action ("No research yet — run your first query")
- [ ] Add error boundaries for failed API calls
- [ ] Add retry logic for LLM failures (with exponential backoff)
- [ ] Add YouTube API quota handling (cache + rate limit)
- [ ] Add data freshness indicators (expires_at display)
- [ ] Test full flow: research → save → strategy → scheduling
- [ ] Test edge cases: empty results, API failures, expired data
- [ ] Verify mobile responsiveness of new tabs

### Success Criteria
- All tabs show loading states during API calls
- Empty states guide users to take action
- API failures show user-friendly error messages
- Full research → content pipeline works end-to-end
- No console errors in any tab

### Files Likely Affected
- `frontend/src/components/research/` (loading/error states)
- `backend/app/api/research.py` (error handling, retry logic)
- `backend/app/services/research_service.py` (caching, rate limiting)

---

## Post-Implementation
- [ ] Update ARCHITECTURE.md with new research engine diagram
- [ ] Update README.md features section
- [ ] Add e2e tests for research → strategy flow
- [ ] Performance test: 100 concurrent research queries

## Notes
- YouTube Data API has 10,000 units/day quota. Each search = 100 units. Budget: ~100 queries/day without caching.
- LLM fallback works without YouTube API — users can still get insights, just less structured data.
- `research_items` uses JSONB for flexible storage — different research types store different fields in the same `data` column.
- Trend data has `expires_at` — stale trends should be flagged in the UI, not silently hidden.
