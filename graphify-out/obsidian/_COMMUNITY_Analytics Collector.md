---
type: community
cohesion: 0.18
members: 15
---

# Analytics Collector

**Cohesion:** 0.18 - loosely connected
**Members:** 15 nodes

## Members
- [[Analytics data collection from social platforms — fetches real performance data.]] - rationale - backend/app/services/analytics_collector.py
- [[Fetch Facebook post insights via Graph API.]] - rationale - backend/app/services/analytics_collector.py
- [[Fetch Instagram media insights via Graph API.]] - rationale - backend/app/services/analytics_collector.py
- [[Fetch LinkedIn post statistics via Marketing API.]] - rationale - backend/app/services/analytics_collector.py
- [[Fetch TwitterX tweet metrics via v2 API.]] - rationale - backend/app/services/analytics_collector.py
- [[Fetch YouTube video statistics via Data API v3 — uses OAuth bearer token.]] - rationale - backend/app/services/analytics_collector.py
- [[Fetch metrics from a specific platform API.]] - rationale - backend/app/services/analytics_collector.py
- [[PlatformConnection_1]] - code
- [[_fetch_facebook()]] - code - backend/app/services/analytics_collector.py
- [[_fetch_instagram()]] - code - backend/app/services/analytics_collector.py
- [[_fetch_linkedin()]] - code - backend/app/services/analytics_collector.py
- [[_fetch_platform_metrics()]] - code - backend/app/services/analytics_collector.py
- [[_fetch_twitter()]] - code - backend/app/services/analytics_collector.py
- [[_fetch_youtube()]] - code - backend/app/services/analytics_collector.py
- [[analytics_collector.py]] - code - backend/app/services/analytics_collector.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Analytics_Collector
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_Asyncsession_1]]
- 1 edge to [[_COMMUNITY_Any_1]]

## Top bridge nodes
- [[analytics_collector.py]] - degree 9, connects to 2 communities
- [[_fetch_platform_metrics()]] - degree 9, connects to 1 community