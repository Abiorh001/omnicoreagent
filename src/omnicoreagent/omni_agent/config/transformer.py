import json
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
import uuid
from omnicoreagent.core.utils import logger
from decouple import config


class TransportType(str, Enum):
    """Supported transport types for MCP tools"""

    STDIO = "stdio"
    SSE = "sse"
    STREAMABLE_HTTP = "streamable_http"


@dataclass
class ModelConfig:
    """User-friendly model configuration"""

    provider: str
    model: str

    temperature: Optional[float] = 0.5
    max_tokens: Optional[int] = 5000
    max_context_length: Optional[int] = 100000
    top_p: Optional[float] = 0.7
    top_k: Optional[Union[int, str]] = "N/A"


@dataclass
class EmbeddingConfig:
    """User-friendly embedding configuration"""

    provider: str
    model: str

    dimensions: Optional[int] = None
    encoding_format: Optional[str] = "float"
    timeout: Optional[int] = 600


@dataclass
class MCPToolConfig:
    """User-friendly MCP tool configuration"""

    name: Optional[str] = None
    transport_type: TransportType = TransportType.STDIO
    url: Optional[str] = None
    command: Optional[str] = None
    args: Optional[List[str]] = None
    headers: Optional[Dict[str, str]] = None
    env: Optional[Dict[str, str]] = None
    timeout: Optional[int] = 60
    sse_read_timeout: Optional[int] = 120
    auth: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if not self.name:
            base = self.command or self.url or "mcp_tool"
            self.name = f"{base}_{uuid.uuid4().hex[:6]}"


@dataclass
class AgentConfig:
    """User-friendly agent configuration"""

    agent_name: str = "OmniAgent"
    tool_call_timeout: int = 30
    max_steps: int = 15
    request_limit: int = 0
    total_tokens_limit: int = 0
    enable_tools_knowledge_base: bool = False
    tools_results_limit: int = 10
    tools_similarity_threshold: float = 0.5
    memory_config: dict = field(
        default_factory=lambda: {"mode": "token_budget", "value": 30000}
    )
    memory_results_limit: int = 5
    memory_similarity_threshold: float = 0.5


