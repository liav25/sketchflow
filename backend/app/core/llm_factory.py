import os
from typing import Tuple, Literal
from enum import Enum

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

Provider = Literal["openai", "anthropic"]


class TaskType(Enum):
    """Different task types requiring optimized model selection."""
    VISION = "vision"  # Image understanding and scene description
    REASONING = "reasoning"  # Structure analysis and logical reasoning
    CODE_GENERATION = "code_generation"  # Generating diagram code
    SYNTHESIS = "synthesis"  # Selecting and refining final output


# Task-optimized model defaults
TASK_OPTIMIZED_MODELS = {
    TaskType.VISION: {
        "default": "gpt-4.1",  # GPT-4V for vision capabilities
        "temperature": 0.1,
        "fallback": "gpt-4.1"
    },
    TaskType.REASONING: {
        "default": "claude-3-5-sonnet-20241022",  # Claude Sonnet for reasoning
        "temperature": 0.0,
        "fallback": "gpt-4.1"
    },
    TaskType.CODE_GENERATION: {
        "default": "gpt-4.1",  # Good for code generation
        "temperature": 0.1,
        "fallback": "gpt-4.1"
    },
    TaskType.SYNTHESIS: {
        "default": "claude-3-5-sonnet-20241022",  # Claude for synthesis and selection
        "temperature": 0.0,
        "fallback": "gpt-4.1"
    }
}


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


def get_task_optimized_model(
    task_type: TaskType,
    *,
    override_model: str | None = None,
    override_temperature: float | None = None,
) -> Tuple[object, Provider]:
    """Get the optimal model for a specific task type.
    
    Args:
        task_type: The type of task (vision, reasoning, code_generation, synthesis)
        override_model: Optional model override from environment or config
        override_temperature: Optional temperature override
        
    Returns:
        Tuple of (model_client, provider)
    """
    task_config = TASK_OPTIMIZED_MODELS[task_type]
    
    # Use override model if provided, otherwise use task-optimized default
    model_name = override_model or task_config["default"]
    temperature = override_temperature if override_temperature is not None else task_config["temperature"]
    
    try:
        return get_chat_model(model_name, temperature=temperature)
    except Exception as e:
        # Fallback to backup model if primary fails
        fallback_model = task_config["fallback"]
        print(f"Warning: Failed to initialize {model_name}, falling back to {fallback_model}: {e}")
        return get_chat_model(fallback_model, temperature=temperature)


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

