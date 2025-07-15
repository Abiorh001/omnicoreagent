import os
from typing import Any

from dotenv import load_dotenv
import litellm
from mcpomni_connect.utils import logger
import warnings

# Suppress Pydantic serialization warnings
warnings.filterwarnings("ignore", message="PydanticSerializationUnexpectedValue")

load_dotenv()


class LLMConnection:
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.llm_config = None

        # Set LiteLLM API key
        os.environ["OPENAI_API_KEY"] = self.config.llm_api_key
        os.environ["ANTHROPIC_API_KEY"] = self.config.llm_api_key
        os.environ["GROQ_API_KEY"] = self.config.llm_api_key
        os.environ["GEMINI_API_KEY"] = self.config.llm_api_key
        os.environ["DEEPSEEK_API_KEY"] = self.config.llm_api_key
        os.environ["OPENROUTER_API_KEY"] = self.config.llm_api_key
        os.environ["AZURE_API_KEY"] = self.config.llm_api_key

        if not self.llm_config:
            logger.info("updating llm configuration")
            self.llm_configuration()
            logger.info(f"LLM configuration: {self.llm_config}")

    def llm_configuration(self):
        """Load the LLM configuration"""
        llm_config = self.config.load_config("servers_config.json")["LLM"]
        try:
            provider = llm_config.get("provider", "openai")
            model = llm_config.get("model", "gpt-4o-mini")
            temperature = llm_config.get("temperature", 0.5)
            max_tokens = llm_config.get("max_tokens", 5000)
            top_p = llm_config.get("top_p", 0)

            # Map provider names to LiteLLM format
            provider_model_map = {
                "openai": f"openai/{model}",
                "anthropic": f"anthropic/{model}",
                "groq": f"groq/{model}",
                "gemini": f"gemini/{model}",
                "deepseek": f"deepseek/{model}",
                "openrouter": f"openrouter/{model}",
                "azureopenai": f"azure/{model}",
                "ollama": f"ollama/{model}",
            }

            # Get the full model name for LiteLLM
            full_model = provider_model_map.get(provider.lower())

            self.llm_config = {
                "provider": provider,
                "model": full_model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
            }

            # Add Azure OpenAI specific configuration if provider is azureopenai
            if provider.lower() == "azureopenai":
                azure_endpoint = llm_config.get("azure_endpoint")
                azure_api_version = llm_config.get("azure_api_version", "2024-02-01")
                azure_deployment = llm_config.get("azure_deployment", model)

                if azure_endpoint:
                    os.environ["AZURE_API_BASE"] = azure_endpoint
                if azure_api_version:
                    os.environ["AZURE_API_VERSION"] = azure_api_version

                self.llm_config["model"] = f"azure/{azure_deployment}"

            # Add Ollama specific configuration if provider is ollama
            if provider.lower() == "ollama":
                ollama_host = llm_config.get("ollama_host", "http://localhost:11434")
                os.environ["OLLAMA_API_BASE"] = ollama_host

            return self.llm_config
        except Exception as e:
            logger.error(f"Error loading LLM configuration: {e}")
            return None

    async def llm_call(
        self,
        messages: list[Any],
        tools: list[dict[str, Any]] = None,
    ):
        """Call the LLM using LiteLLM"""
        try:
            # Convert Message objects to dicts before sending to LiteLLM
            def to_dict(msg):
                if hasattr(msg, "model_dump"):
                    return msg.model_dump(exclude_none=True)
                elif isinstance(msg, dict):
                    return msg
                elif hasattr(msg, "__dict__"):
                    return {k: v for k, v in msg.__dict__.items() if v is not None}
                else:
                    return msg

            messages_dicts = [to_dict(m) for m in messages]

            # Prepare the parameters for LiteLLM
            params = {
                "model": self.llm_config["model"],
                "messages": messages_dicts,
                "max_tokens": self.llm_config["max_tokens"],
                "temperature": self.llm_config["temperature"],
                "top_p": self.llm_config["top_p"],
            }

            # Add tools if provided
            if tools:
                params["tools"] = tools
                params["tool_choice"] = "auto"

            # Special handling for OpenRouter
            if self.llm_config["provider"].lower() == "openrouter":
                if not tools:
                    params["stop"] = ["\n\nObservation:"]

            # Call LiteLLM
            response = await litellm.acompletion(**params)

            return response

        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            return None