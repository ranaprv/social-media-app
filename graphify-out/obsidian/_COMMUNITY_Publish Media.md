---
type: community
cohesion: 0.33
members: 6
---

# Publish Media

**Cohesion:** 0.33 - loosely connected
**Members:** 6 nodes

## Members
- [[Any_104]] - code
- [[AsyncSession_93]] - code
- [[Find media assets assigned to a platform directory.      Queries the assets tabl]] - rationale - backend/app/tasks/publish_media.py
- [[Resolve media assets from platform-specific directories.  When a post is schedul]] - rationale - backend/app/tasks/publish_media.py
- [[publish_media.py]] - code - backend/app/tasks/publish_media.py
- [[resolve_platform_media()]] - code - backend/app/tasks/publish_media.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Publish_Media
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Any_1]]
- 1 edge to [[_COMMUNITY_Asyncsession]]

## Top bridge nodes
- [[resolve_platform_media()]] - degree 5, connects to 1 community
- [[publish_media.py]] - degree 3, connects to 1 community