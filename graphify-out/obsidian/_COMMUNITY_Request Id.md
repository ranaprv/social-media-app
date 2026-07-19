---
type: community
cohesion: 0.29
members: 7
---

# Request Id

**Cohesion:** 0.29 - loosely connected
**Members:** 7 nodes

## Members
- [[.dispatch()_1]] - code - backend/app/middleware/request_id.py
- [[Add unique request ID to every requestresponse cycle.]] - rationale - backend/app/middleware/request_id.py
- [[BaseHTTPMiddleware_1]] - code
- [[Request_6]] - code
- [[Request ID middleware — generates and propagates correlation IDs.  Every request]] - rationale - backend/app/middleware/request_id.py
- [[RequestIDMiddleware]] - code - backend/app/middleware/request_id.py
- [[request_id.py]] - code - backend/app/middleware/request_id.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Request_Id
SORT file.name ASC
```