class ConfigTransformer:
    """Transforms user-friendly configuration to internal format"""

    def __init__(self):
        self.supported_providers = {
            "openai": "openai",
            "anthropic": "anthropic",
            "groq": "groq",
            "ollama": "ollama",
            "azure": "azure",
            "gemini": "gemini",
        }

        self.supported_embedding_providers = {
            "openai": "openai",
            "cohere": "cohere",
            "mistral": "mistral",
            "gemini": "gemini",
            "vertex_ai": "vertex_ai",
            "voyage": "voyage",
            "nebius": "nebius",
            "nvidia_nim": "nvidia_nim",
            "bedrock": "bedrock",
            "huggingface": "huggingface",
        }

        self.supported_transports = {
            TransportType.STDIO: self._transform_stdio_config,
            TransportType.SSE: self._transform_sse_config,
            TransportType.STREAMABLE_HTTP: self._transform_streamable_http_config,
        }

    def transform_config(
        self,
        model_config: Union[Dict[str, Any], ModelConfig],
        mcp_tools: List[Union[Dict[str, Any], MCPToolConfig]],
        agent_config: Optional[Union[Dict[str, Any], AgentConfig]] = None,
        embedding_config: Optional[Union[Dict[str, Any], EmbeddingConfig]] = None,
    ) -> Dict[str, Any]:
        """
        Transform user configuration to internal format

        Args:
            model_config: Model configuration (dict or ModelConfig)
            mcp_tools: List of MCP tool configurations
            agent_config: Optional agent configuration
            embedding_config: Optional embedding configuration (dict or EmbeddingConfig)

        Returns:
            Internal configuration dictionary
        """
        try:
            # Convert to dataclasses if needed
            model = self._ensure_model_config(model_config)
            tools = [self._ensure_tool_config(tool) for tool in mcp_tools]
            agent = (
                self._ensure_agent_config(agent_config)
                if agent_config
                else AgentConfig()
            )
            embedding = (
                self._ensure_embedding_config(embedding_config)
                if embedding_config
                else None
            )

            # Validate configurations
            self._validate_model_config(model)
            self._validate_tools_config(tools)
            if embedding:
                self._validate_embedding_config(embedding)

            # Check if vector database is enabled and require embedding configuration
            ENABLE_VECTOR_DB = config("ENABLE_VECTOR_DB", default=False, cast=bool)
            if ENABLE_VECTOR_DB and not embedding:
                raise ValueError(
                    "Vector database is enabled (ENABLE_VECTOR_DB=True) but no embedding configuration provided. "
                    "Embedding configuration is REQUIRED when vector database is enabled."
                )
            elif ENABLE_VECTOR_DB and embedding:
                logger.info(
                    "Vector database validation passed: embedding configuration provided"
                )

            # Transform to internal format
            internal_config = {
                "AgentConfig": asdict(agent),
                "LLM": self._transform_model_config(model),
                "mcpServers": self._transform_tools_config(tools),
            }

            # Add EMBEDDING if provided
            if embedding:
                internal_config["EMBEDDING"] = self._transform_embedding_config(
                    embedding
                )

            embedding_info = " with embedding" if embedding else ""
            logger.info(
                f"Successfully transformed configuration for {len(tools)} MCP tools{embedding_info}"
            )
            return internal_config

        except Exception as e:
            logger.error(f"Configuration transformation failed: {e}")
            raise ValueError(f"Invalid configuration: {e}")

    def _ensure_model_config(
        self, config: Union[Dict[str, Any], ModelConfig]
    ) -> ModelConfig:
        """Ensure model config is a ModelConfig instance"""
        if isinstance(config, dict):
            return ModelConfig(**config)
        elif isinstance(config, ModelConfig):
            return config
        else:
            raise ValueError("model_config must be dict or ModelConfig")

    def _ensure_tool_config(
        self, config: Union[Dict[str, Any], MCPToolConfig]
    ) -> MCPToolConfig:
        """Ensure tool config is an MCPToolConfig instance"""
        if isinstance(config, dict):
            return MCPToolConfig(**config)
        elif isinstance(config, MCPToolConfig):
            return config
        else:
            raise ValueError("mcp_tools must contain dict or MCPToolConfig")

    def _ensure_agent_config(
        self, config: Union[Dict[str, Any], AgentConfig]
    ) -> AgentConfig:
        """Ensure agent config is an AgentConfig instance"""
        if isinstance(config, dict):
            # Filter out None values for limits to use defaults
            filtered_config = config.copy()
            if filtered_config.get("request_limit") is None:
                filtered_config.pop("request_limit", None)
            if filtered_config.get("total_tokens_limit") is None:
                filtered_config.pop("total_tokens_limit", None)
            return AgentConfig(**filtered_config)
        elif isinstance(config, AgentConfig):
            return config
        else:
            raise ValueError("agent_config must be dict or AgentConfig")

    def _validate_model_config(self, config: ModelConfig):
        """Validate model configuration"""
        if not config.provider:
            raise ValueError("Model provider is required")

        if config.provider not in self.supported_providers:
            supported = ", ".join(self.supported_providers.keys())
            raise ValueError(
                f"Unsupported provider: {config.provider}. Supported: {supported}"
            )

        if not config.model:
            raise ValueError("Model name is required")

        # Validate numeric ranges
        if config.temperature is not None and not (0 <= config.temperature <= 2):
            raise ValueError("Temperature must be between 0 and 2")

        if config.max_tokens is not None and config.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")

        if config.max_context_length is not None and config.max_context_length <= 0:
            raise ValueError("max_context_length must be positive")

    def _validate_tools_config(self, tools: List[MCPToolConfig]):
        """Validate MCP tools configuration"""
        if not tools:
            logger.warning("No MCP tools provided, using local tools only")
            return

        tool_names = set()
        for tool in tools:
            if not tool.name:
                raise ValueError("Tool name is required")

            if tool.name in tool_names:
                raise ValueError(f"Duplicate tool name: {tool.name}")
            tool_names.add(tool.name)

            if tool.transport_type not in self.supported_transports:
                supported = ", ".join([t.value for t in TransportType])
                raise ValueError(
                    f"Unsupported transport type: {tool.transport_type}. Supported: {supported}"
                )

            # Validate transport-specific requirements
            self._validate_tool_transport(tool)

    def _validate_tool_transport(self, tool: MCPToolConfig):
        """Validate tool transport configuration"""
        if tool.transport_type in [TransportType.SSE, TransportType.STREAMABLE_HTTP]:
            if not tool.url:
                raise ValueError(f"URL is required for {tool.transport_type} transport")

        elif tool.transport_type == TransportType.STDIO:
            if not tool.command:
                raise ValueError("Command is required for stdio transport")

    def _transform_model_config(self, config: ModelConfig) -> Dict[str, Any]:
        """Transform model config to internal LLM format"""
        return {
            "provider": self.supported_providers[config.provider],
            "model": config.model,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "max_context_length": config.max_context_length,
            "top_p": config.top_p,
            "top_k": config.top_k,
        }

    def _ensure_embedding_config(
        self, config: Union[Dict[str, Any], EmbeddingConfig]
    ) -> EmbeddingConfig:
        """Ensure embedding config is an EmbeddingConfig instance"""
        if isinstance(config, dict):
            return EmbeddingConfig(**config)
        elif isinstance(config, EmbeddingConfig):
            return config
        else:
            raise ValueError("embedding_config must be dict or EmbeddingConfig")

    def _validate_embedding_config(self, config: EmbeddingConfig):
        """Validate embedding configuration"""
        if not config.provider:
            raise ValueError("Embedding provider is required")

        if config.provider not in self.supported_embedding_providers:
            supported = ", ".join(self.supported_embedding_providers.keys())
            raise ValueError(
                f"Unsupported embedding provider: {config.provider}. Supported: {supported}"
            )

        if not config.model:
            raise ValueError("Embedding model name is required")

        # Dimensions is MANDATORY for vector database compatibility
        if config.dimensions is None:
            raise ValueError(
                "Embedding dimensions is REQUIRED and cannot be None. This is needed for vector database index creation."
            )

        if not isinstance(config.dimensions, int) or config.dimensions <= 0:
            raise ValueError("Embedding dimensions must be a positive integer")

        if config.timeout is not None and config.timeout <= 0:
            raise ValueError("Embedding timeout must be positive")

    def _transform_embedding_config(self, config: EmbeddingConfig) -> Dict[str, Any]:
        """Transform embedding config to internal EMBEDDING format"""
        return {
            "provider": self.supported_embedding_providers[config.provider],
            "model": config.model,
            "dimensions": config.dimensions,
            "encoding_format": config.encoding_format,
            "timeout": config.timeout,
        }

    def _transform_tools_config(self, tools: List[MCPToolConfig]) -> Dict[str, Any]:
        """Transform tools config to internal mcpServers format"""
        servers = {}

        for tool in tools:
            transformer = self.supported_transports[tool.transport_type]
            servers[tool.name] = transformer(tool)

        return servers

    def _transform_stdio_config(self, tool: MCPToolConfig) -> Dict[str, Any]:
        """Transform stdio transport configuration"""
        config = {
            "transport_type": "stdio",
            "command": tool.command,
            "args": tool.args or [],
        }

        if tool.env:
            config["env"] = tool.env

        return config

    def _transform_sse_config(self, tool: MCPToolConfig) -> Dict[str, Any]:
        """Transform SSE transport configuration"""
        config = {
            "transport_type": "sse",
            "url": tool.url,
            "timeout": tool.timeout,
            "sse_read_timeout": tool.sse_read_timeout,
        }

        if tool.headers:
            # ensure its dict
            if not isinstance(tool.headers, dict):
                raise ValueError("headers must be a dictionary")
            config["headers"] = tool.headers

        return config

    def _transform_streamable_http_config(self, tool: MCPToolConfig) -> Dict[str, Any]:
        """Transform streamable HTTP transport configuration"""
        config = {
            "transport_type": "streamable_http",
            "url": tool.url,
            "timeout": tool.timeout,
        }

        if tool.headers:
            if not isinstance(tool.headers, dict):
                raise ValueError("headers must be a dictionary")
            config["headers"] = tool.headers

        if tool.auth:
            if not isinstance(tool.auth, dict):
                raise ValueError("auth must be a dictionary")
            config["auth"] = tool.auth

        return config

    def save_config(self, config: Dict[str, Any], filepath: str):
        """Save configuration to file"""
        try:
            with open(filepath, "w") as f:
                json.dump(config, f, indent=2)
            logger.info(f"Configuration saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise


# Global transformer instance
config_transformer = ConfigTransformer()
