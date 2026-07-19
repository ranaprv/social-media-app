---
type: community
cohesion: 0.20
members: 10
---

# Advocacy

**Cohesion:** 0.20 - loosely connected
**Members:** 10 nodes

## Members
- [[Employee Advocacy (Amplify) — share approved content on personal networks.]] - rationale - backend/app/api/advocacy.py
- [[Get advocacy program metrics.]] - rationale - backend/app/api/advocacy.py
- [[Invite employees to join advocacy program.]] - rationale - backend/app/api/advocacy.py
- [[List content available for employee sharing.]] - rationale - backend/app/api/advocacy.py
- [[Share content to a personal social network.]] - rationale - backend/app/api/advocacy.py
- [[advocacy.py]] - code - backend/app/api/advocacy.py
- [[get_advocacy_metrics()]] - code - backend/app/api/advocacy.py
- [[invite_advocate()]] - code - backend/app/api/advocacy.py
- [[list_shareable()]] - code - backend/app/api/advocacy.py
- [[share_content()]] - code - backend/app/api/advocacy.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Advocacy
SORT file.name ASC
```
