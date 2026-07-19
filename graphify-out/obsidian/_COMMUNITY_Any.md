---
type: community
cohesion: 0.03
members: 84
---

# Any

**Cohesion:** 0.03 - loosely connected
**Members:** 84 nodes

## Members
- [[Admin dashboard metrics — real-time system health and usage stats.  Provides wor]] - rationale - backend/app/services/admin_metrics.py
- [[Analyze actual post performance to recommend best scheduling times.      Queries]] - rationale - backend/app/services/best_time_recommender.py
- [[Any_5]] - code
- [[Any_17]] - code
- [[Any_25]] - code
- [[Any_29]] - code
- [[Any_35]] - code
- [[Any_36]] - code
- [[Any_39]] - code
- [[Any_50]] - code
- [[Any_62]] - code
- [[Any_64]] - code
- [[Any_88]] - code
- [[Any_90]] - code
- [[Any_96]] - code
- [[AsyncSession_38]] - code
- [[AsyncSession_43]] - code
- [[AsyncSession_47]] - code
- [[AsyncSession_50]] - code
- [[AsyncSession_54]] - code
- [[AsyncSession_55]] - code
- [[AsyncSession_57]] - code
- [[AsyncSession_65]] - code
- [[AsyncSession_72]] - code
- [[AsyncSession_74]] - code
- [[AsyncSession_83]] - code
- [[AsyncSession_85]] - code
- [[AsyncSession_88]] - code
- [[Audit content performance and identify issues.      Finds       - Underperformi]] - rationale - backend/app/services/content_audit.py
- [[Automatically schedule recycling for top performers.      Finds the best posts a]] - rationale - backend/app/services/content_recycler.py
- [[Build an optimized posting schedule using historical data.      Uses a weighted]] - rationale - backend/app/services/schedule_optimizer.py
- [[Calculate social media ROI.]] - rationale - backend/app/services/roi_calculator.py
- [[Content recycling — reshare top performers.  Finds posts with high engagement, c]] - rationale - backend/app/services/content_recycler.py
- [[Create a new PostPlatform entry to reshare a top performer.      The new entry g]] - rationale - backend/app/services/content_recycler.py
- [[Data-driven best-time recommender.  Analyzes AnalyticsMetric records to find whe]] - rationale - backend/app/services/best_time_recommender.py
- [[Engagement tracker — monitor comments, mentions, replies.  Tracks engagement sig]] - rationale - backend/app/services/engagement_tracker.py
- [[Export analytics data as CSV.]] - rationale - backend/app/services/export_service.py
- [[Export scheduling data as CSV.]] - rationale - backend/app/services/export_service.py
- [[Export scheduling data as structured JSON.]] - rationale - backend/app/services/export_service.py
- [[Export service — CSVJSON scheduling reports.  Exports scheduling data, analytic]] - rationale - backend/app/services/export_service.py
- [[Find top-performing posts eligible for recycling.      Criteria       - Publish]] - rationale - backend/app/services/content_recycler.py
- [[Get analytics about posting patterns and performance.]] - rationale - backend/app/services/calendar_analytics.py
- [[Get audience growth trends across platforms.]] - rationale - backend/app/services/audience_growth.py
- [[Get community health metrics.]] - rationale - backend/app/services/community_health.py
- [[Get comprehensive workspace metrics for the admin dashboard.]] - rationale - backend/app/services/admin_metrics.py
- [[Get current workload distribution across team members.]] - rationale - backend/app/services/team_workload.py
- [[Get engagement summary for the workspace.]] - rationale - backend/app/services/engagement_tracker.py
- [[Get posts with highest engagement.]] - rationale - backend/app/services/engagement_tracker.py
- [[Get system-wide health metrics across all workspaces.]] - rationale - backend/app/services/admin_metrics.py
- [[Get the next optimal time slot to schedule a post for a platform.      Looks at]] - rationale - backend/app/services/best_time_recommender.py
- [[Perform cohort analysis on published posts.      Cohort options       - platfor]] - rationale - backend/app/services/cohort_analysis.py
- [[PostPlatform_1]] - code
- [[Suggest how to distribute new posts across team members.]] - rationale - backend/app/services/team_workload.py
- [[Team workload balancer — distribute posts across team members.  Analyzes team ca]] - rationale - backend/app/services/team_workload.py
- [[admin_metrics.py]] - code - backend/app/services/admin_metrics.py
- [[audit_content()]] - code - backend/app/services/content_audit.py
- [[auto_recycle_top_performers()]] - code - backend/app/services/content_recycler.py
- [[best_time_recommender.py]] - code - backend/app/services/best_time_recommender.py
- [[calculate_roi()]] - code - backend/app/services/roi_calculator.py
- [[cohort_analysis()]] - code - backend/app/services/cohort_analysis.py
- [[content_recycler.py]] - code - backend/app/services/content_recycler.py
- [[datetime_5]] - code
- [[datetime_6]] - code
- [[engagement_tracker.py]] - code - backend/app/services/engagement_tracker.py
- [[export_analytics_csv()]] - code - backend/app/services/export_service.py
- [[export_schedule_csv()]] - code - backend/app/services/export_service.py
- [[export_schedule_json()]] - code - backend/app/services/export_service.py
- [[export_service.py]] - code - backend/app/services/export_service.py
- [[find_top_performers()]] - code - backend/app/services/content_recycler.py
- [[get_audience_growth()]] - code - backend/app/services/audience_growth.py
- [[get_best_times_for_workspace()]] - code - backend/app/services/best_time_recommender.py
- [[get_calendar_analytics()]] - code - backend/app/services/calendar_analytics.py
- [[get_community_health()]] - code - backend/app/services/community_health.py
- [[get_engagement_summary()]] - code - backend/app/services/engagement_tracker.py
- [[get_next_suggested_time()]] - code - backend/app/services/best_time_recommender.py
- [[get_system_health()]] - code - backend/app/services/admin_metrics.py
- [[get_team_workload()]] - code - backend/app/services/team_workload.py
- [[get_top_engaging_posts()]] - code - backend/app/services/engagement_tracker.py
- [[get_workspace_metrics()]] - code - backend/app/services/admin_metrics.py
- [[optimize_schedule()]] - code - backend/app/services/schedule_optimizer.py
- [[schedule_recycle()]] - code - backend/app/services/content_recycler.py
- [[suggest_assignments()]] - code - backend/app/services/team_workload.py
- [[team_workload.py]] - code - backend/app/services/team_workload.py
- [[timedelta]] - code

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Any
SORT file.name ASC
```

## Connections to other communities
- 13 edges to [[_COMMUNITY_Any_1]]
- 10 edges to [[_COMMUNITY_Asyncsession_1]]
- 10 edges to [[_COMMUNITY_Asyncsession_2]]
- 8 edges to [[_COMMUNITY_Any_3]]
- 5 edges to [[_COMMUNITY_Any_4]]
- 4 edges to [[_COMMUNITY_Asyncsession]]
- 4 edges to [[_COMMUNITY_Team]]
- 3 edges to [[_COMMUNITY_Connections Callback]]
- 3 edges to [[_COMMUNITY_Listening]]
- 3 edges to [[_COMMUNITY_Security Api]]
- 2 edges to [[_COMMUNITY_Competitors]]
- 2 edges to [[_COMMUNITY_Content Generation]]
- 2 edges to [[_COMMUNITY_Dead Letter Queue]]
- 2 edges to [[_COMMUNITY_Error Dashboard]]
- 2 edges to [[_COMMUNITY_Hashtag Performance]]
- 2 edges to [[_COMMUNITY_Queue Manager]]
- 2 edges to [[_COMMUNITY_Rate Limit Tracker]]
- 1 edge to [[_COMMUNITY_Ads]]
- 1 edge to [[_COMMUNITY_Approvals]]
- 1 edge to [[_COMMUNITY_Calendar]]
- 1 edge to [[_COMMUNITY_Inbox]]
- 1 edge to [[_COMMUNITY_Media]]
- 1 edge to [[_COMMUNITY_Tasks]]
- 1 edge to [[_COMMUNITY_Web Analytics]]
- 1 edge to [[_COMMUNITY_Analytics Feedback]]
- 1 edge to [[_COMMUNITY_Calendar Service]]
- 1 edge to [[_COMMUNITY_Content Forecast]]
- 1 edge to [[_COMMUNITY_Content Performance Engine]]
- 1 edge to [[_COMMUNITY_Recurring Series]]
- 1 edge to [[_COMMUNITY_Report Generator]]
- 1 edge to [[_COMMUNITY_Smart Rules]]
- 1 edge to [[_COMMUNITY_Asyncsession_3]]

## Top bridge nodes
- [[timedelta]] - degree 75, connects to 31 communities
- [[find_top_performers()]] - degree 8, connects to 2 communities
- [[schedule_recycle()]] - degree 8, connects to 2 communities
- [[export_schedule_json()]] - degree 8, connects to 2 communities
- [[get_best_times_for_workspace()]] - degree 7, connects to 2 communities