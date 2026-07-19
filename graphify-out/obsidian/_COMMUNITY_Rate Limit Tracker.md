---
type: community
cohesion: 0.20
members: 15
---

# Rate Limit Tracker

**Cohesion:** 0.20 - loosely connected
**Members:** 15 nodes

## Members
- [[Any_83]] - code
- [[Check if we can make another API call to a platform.      Returns whether the ca]] - rationale - backend/app/services/rate_limit_tracker.py
- [[Get list of platforms currently throttled.]] - rationale - backend/app/services/rate_limit_tracker.py
- [[Get rate limit configuration for a platform.]] - rationale - backend/app/services/rate_limit_tracker.py
- [[Get rate limit status for all platforms.]] - rationale - backend/app/services/rate_limit_tracker.py
- [[Rate limit tracker — per-platform quota tracking and throttling.  Tracks API cal]] - rationale - backend/app/services/rate_limit_tracker.py
- [[Record an API call to a platform.      Should be called after every platform API]] - rationale - backend/app/services/rate_limit_tracker.py
- [[Record that we hit a rate limit on a platform.      Called when we receive a 429]] - rationale - backend/app/services/rate_limit_tracker.py
- [[check_rate_limit()]] - code - backend/app/services/rate_limit_tracker.py
- [[get_all_rate_status()]] - code - backend/app/services/rate_limit_tracker.py
- [[get_rate_limit_info()]] - code - backend/app/services/rate_limit_tracker.py
- [[get_throttled_platforms()]] - code - backend/app/services/rate_limit_tracker.py
- [[rate_limit_tracker.py]] - code - backend/app/services/rate_limit_tracker.py
- [[record_api_call()]] - code - backend/app/services/rate_limit_tracker.py
- [[record_rate_limit_hit()]] - code - backend/app/services/rate_limit_tracker.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Rate_Limit_Tracker
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_Any]]
- 1 edge to [[_COMMUNITY_Any_1]]

## Top bridge nodes
- [[rate_limit_tracker.py]] - degree 8, connects to 1 community
- [[record_api_call()]] - degree 4, connects to 1 community
- [[record_rate_limit_hit()]] - degree 4, connects to 1 community