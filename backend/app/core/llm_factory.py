import os
from typing import Tuple, Literal

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

Provider = Literal["openai", "anthropic"]


def _infer_provider(model_name: str) -> Provider:
    name = model_name.lower().strip()
    # Explicit prefix takes precedence: openai:..., anthropic:...
    if ":" in name:
        prefix, _ = name.split(":", 1)
        if prefix in ("openai", "anthropic"):
            return prefix  # type: ignore[return-value]
    # Heuristics
    if "claude" in name or "sonnet" in name or name.startswith("anthropic"):
        return "anthropic"
    # Default to OpenAI for gpt/o families
    return "openai"


def _strip_prefix(model_name: str) -> str:
    if ":" in model_name:
        prefix, rest = model_name.split(":", 1)
        if prefix in ("openai", "anthropic"):
            return rest
    return model_name


def get_chat_model(
    model_name: str,
    *,
    temperature: float = 0.0,
) -> Tuple[object, Provider]:
    """Return a single chat model client and provider based on model name.

    Accepts provider-qualified names like `openai:gpt-4.1` or
    `anthropic:claude-3-5-sonnet-20241022`, otherwise infers by heuristics.
    """
    if not model_name or not isinstance(model_name, str):
        raise ValueError("model_name must be a non-empty string")

    provider: Provider = _infer_provider(model_name)
    pure_model = _strip_prefix(model_name)

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set, required for provider 'openai'")
        client = ChatOpenAI(model=pure_model, api_key=api_key, temperature=temperature)
        return client, provider

    if provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set, required for provider 'anthropic'")
        client = ChatAnthropic(model=pure_model, api_key=api_key, temperature=temperature)
        return client, provider

    # Should never reach here due to typing/heuristics
    raise ValueError(f"Unsupported provider for model '{model_name}'")
