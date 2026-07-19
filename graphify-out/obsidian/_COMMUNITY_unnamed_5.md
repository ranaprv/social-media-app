---
type: community
cohesion: 0.03
members: 122
---

# 

**Cohesion:** 0.03 - loosely connected
**Members:** 122 nodes

## Members
- [[TODO extract workspace_id from auth context  JWT]] - rationale - backend/app/api/ai_workflow.py
- [[.__init__()_5]] - code - backend/app/services/ai_engine/openai_x.py
- [[.__init__()_6]] - code - backend/app/services/ai_engine/openrouter.py
- [[.__init__()_8]] - code - backend/app/services/orchestrator.py
- [[.__repr__()]] - code - backend/app/services/ai_engine/base.py
- [[._advance()]] - code - backend/app/services/orchestrator.py
- [[._bootstrap_registry()]] - code - backend/app/services/ai_engine/factory.py
- [[._build_system_prompt()]] - code - backend/app/services/ai_engine/base.py
- [[._instantiate()]] - code - backend/app/services/ai_engine/factory.py
- [[._resolve_provider_from_db()]] - code - backend/app/services/ai_engine/factory.py
- [[._stage_draft()]] - code - backend/app/services/orchestrator.py
- [[._stage_hitl_staging()]] - code - backend/app/services/orchestrator.py
- [[._stage_research()]] - code - backend/app/services/orchestrator.py
- [[._stage_save_to_db()]] - code - backend/app/services/orchestrator.py
- [[._stage_visual_prompt()]] - code - backend/app/services/orchestrator.py
- [[.create()]] - code - backend/app/services/ai_engine/factory.py
- [[.create_from_db()]] - code - backend/app/services/ai_engine/factory.py
- [[.current_status()]] - code - backend/app/services/orchestrator.py
- [[.final_text()]] - code - backend/app/services/orchestrator.py
- [[.generate_media_prompts()]] - code - backend/app/services/ai_engine/base.py
- [[.generate_media_prompts()_4]] - code - backend/app/services/ai_engine/openai_x.py
- [[.generate_media_prompts()_5]] - code - backend/app/services/ai_engine/openrouter.py
- [[.generated_texts()]] - code - backend/app/services/orchestrator.py
- [[.register()]] - code - backend/app/services/ai_engine/factory.py
- [[.run_workflow()]] - code - backend/app/services/orchestrator.py
- [[.to_response()]] - code - backend/app/services/orchestrator.py
- [[.visual_prompts()]] - code - backend/app/services/orchestrator.py
- [[A content idea flowing through the Research → Draft → HITL pipeline.]] - rationale - backend/app/models/ai_workflow.py
- [[A post that has been submitted to (or scheduled on) a social platform.]] - rationale - backend/app/models/ai_workflow.py
- [[AIContentGenerator]] - code - backend/app/services/ai_engine/base.py
- [[AIProvider]] - code - backend/app/schemas/ai_workflow.py
- [[Abstract base that every platform-specific generator must implement.      Contra]] - rationale - backend/app/services/ai_engine/base.py
- [[All provider configs for a workspace.]] - rationale - backend/app/schemas/ai_workflow.py
- [[AnalyticsIngestRequest]] - code - backend/app/schemas/ai_workflow.py
- [[Any]] - code
- [[Any_8]] - code
- [[Any_12]] - code
- [[Any_13]] - code
- [[AsyncSession_4]] - code
- [[AsyncSession_39]] - code
- [[AsyncSession_77]] - code
- [[Attempt a state transition; raises ``WorkflowError`` if invalid.]] - rationale - backend/app/services/orchestrator.py
- [[BaseModel_1]] - code
- [[BaseModel_6]] - code
- [[Body for upserting a provider config.]] - rationale - backend/app/api/ai_workflow.py
- [[Build a system prompt with platform-specific tone guidelines.]] - rationale - backend/app/services/ai_engine/base.py
- [[Content orchestration state machine.  Runs an async pipeline     Research → Dra]] - rationale - backend/app/services/orchestrator.py
- [[ContentIdeaRequest]] - code - backend/app/schemas/ai_workflow.py
- [[ContentItem]] - code - backend/app/models/ai_workflow.py
- [[ContentItemResponse]] - code - backend/app/schemas/ai_workflow.py
- [[ContentOrchestrator]] - code - backend/app/services/orchestrator.py
- [[ContentStatus]] - code - backend/app/schemas/ai_workflow.py
- [[Create a generator instance, passing the relevant API key.]] - rationale - backend/app/services/ai_engine/factory.py
- [[Create generator with explicit provider or first available with an API key.]] - rationale - backend/app/services/ai_engine/factory.py
- [[Create or update the AI provider for a platform within a workspace.      Called]] - rationale - backend/app/api/ai_workflow.py
- [[Creates the right ``AIContentGenerator`` instance.      Usage           With]] - rationale - backend/app/services/ai_engine/factory.py
- [[Daily raw engagement stats ingested from platform APIs.]] - rationale - backend/app/models/ai_workflow.py
- [[Drives a single content item through the generation pipeline.      Provider reso]] - rationale - backend/app/services/orchestrator.py
- [[Enum_1]] - code
- [[Exception_1]] - code
- [[Execute the full pipeline and return a trigger response.]] - rationale - backend/app/services/orchestrator.py
- [[FastAPI router for the autonomous AI content workflow pipeline.  Endpoints]] - rationale - backend/app/api/ai_workflow.py
- [[Generate image prompts optimised for XTwitter card previews.]] - rationale - backend/app/services/ai_engine/openai_x.py
- [[Generate image prompts via OpenRouter.]] - rationale - backend/app/services/ai_engine/openrouter.py
- [[GeneratedText]] - code - backend/app/schemas/ai_workflow.py
- [[Generates XTwitter posts and threads via OpenAI.]] - rationale - backend/app/services/ai_engine/openai_x.py
- [[Generates content via OpenRouter's OpenAI-compatible API.]] - rationale - backend/app/services/ai_engine/openrouter.py
- [[HITL approval payload — moves post to SCHEDULED.]] - rationale - backend/app/schemas/ai_workflow.py
- [[Imagevideo generation prompt produced during visual asset stage.]] - rationale - backend/app/schemas/ai_workflow.py
- [[Incoming request to trigger the AI content workflow.]] - rationale - backend/app/schemas/ai_workflow.py
- [[Ingest raw daily platform stats and trigger the analytics feedback loop.      1.]] - rationale - backend/app/api/ai_workflow.py
- [[Initiate the automated AI research and generation pipeline.      Provider select]] - rationale - backend/app/api/ai_workflow.py
- [[Look up the user-configured provider from the DB, fall back to first available.]] - rationale - backend/app/services/ai_engine/factory.py
- [[OpenAIXGenerator]] - code - backend/app/services/ai_engine/openai_x.py
- [[OpenRouterGenerator]] - code - backend/app/services/ai_engine/openrouter.py
- [[Output of the analytics feedback loop.]] - rationale - backend/app/schemas/ai_workflow.py
- [[Per-workspace, per-platform AI provider selection.      Users configure this via]] - rationale - backend/app/models/ai_workflow.py
- [[PerformanceScoreResponse]] - code - backend/app/schemas/ai_workflow.py
- [[PlatformAnalytics]] - code - backend/app/models/ai_workflow.py
- [[PlatformPost]] - code - backend/app/models/ai_workflow.py
- [[PlatformProviderConfig]] - code - backend/app/models/ai_workflow.py
- [[PlatformType]] - code - backend/app/schemas/ai_workflow.py
- [[PlatformWorkflowFactory]] - code - backend/app/services/ai_engine/factory.py
- [[PostApprovalRequest]] - code - backend/app/schemas/ai_workflow.py
- [[ProviderConfigBulkResponse]] - code - backend/app/schemas/ai_workflow.py
- [[ProviderConfigCreate]] - code - backend/app/schemas/ai_workflow.py
- [[ProviderConfigResponse]] - code - backend/app/schemas/ai_workflow.py
- [[ProviderConfigUpdate]] - code - backend/app/schemas/ai_workflow.py
- [[Pydantic V2 schemas for AI workflow pipeline.]] - rationale - backend/app/schemas/ai_workflow.py
- [[Query ``platform_provider_configs`` for the user's chosen provider.]] - rationale - backend/app/services/ai_engine/factory.py
- [[Raised when a state transition is invalid or a stage fails.]] - rationale - backend/app/services/orchestrator.py
- [[Raw daily stats from a platform for a single post.]] - rationale - backend/app/schemas/ai_workflow.py
- [[Representation of a content item flowing through the pipeline.]] - rationale - backend/app/schemas/ai_workflow.py
- [[Response after triggering the content workflow.]] - rationale - backend/app/schemas/ai_workflow.py
- [[Return a list of imagevideo generation prompt dicts.          Each dict must co]] - rationale - backend/app/services/ai_engine/base.py
- [[Return all provider configs for a workspace — one row per platform.      The UI]] - rationale - backend/app/api/ai_workflow.py
- [[Returned provider config for a platform.]] - rationale - backend/app/schemas/ai_workflow.py
- [[SQLAlchemy models for the autonomous AI workflow pipeline.  Tables     content_]] - rationale - backend/app/models/ai_workflow.py
- [[Set the AI provider for a specific platform within a workspace.]] - rationale - backend/app/schemas/ai_workflow.py
- [[Simulate the Human-In-The-Loop dashboard step.      Moves a post from ``PENDING_]] - rationale - backend/app/api/ai_workflow.py
- [[Snapshot of the content item as a response model.]] - rationale - backend/app/services/orchestrator.py
- [[Stage 1 Research — gather context and notes on the topic.]] - rationale - backend/app/services/orchestrator.py
- [[Stage 2 Draft — generate text content via the AI engine.]] - rationale - backend/app/services/orchestrator.py
- [[Stage 3 Generate imagevideo prompts for visual asset creation.]] - rationale - backend/app/services/orchestrator.py
- [[Stage 4 Persist the content item (mock — returns data for the API layer).]] - rationale - backend/app/services/orchestrator.py
- [[Stage 5 Place the item in the human-in-the-loop staging queue.]] - rationale - backend/app/services/orchestrator.py
- [[Text content generated by an AI provider.]] - rationale - backend/app/schemas/ai_workflow.py
- [[Update an existing provider config.]] - rationale - backend/app/schemas/ai_workflow.py
- [[VisualPrompt]] - code - backend/app/schemas/ai_workflow.py
- [[WorkflowError]] - code - backend/app/services/orchestrator.py
- [[WorkflowTriggerResponse]] - code - backend/app/schemas/ai_workflow.py
- [[_UpsertBody]] - code - backend/app/api/ai_workflow.py
- [[ai_workflow.py]] - code - backend/app/api/ai_workflow.py
- [[ai_workflow.py_1]] - code - backend/app/models/ai_workflow.py
- [[ai_workflow.py_2]] - code - backend/app/schemas/ai_workflow.py
- [[approve_post()]] - code - backend/app/api/ai_workflow.py
- [[ingest_analytics()]] - code - backend/app/api/ai_workflow.py
- [[list_provider_configs()]] - code - backend/app/api/ai_workflow.py
- [[orchestrator.py]] - code - backend/app/services/orchestrator.py
- [[str]] - code
- [[trigger_workflow()]] - code - backend/app/api/ai_workflow.py
- [[upsert_provider_config()]] - code - backend/app/api/ai_workflow.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/
SORT file.name ASC
```

## Connections to other communities
- 23 edges to [[_COMMUNITY_unnamed_25]]
- 5 edges to [[_COMMUNITY_Any_1]]
- 4 edges to [[_COMMUNITY_Database]]
- 3 edges to [[_COMMUNITY_Asyncsession_3]]
- 2 edges to [[_COMMUNITY_Analytics Feedback]]

## Top bridge nodes
- [[PlatformWorkflowFactory]] - degree 17, connects to 2 communities
- [[OpenAIXGenerator]] - degree 11, connects to 2 communities
- [[OpenRouterGenerator]] - degree 11, connects to 2 communities
- [[AIContentGenerator]] - degree 26, connects to 1 community
- [[ContentOrchestrator]] - degree 20, connects to 1 community