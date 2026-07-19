---
type: community
cohesion: 0.40
members: 5
---

# Test Workspaces

**Cohesion:** 0.40 - moderately connected
**Members:** 5 nodes

## Members
- [[Tests for workspace endpoints.]] - rationale - backend/tests/test_workspaces.py
- [[test_create_workspace()]] - code - backend/tests/test_workspaces.py
- [[test_create_workspace_duplicate_slug()]] - code - backend/tests/test_workspaces.py
- [[test_list_workspaces()]] - code - backend/tests/test_workspaces.py
- [[test_workspaces.py]] - code - backend/tests/test_workspaces.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Test_Workspaces
SORT file.name ASC
```
