---
type: community
cohesion: 0.21
members: 30
---

# Content Generation

**Cohesion:** 0.21 - loosely connected
**Members:** 30 nodes

## Members
- [[Approval Workflow State Machine]] - rationale - docs/feature-specs-phase1.md
- [[Approve Action Logic]] - code - docs/feature-specs-phase1.md
- [[AsyncSession_16]] - code
- [[BaseModel_3]] - code
- [[BulkApprove]] - code - backend/app/api/content_generation.py
- [[BulkReject]] - code - backend/app/api/content_generation.py
- [[Content Generation, Scheduling, and Approval API endpoints.]] - rationale - backend/app/api/content_generation.py
- [[ContentPlan]] - code - backend/app/models/strategy.py
- [[ContentSlot]] - code - backend/app/models/strategy.py
- [[GenerateRequest]] - code - backend/app/api/content_generation.py
- [[SlotApprove]] - code - backend/app/api/content_generation.py
- [[SlotReject]] - code - backend/app/api/content_generation.py
- [[SlotUpdate]] - code - backend/app/api/content_generation.py
- [[Strategy-Driven Content Scheduling Engine models.]] - rationale - backend/app/models/strategy.py
- [[User_15]] - code
- [[_generate_recommendations()]] - code - backend/app/api/content_generation.py
- [[approve_slot()_1]] - code - backend/app/api/content_generation.py
- [[bulk_approve()]] - code - backend/app/api/content_generation.py
- [[bulk_reject()]] - code - backend/app/api/content_generation.py
- [[content_generation.py]] - code - backend/app/api/content_generation.py
- [[generate_content()]] - code - backend/app/api/content_generation.py
- [[get_adherence()]] - code - backend/app/api/content_generation.py
- [[get_plan()]] - code - backend/app/api/content_generation.py
- [[get_plan_progress()]] - code - backend/app/api/content_generation.py
- [[get_slot()]] - code - backend/app/api/content_generation.py
- [[list_plans()]] - code - backend/app/api/content_generation.py
- [[reject_slot()_1]] - code - backend/app/api/content_generation.py
- [[skip_slot()]] - code - backend/app/api/content_generation.py
- [[strategy.py]] - code - backend/app/models/strategy.py
- [[update_slot()]] - code - backend/app/api/content_generation.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Content_Generation
SORT file.name ASC
```

## Connections to other communities
- 22 edges to [[_COMMUNITY_Asyncsession_1]]
- 7 edges to [[_COMMUNITY_Asyncsession_2]]
- 7 edges to [[_COMMUNITY_Any_3]]
- 5 edges to [[_COMMUNITY_Approvals]]
- 2 edges to [[_COMMUNITY_Any]]
- 2 edges to [[_COMMUNITY_Database]]

## Top bridge nodes
- [[BulkApprove]] - degree 9, connects to 3 communities
- [[BulkReject]] - degree 9, connects to 3 communities
- [[GenerateRequest]] - degree 9, connects to 3 communities
- [[SlotApprove]] - degree 9, connects to 3 communities
- [[SlotReject]] - degree 9, connects to 3 communities