---
type: community
cohesion: 0.18
members: 19
---

# Approvals

**Cohesion:** 0.18 - loosely connected
**Members:** 19 nodes

## Members
- [[Approval stats count of slots by status.]] - rationale - backend/app/api/approvals.py
- [[Approve a pending ContentSlot and create Post + PostPlatform rows.]] - rationale - backend/app/api/approvals.py
- [[ApproveRequest]] - code - backend/app/api/approvals.py
- [[AsyncSession_7]] - code
- [[BaseModel_2]] - code
- [[Create an approval workflow template.]] - rationale - backend/app/api/approvals.py
- [[List ContentSlots awaiting approval (status = pending_approval).]] - rationale - backend/app/api/approvals.py
- [[List approval workflow templates.]] - rationale - backend/app/api/approvals.py
- [[Multi-Tier Approval Workflows — DB-backed approval queue.  Replaced hardcoded mo]] - rationale - backend/app/api/approvals.py
- [[Reject a pending ContentSlot and return it to draft.]] - rationale - backend/app/api/approvals.py
- [[RejectRequest]] - code - backend/app/api/approvals.py
- [[User_7]] - code
- [[approvals.py]] - code - backend/app/api/approvals.py
- [[approve_slot()]] - code - backend/app/api/approvals.py
- [[create_workflow()]] - code - backend/app/api/approvals.py
- [[get_approval_stats()]] - code - backend/app/api/approvals.py
- [[list_pending_approvals()]] - code - backend/app/api/approvals.py
- [[list_workflows()]] - code - backend/app/api/approvals.py
- [[reject_slot()]] - code - backend/app/api/approvals.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Approvals
SORT file.name ASC
```

## Connections to other communities
- 6 edges to [[_COMMUNITY_Asyncsession_1]]
- 5 edges to [[_COMMUNITY_Content Generation]]
- 3 edges to [[_COMMUNITY_Asyncsession_2]]
- 3 edges to [[_COMMUNITY_Any_3]]
- 1 edge to [[_COMMUNITY_Any]]

## Top bridge nodes
- [[approve_slot()]] - degree 9, connects to 4 communities
- [[ApproveRequest]] - degree 7, connects to 4 communities
- [[RejectRequest]] - degree 7, connects to 4 communities
- [[reject_slot()]] - degree 7, connects to 2 communities
- [[get_approval_stats()]] - degree 6, connects to 2 communities