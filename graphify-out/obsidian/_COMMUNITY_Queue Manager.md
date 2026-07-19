---
type: community
cohesion: 0.29
members: 10
---

# Queue Manager

**Cohesion:** 0.29 - loosely connected
**Members:** 10 nodes

## Members
- [[Advanced queue manager — priority ordering, bulk operations, queue analytics.  P]] - rationale - backend/app/services/queue_manager.py
- [[Any_82]] - code
- [[AsyncSession_79]] - code
- [[Bulk update status for multiple queue items.]] - rationale - backend/app/services/queue_manager.py
- [[Get analytics about the publishing queue health.]] - rationale - backend/app/services/queue_manager.py
- [[Reorder the queue by updating scheduled_at times.      Items are rescheduled wit]] - rationale - backend/app/services/queue_manager.py
- [[bulk_update_status()_1]] - code - backend/app/services/queue_manager.py
- [[get_queue_analytics()]] - code - backend/app/services/queue_manager.py
- [[queue_manager.py]] - code - backend/app/services/queue_manager.py
- [[reorder_queue()]] - code - backend/app/services/queue_manager.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Queue_Manager
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_Any]]
- 2 edges to [[_COMMUNITY_Any_3]]
- 1 edge to [[_COMMUNITY_Any_1]]

## Top bridge nodes
- [[reorder_queue()]] - degree 6, connects to 2 communities
- [[queue_manager.py]] - degree 5, connects to 1 community
- [[bulk_update_status()_1]] - degree 5, connects to 1 community
- [[get_queue_analytics()]] - degree 5, connects to 1 community