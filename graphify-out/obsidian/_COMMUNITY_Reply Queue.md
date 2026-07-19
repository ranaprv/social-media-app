---
type: community
cohesion: 0.27
members: 10
---

# Reply Queue

**Cohesion:** 0.27 - loosely connected
**Members:** 10 nodes

## Members
- [[Any_85]] - code
- [[AsyncSession_81]] - code
- [[Create and send a reply to a mentioncomment.]] - rationale - backend/app/services/reply_queue.py
- [[Get all reply templates.]] - rationale - backend/app/services/reply_queue.py
- [[Get items in the reply queue.]] - rationale - backend/app/services/reply_queue.py
- [[Reply Queue — centralized commentmention management with templates.  Manages in]] - rationale - backend/app/services/reply_queue.py
- [[create_reply()]] - code - backend/app/services/reply_queue.py
- [[get_reply_queue()]] - code - backend/app/services/reply_queue.py
- [[get_reply_templates()]] - code - backend/app/services/reply_queue.py
- [[reply_queue.py]] - code - backend/app/services/reply_queue.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Reply_Queue
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Any_1]]
- 1 edge to [[_COMMUNITY_Any_4]]

## Top bridge nodes
- [[reply_queue.py]] - degree 5, connects to 1 community
- [[create_reply()]] - degree 5, connects to 1 community