---
type: community
cohesion: 0.06
members: 44
---

# 

**Cohesion:** 0.06 - loosely connected
**Members:** 44 nodes

## Members
- [[.__init__()_2]] - code - backend/app/services/ai_engine/claude_linkedin.py
- [[.__init__()_3]] - code - backend/app/services/ai_engine/gemini_instagram.py
- [[.__init__()_4]] - code - backend/app/services/ai_engine/omniroute.py
- [[._get_provider_generator()]] - code - backend/app/services/ai_engine/omniroute.py
- [[._mock_text()]] - code - backend/app/services/ai_engine/omniroute.py
- [[._resolve_best_backend()]] - code - backend/app/services/ai_engine/omniroute.py
- [[.generate_media_prompts()_1]] - code - backend/app/services/ai_engine/claude_linkedin.py
- [[.generate_media_prompts()_2]] - code - backend/app/services/ai_engine/gemini_instagram.py
- [[.generate_media_prompts()_3]] - code - backend/app/services/ai_engine/omniroute.py
- [[.generate_text()]] - code - backend/app/services/ai_engine/base.py
- [[.generate_text()_1]] - code - backend/app/services/ai_engine/claude_linkedin.py
- [[.generate_text()_2]] - code - backend/app/services/ai_engine/gemini_instagram.py
- [[.generate_text()_3]] - code - backend/app/services/ai_engine/omniroute.py
- [[.generate_text()_4]] - code - backend/app/services/ai_engine/openai_x.py
- [[.generate_text()_5]] - code - backend/app/services/ai_engine/openrouter.py
- [[.get_routing_info()]] - code - backend/app/services/ai_engine/omniroute.py
- [[ABC]] - code
- [[Abstract base class for all AI content generators.]] - rationale - backend/app/services/ai_engine/base.py
- [[Any_9]] - code
- [[Any_10]] - code
- [[Any_11]] - code
- [[Call Anthropic Messages API for a LinkedIn post draft.]] - rationale - backend/app/services/ai_engine/claude_linkedin.py
- [[Call Google Gemini API for an Instagram caption.]] - rationale - backend/app/services/ai_engine/gemini_instagram.py
- [[Call OpenAI Chat Completions for a tweet thread.]] - rationale - backend/app/services/ai_engine/openai_x.py
- [[Call OpenRouter for text generation.]] - rationale - backend/app/services/ai_engine/openrouter.py
- [[Claude-powered generator optimised for LinkedIn long-form content.]] - rationale - backend/app/services/ai_engine/claude_linkedin.py
- [[ClaudeLinkedInGenerator]] - code - backend/app/services/ai_engine/claude_linkedin.py
- [[GeminiInstagramGenerator]] - code - backend/app/services/ai_engine/gemini_instagram.py
- [[Generate DALL-E  image prompts for a LinkedIn carousel or banner.]] - rationale - backend/app/services/ai_engine/claude_linkedin.py
- [[Generate image prompts optimised for Instagram carousel  feed posts.]] - rationale - backend/app/services/ai_engine/gemini_instagram.py
- [[Generate platform-optimised text content for topic.]] - rationale - backend/app/services/ai_engine/base.py
- [[Generates Instagram captions and image prompts via Google Gemini.]] - rationale - backend/app/services/ai_engine/gemini_instagram.py
- [[Generates LinkedIn posts via Anthropic Claude.]] - rationale - backend/app/services/ai_engine/claude_linkedin.py
- [[GenerationResult]] - code - backend/app/services/ai_engine/base.py
- [[Instantiate the right generator for the resolved provider.]] - rationale - backend/app/services/ai_engine/omniroute.py
- [[Intelligent multi-provider router that picks the best backend per task.      Unl]] - rationale - backend/app/services/ai_engine/omniroute.py
- [[OmniRouteGenerator]] - code - backend/app/services/ai_engine/omniroute.py
- [[Pick the best (provider, model) pair for the given task type.          Returns (]] - rationale - backend/app/services/ai_engine/omniroute.py
- [[Return routing configuration and provider status for the UI.]] - rationale - backend/app/services/ai_engine/omniroute.py
- [[Route media prompt generation through the optimal provider.]] - rationale - backend/app/services/ai_engine/omniroute.py
- [[Route text generation through the optimal provider.]] - rationale - backend/app/services/ai_engine/omniroute.py
- [[Unified return type for all generators.]] - rationale - backend/app/services/ai_engine/base.py
- [[base.py]] - code - backend/app/services/ai_engine/base.py
- [[claude_linkedin.py]] - code - backend/app/services/ai_engine/claude_linkedin.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/
SORT file.name ASC
```

## Connections to other communities
- 23 edges to [[_COMMUNITY_unnamed_5]]
- 4 edges to [[_COMMUNITY_Any_1]]
- 3 edges to [[_COMMUNITY_Asyncsession_3]]
- 1 edge to [[_COMMUNITY_Ai Models]]

## Top bridge nodes
- [[OmniRouteGenerator]] - degree 17, connects to 2 communities
- [[GeminiInstagramGenerator]] - degree 11, connects to 2 communities
- [[._get_provider_generator()]] - degree 10, connects to 2 communities
- [[base.py]] - degree 5, connects to 2 communities
- [[.get_routing_info()]] - degree 5, connects to 2 communities