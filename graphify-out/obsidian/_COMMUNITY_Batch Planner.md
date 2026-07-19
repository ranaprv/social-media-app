---
type: community
cohesion: 0.38
members: 7
---

# Batch Planner

**Cohesion:** 0.38 - loosely connected
**Members:** 7 nodes

## Members
- [[Any_23]] - code
- [[Content Batch Planner — weeklymonthly batch creation with scheduling.  Plans co]] - rationale - backend/app/services/batch_planner.py
- [[Plan a month of content (4 weekly batches).]] - rationale - backend/app/services/batch_planner.py
- [[Plan a week of content across platforms.]] - rationale - backend/app/services/batch_planner.py
- [[batch_planner.py]] - code - backend/app/services/batch_planner.py
- [[plan_monthly_batch()]] - code - backend/app/services/batch_planner.py
- [[plan_weekly_batch()]] - code - backend/app/services/batch_planner.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Batch_Planner
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Any_1]]
- 1 edge to [[_COMMUNITY_Any_2]]

## Top bridge nodes
- [[plan_weekly_batch()]] - degree 5, connects to 1 community
- [[batch_planner.py]] - degree 4, connects to 1 community