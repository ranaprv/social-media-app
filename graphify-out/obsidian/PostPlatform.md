---
source_file: "backend/app/models/post_platform.py"
type: "code"
community: "Any"
location: "L12"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/Any
---

# PostPlatform

## Connections
- [[ApproveRequest]] - `uses` [INFERRED]
- [[Base]] - `uses` [INFERRED]
- [[BulkApprove]] - `uses` [INFERRED]
- [[BulkReject]] - `uses` [INFERRED]
- [[GenerateRequest]] - `uses` [INFERRED]
- [[RejectRequest]] - `uses` [INFERRED]
- [[SlotApprove]] - `uses` [INFERRED]
- [[SlotReject]] - `uses` [INFERRED]
- [[SlotUpdate]] - `uses` [INFERRED]
- [[_auto_approve_slot()]] - `calls` [INFERRED]
- [[_handle_youtube_webhook()]] - `indirect_call` [INFERRED]
- [[_has_cycle()]] - `indirect_call` [INFERRED]
- [[add_dependency()]] - `indirect_call` [INFERRED]
- [[analyze_failure()]] - `indirect_call` [INFERRED]
- [[approve_post()_1]] - `indirect_call` [INFERRED]
- [[approve_slot()]] - `calls` [INFERRED]
- [[approve_slot()_1]] - `calls` [INFERRED]
- [[auto_apply_winner()]] - `indirect_call` [INFERRED]
- [[auto_select_winner()]] - `indirect_call` [INFERRED]
- [[bulk_cancel()]] - `indirect_call` [INFERRED]
- [[bulk_reschedule()]] - `indirect_call` [INFERRED]
- [[bulk_retry_dead_letter()]] - `indirect_call` [INFERRED]
- [[bulk_retry_failed()]] - `indirect_call` [INFERRED]
- [[bulk_schedule()]] - `indirect_call` [INFERRED]
- [[bulk_update_caption()]] - `indirect_call` [INFERRED]
- [[bulk_update_status()_1]] - `indirect_call` [INFERRED]
- [[check_dependencies_met()]] - `indirect_call` [INFERRED]
- [[check_overdue_posts()]] - `indirect_call` [INFERRED]
- [[create_ab_test()]] - `calls` [INFERRED]
- [[create_and_schedule_post()]] - `calls` [INFERRED]
- [[create_from_template()]] - `calls` [INFERRED]
- [[create_recurring_series()]] - `calls` [INFERRED]
- [[create_snapshot()]] - `indirect_call` [INFERRED]
- [[export_schedule_csv()]] - `indirect_call` [INFERRED]
- [[export_schedule_json()]] - `indirect_call` [INFERRED]
- [[export_to_csv()]] - `indirect_call` [INFERRED]
- [[find_top_performers()]] - `indirect_call` [INFERRED]
- [[generate_failure_report()]] - `indirect_call` [INFERRED]
- [[get_ab_test_results()]] - `indirect_call` [INFERRED]
- [[get_calendar_events()_1]] - `indirect_call` [INFERRED]
- [[get_dead_letter_queue()]] - `indirect_call` [INFERRED]
- [[get_dependencies()]] - `indirect_call` [INFERRED]
- [[get_error_analytics()]] - `indirect_call` [INFERRED]
- [[get_error_summary()]] - `indirect_call` [INFERRED]
- [[get_pending_approvals()]] - `indirect_call` [INFERRED]
- [[get_upcoming_reminders()]] - `indirect_call` [INFERRED]
- [[import_from_csv()]] - `calls` [INFERRED]
- [[ingest_rss_feed()]] - `calls` [INFERRED]
- [[post_platform.py]] - `contains` [EXTRACTED]
- [[reject_post()]] - `indirect_call` [INFERRED]
- [[remove_dependency()]] - `indirect_call` [INFERRED]
- [[reorder_queue()]] - `indirect_call` [INFERRED]
- [[request_approval()]] - `indirect_call` [INFERRED]
- [[reschedule_event()]] - `indirect_call` [INFERRED]
- [[retry_from_dead_letter()]] - `indirect_call` [INFERRED]
- [[rollback_to_version()]] - `indirect_call` [INFERRED]
- [[schedule_recycle()]] - `indirect_call` [INFERRED]
- [[transition_status()]] - `indirect_call` [INFERRED]

#graphify/code #graphify/INFERRED #community/Any