---
type: community
cohesion: 0.17
members: 17
---

# Ai Keys

**Cohesion:** 0.17 - loosely connected
**Members:** 17 nodes

## Members
- [[API for managing AI provider API keys — stored in DB, not .env.]] - rationale - backend/app/api/ai_keys.py
- [[APIKeyPayload]] - code - backend/app/api/ai_keys.py
- [[BaseModel]] - code
- [[Get API key from in-memory store, falling back to env var.]] - rationale - backend/app/api/ai_keys.py
- [[List all providers and their key status.      Returns only a fingerprint hash —]] - rationale - backend/app/api/ai_keys.py
- [[Remove an API key for a provider.]] - rationale - backend/app/api/ai_keys.py
- [[Return a short SHA-256 fingerprint — safe to show in UI.]] - rationale - backend/app/api/ai_keys.py
- [[Save an API key for a provider. Returns fingerprint only.]] - rationale - backend/app/api/ai_keys.py
- [[Store key in memory and set env var for existing services.]] - rationale - backend/app/api/ai_keys.py
- [[User_3]] - code
- [[_apply_key()]] - code - backend/app/api/ai_keys.py
- [[_fingerprint()]] - code - backend/app/api/ai_keys.py
- [[_get_stored_key()]] - code - backend/app/api/ai_keys.py
- [[ai_keys.py]] - code - backend/app/api/ai_keys.py
- [[delete_key()]] - code - backend/app/api/ai_keys.py
- [[list_keys()]] - code - backend/app/api/ai_keys.py
- [[save_key()]] - code - backend/app/api/ai_keys.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Ai_Keys
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Any_1]]
- 1 edge to [[_COMMUNITY_Asyncsession_1]]

## Top bridge nodes
- [[ai_keys.py]] - degree 9, connects to 1 community
- [[APIKeyPayload]] - degree 4, connects to 1 community