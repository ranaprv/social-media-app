---
type: community
cohesion: 0.19
members: 18
---

# Listening

**Cohesion:** 0.19 - loosely connected
**Members:** 18 nodes

## Members
- [[AsyncSession_19]] - code
- [[Create a new listening alert.]] - rationale - backend/app/api/listening.py
- [[Delete a listening alert.]] - rationale - backend/app/api/listening.py
- [[Get trend summary — mentions over time, sentiment distribution, keyword cloud.]] - rationale - backend/app/api/listening.py
- [[List all listening alerts for the workspace.]] - rationale - backend/app/api/listening.py
- [[List mentions from listening alerts.]] - rationale - backend/app/api/listening.py
- [[Manually trigger a scan for a specific keyword.]] - rationale - backend/app/api/listening.py
- [[Social Listening API — alerts, mentions, trend discovery.]] - rationale - backend/app/api/listening.py
- [[Toggle alert active status.]] - rationale - backend/app/api/listening.py
- [[User_18]] - code
- [[create_alert()]] - code - backend/app/api/listening.py
- [[delete_alert()]] - code - backend/app/api/listening.py
- [[get_trends()]] - code - backend/app/api/listening.py
- [[list_alerts()]] - code - backend/app/api/listening.py
- [[list_mentions()]] - code - backend/app/api/listening.py
- [[listening.py]] - code - backend/app/api/listening.py
- [[toggle_alert()]] - code - backend/app/api/listening.py
- [[trigger_scan()]] - code - backend/app/api/listening.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Listening
SORT file.name ASC
```

## Connections to other communities
- 3 edges to [[_COMMUNITY_Any]]

## Top bridge nodes
- [[get_trends()]] - degree 5, connects to 1 community
- [[list_alerts()]] - degree 5, connects to 1 community
- [[list_mentions()]] - degree 5, connects to 1 community