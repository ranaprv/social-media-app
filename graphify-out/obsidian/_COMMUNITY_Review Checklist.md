---
type: community
cohesion: 0.25
members: 9
---

# Review Checklist

**Cohesion:** 0.25 - loosely connected
**Members:** 9 nodes

## Members
- [[Any_87]] - code
- [[Get all platforms with checklists.]] - rationale - backend/app/services/review_checklist.py
- [[Get the review checklist for a platform.]] - rationale - backend/app/services/review_checklist.py
- [[Pre-Publish Review Checklist — quality gate before content goes live.  Generates]] - rationale - backend/app/services/review_checklist.py
- [[Validate a completed checklist and return results.]] - rationale - backend/app/services/review_checklist.py
- [[get_all_platforms()]] - code - backend/app/services/review_checklist.py
- [[get_review_checklist()]] - code - backend/app/services/review_checklist.py
- [[review_checklist.py]] - code - backend/app/services/review_checklist.py
- [[validate_checklist()]] - code - backend/app/services/review_checklist.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Review_Checklist
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Any_1]]

## Top bridge nodes
- [[review_checklist.py]] - degree 5, connects to 1 community