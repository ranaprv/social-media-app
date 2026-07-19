---
type: community
cohesion: 0.33
members: 9
---

# Media Optimizer

**Cohesion:** 0.33 - loosely connected
**Members:** 9 nodes

## Members
- [[Analyze a media file against platform requirements.      Args         file_info]] - rationale - backend/app/services/media_optimizer.py
- [[Any_69]] - code
- [[Get media specifications for a platform and type.]] - rationale - backend/app/services/media_optimizer.py
- [[Get optimization summary for multiple assets across platforms.]] - rationale - backend/app/services/media_optimizer.py
- [[Media optimizer — auto-resize, format convert for each platform.  Analyzes media]] - rationale - backend/app/services/media_optimizer.py
- [[analyze_media_for_platform()]] - code - backend/app/services/media_optimizer.py
- [[get_optimization_summary()]] - code - backend/app/services/media_optimizer.py
- [[get_platform_media_specs()]] - code - backend/app/services/media_optimizer.py
- [[media_optimizer.py]] - code - backend/app/services/media_optimizer.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Media_Optimizer
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Any_1]]

## Top bridge nodes
- [[media_optimizer.py]] - degree 5, connects to 1 community