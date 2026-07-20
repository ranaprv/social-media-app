# Content Quality Implementation Plan

> Addresses gaps identified in codebase review. Each phase ships independently.

---

## Phase 1: Image Generation (DALL-E 3)
**Effort:** 1-2 days | **Impact:** Unblocks visual content creation

### Problem
`ai_media.py:generate_image` returns fake URLs. No actual image generation.

### Plan
1. Add DALL-E 3 integration to `backend/app/services/ai_media_service.py` (new file)
   - Accept prompt, style, dimensions, brand_colors
   - Build enhanced prompt using `visual_guidelines.py` specs per platform
   - Call OpenAI DALL-E 3 API
   - Save to S3 (reuse existing `storage.py`)
   - Return real URL
2. Rewrite `ai_media.py:generate_image` to call the service
3. Add frontend: image preview, regeneration, download in content studio
4. Wire brand voice into image prompt generation

### Success Criteria
- Generate image → returns real URL → image displays in frontend
- Platform-correct dimensions applied automatically
- Brand colors reflected in generation

### Files
- `backend/app/services/ai_media_service.py` (new)
- `backend/app/api/ai_media.py` (rewrite endpoint)
- `frontend/src/components/content-studio/image-generator.tsx` (new)

---

## Phase 2: Orchestrated Content Pipeline
**Effort:** 2-3 days | **Impact:** One-click content packages

### Problem
Text, image, video, audio are separate endpoints. No pipeline.

### Plan
1. Create `backend/app/services/content_pipeline.py` (new)
   - Input: topic, platforms, content_types, brand_voice
   - Step 1: Generate script via LLM (reuse `ai_content.py` prompts)
   - Step 2: Generate image prompts from script (reuse `ai_engine/`)
   - Step 3: Generate images via DALL-E 3 (Phase 1 service)
   - Step 4: Generate voiceover via OpenAI TTS (existing endpoint, fix storage)
   - Step 5: Score all outputs via `content_quality_rubric.py`
   - Step 6: If score < 70, regenerate with feedback loop (max 2 retries)
   - Return: `{script, images[], audio_url, score, suggestions}`
2. Add `POST /ai/pipeline/generate` endpoint
3. Frontend: pipeline wizard UI (topic → platform → content type → generate → preview → approve)

### Success Criteria
- Single API call produces complete content package (text + image + audio)
- Quality score displayed before user approves
- Low-score content auto-regenerated

### Files
- `backend/app/services/content_pipeline.py` (new)
- `backend/app/api/ai_pipeline.py` (new)
- `frontend/src/components/content-studio/content-pipeline.tsx` (new)

---

## Phase 3: Self-Improving Prompts
**Effort:** 3-4 days | **Impact:** Content gets better over time

### Problem
Prompts are static strings. No versioning, no A/B testing, no learning.

### Plan
1. Create `prompt_versions` table (Alembic migration)
   - Columns: id, prompt_key (e.g. "linkedin_post"), version, system_prompt, 
     user_template, is_active, performance_score, created_at
2. Create `backend/app/services/prompt_manager.py` (new)
   - `get_active_prompt(key)` → returns best-performing version
   - `log_prompt_usage(prompt_id, content_id, engagement_score)` → records performance
   - `promote_winner(prompt_id)` → sets as active
   - `create_variant(prompt_id, modified_prompt)` → A/B test
3. Modify `ai_content.py` to use `prompt_manager.get_active_prompt()` instead of hardcoded dict
4. Add admin UI: view prompt versions, performance metrics, create variants
5. Nightly job: aggregate engagement scores per prompt version, promote winner

### Success Criteria
- Prompts stored in DB, not hardcoded
- Each prompt version tracks engagement of content it produced
- Best-performing version auto-promoted weekly
- Can create and test prompt variants from UI

### Files
- `backend/alembic/versions/xxx_add_prompt_versions.py` (new)
- `backend/app/models/prompt_version.py` (new)
- `backend/app/services/prompt_manager.py` (new)
- `backend/app/api/prompt_admin.py` (new)
- `backend/app/api/ai_content.py` (modify to use prompt_manager)
- `frontend/src/app/dashboard/prompts/page.tsx` (new)

---

## Phase 4: Content Quality Feedback Loop
**Effort:** 2-3 days | **Impact:** Analytics improve generation

