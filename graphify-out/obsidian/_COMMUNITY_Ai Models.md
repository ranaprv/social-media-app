---
type: community
cohesion: 0.25
members: 8
---

# Ai Models

**Cohesion:** 0.25 - loosely connected
**Members:** 8 nodes

## Members
- [[API endpoints for AI model discovery and provider status.]] - rationale - backend/app/api/ai_models.py
- [[Return OmniRoute routing recommendations per task type.]] - rationale - backend/app/api/ai_models.py
- [[Return all available models grouped by provider (only configured ones).]] - rationale - backend/app/api/ai_models.py
- [[Return all providers with their configuration status.]] - rationale - backend/app/api/ai_models.py
- [[ai_models.py]] - code - backend/app/api/ai_models.py
- [[get_routing_recommendations()]] - code - backend/app/api/ai_models.py
- [[list_available_models()]] - code - backend/app/api/ai_models.py
- [[list_providers()]] - code - backend/app/api/ai_models.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Ai_Models
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Asyncsession_3]]
- 1 edge to [[_COMMUNITY_Any_2]]
- 1 edge to [[_COMMUNITY_unnamed_25]]

## Top bridge nodes
- [[get_routing_recommendations()]] - degree 3, connects to 1 community
- [[list_available_models()]] - degree 3, connects to 1 community
- [[list_providers()]] - degree 3, connects to 1 community