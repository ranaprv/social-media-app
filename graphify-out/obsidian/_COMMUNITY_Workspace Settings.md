---
type: community
cohesion: 0.27
members: 10
---

# Workspace Settings

**Cohesion:** 0.27 - loosely connected
**Members:** 10 nodes

## Members
- [[Any_103]] - code
- [[AsyncSession_92]] - code
- [[Get the settings schema for UI rendering.]] - rationale - backend/app/services/workspace_settings.py
- [[Get workspace scheduling settings.]] - rationale - backend/app/services/workspace_settings.py
- [[Update workspace scheduling settings.]] - rationale - backend/app/services/workspace_settings.py
- [[Workspace settings — platform defaults, timezone, posting preferences.  Manages]] - rationale - backend/app/services/workspace_settings.py
- [[get_settings_schema()]] - code - backend/app/services/workspace_settings.py
- [[get_workspace_settings()]] - code - backend/app/services/workspace_settings.py
- [[update_workspace_settings()]] - code - backend/app/services/workspace_settings.py
- [[workspace_settings.py]] - code - backend/app/services/workspace_settings.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Workspace_Settings
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_Asyncsession]]
- 1 edge to [[_COMMUNITY_Any_1]]

## Top bridge nodes
- [[workspace_settings.py]] - degree 5, connects to 1 community
- [[get_workspace_settings()]] - degree 5, connects to 1 community
- [[update_workspace_settings()]] - degree 5, connects to 1 community