---
type: community
cohesion: 0.28
members: 9
---

# Platform Deep Features

**Cohesion:** 0.28 - loosely connected
**Members:** 9 nodes

## Members
- [[Any_72]] - code
- [[Get available deep features, optionally filtered by platform.]] - rationale - backend/app/services/platform_deep_features.py
- [[Get specs for a platform deep feature.]] - rationale - backend/app/services/platform_deep_features.py
- [[Platform deep features — Reels, Shorts, Articles scheduling.  Platform-specific]] - rationale - backend/app/services/platform_deep_features.py
- [[Validate content against deep feature requirements.]] - rationale - backend/app/services/platform_deep_features.py
- [[get_available_deep_features()]] - code - backend/app/services/platform_deep_features.py
- [[get_deep_feature_specs()]] - code - backend/app/services/platform_deep_features.py
- [[platform_deep_features.py]] - code - backend/app/services/platform_deep_features.py
- [[validate_deep_feature_content()]] - code - backend/app/services/platform_deep_features.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Platform_Deep_Features
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Any_1]]

## Top bridge nodes
- [[platform_deep_features.py]] - degree 5, connects to 1 community