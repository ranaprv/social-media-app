---
type: community
cohesion: 0.17
members: 16
---

# 

**Cohesion:** 0.17 - loosely connected
**Members:** 16 nodes

## Members
- [[.__init__()_1]] - code - backend/app/middleware/rate_limiter.py
- [[._check_memory()]] - code - backend/app/middleware/rate_limiter.py
- [[._check_rate_limit()]] - code - backend/app/middleware/rate_limiter.py
- [[._check_redis()]] - code - backend/app/middleware/rate_limiter.py
- [[._get_client_id()]] - code - backend/app/middleware/rate_limiter.py
- [[.dispatch()]] - code - backend/app/middleware/rate_limiter.py
- [[BaseHTTPMiddleware]] - code
- [[Check rate limit using Redis sorted sets.]] - rationale - backend/app/middleware/rate_limiter.py
- [[Check rate limit using in-memory sliding window.]] - rationale - backend/app/middleware/rate_limiter.py
- [[Check rate limit using sliding window. Returns (allowed, remaining, reset_at).]] - rationale - backend/app/middleware/rate_limiter.py
- [[Get client identifier (user ID or IP).]] - rationale - backend/app/middleware/rate_limiter.py
- [[Rate limiter middleware — per-user, per-endpoint rate limiting.  Uses sliding wi]] - rationale - backend/app/middleware/rate_limiter.py
- [[RateLimiterMiddleware]] - code - backend/app/middleware/rate_limiter.py
- [[Request_5]] - code
- [[Sliding window rate limiter.]] - rationale - backend/app/middleware/rate_limiter.py
- [[rate_limiter.py]] - code - backend/app/middleware/rate_limiter.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Asyncsession]]
- 1 edge to [[_COMMUNITY_Any_1]]

## Top bridge nodes
- [[._get_client_id()]] - degree 5, connects to 1 community
- [[rate_limiter.py]] - degree 3, connects to 1 community