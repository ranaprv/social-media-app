# Research Engine Redesign Research

## Overview

Redesign the Research Engine from a generic LLM-powered trend/keyword tool into a Video SEO-focused research platform. The new engine follows Video SEO best practices, persists findings to database, and feeds research data directly into the Repurpose and Scheduling engines for content creation.

## Problem Statement

The current Research Engine has three basic tabs (Trends, Competitors, Keywords) that call an LLM to generate generic results. Problems:

1. **No persistence** — results disappear on page reload. No history, no comparison over time.
2. **No Video SEO focus** — generic "trends" research doesn't follow YouTube/Reels/TikTok SEO best practices (keyword difficulty, search volume, competition analysis).
3. **Disconnected from content pipeline** — Repurpose and Scheduling engines can't access research findings. Users manually copy-paste topics and pillars.
4. **Missing capabilities** — no thumbnail/title testing, no audience analytics, no trend tracking over time.
5. **Irrelevant options** — current tabs mix unrelated capabilities.

## User Stories / Use Cases

1. **As a content creator**, I want to research trending topics in my niche with Video SEO data (search volume, competition, difficulty) so I can choose topics that will rank.
2. **As a social media manager**, I want to analyze competitors' top-performing content (thumbnails, titles, posting times) so I can model my strategy on what works.
3. **As a marketer**, I want to track trend direction over weeks so I can ride waves at the right time.
4. **As a video producer**, I want A/B test thumbnail and title ideas before publishing so I maximize CTR.
5. **As a team lead**, I want audience analytics (demographics, peak hours, engagement patterns) so I can optimize posting schedules.
6. **As a content planner**, I want researched topics and content pillars saved to the database so the Scheduling Engine can auto-generate a content calendar from them.

## Technical Research

### Current Architecture

```
Frontend (Research Page)
  ├── Tab: Trends → POST /research/trends
  ├── Tab: Competitors → POST /research/competitors
  └── Tab: Keywords → POST /research/keywords
          │
          ▼
Backend (research.py)
  └── call_llm_json() → LLM generates results → returns JSON
          │
          ▼
    No database persistence
    No connection to strategy/scheduling
```

### Proposed Architecture

```
Frontend (Research Page)
  ├── Tab: Keyword Research → POST /research/keywords
  ├── Tab: Competitor Analysis → POST /research/competitors
  ├── Tab: Trend Analysis → POST /research/trends
  ├── Tab: Thumbnail & Title Testing → POST /research/thumbnails
  ├── Tab: Audience Analytics → POST /research/audience
  └── Saved Research List → GET /research/saved
          │
          ▼
Backend (research.py)
  ├── LLM-powered analysis
  ├── Database persistence (ResearchItem model)
  ├── Video SEO scoring algorithm
  └── Export to strategy/scheduling APIs
          │
          ▼
Database (research_items table)
  ├── topics, keywords, pillars
  ├── competitor insights
  ├── trend data with timestamps
  ├── thumbnail/title test results
  ├── audience demographics
  └── Video SEO scores
          │
          ▼
Strategy Engine ← reads research_items for content pillars
Scheduling Engine ← reads research_items for topic scheduling
Repurpose Engine ← reads research_items for repurpose targets
```

### New Capabilities (per user specification)

#### 1. Keyword & Topic Research (enhanced)
- **Video SEO scoring**: keyword difficulty (1-100), search volume estimate, competition level
- **Topic clustering**: group related keywords into content pillar ideas
- **Long-tail discovery**: find specific queries with low competition
- **Platform-specific keywords**: YouTube search terms vs. Instagram hashtags vs. TikTok sounds

#### 2. Competitor Analysis (enhanced)
- **Top content analysis**: identify competitor's highest-performing posts
- **Thumbnail style catalog**: what visual styles get engagement
- **Title pattern analysis**: headline structures that drive clicks
- **Posting cadence**: how often, when, what formats
- **Gap analysis**: topics competitors cover that you don't

#### 3. Trend Analysis (enhanced)
- **Direction tracking**: rising/stable/declining with velocity
- **Seasonal patterns**: detect recurring trends by time of year
- **Cross-platform comparison**: same trend performance across YouTube, TikTok, Instagram
- **Opportunity scoring**: combine trend direction + competition + audience fit

#### 4. Thumbnail & Title Testing (new)
- **A/B title variants**: generate 5 title options scored by predicted CTR
- **Thumbnail concept scoring**: rate visual concepts by engagement prediction
- **Hook analysis**: first 3 seconds hook strength scoring
- **Emoji/symbol optimization**: which visual cues improve CTR
- **Platform-specific formatting**: YouTube title length vs. Instagram caption vs. TikTok text overlay

#### 5. Audience Analytics (new)
- **Demographic profiling**: age, gender, location, interests from engagement data
- **Peak engagement windows**: best days and hours per platform
- **Content preference analysis**: what formats/topics get most engagement
- **Growth trajectory**: follower growth rate, engagement trend
- **Cross-audience comparison**: compare your audience vs. competitor audiences

### Database Schema

