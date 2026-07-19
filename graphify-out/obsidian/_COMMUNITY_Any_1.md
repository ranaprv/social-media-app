---
type: community
cohesion: 0.03
members: 79
---

# Any

**Cohesion:** 0.03 - loosely connected
**Members:** 79 nodes

## Members
- [[AB Test Auto-Apply — push winning variant to all platforms.  Extends AB testin]] - rationale - backend/app/services/ab_auto_apply.py
- [[Advanced analytics — cohort analysis for audience insights.  Groups posts into c]] - rationale - backend/app/services/cohort_analysis.py
- [[Analyze content gaps and suggest missing topics.      Compares existing content]] - rationale - backend/app/services/content_gap_analyzer.py
- [[Any_3]] - code
- [[Any_34]] - code
- [[Any_38]] - code
- [[Any_43]] - code
- [[Any_49]] - code
- [[Any_100]] - code
- [[Apply the winning variant across all target platforms.      Creates new PostPlat]] - rationale - backend/app/services/ab_auto_apply.py
- [[AsyncSession_36]] - code
- [[Audience growth tracker — followersubscriber trends.  Tracks audience growth ac]] - rationale - backend/app/services/audience_growth.py
- [[Caption Variant Generator — 3-5 caption variations per platform.  Generates mult]] - rationale - backend/app/services/caption_variants.py
- [[Celery task for auto-recycling top performers.  Runs weekly to find and schedule]] - rationale - backend/app/tasks/recycle.py
- [[Celery task to collect analytics from social platforms.]] - rationale - backend/app/tasks/analytics.py
- [[Celery task to fill empty ContentSlot rows with AI-generated content. Includes a]] - rationale - backend/app/tasks/content_generation.py
- [[Celery task to publish a post to a social platform.  Uses PostPlatform rows to d]] - rationale - backend/app/tasks/publish_post.py
- [[Check content compliance across multiple platforms.]] - rationale - backend/app/services/compliance_checker.py
- [[Check content for platform compliance issues.]] - rationale - backend/app/services/compliance_checker.py
- [[Collect analytics for all workspaces with connected platforms.]] - rationale - backend/app/tasks/analytics.py
- [[Community Health Dashboard — engagement quality metrics.  Measures community hea]] - rationale - backend/app/services/community_health.py
- [[Content Audit Service — identify underperforming content.  Analyzes published co]] - rationale - backend/app/services/content_audit.py
- [[Content calendar analytics — what posted when + performance.  Provides analytics]] - rationale - backend/app/services/calendar_analytics.py
- [[Content gap analyzer — identify what topics are missing.  Analyzes existing cont]] - rationale - backend/app/services/content_gap_analyzer.py
- [[Content quality rubric — score content on 10 dimensions.  Provides detailed qual]] - rationale - backend/app/services/content_quality_rubric.py
- [[Factory that resolves the correct AI generator.  Resolution order (no hardcoded]] - rationale - backend/app/services/ai_engine/factory.py
- [[Find top performers across all workspaces and schedule recycles.]] - rationale - backend/app/tasks/recycle.py
- [[Gemini-powered generator optimised for Instagram engaging copy + image prompts.]] - rationale - backend/app/services/ai_engine/gemini_instagram.py
- [[Generate LLM content for all empty slots in a plan.      After generation, auto-]] - rationale - backend/app/tasks/content_generation.py
- [[Generate multiple caption variants for AB testing.]] - rationale - backend/app/services/caption_variants.py
- [[Log API requests with method, path, status, and duration.]] - rationale - backend/app/middleware/logging.py
- [[OmniRoute — intelligent multi-provider routing layer.  Routes requests to the op]] - rationale - backend/app/services/ai_engine/omniroute.py
- [[OpenAI-powered generator optimised for XTwitter short-form threads.]] - rationale - backend/app/services/ai_engine/openai_x.py
- [[OpenRouter-powered generator — unified access to 200+ models via openrouter.ai.]] - rationale - backend/app/services/ai_engine/openrouter.py
- [[Platform compliance checker — validate content against platform ToS.  Checks con]] - rationale - backend/app/services/compliance_checker.py
- [[Posting schedule optimizer — ML-based time selection.  Uses historical engagemen]] - rationale - backend/app/services/schedule_optimizer.py
- [[Predict viral potential of content (0-100 score).      Analyzes multiple factors]] - rationale - backend/app/services/viral_score.py
- [[Publish a PostPlatform to the specified platform.      Args         post_id Th]] - rationale - backend/app/tasks/publish_post.py
- [[ROI Calculator — social media revenue attribution.  Calculates return on investm]] - rationale - backend/app/services/roi_calculator.py
- [[Request_4]] - code
- [[Requestresponse logging middleware.]] - rationale - backend/app/middleware/logging.py
- [[Score content across 10 quality dimensions.      Returns dimension scores (0-100]] - rationale - backend/app/services/content_quality_rubric.py
- [[Social Publishers]] - code - backend/app/services/publishers/__init__.py
- [[Viral Score Predictor — predict shareability before publishing.  Analyzes conten]] - rationale - backend/app/services/viral_score.py
- [[ab_auto_apply.py]] - code - backend/app/services/ab_auto_apply.py
- [[analytics.py]] - code - backend/app/tasks/analytics.py
- [[analyze_content_gaps()]] - code - backend/app/services/content_gap_analyzer.py
- [[audience_growth.py]] - code - backend/app/services/audience_growth.py
- [[auto_apply_winner()]] - code - backend/app/services/ab_auto_apply.py
- [[auto_recycle_posts()]] - code - backend/app/tasks/recycle.py
- [[calendar_analytics.py]] - code - backend/app/services/calendar_analytics.py
- [[caption_variants.py]] - code - backend/app/services/caption_variants.py
- [[check_all_platforms()]] - code - backend/app/services/compliance_checker.py
- [[check_compliance()]] - code - backend/app/services/compliance_checker.py
- [[cohort_analysis.py]] - code - backend/app/services/cohort_analysis.py
- [[collect_all_analytics()]] - code - backend/app/tasks/analytics.py
- [[community_health.py]] - code - backend/app/services/community_health.py
- [[compliance_checker.py]] - code - backend/app/services/compliance_checker.py
- [[content_audit.py]] - code - backend/app/services/content_audit.py
- [[content_gap_analyzer.py]] - code - backend/app/services/content_gap_analyzer.py
- [[content_generation.py_1]] - code - backend/app/tasks/content_generation.py
- [[content_quality_rubric.py]] - code - backend/app/services/content_quality_rubric.py
- [[factory.py]] - code - backend/app/services/ai_engine/factory.py
- [[gemini_instagram.py]] - code - backend/app/services/ai_engine/gemini_instagram.py
- [[generate_caption_variants()]] - code - backend/app/services/caption_variants.py
- [[generate_content_for_plan()]] - code - backend/app/tasks/content_generation.py
- [[log_requests()]] - code - backend/app/middleware/logging.py
- [[logging.py]] - code - backend/app/middleware/logging.py
- [[omniroute.py]] - code - backend/app/services/ai_engine/omniroute.py
- [[openai_x.py]] - code - backend/app/services/ai_engine/openai_x.py
- [[openrouter.py]] - code - backend/app/services/ai_engine/openrouter.py
- [[predict_viral_score()]] - code - backend/app/services/viral_score.py
- [[publish_post()]] - code - backend/app/tasks/publish_post.py
- [[publish_post.py]] - code - backend/app/tasks/publish_post.py
- [[recycle.py]] - code - backend/app/tasks/recycle.py
- [[roi_calculator.py]] - code - backend/app/services/roi_calculator.py
- [[schedule_optimizer.py]] - code - backend/app/services/schedule_optimizer.py
- [[score_content_rubric()]] - code - backend/app/services/content_quality_rubric.py
- [[viral_score.py]] - code - backend/app/services/viral_score.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Any
SORT file.name ASC
```

## Connections to other communities
- 13 edges to [[_COMMUNITY_Any]]
- 7 edges to [[_COMMUNITY_Any_3]]
- 7 edges to [[_COMMUNITY_Any_2]]
- 5 edges to [[_COMMUNITY_unnamed_5]]
- 5 edges to [[_COMMUNITY_Any_4]]
- 4 edges to [[_COMMUNITY_Asyncsession_3]]
- 4 edges to [[_COMMUNITY_unnamed_25]]
- 3 edges to [[_COMMUNITY_Asyncsession_2]]
- 2 edges to [[_COMMUNITY_Any_5]]
- 1 edge to [[_COMMUNITY_Ai Keys]]
- 1 edge to [[_COMMUNITY_Connections Callback]]
- 1 edge to [[_COMMUNITY_Webhooks]]
- 1 edge to [[_COMMUNITY_Env]]
- 1 edge to [[_COMMUNITY_unnamed_55]]
- 1 edge to [[_COMMUNITY_unnamed_78]]
- 1 edge to [[_COMMUNITY_Ai Calendar Generator]]
- 1 edge to [[_COMMUNITY_Analytics Collector]]
- 1 edge to [[_COMMUNITY_Analytics Feedback]]
- 1 edge to [[_COMMUNITY_Asyncsession_1]]
- 1 edge to [[_COMMUNITY_Audience Persona]]
- 1 edge to [[_COMMUNITY_Auto Ab Winner]]
- 1 edge to [[_COMMUNITY_Automation Rules]]
- 1 edge to [[_COMMUNITY_Batch Helper]]
- 1 edge to [[_COMMUNITY_Batch Planner]]
- 1 edge to [[_COMMUNITY_Benchmarking]]
- 1 edge to [[_COMMUNITY_Brand Voice Checker]]
- 1 edge to [[_COMMUNITY_Calendar Service]]
- 1 edge to [[_COMMUNITY_Competitor Tracking]]
- 1 edge to [[_COMMUNITY_Content Brief]]
- 1 edge to [[_COMMUNITY_Content Forecast]]
- 1 edge to [[_COMMUNITY_Content Performance Engine]]
- 1 edge to [[_COMMUNITY_Content Pillar Manager]]
- 1 edge to [[_COMMUNITY_Content Repurposing Engine]]
- 1 edge to [[_COMMUNITY_Content Scorer]]
- 1 edge to [[_COMMUNITY_Content Series]]
- 1 edge to [[_COMMUNITY_Postversion]]
- 1 edge to [[_COMMUNITY_Crisis Playbook]]
- 1 edge to [[_COMMUNITY_Cta Library]]
- 1 edge to [[_COMMUNITY_Dead Letter Queue]]
- 1 edge to [[_COMMUNITY_Error Dashboard]]
- 1 edge to [[_COMMUNITY_unnamed_83]]
- 1 edge to [[_COMMUNITY_Hashtag Performance]]
- 1 edge to [[_COMMUNITY_Hashtag Strategist]]
- 1 edge to [[_COMMUNITY_Influencer Discovery]]
- 1 edge to [[_COMMUNITY_Link Shortener]]
- 1 edge to [[_COMMUNITY_Media Optimizer]]
- 1 edge to [[_COMMUNITY_Multilang Translator]]
- 1 edge to [[_COMMUNITY_Notifications]]
- 1 edge to [[_COMMUNITY_Platform Deep Features]]
- 1 edge to [[_COMMUNITY_Platform Health]]
- 1 edge to [[_COMMUNITY_Post Preview]]
- 1 edge to [[_COMMUNITY_unnamed_65]]
- 1 edge to [[_COMMUNITY_unnamed_72]]
- 1 edge to [[_COMMUNITY_unnamed_66]]
- 1 edge to [[_COMMUNITY_unnamed_81]]
- 1 edge to [[_COMMUNITY_unnamed_84]]
- 1 edge to [[_COMMUNITY_unnamed_74]]
- 1 edge to [[_COMMUNITY_Queue Manager]]
- 1 edge to [[_COMMUNITY_Rate Limit Tracker]]
- 1 edge to [[_COMMUNITY_Recurring Series]]
- 1 edge to [[_COMMUNITY_Reply Queue]]
- 1 edge to [[_COMMUNITY_Report Generator]]
- 1 edge to [[_COMMUNITY_Review Checklist]]
- 1 edge to [[_COMMUNITY_Rss Ingestion]]
- 1 edge to [[_COMMUNITY_Smart Rules]]
- 1 edge to [[_COMMUNITY_Social Listening]]
- 1 edge to [[_COMMUNITY_Social Proof]]
- 1 edge to [[_COMMUNITY_Sse Events]]
- 1 edge to [[_COMMUNITY_unnamed_95]]
- 1 edge to [[_COMMUNITY_Story Templates]]
- 1 edge to [[_COMMUNITY_Timezone Scheduler]]
- 1 edge to [[_COMMUNITY_Ugc Campaigns]]
- 1 edge to [[_COMMUNITY_Utm Builder]]
- 1 edge to [[_COMMUNITY_Visual Guidelines]]
- 1 edge to [[_COMMUNITY_Webhook Receiver]]
- 1 edge to [[_COMMUNITY_Workspace Settings]]
- 1 edge to [[_COMMUNITY_Publish Media]]

## Top bridge nodes
- [[logging.py]] - degree 126, connects to 77 communities
- [[auto_apply_winner()]] - degree 5, connects to 1 community
- [[generate_caption_variants()]] - degree 4, connects to 1 community
- [[analyze_content_gaps()]] - degree 4, connects to 1 community
- [[content_generation.py_1]] - degree 4, connects to 1 community