---
type: community
cohesion: 0.04
members: 67
---

# Any

**Cohesion:** 0.04 - loosely connected
**Members:** 67 nodes

## Members
- [[AI Caption Generator — generate platform-specific captions using LLM.  Takes a t]] - rationale - backend/app/services/caption_generator.py
- [[AI Ideas Generator — multi-LLM brainstorming with voting.]] - rationale - backend/app/api/ai_ideas.py
- [[AI Sentiment Analysis service.]] - rationale - backend/app/services/sentiment.py
- [[Analyze competitor content and strategy.]] - rationale - backend/app/api/research.py
- [[Analyze text sentiment using AI. Returns sentiment + score.]] - rationale - backend/app/services/sentiment.py
- [[Any_33]] - code
- [[Any_44]] - code
- [[Any_68]] - code
- [[AsyncSession_25]] - code
- [[AsyncSession_76]] - code
- [[Call LLM and parse JSON response. Returns parsed data or None.]] - rationale - backend/app/services/llm.py
- [[Call an LLM provider with the given prompt. Returns raw text response.]] - rationale - backend/app/services/llm.py
- [[Call multiple LLM providers in parallel. Returns {provider response}.]] - rationale - backend/app/services/llm.py
- [[Content idea generator — AI brainstorm from keywords.  Generates content ideas b]] - rationale - backend/app/services/content_idea_generator.py
- [[Extract and parse JSON from LLM response (handles markdown fences).]] - rationale - backend/app/services/llm.py
- [[Fetch recent generated content in same pillar+platform for diversity checks.]] - rationale - backend/app/services/llm_generator.py
- [[Generate an AI caption for a specific platform.      Returns the generated capti]] - rationale - backend/app/services/caption_generator.py
- [[Generate captions for multiple platforms at once.]] - rationale - backend/app/services/caption_generator.py
- [[Generate content for a single ContentSlot using LLM.      Args         db Data]] - rationale - backend/app/services/llm_generator.py
- [[Generate content ideas based on keywords and parameters.      Returns a list of]] - rationale - backend/app/services/content_idea_generator.py
- [[Generate content ideas using selected LLM model(s) with optional voting.]] - rationale - backend/app/api/ai_ideas.py
- [[Generate ideas based on current trends.]] - rationale - backend/app/services/content_idea_generator.py
- [[Improve an existing caption with specific instructions.]] - rationale - backend/app/services/caption_generator.py
- [[LLM-powered content generator for ContentSlots.  Builds prompts from strategy co]] - rationale - backend/app/services/llm_generator.py
- [[List available LLM models by provider.]] - rationale - backend/app/api/ai_ideas.py
- [[Multi-LLM service — unified interface for OpenAI, Anthropic, Gemini, OpenRouter,]] - rationale - backend/app/services/llm.py
- [[Parse and merge ideas from multiple LLM responses, deduplicate, rank by frequenc]] - rationale - backend/app/services/llm.py
- [[Placeholder ideas when AI is unavailable.]] - rationale - backend/app/api/ai_ideas.py
- [[Research API — trends, competitors, keyword research.]] - rationale - backend/app/api/research.py
- [[Research keywords with volume and difficulty estimates.]] - rationale - backend/app/api/research.py
- [[Return all available models grouped by provider.]] - rationale - backend/app/services/llm.py
- [[Search trending topics for a nichekeyword.]] - rationale - backend/app/api/research.py
- [[Shared caller for OpenAI-compatible APIs (OpenRouter, DeepSeek, etc.).]] - rationale - backend/app/services/llm.py
- [[User_24]] - code
- [[_call_anthropic()]] - code - backend/app/services/llm.py
- [[_call_deepseek()]] - code - backend/app/services/llm.py
- [[_call_gemini()]] - code - backend/app/services/llm.py
- [[_call_openai()]] - code - backend/app/services/llm.py
- [[_call_openai_compatible()]] - code - backend/app/services/llm.py
- [[_call_openrouter()]] - code - backend/app/services/llm.py
- [[_fallback_ideas()]] - code - backend/app/api/ai_ideas.py
- [[_fetch_recent_posts()]] - code - backend/app/services/llm_generator.py
- [[_parse_json_response()]] - code - backend/app/services/llm.py
- [[ai_ideas.py]] - code - backend/app/api/ai_ideas.py
- [[analyze_competitors()]] - code - backend/app/api/research.py
- [[analyze_sentiment()]] - code - backend/app/services/sentiment.py
- [[call_llm()]] - code - backend/app/services/llm.py
- [[call_llm_json()]] - code - backend/app/services/llm.py
- [[caption_generator.py]] - code - backend/app/services/caption_generator.py
- [[content_idea_generator.py]] - code - backend/app/services/content_idea_generator.py
- [[generate_caption()_1]] - code - backend/app/services/caption_generator.py
- [[generate_content_ideas()]] - code - backend/app/services/content_idea_generator.py
- [[generate_ideas()]] - code - backend/app/api/ai_ideas.py
- [[generate_multi_platform_captions()]] - code - backend/app/services/caption_generator.py
- [[generate_slot_content()]] - code - backend/app/services/llm_generator.py
- [[generate_trending_ideas()]] - code - backend/app/services/content_idea_generator.py
- [[get_available_models()]] - code - backend/app/services/llm.py
- [[improve_caption()]] - code - backend/app/services/caption_generator.py
- [[list_models()]] - code - backend/app/api/ai_ideas.py
- [[llm.py]] - code - backend/app/services/llm.py
- [[llm_generator.py]] - code - backend/app/services/llm_generator.py
- [[multi_model_brainstorm()]] - code - backend/app/services/llm.py
- [[research.py]] - code - backend/app/api/research.py
- [[research_keywords()]] - code - backend/app/api/research.py
- [[search_trends()]] - code - backend/app/api/research.py
- [[sentiment.py]] - code - backend/app/services/sentiment.py
- [[vote_on_ideas()]] - code - backend/app/services/llm.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Any
SORT file.name ASC
```

## Connections to other communities
- 7 edges to [[_COMMUNITY_Any_1]]
- 2 edges to [[_COMMUNITY_Asyncsession_3]]
- 1 edge to [[_COMMUNITY_Ai Models]]
- 1 edge to [[_COMMUNITY_Ai Calendar Generator]]
- 1 edge to [[_COMMUNITY_Any_5]]
- 1 edge to [[_COMMUNITY_Audience Persona]]
- 1 edge to [[_COMMUNITY_Batch Planner]]
- 1 edge to [[_COMMUNITY_Brand Voice Checker]]
- 1 edge to [[_COMMUNITY_Content Repurposing Engine]]
- 1 edge to [[_COMMUNITY_Hashtag Strategist]]
- 1 edge to [[_COMMUNITY_Influencer Discovery]]
- 1 edge to [[_COMMUNITY_Multilang Translator]]

## Top bridge nodes
- [[call_llm_json()]] - degree 20, connects to 8 communities
- [[call_llm()]] - degree 15, connects to 4 communities
- [[get_available_models()]] - degree 6, connects to 2 communities
- [[llm.py]] - degree 14, connects to 1 community
- [[caption_generator.py]] - degree 5, connects to 1 community