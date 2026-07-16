"""Multi-LLM service — unified interface for OpenAI, Anthropic, Gemini."""
import json
import logging
from typing import Optional
from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Available models across providers
AVAILABLE_MODELS = {
    "openai": {
        "name": "OpenAI",
        "models": [
            {"id": "gpt-4o", "name": "GPT-4o", "max_tokens": 4096, "cost_tier": "high"},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "max_tokens": 4096, "cost_tier": "low"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "max_tokens": 4096, "cost_tier": "low"},
        ],
    },
    "anthropic": {
        "name": "Anthropic",
        "models": [
            {"id": "claude-sonnet-4-20250514", "name": "Claude Sonnet 4", "max_tokens": 4096, "cost_tier": "medium"},
            {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku", "max_tokens": 4096, "cost_tier": "low"},
        ],
    },
    "gemini": {
        "name": "Google Gemini",
        "models": [
            {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash", "max_tokens": 4096, "cost_tier": "low"},
            {"id": "gemini-2.5-flash-preview-05-20", "name": "Gemini 2.5 Flash", "max_tokens": 8192, "cost_tier": "medium"},
        ],
    },
}


def get_available_models() -> dict:
    """Return all available models grouped by provider."""
    settings = get_settings()
    available = {}
    if settings.OPENAI_API_KEY:
        available["openai"] = AVAILABLE_MODELS["openai"]
    if settings.ANTHROPIC_API_KEY:
        available["anthropic"] = AVAILABLE_MODELS["anthropic"]
    if settings.GOOGLE_AI_API_KEY:
        available["gemini"] = AVAILABLE_MODELS["gemini"]
    return available


async def call_llm(
    prompt: str,
    system_prompt: str = "",
    provider: str = "openai",
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 3000,
) -> str:
    """Call an LLM provider with the given prompt. Returns raw text response."""
    settings = get_settings()

    if provider == "openai" and settings.OPENAI_API_KEY:
        return await _call_openai(prompt, system_prompt, model or "gpt-4o", temperature, max_tokens, settings.OPENAI_API_KEY)
    elif provider == "anthropic" and settings.ANTHROPIC_API_KEY:
        return await _call_anthropic(prompt, system_prompt, model or "claude-sonnet-4-20250514", temperature, max_tokens, settings.ANTHROPIC_API_KEY)
    elif provider == "gemini" and settings.GOOGLE_AI_API_KEY:
        return await _call_gemini(prompt, system_prompt, model or "gemini-2.0-flash", temperature, max_tokens, settings.GOOGLE_AI_API_KEY)
    else:
        logger.warning(f"Provider '{provider}' not configured or API key missing")
        return ""


async def call_llm_json(
    prompt: str,
    system_prompt: str = "",
    provider: str = "openai",
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 3000,
) -> Optional[list | dict]:
    """Call LLM and parse JSON response. Returns parsed data or None."""
    raw = await call_llm(prompt, system_prompt, provider, model, temperature, max_tokens)
    if not raw:
        return None
    return _parse_json_response(raw)


async def multi_model_brainstorm(
    prompt: str,
    system_prompt: str = "",
    providers: Optional[list[str]] = None,
    temperature: float = 0.8,
    max_tokens: int = 3000,
) -> dict[str, str]:
    """Call multiple LLM providers in parallel. Returns {provider: response}."""
    import asyncio

    if not providers:
        providers = list(get_available_models().keys())

    tasks = {
        provider: call_llm(prompt, system_prompt, provider, temperature=temperature, max_tokens=max_tokens)
        for provider in providers
    }

    results = {}
    responses = await asyncio.gather(*tasks.values(), return_exceptions=True)
    for provider, response in zip(tasks.keys(), responses):
        if isinstance(response, Exception):
            logger.error(f"{provider} failed: {response}")
            results[provider] = ""
        else:
            results[provider] = response

    return results


def vote_on_ideas(multi_responses: dict[str, str], system_prompt: str = "") -> list[dict]:
    """Parse and merge ideas from multiple LLM responses, deduplicate, rank by frequency."""
    all_ideas: dict[str, dict] = {}  # title -> idea (best version)

    for provider, response in multi_responses.items():
        if not response:
            continue
        parsed = _parse_json_response(response)
        if not parsed or not isinstance(parsed, list):
            continue
        for idea in parsed:
            title = idea.get("title", "").strip().lower()
            if not title:
                continue
            if title not in all_ideas:
                idea["voted_by"] = [provider]
                idea["vote_count"] = 1
                all_ideas[title] = idea
            else:
                if provider not in all_ideas[title]["voted_by"]:
                    all_ideas[title]["voted_by"].append(provider)
                    all_ideas[title]["vote_count"] += 1

    # Sort by vote count descending
    ranked = sorted(all_ideas.values(), key=lambda x: x.get("vote_count", 0), reverse=True)
    return ranked


async def _call_openai(prompt: str, system_prompt: str, model: str, temperature: float, max_tokens: int, api_key: str) -> str:
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=api_key)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = await client.chat.completions.create(
            model=model, messages=messages, temperature=temperature, max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return ""


async def _call_anthropic(prompt: str, system_prompt: str, model: str, temperature: float, max_tokens: int, api_key: str) -> str:
    try:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=api_key)
        response = await client.messages.create(
            model=model, max_tokens=max_tokens, temperature=temperature,
            system=system_prompt if system_prompt else "You are a helpful assistant.",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text if response.content else ""
    except Exception as e:
        logger.error(f"Anthropic error: {e}")
        return ""


async def _call_gemini(prompt: str, system_prompt: str, model: str, temperature: float, max_tokens: int, api_key: str) -> str:
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        response = await client.aio.models.generate_content(
            model=model, contents=full_prompt,
            config=genai.types.GenerateContentConfig(temperature=temperature, max_output_tokens=max_tokens),
        )
        return response.text or ""
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return ""


def _parse_json_response(raw: str) -> Optional[list | dict]:
    """Extract and parse JSON from LLM response (handles markdown fences)."""
    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        return json.loads(cleaned.strip())
    except (json.JSONDecodeError, IndexError):
        return None
