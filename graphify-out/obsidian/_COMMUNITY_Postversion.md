---
type: community
cohesion: 0.31
members: 11
---

# Postversion

**Cohesion:** 0.31 - loosely connected
**Members:** 11 nodes

## Members
- [[Any_56]] - code
- [[AsyncSession_69]] - code
- [[Content versioning — snapshot + rollback for posts.  Creates version snapshots o]] - rationale - backend/app/services/content_versioning.py
- [[Create a version snapshot of a post and its platform entries.      Captures the]] - rationale - backend/app/services/content_versioning.py
- [[Get version history for a post._1]] - rationale - backend/app/services/content_versioning.py
- [[PostVersion]] - code - backend/app/models/content.py
- [[Rollback a post to a previous version.      Restores the post content and platfo]] - rationale - backend/app/services/content_versioning.py
- [[content_versioning.py]] - code - backend/app/services/content_versioning.py
- [[create_snapshot()]] - code - backend/app/services/content_versioning.py
- [[get_version_history()_1]] - code - backend/app/services/content_versioning.py
- [[rollback_to_version()]] - code - backend/app/services/content_versioning.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Postversion
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_Asyncsession_2]]
- 2 edges to [[_COMMUNITY_Any_3]]
- 1 edge to [[_COMMUNITY_Database]]
- 1 edge to [[_COMMUNITY_Any_1]]
- 1 edge to [[_COMMUNITY_Asyncsession]]

## Top bridge nodes
- [[create_snapshot()]] - degree 8, connects to 2 communities
- [[rollback_to_version()]] - degree 8, connects to 2 communities
- [[PostVersion]] - degree 5, connects to 2 communities
- [[content_versioning.py]] - degree 5, connects to 1 community