---
type: community
cohesion: 0.22
members: 9
---

# Bulk Scheduler

**Cohesion:** 0.22 - loosely connected
**Members:** 9 nodes

## Members
- [[AsyncSession_11]] - code
- [[Bulk scheduling — CSV upload for up to 350 posts.]] - rationale - backend/app/api/bulk_scheduler.py
- [[Download a CSV template for bulk scheduling.]] - rationale - backend/app/api/bulk_scheduler.py
- [[Upload CSV to schedule up to 350 posts at once.      CSV columns title, content]] - rationale - backend/app/api/bulk_scheduler.py
- [[UploadFile]] - code
- [[User_11]] - code
- [[bulk_scheduler.py]] - code - backend/app/api/bulk_scheduler.py
- [[bulk_upload()]] - code - backend/app/api/bulk_scheduler.py
- [[download_template()]] - code - backend/app/api/bulk_scheduler.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Bulk_Scheduler
SORT file.name ASC
```