### Problem
Analytics collected but never fed back to improve content.

### Plan
1. Create `backend/app/services/quality_feedback.py` (new)
   - After content publishes + 7 days: fetch analytics (engagement, reach, clicks)
   - Compare actual vs predicted score from `content_scorer.py`
   - Store delta in `content_performance` table
   - Identify patterns: "questions in headlines get 2x comments for this audience"
2. Create `content_performance` table
   - Columns: content_id, platform, predicted_score, actual_engagement, 
     patterns_detected (JSONB), created_at
3. Modify `content_scorer.py` to incorporate historical performance data
   - Instead of hardcoded heuristics: "for this workspace, posts with questions average 3.2% engagement"
4. Modify content generation to include performance insights in prompts
   - "Based on your history, posts with X get Y% more engagement"

### Success Criteria
- Content scorer uses workspace-specific historical data
- Generation prompts include performance insights
- Dashboard shows "what works for your audience" recommendations

### Files
- `backend/alembic/versions/xxx_add_content_performance.py` (new)
- `backend/app/models/content_performance.py` (new)
- `backend/app/services/quality_feedback.py` (new)
- `backend/app/services/content_scorer.py` (modify to use historical data)
- `backend/app/api/ai_content.py` (inject performance context into prompts)

---

## Phase 5: Reel/Short Video Workflow
**Effort:** 2-3 days | **Impact:** Dedicated short-form video creation

### Problem
"Reel" content type exists but only generates text script. No visual/audio pipeline.

### Plan
1. Create `backend/app/services/reel_generator.py` (new)
   - Input: topic, platform (instagram/youtube/tiktok), duration
   - Step 1: Generate hook script (0-3s) via LLM
   - Step 2: Generate scene-by-scene breakdown via LLM
   - Step 3: Generate visual prompts per scene
   - Step 4: Generate images per scene via DALL-E 3
   - Step 5: Generate voiceover via TTS
   - Step 6: Return structured output: `{scenes[{script, image_url, duration}], audio_url, caption, hashtags}`
2. Add `POST /ai/reel/generate` endpoint
3. Frontend: scene editor with preview, reorder, regenerate individual scenes

### Success Criteria
- Generate reel → structured scene breakdown + images + audio
- Scenes individually editable/regeneratable
- Platform-correct duration and aspect ratio enforced

### Files
- `backend/app/services/reel_generator.py` (new)
- `backend/app/api/ai_reel.py` (new)
- `frontend/src/components/content-studio/reel-editor.tsx` (new)

---

## Phase 6: Research → Generation Bridge
**Effort:** 1 day | **Impact:** Research automatically feeds content

### Problem
Research engine finds high-scoring topics. Users must manually copy to content generation.

### Plan
1. Add `POST /ai/generate-from-research` endpoint
   - Input: research_item_id, platform, content_type
   - Read research item from DB
   - Use research data (keywords, scores, opportunities) as context for generation
   - Generate content informed by research
2. Add "Generate Content" button on research items in sidebar
3. Auto-suggest content types based on research category

### Success Criteria
- Click "Generate" on research item → content generated with research context
- Research keywords/scores appear in generated content
- One-click from research to published content

### Files
- `backend/app/api/ai_content.py` (add generate-from-research endpoint)
- `frontend/src/components/research/research-sidebar.tsx` (add generate button)

---

## Execution Order

```
Phase 1 (Image Gen)  →  Phase 2 (Pipeline)  →  Phase 4 (Feedback Loop)
                                        ↓
                              Phase 3 (Prompt Library)
                                        ↓
                              Phase 5 (Reel Workflow)
                                        ↓
                              Phase 6 (Research Bridge)
```

Phase 1 must come first (Phase 2 depends on it). Phase 3-6 can be parallelized after Phase 2.

---

## Risk Notes

- **DALL-E 3 cost:** ~$0.04/image. Budget: ~100 images/day = $4/day. Add user credit check before generation.
- **Video generation APIs** (Runway, Pika) are expensive ($0.10-0.50/second). Phase 5 uses image-based scene generation, not full video synthesis. Full video API integration deferred to Phase 7.
- **Self-improving prompts** need sufficient engagement data. Start with minimum 50 published posts before promoting winners.
- **Quality feedback loop** requires analytics collection to be working (TASK-012 in TODO.md — already completed).
