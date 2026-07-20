"""Multi-LLM service — unified interface for OpenAI, Anthropic, Gemini, OpenRouter, DeepSeek."""
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
    "openrouter": {
        "name": "OpenRouter (200+ models)",
        "models": [
            {"id": "anthropic/claude-sonnet-4", "name": "Claude Sonnet 4", "max_tokens": 8192, "cost_tier": "medium", "context_window": 200000},
            {"id": "anthropic/claude-3.5-haiku", "name": "Claude 3.5 Haiku", "max_tokens": 8192, "cost_tier": "low", "context_window": 200000},
            {"id": "openai/gpt-4o", "name": "GPT-4o", "max_tokens": 4096, "cost_tier": "high", "context_window": 128000},
            {"id": "openai/gpt-4o-mini", "name": "GPT-4o Mini", "max_tokens": 4096, "cost_tier": "low", "context_window": 128000},
            {"id": "google/gemini-2.5-flash", "name": "Gemini 2.5 Flash", "max_tokens": 8192, "cost_tier": "low", "context_window": 1000000},
            {"id": "google/gemini-2.5-pro", "name": "Gemini 2.5 Pro", "max_tokens": 8192, "cost_tier": "medium", "context_window": 1000000},
            {"id": "meta-llama/llama-4-maverick", "name": "Llama 4 Maverick", "max_tokens": 4096, "cost_tier": "low", "context_window": 1000000},
            {"id": "mistralai/mistral-large", "name": "Mistral Large", "max_tokens": 4096, "cost_tier": "medium", "context_window": 128000},
            {"id": "deepseek/deepseek-r1", "name": "DeepSeek R1", "max_tokens": 4096, "cost_tier": "low", "context_window": 128000},
            {"id": "qwen/qwen-2.5-72b-instruct", "name": "Qwen 2.5 72B", "max_tokens": 4096, "cost_tier": "low", "context_window": 128000},
        ],
    },
    "deepseek": {
        "name": "DeepSeek",
        "models": [
            {"id": "deepseek-chat", "name": "DeepSeek V3", "max_tokens": 8192, "cost_tier": "low", "context_window": 128000},
            {"id": "deepseek-reasoner", "name": "DeepSeek R1", "max_tokens": 8192, "cost_tier": "low", "context_window": 128000},
        ],
    },
}


def get_available_models() -> dict:
    """Return all available models grouped by provider."""
    settings = get_settings()
    available = {}
    if settings.OPENROUTER_API_KEY:
        available["openrouter"] = AVAILABLE_MODELS["openrouter"]
    if settings.OPENAI_API_KEY:
        available["openai"] = AVAILABLE_MODELS["openai"]
    if settings.ANTHROPIC_API_KEY:
        available["anthropic"] = AVAILABLE_MODELS["anthropic"]
    if settings.GOOGLE_AI_API_KEY:
        available["gemini"] = AVAILABLE_MODELS["gemini"]
    if settings.DEEPSEEK_API_KEY:
        available["deepseek"] = AVAILABLE_MODELS["deepseek"]
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

    if provider == "openrouter" and settings.OPENROUTER_API_KEY:
        return await _call_openrouter(prompt, system_prompt, model or "anthropic/claude-sonnet-4", temperature, max_tokens, settings.OPENROUTER_API_KEY)
    elif provider == "openai" and settings.OPENAI_API_KEY:
        return await _call_openai(prompt, system_prompt, model or "gpt-4o", temperature, max_tokens, settings.OPENAI_API_KEY)
    elif provider == "anthropic" and settings.ANTHROPIC_API_KEY:
        return await _call_anthropic(prompt, system_prompt, model or "claude-sonnet-4-20250514", temperature, max_tokens, settings.ANTHROPIC_API_KEY)
    elif provider == "gemini" and settings.GOOGLE_AI_API_KEY:
        return await _call_gemini(prompt, system_prompt, model or "gemini-2.0-flash", temperature, max_tokens, settings.GOOGLE_AI_API_KEY)
    elif provider == "deepseek" and settings.DEEPSEEK_API_KEY:
        return await _call_deepseek(prompt, system_prompt, model or "deepseek-chat", temperature, max_tokens, settings.DEEPSEEK_API_KEY)
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
    retries: int = 3,
) -> Optional[list | dict]:
    """Call LLM and parse JSON response. Retries on failure with exponential backoff."""
    import asyncio

    last_error = None
    for attempt in range(retries):
        try:
            raw = await call_llm(prompt, system_prompt, provider, model, temperature, max_tokens)
            if raw:
                result = _parse_json_response(raw)
                if result is not None:
                    return result
            last_error = "Empty or unparseable response"
        except Exception as e:
            last_error = str(e)
            logger.warning(f"LLM call attempt {attempt + 1}/{retries} failed: {e}")

        if attempt < retries - 1:
            delay = 2 ** attempt
            logger.info(f"Retrying in {delay}s...")
            await asyncio.sleep(delay)

    logger.error(f"LLM call failed after {retries} attempts: {last_error}")
    return None


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


async def _call_openai_compatible(
    prompt: str,
    system_prompt: str,
    model: str,
    temperature: float,
    max_tokens: int,
    api_key: str,
    base_url: str,
    provider_name: str,
    default_headers: dict | None = None,
) -> str:
    """Shared caller for OpenAI-compatible APIs (OpenRouter, DeepSeek, etc.)."""
    try:
        from openai import AsyncOpenAI

        kwargs: dict = {
            "api_key": api_key,
            "base_url": base_url,
        }
        if default_headers:
            kwargs["default_headers"] = default_headers

        client = AsyncOpenAI(**kwargs)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        logger.error(f"{provider_name} error: {e}")
        return ""


async def _call_openrouter(prompt, system_prompt, model, temperature, max_tokens, api_key):
    return await _call_openai_compatible(
        prompt, system_prompt, model, temperature, max_tokens, api_key,
        base_url="https://openrouter.ai/api/v1",
        provider_name="OpenRouter",
        default_headers={
            "HTTP-Referer": "https://socialmedia-manager.ai",
            "X-Title": "Social Media Manager",
        },
    )


async def _call_deepseek(prompt, system_prompt, model, temperature, max_tokens, api_key):
    return await _call_openai_compatible(
        prompt, system_prompt, model, temperature, max_tokens, api_key,
        base_url="https://api.deepseek.com/v1",
        provider_name="DeepSeek",
    )


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
