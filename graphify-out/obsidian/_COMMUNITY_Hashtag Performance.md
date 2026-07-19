---
type: community
cohesion: 0.32
members: 8
---

# Hashtag Performance

**Cohesion:** 0.32 - loosely connected
**Members:** 8 nodes

## Members
- [[Analyze hashtag performance across published posts.]] - rationale - backend/app/services/hashtag_performance.py
- [[Any_65]] - code
- [[AsyncSession_75]] - code
- [[Hashtag Performance Tracker — track hashtag reach over time, identify trending t]] - rationale - backend/app/services/hashtag_performance.py
- [[Track a specific hashtag's performance over time.]] - rationale - backend/app/services/hashtag_performance.py
- [[get_hashtag_performance()]] - code - backend/app/services/hashtag_performance.py
- [[get_hashtag_trends()]] - code - backend/app/services/hashtag_performance.py
- [[hashtag_performance.py]] - code - backend/app/services/hashtag_performance.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Hashtag_Performance
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_Any]]
- 2 edges to [[_COMMUNITY_Asyncsession_1]]
- 1 edge to [[_COMMUNITY_Any_1]]

## Top bridge nodes
- [[get_hashtag_performance()]] - degree 6, connects to 2 communities
- [[get_hashtag_trends()]] - degree 6, connects to 2 communities
- [[hashtag_performance.py]] - degree 4, connects to 1 community