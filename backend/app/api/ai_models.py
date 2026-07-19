"""API endpoints for AI model discovery and provider status."""
from fastapi import APIRouter
from app.core.config import get_settings
from app.services.llm import AVAILABLE_MODELS, get_available_models

router = APIRouter(prefix="/ai/models", tags=["ai-models"])


@router.get("/providers")
async def list_providers():
    """Return all providers with their configuration status."""
    settings = get_settings()
    providers = {
        "openrouter": {
            "name": "OpenRouter",
            "configured": bool(settings.OPENROUTER_API_KEY),
            "description": "Access 200+ models from all major providers through a single API key.",
            "models_count": len(AVAILABLE_MODELS.get("openrouter", {}).get("models", [])),
            "setup_url": "https://openrouter.ai/keys",
            "benefit": "One key → all models. Cost-optimized routing.",
        },
        "openai": {
            "name": "OpenAI",
            "configured": bool(settings.OPENAI_API_KEY),
            "description": "Direct access to GPT-4o, GPT-4o Mini, and DALL-E.",
            "models_count": len(AVAILABLE_MODELS.get("openai", {}).get("models", [])),
            "setup_url": "https://platform.openai.com/api-keys",
            "benefit": "Direct provider access. Lowest latency.",
        },
        "anthropic": {
            "name": "Anthropic",
            "configured": bool(settings.ANTHROPIC_API_KEY),
            "description": "Direct access to Claude Sonnet 4, Claude 3.5 Haiku.",
            "models_count": len(AVAILABLE_MODELS.get("anthropic", {}).get("models", [])),
            "setup_url": "https://console.anthropic.com/",
            "benefit": "Best for long-form content and nuanced writing.",
        },
        "gemini": {
            "name": "Google Gemini",
            "configured": bool(settings.GOOGLE_AI_API_KEY),
            "description": "Direct access to Gemini 2.0 Flash and Gemini 2.5 Pro.",
            "models_count": len(AVAILABLE_MODELS.get("gemini", {}).get("models", [])),
            "setup_url": "https://aistudio.google.com/",
            "benefit": "Largest context window (1M tokens). Great for brainstorming.",
        },
        "deepseek": {
            "name": "DeepSeek",
            "configured": bool(settings.DEEPSEEK_API_KEY),
            "description": "Direct access to DeepSeek V3 and R1 reasoning models.",
            "models_count": len(AVAILABLE_MODELS.get("deepseek", {}).get("models", [])),
            "setup_url": "https://platform.deepseek.com/",
            "benefit": "Best cost/performance ratio. Strong at reasoning tasks.",
        },
    }
    configured_count = sum(1 for p in providers.values() if p["configured"])
    total_models = sum(
        len(AVAILABLE_MODELS.get(k, {}).get("models", []))
        for k, v in providers.items()
        if v["configured"]
    )
    return {
        "providers": providers,
        "configured_count": configured_count,
        "total_available_models": total_models,
    }


@router.get("/available")
async def list_available_models():
    """Return all available models grouped by provider (only configured ones)."""
    available = get_available_models()
    return {"providers": available}


@router.get("/routing")
async def get_routing_recommendations():
    """Return OmniRoute routing recommendations per task type."""
    from app.services.ai_engine.omniroute import OmniRouteGenerator
    return OmniRouteGenerator.get_routing_info()
