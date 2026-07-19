---
type: community
cohesion: 0.20
members: 14
---

# Sse Events

**Cohesion:** 0.20 - loosely connected
**Members:** 14 nodes

## Members
- [[Any_94]] - code
- [[Notify subscribers that a publish failed.]] - rationale - backend/app/services/sse_events.py
- [[Notify subscribers that a publish has started.]] - rationale - backend/app/services/sse_events.py
- [[Notify subscribers that the queue has been updated.]] - rationale - backend/app/services/sse_events.py
- [[Publish an event to all subscribers of a workspace.]] - rationale - backend/app/services/sse_events.py
- [[SSE (Server-Sent Events) — live queue status updates.  Provides real-time update]] - rationale - backend/app/services/sse_events.py
- [[Subscribe to events for a workspace. Yields SSE-formatted strings.]] - rationale - backend/app/services/sse_events.py
- [[notify_publish_completed()]] - code - backend/app/services/sse_events.py
- [[notify_publish_failed()]] - code - backend/app/services/sse_events.py
- [[notify_publish_started()]] - code - backend/app/services/sse_events.py
- [[notify_queue_updated()]] - code - backend/app/services/sse_events.py
- [[publish_event()]] - code - backend/app/services/sse_events.py
- [[sse_events.py]] - code - backend/app/services/sse_events.py
- [[subscribe_events()]] - code - backend/app/services/sse_events.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Sse_Events
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Any_1]]

## Top bridge nodes
- [[sse_events.py]] - degree 8, connects to 1 community