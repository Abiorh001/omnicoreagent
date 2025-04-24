from typing import Any, Dict, List, Optional

from mcpomni_connect.utils import logger


class LLMToolSupport:
    """Class to handle LLM tool support checking"""

    # Define model tool support mapping
    MODEL_TOOL_SUPPORT = {
        "openai": {
            "provider": "openai",
            "models": None,  # None means all models support tools
        },
        "groq": {
            "provider": "groq",
            "models": None,  # None means all models support tools
        },
        "openrouter": {
            "provider": "openrouter",
            "models": ["openai", "anthropic", "groq", "mistralai", "gemini"],
        },
        "gemini": {
            "provider": "gemini",
            "models": None,  # None means all models support tools
        },
        "deepseek": {
            "provider": "deepseek",
            "models": None,  # None means all models support tools
        },
        "ollama": {
            "provider": "ollama",
            "models": ["mistral", "llama3.2", "phi4-mini"],  # None means all models support tools, add other
        },
    }

    @classmethod
    def check_tool_support(cls, llm_config: Dict[str, Any]) -> bool:
        """Check if the current LLM configuration supports tools.

        Args:
            llm_config: LLM configuration dictionary containing model and provider

        Returns:
            bool: True if the LLM supports tools, False otherwise
        """
        model = llm_config.get("model", "")
        model_provider = llm_config.get("provider", "").lower()

        # Check if provider supports tools
        for provider_info in cls.MODEL_TOOL_SUPPORT.values():
            if provider_info["provider"] in model_provider:
                if provider_info["models"] is None:
                    # Provider supports tools for all models
                    return True
                else:
                    # Check if specific model is supported
                    return any(
                        supported_model in model
                        for supported_model in provider_info["models"]
                    )

        return False

    @classmethod
    def get_supported_models(cls, provider: str) -> Optional[List[str]]:
        """Get list of supported models for a provider.

        Args:
            provider: The provider name

        Returns:
            Optional[List[str]]: List of supported models or None if all models are supported
        """
        for provider_info in cls.MODEL_TOOL_SUPPORT.values():
            if provider_info["provider"] == provider.lower():
                return provider_info["models"]
        return None
