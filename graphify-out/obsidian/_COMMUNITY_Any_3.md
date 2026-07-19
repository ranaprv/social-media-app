---
type: community
cohesion: 0.05
members: 65
---

# Any

**Cohesion:** 0.05 - loosely connected
**Members:** 65 nodes

## Members
- [[AB content testing — schedule variant posts and track winner selection.  Create]] - rationale - backend/app/services/ab_testing.py
- [[Add a dependency post_id cannot be published until depends_on_post_id is publis]] - rationale - backend/app/services/content_dependencies.py
- [[Analyze a specific failed publish attempt.]] - rationale - backend/app/services/postmortem.py
- [[Any_4]] - code
- [[Any_27]] - code
- [[Any_28]] - code
- [[Any_30]] - code
- [[Any_41]] - code
- [[Any_75]] - code
- [[AsyncSession_37]] - code
- [[AsyncSession_48]] - code
- [[AsyncSession_49]] - code
- [[AsyncSession_51]] - code
- [[AsyncSession_59]] - code
- [[AsyncSession_78]] - code
- [[Automated content calendar reminders.  Sends reminders for upcoming posts, deadl]] - rationale - backend/app/services/calendar_reminders.py
- [[Bulk import service — import content from CSVGoogle Sheets.  Supports importing]] - rationale - backend/app/services/bulk_import.py
- [[Bulk operations — schedule, publish, cancel in batch.  Efficiently handle bulk o]] - rationale - backend/app/services/bulk_operations.py
- [[Cancel multiple scheduled items.]] - rationale - backend/app/services/bulk_operations.py
- [[Check for posts that are overdue (past scheduled_at but not published).]] - rationale - backend/app/services/calendar_reminders.py
- [[Check if adding from_post - to_post would create a cycle.]] - rationale - backend/app/services/content_dependencies.py
- [[Check if all dependencies for a post are met (all deps published).]] - rationale - backend/app/services/content_dependencies.py
- [[Content dependency scheduler — post A before post B.  Manages dependencies betwe]] - rationale - backend/app/services/content_dependencies.py
- [[Create an AB test with multiple caption variants.      Each variant gets its ow]] - rationale - backend/app/services/ab_testing.py
- [[Export posts to CSV format.]] - rationale - backend/app/services/bulk_import.py
- [[Generate a failure analysis report.]] - rationale - backend/app/services/postmortem.py
- [[Get AB test results by comparing variant performance.      Queries analytics fo]] - rationale - backend/app/services/ab_testing.py
- [[Get all dependencies for a post (what it depends on and what depends on it).]] - rationale - backend/app/services/content_dependencies.py
- [[Get upcoming reminders for posts due in the next N hours.]] - rationale - backend/app/services/calendar_reminders.py
- [[Import posts from CSV content.      Expected CSV columns title, content, platfo]] - rationale - backend/app/services/bulk_import.py
- [[PostPlatform]] - code - backend/app/models/post_platform.py
- [[PostPlatform — per-platform scheduling and publishing state.  One Post can targe]] - rationale - backend/app/models/post_platform.py
- [[Postmortem service — auto-analyze failed publishes.  Analyzes failed publish att]] - rationale - backend/app/services/postmortem.py
- [[Remove a dependency between two posts.]] - rationale - backend/app/services/content_dependencies.py
- [[Reschedule multiple items with staggered times.]] - rationale - backend/app/services/bulk_operations.py
- [[Schedule multiple posts to multiple platforms in one operation.]] - rationale - backend/app/services/bulk_operations.py
- [[Update captions for multiple items using a template.      Template supports plac]] - rationale - backend/app/services/bulk_operations.py
- [[_categorize()]] - code - backend/app/services/postmortem.py
- [[_determine_root_cause()]] - code - backend/app/services/postmortem.py
- [[_has_cycle()]] - code - backend/app/services/content_dependencies.py
- [[_suggest_fix()]] - code - backend/app/services/postmortem.py
- [[ab_testing.py]] - code - backend/app/services/ab_testing.py
- [[add_dependency()]] - code - backend/app/services/content_dependencies.py
- [[analyze_failure()]] - code - backend/app/services/postmortem.py
- [[bulk_cancel()]] - code - backend/app/services/bulk_operations.py
- [[bulk_import.py]] - code - backend/app/services/bulk_import.py
- [[bulk_operations.py]] - code - backend/app/services/bulk_operations.py
- [[bulk_reschedule()]] - code - backend/app/services/bulk_operations.py
- [[bulk_schedule()]] - code - backend/app/services/bulk_operations.py
- [[bulk_update_caption()]] - code - backend/app/services/bulk_operations.py
- [[calendar_reminders.py]] - code - backend/app/services/calendar_reminders.py
- [[check_dependencies_met()]] - code - backend/app/services/content_dependencies.py
- [[check_overdue_posts()]] - code - backend/app/services/calendar_reminders.py
- [[content_dependencies.py]] - code - backend/app/services/content_dependencies.py
- [[create_ab_test()]] - code - backend/app/services/ab_testing.py
- [[datetime_2]] - code
- [[export_to_csv()]] - code - backend/app/services/bulk_import.py
- [[generate_failure_report()]] - code - backend/app/services/postmortem.py
- [[get_ab_test_results()]] - code - backend/app/services/ab_testing.py
- [[get_dependencies()]] - code - backend/app/services/content_dependencies.py
- [[get_upcoming_reminders()]] - code - backend/app/services/calendar_reminders.py
- [[import_from_csv()]] - code - backend/app/services/bulk_import.py
- [[post_platform.py]] - code - backend/app/models/post_platform.py
- [[postmortem.py]] - code - backend/app/services/postmortem.py
- [[remove_dependency()]] - code - backend/app/services/content_dependencies.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Any
SORT file.name ASC
```

## Connections to other communities
- 8 edges to [[_COMMUNITY_Any]]
- 7 edges to [[_COMMUNITY_Content Generation]]
- 7 edges to [[_COMMUNITY_Any_1]]
- 5 edges to [[_COMMUNITY_Asyncsession_2]]
- 4 edges to [[_COMMUNITY_Asyncsession_1]]
- 4 edges to [[_COMMUNITY_Dead Letter Queue]]
- 3 edges to [[_COMMUNITY_Approvals]]
- 2 edges to [[_COMMUNITY_Calendar Service]]
- 2 edges to [[_COMMUNITY_Any_4]]
- 2 edges to [[_COMMUNITY_Postversion]]
- 2 edges to [[_COMMUNITY_Error Dashboard]]
- 2 edges to [[_COMMUNITY_Queue Manager]]
- 1 edge to [[_COMMUNITY_Database]]
- 1 edge to [[_COMMUNITY_Auto Ab Winner]]
- 1 edge to [[_COMMUNITY_Recurring Series]]
- 1 edge to [[_COMMUNITY_Rss Ingestion]]
- 1 edge to [[_COMMUNITY_Webhook Receiver]]

## Top bridge nodes
- [[PostPlatform]] - degree 58, connects to 17 communities
- [[create_ab_test()]] - degree 7, connects to 2 communities
- [[generate_failure_report()]] - degree 8, connects to 1 community
- [[bulk_operations.py]] - degree 7, connects to 1 community
- [[bulk_reschedule()]] - degree 7, connects to 1 community