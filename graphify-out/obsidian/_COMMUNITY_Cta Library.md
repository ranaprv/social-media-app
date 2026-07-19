---
type: community
cohesion: 0.18
members: 11
---

# Cta Library

**Cohesion:** 0.18 - loosely connected
**Members:** 11 nodes

## Members
- [[Any_60]] - code
- [[CTA Library — organized library by goal, platform, and tone.  Pre-built call-to-]] - rationale - backend/app/services/cta_library.py
- [[Get CTAs filtered by goal.]] - rationale - backend/app/services/cta_library.py
- [[Get all CTAs that work on a specific platform.]] - rationale - backend/app/services/cta_library.py
- [[Get all available CTA goals.]] - rationale - backend/app/services/cta_library.py
- [[Search CTAs by keyword.]] - rationale - backend/app/services/cta_library.py
- [[cta_library.py]] - code - backend/app/services/cta_library.py
- [[get_all_cta_goals()]] - code - backend/app/services/cta_library.py
- [[get_ctas_by_goal()]] - code - backend/app/services/cta_library.py
- [[get_ctas_by_platform()]] - code - backend/app/services/cta_library.py
- [[search_ctas()]] - code - backend/app/services/cta_library.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Cta_Library
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Any_1]]

## Top bridge nodes
- [[cta_library.py]] - degree 6, connects to 1 community