```sql
CREATE TABLE research_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id),
    
    -- Classification
    category VARCHAR(50) NOT NULL,  -- 'keyword', 'competitor', 'trend', 'thumbnail', 'audience'
    subcategory VARCHAR(50),         -- 'video_seo', 'title_test', 'demographics', etc.
    
    -- Core data
    topic VARCHAR(255),
    platform VARCHAR(50),            -- 'youtube', 'tiktok', 'instagram', 'all'
    data JSONB NOT NULL,             -- flexible storage for different research types
    
    -- Video SEO metrics
    keyword_difficulty INTEGER,      -- 1-100
    search_volume VARCHAR(50),       -- 'high', 'medium', 'low', or numeric
    competition_level VARCHAR(20),   -- 'low', 'medium', 'high'
    video_seo_score INTEGER,         -- 0-100 composite score
    
    -- Trend tracking
    trend_direction VARCHAR(20),     -- 'rising', 'stable', 'declining'
    trend_velocity FLOAT,            -- rate of change
    
    -- Content integration
    content_pillar VARCHAR(100),     -- linked to strategy pillars
    pillar_id UUID,                  -- FK to strategy_content_pillars
    priority INTEGER DEFAULT 0,      -- for scheduling engine ordering
    
    -- Engagement metrics
    engagement_rate FLOAT,
    estimated_reach INTEGER,
    estimated_impressions INTEGER,
    
    -- Metadata
    source VARCHAR(50),              -- 'llm', 'api', 'manual'
    confidence FLOAT,                -- 0-1 how reliable this data is
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP            -- for trend data freshness
);

CREATE INDEX idx_research_workspace ON research_items(workspace_id);
CREATE INDEX idx_research_category ON research_items(category);
CREATE INDEX idx_research_platform ON research_items(platform);
CREATE INDEX idx_research_pillar ON research_items(content_pillar);
CREATE INDEX idx_research_created ON research_items(created_at);
```

### Integration with Existing Engines

#### Strategy Engine Integration
- Strategy wizard's "Content Pillars" step reads `research_items WHERE category='keyword' GROUP BY content_pillar`
- Pre-populates pillar suggestions from researched keywords
- Auto-assigns topics to pillars based on Video SEO scores

#### Scheduling Engine Integration
- When generating a content calendar, the scheduler queries:
  ```sql
  SELECT * FROM research_items 
  WHERE content_pillar = :pillar 
  AND trend_direction = 'rising'
  AND video_seo_score > 60
  ORDER BY video_seo_score DESC
  LIMIT 10
  ```
- Uses high-scoring topics as content slots in the calendar
- Prioritizes topics with rising trends and low competition

#### Repurpose Engine Integration
- When repurposing content, the engine can suggest:
  - Which platform each topic performs best on (from research data)
  - Optimal title variants (from thumbnail/title testing)
  - Best posting times (from audience analytics)

### Approach Options

| Approach | Pros | Cons |
|----------|------|------|
| **A: LLM-only (current)** | Simple, no external APIs | No real data, results are generic |
| **B: LLM + YouTube Data API** | Real search volume, real competitor data | API quota limits, requires OAuth setup |
| **C: LLM + third-party SEO tools** | Rich keyword data, historical trends | Cost per query, API complexity |
| **D: LLM + web scraping** | Free, comprehensive | Fragile, rate-limited, legal concerns |

**Recommended: Hybrid (B+D)** — Use YouTube Data API for structured data (search volume, competitor metrics) and LLM for analysis/insights. Fall back to web scraping for data the API doesn't cover.

## UI/UX Considerations

### Research Page Redesign
- **5 tabs** instead of 3: Keywords, Competitors, Trends, Thumbnails, Audience
- **Persistent sidebar** showing saved research items (like a bookmark list)
- **Visual scoring gauges** for Video SEO scores, competition levels
- **Trend charts** showing direction over time (line charts)
- **Save to strategy** button that links research items to content pillars
- **Compare mode** side-by-side competitor analysis

### Research → Content Pipeline UI
- **Drag-and-drop** from research sidebar to strategy wizard
- **Auto-suggest** research items when creating content calendar slots
- **Research badge** on calendar items showing which research informed them

## Risks and Challenges

1. **API costs**: YouTube Data API has daily quotas. Need caching and rate limiting.
2. **Data freshness**: Trend data expires. Need `expires_at` column and refresh logic.
3. **LLM accuracy**: Video SEO scores from LLM are estimates. Need confidence scores.
4. **Schema migration**: Adding `research_items` table requires Alembic migration.
5. **Frontend complexity**: 5 tabs + persistent sidebar + charts = more components.

## Open Questions

1. Should thumbnail/title testing use real A/B testing (publish two versions) or simulated scoring?
2. What's the refresh cadence for trend data? Daily? Weekly?
3. Should we cache YouTube API responses to stay within quota?
4. How deep should the competitor analysis go — just top 5 posts, or full channel audit?

## References

- [YouTube Data API v3 docs](https://developers.google.com/youtube/v3)
- [VidIQ Video SEO best practices](https://vidiq.com/blog/post/youtube-seo/)
- [TubeBuddy keyword research](https://www.tubebuddy.com/tools#keyword)
- [Social Blade competitor analysis](https://socialblade.com/)
