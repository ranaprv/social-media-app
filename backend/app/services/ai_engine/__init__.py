"""Loosely-coupled multi-model AI content generation engine.

Provides an abstract base class ``AIContentGenerator`` and concrete
implementations for Claude (LinkedIn), OpenAI (X/Twitter), Gemini
(Instagram), OpenRouter (200+ models), and OmniRoute (intelligent routing).
A ``PlatformWorkflowFactory`` resolves the correct generator from a
(platform, provider) pair at runtime.
"""
from app.services.ai_engine.base import AIContentGenerator
from app.services.ai_engine.claude_linkedin import ClaudeLinkedInGenerator
from app.services.ai_engine.openai_x import OpenAIXGenerator
from app.services.ai_engine.gemini_instagram import GeminiInstagramGenerator
from app.services.ai_engine.openrouter import OpenRouterGenerator
from app.services.ai_engine.omniroute import OmniRouteGenerator
from app.services.ai_engine.factory import PlatformWorkflowFactory

__all__ = [
    "AIContentGenerator",
    "ClaudeLinkedInGenerator",
    "OpenAIXGenerator",
    "GeminiInstagramGenerator",
    "OpenRouterGenerator",
    "OmniRouteGenerator",
    "PlatformWorkflowFactory",
]
