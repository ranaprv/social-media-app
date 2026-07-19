# Analytics Platform Tabs Research

## Overview

Redesign the analytics dashboard to show platform-specific metrics via tabs. Each platform (LinkedIn, X, Instagram, Facebook, YouTube) gets its own tab with charts and KPIs unique to that platform's content format and engagement model.

## Problem Statement

Current analytics page shows generic metrics (reach, impressions, engagement) across all platforms. This doesn't reflect how each platform actually works:

- LinkedIn values professional engagement (comments, shares, article reads)
- X values virality (retweets, quote tweets, thread completions)
- Instagram values visual engagement (saves, story views, reel plays)
- Facebook values community (reactions, shares, group posts)
- YouTube values watch time (view duration, subscribers, CTR)

Generic metrics hide what's actually working on each platform.

## User Stories

1. As a content creator, I want to see LinkedIn-specific metrics so I know if my professional content is resonating
2. As a social media manager, I want to compare Instagram engagement (saves, shares) vs X engagement (retweets, replies)
3. As a marketer, I want to see YouTube watch time and subscriber growth, not just "impressions"
4. As a team lead, I want platform-specific insights to allocate content creation resources

## Technical Research

### Current State

- `analytics/page.tsx` — 371 lines, uses mock data
- `backend/app/api/analytics.py` — Has endpoints for dashboard, platform-comparison, top-posts, best-times, content-trends
- All endpoints return generic metrics, not platform-specific data
- Charts use Recharts (already installed)

### Platform-Specific Metrics

#### LinkedIn
- Impressions, Engagement Rate, Clicks, Shares, Comments
- Article Reads, Company Page Views, Follower Growth
- Best for: professional content, thought leadership

#### X (Twitter)
- Impressions, Engagement Rate, Retweets, Replies
- Profile Visits, Link Clicks, Quote Tweets
- Best for: quick takes, threads, viral content

#### Instagram
- Reach, Impressions, Engagement Rate, Saves, Shares
- Story Views, Reel Plays, Profile Visits
- Best for: visual content, reels, stories

#### Facebook
- Reach, Impressions, Engagement Rate, Shares, Comments
- Reactions, Page Views, Video Views
- Best for: community posts, video, groups

#### YouTube
- Views, Watch Time, Subscribers, CTR
- Average View Duration, Likes, Comments
- Best for: long-form video, tutorials, shorts

### Required Backend Changes

Add new endpoint: `GET /analytics/platform/{platform}`

Query `AnalyticsMetric` table filtered by platform, return platform-specific fields.

### Required Frontend Changes

1. Add Tabs component for platform selection
2. Create platform-specific dashboard component
3. Wire to new API endpoint
4. Platform-specific chart configurations

## UI/UX Considerations

### Tab Design
- Platform icons + names in tabs
- Active tab shows platform color
- Consistent layout across all tabs

### Chart Types per Platform

| Platform | Primary Chart | Secondary Chart |
|----------|---------------|-----------------|
| LinkedIn | Engagement over time | Content type performance |
| X | Impressions + retweets | Best posting times |
| Instagram | Reach + saves | Reel vs post performance |
| Facebook | Reactions breakdown | Video vs photo performance |
| YouTube | Watch time trend | Subscriber growth |

### KPI Cards per Platform

| Platform | KPI 1 | KPI 2 | KPI 3 | KPI 4 |
|----------|-------|-------|-------|-------|
| LinkedIn | Impressions | Engagement Rate | Clicks | Article Reads |
| X | Impressions | Retweets | Replies | Profile Visits |
| Instagram | Reach | Saves | Story Views | Reel Plays |
| Facebook | Reach | Reactions | Shares | Video Views |
| YouTube | Views | Watch Time | Subscribers | Avg View Duration |

## Integration Points

- `components/ui/tabs.tsx` — Already exists, use for platform tabs
- `components/ui/card.tsx` — KPI cards
- `recharts` — Charts library, already installed
- `backend/app/api/analytics.py` — Extend with platform endpoint
- `backend/app/models/content.py` — AnalyticsMetric model

## Risks and Challenges

1. **Data availability** — Backend may not have platform-specific fields yet
2. **Mock data** — Need realistic mock data per platform for development
3. **Chart complexity** — Different chart types per platform increases code
4. **Responsive design** — Tabs must work on mobile

## Recommended Approach

1. **Phase 1:** Backend — Add platform-specific endpoint
2. **Phase 2:** Frontend — Tab structure + platform selector
3. **Phase 3:** Frontend — Platform-specific KPI cards
4. **Phase 4:** Frontend — Platform-specific charts
5. **Phase 5:** Polish — Animations, responsive, empty states

## Open Questions

1. Should the "All Platforms" overview tab remain?
2. How to handle platforms with no data yet?
3. Real-time updates or periodic refresh?

## References

- Recharts docs: https://recharts.org
- Current analytics page: `frontend/src/app/dashboard/analytics/page.tsx`
- Backend analytics API: `backend/app/api/analytics.py`
