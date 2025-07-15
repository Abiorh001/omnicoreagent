import os
import json
import shutil
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from mcpomni_connect.agents.react_agent import ReactAgent
from mcpomni_connect.agents.types import AgentConfig as ReactAgentConfig
from mcpomni_connect.client import Configuration, MCPClient
from mcpomni_connect.llm import LLMConnection
from mcpomni_connect.memory import InMemoryStore
from mcpomni_connect.omni_agent.config import (
    config_transformer,
    ModelConfig,
    MCPToolConfig,
    TransportType,
    AgentConfig,
)
from mcpomni_connect.system_prompts import generate_react_agent_prompt
from mcpomni_connect.constants import date_time_func
from mcpomni_connect.omni_agent.prompts.prompt_builder import OmniAgentPromptBuilder
from mcpomni_connect.omni_agent.prompts.react_suffix import SYSTEM_SUFFIX
from mcpomni_connect.memory_store.memory_router import MemoryRouter


class OmniAgent:
    """
    A simple, user-friendly interface for creating and using MCP agents.

    This class provides a high-level API that abstracts away the complexity
    of MCP client configuration and agent creation.
    """

    def __init__(
        self,
        name: str,
        system_instruction: str,
        model_config: Union[Dict[str, Any], ModelConfig],
        mcp_tools: List[Union[Dict[str, Any], MCPToolConfig]] = None,
        local_tools: Optional[Any] = None,  # LocalToolsIntegration instance
        agent_config: Optional[Union[Dict[str, Any], AgentConfig]] = None,
        memory_store: Optional[MemoryRouter] = None,
        debug: bool = False,
    ):
        """
        Initialize the OmniAgent with user-friendly configuration.

        Args:
            name: Name of the agent
            system_instruction: System instruction for the agent
            model_config: Model configuration (dict or ModelConfig)
            mcp_tools: List of MCP tool configurations (optional)
            local_tools: LocalToolsIntegration instance (optional)
            agent_config: Optional agent configuration
            memory_store: Optional memory store (MemoryRouter)
            debug: Enable debug logging
        """
        # Core attributes
        self.name = name
        self.system_instruction = system_instruction
        self.model_config = model_config
        self.mcp_tools = mcp_tools or []
        self.local_tools = local_tools
        self.agent_config = agent_config
        self.debug = debug
        self.memory_store = memory_store

        # Internal components
        self.config_transformer = config_transformer
        self.prompt_builder = OmniAgentPromptBuilder(SYSTEM_SUFFIX)
        self.agent = None
        self.mcp_client = None
        self.llm_connection = None

        # Transform user config to internal format
        self.internal_config = self._create_internal_config()

        # Create agent
        self._create_agent()

    def _create_internal_config(self) -> Dict[str, Any]:
        """Transform user configuration to internal format"""
        agent_config_with_name = self._prepare_agent_config()

        internal_config = config_transformer.transform_config(
            model_config=self.model_config,
            mcp_tools=self.mcp_tools,
            agent_config=agent_config_with_name,
        )

        # Save to hidden location
        self._save_config_hidden(internal_config)

        return internal_config

    def _prepare_agent_config(self) -> Dict[str, Any]:
        """Prepare agent config with the agent name included"""
        if self.agent_config:
            if isinstance(self.agent_config, dict):
                agent_config_dict = self.agent_config.copy()
                agent_config_dict["agent_name"] = self.name
                return agent_config_dict
            else:
                agent_config_dict = self.agent_config.__dict__.copy()
                agent_config_dict["agent_name"] = self.name
                return agent_config_dict
        else:
            # Default agent config with the agent name
            return {
                "agent_name": self.name,
                "tool_call_timeout": 30,
                "max_steps": 15,
                "request_limit": 5000,
                "total_tokens_limit": 40000000,
                "memory_config": {"mode": "token_budget", "value": 30000},
            }

    def _save_config_hidden(self, config: Dict[str, Any]):
        """Save config to hidden location"""
        hidden_dir = Path(".mcp_config")
        hidden_dir.mkdir(exist_ok=True)

        hidden_config_path = hidden_dir / "servers_config.json"
        self.config_transformer.save_config(config, str(hidden_config_path))

    def _create_agent(self):
        """Create the appropriate agent based on configuration"""
        # Initialize MCP client (only if MCP tools are provided)
        if self.mcp_tools:
            config = Configuration()
            self.mcp_client = MCPClient(config, debug=self.debug)
        else:
            self.mcp_client = None

        self.llm_connection = LLMConnection(Configuration())

        # Get agent config from internal config
        agent_config_dict = self.internal_config["AgentConfig"]
        agent_settings = ReactAgentConfig(**agent_config_dict)

        # Set memory config
        if self.memory_store:
            self.memory_store.set_memory_config(
                mode=agent_settings.memory_config["mode"],
                value=agent_settings.memory_config["value"],
            )

        # Create ReactAgent
        self.agent = ReactAgent(config=agent_settings)

    def generate_session_id(self) -> str:
        """Generate a new session ID for the session"""
        return f"omni_agent_{self.name}_{uuid.uuid4().hex[:8]}"

    async def run(self, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the agent with a query and optional session ID.

        Args:
            query: The user query
            session_id: Optional session ID for session continuity

        Returns:
            Dict containing response and session_id
        """
        # Generate session ID if not provided
        if not session_id:
            session_id = self.generate_session_id()

        # Connect to MCP servers if MCP tools are configured
        if self.mcp_client and self.mcp_tools:
            await self.mcp_client.connect_to_servers()

        omni_agent_prompt = self.prompt_builder.build(
            system_instruction=self.system_instruction
        )
        #print(omni_agent_prompt)
        # Prepare extra kwargs - pass tools separately
        extra_kwargs = {
            "sessions": self.mcp_client.sessions if self.mcp_client else {},
            "mcp_tools": self.mcp_client.available_tools if self.mcp_client else {},
            "local_tools": self.local_tools,
            "session_id": session_id,
        }

        # Run the agent with memory object directly
        response = await self.agent._run(
            system_prompt=omni_agent_prompt,
            query=query,
            llm_connection=self.llm_connection,
            add_message_to_history=self.memory_store.store_message,
            message_history=self.memory_store.get_messages,
            debug=self.debug,
            **extra_kwargs,
        )

        return {"response": response, "session_id": session_id, "agent_name": self.name}

    async def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get session history for a specific session ID"""
        if not self.memory_store:
            return []

        return await self.memory_store.get_messages(
            session_id=session_id, agent_name=self.name
        )

    async def clear_session_history(self, session_id: Optional[str] = None):
        """Clear session history for a specific session ID or all history"""
        if not self.memory_store:
            return

        if session_id:
            await self.memory_store.clear_memory(
                session_id=session_id, agent_name=self.name
            )
        else:
            await self.memory_store.clear_memory(agent_name=self.name)

    async def cleanup(self):
        """Clean up resources"""
        if self.mcp_client:
            await self.mcp_client.cleanup()

        # Clean up config files
        self._cleanup_config()

    def _cleanup_config(self):
        """Clean up the config files"""
        try:
            hidden_dir = Path(".mcp_config")
            if hidden_dir.exists():
                shutil.rmtree(hidden_dir)
        except Exception as e:
            # Silently handle cleanup errors
            pass
