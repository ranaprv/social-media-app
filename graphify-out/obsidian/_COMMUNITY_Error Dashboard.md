---
type: community
cohesion: 0.24
members: 12
---

# Error Dashboard

**Cohesion:** 0.24 - loosely connected
**Members:** 12 nodes

## Members
- [[Any_63]] - code
- [[AsyncSession_73]] - code
- [[Error dashboard — provides error analytics and retry controls.  Aggregates publi]] - rationale - backend/app/services/error_dashboard.py
- [[Get a summary of publish errors over the given period.      Returns     {]] - rationale - backend/app/services/error_dashboard.py
- [[Get overall publish statistics for the dashboard.]] - rationale - backend/app/services/error_dashboard.py
- [[Reset all failed items to 'scheduled' for retry.]] - rationale - backend/app/services/error_dashboard.py
- [[Simplify error messages for grouping.]] - rationale - backend/app/services/error_dashboard.py
- [[_simplify_error()]] - code - backend/app/services/error_dashboard.py
- [[bulk_retry_failed()]] - code - backend/app/services/error_dashboard.py
- [[error_dashboard.py]] - code - backend/app/services/error_dashboard.py
- [[get_error_summary()]] - code - backend/app/services/error_dashboard.py
- [[get_publish_stats()]] - code - backend/app/services/error_dashboard.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Error_Dashboard
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_Any]]
- 2 edges to [[_COMMUNITY_Any_3]]
- 1 edge to [[_COMMUNITY_Any_1]]

## Top bridge nodes
- [[get_error_summary()]] - degree 7, connects to 2 communities
- [[error_dashboard.py]] - degree 6, connects to 1 community
- [[bulk_retry_failed()]] - degree 5, connects to 1 community
- [[get_publish_stats()]] - degree 5, connects to 1 community