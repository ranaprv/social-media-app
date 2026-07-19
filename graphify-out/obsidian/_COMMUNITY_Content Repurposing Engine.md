---
type: community
cohesion: 0.33
members: 7
---

# Content Repurposing Engine

**Cohesion:** 0.33 - loosely connected
**Members:** 7 nodes

## Members
- [[Any_51]] - code
- [[Content Repurposing Engine — turn one piece into many formats.  Transforms a blo]] - rationale - backend/app/services/content_repurposing_engine.py
- [[Get available repurposing routes, optionally filtered by source format.]] - rationale - backend/app/services/content_repurposing_engine.py
- [[Repurpose content into multiple target formats.      Returns transformed content]] - rationale - backend/app/services/content_repurposing_engine.py
- [[content_repurposing_engine.py]] - code - backend/app/services/content_repurposing_engine.py
- [[get_available_routes()]] - code - backend/app/services/content_repurposing_engine.py
- [[repurpose_content()_1]] - code - backend/app/services/content_repurposing_engine.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Content_Repurposing_Engine
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Any_1]]
- 1 edge to [[_COMMUNITY_Any_2]]

## Top bridge nodes
- [[content_repurposing_engine.py]] - degree 4, connects to 1 community
- [[repurpose_content()_1]] - degree 4, connects to 1 community