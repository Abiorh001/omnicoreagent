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
from mcpomni_connect.config import config_transformer, ModelConfig, MCPToolConfig, TransportType, AgentConfig
from mcpomni_connect.system_prompts import generate_react_agent_prompt
from mcpomni_connect.constants import date_time_func


class OmniAgent:
    """
    A simple, user-friendly interface for creating and using MCP agents.
    
    This class provides a high-level API that abstracts away the complexity
    of MCP client configuration and agent creation.
    """
    
    def __init__(
        self,
        name: str,
        model_config: Union[Dict[str, Any], ModelConfig],
        mcp_tools: List[Union[Dict[str, Any], MCPToolConfig]] = None,
        local_tools: Optional[Any] = None,  # LocalToolsIntegration instance
        agent_config: Optional[Union[Dict[str, Any], AgentConfig]] = None,
        session_store: Optional[InMemoryStore] = None,
        debug: bool = False,
        internal_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the OmniAgent with user-friendly configuration.
        
        Args:
            name: Name of the agent
            model_config: Model configuration (dict or ModelConfig)
            mcp_tools: List of MCP tool configurations (optional)
            local_tools: LocalToolsIntegration instance (optional)
            agent_config: Optional agent configuration
            session_store: Optional session store (InMemoryStore)
            debug: Enable debug logging
        """
        self.name = name
        self.model_config = model_config
        self.mcp_tools = mcp_tools or []
        self.local_tools = local_tools  
        self.agent_config = agent_config
        self.debug = debug
        self.internal_config = internal_config
        
        # Initialize components
        self.config_transformer = config_transformer
        self.agent = None
        self.mcp_client = None
        self.llm_connection = None
        
        # Initialize memory/session store
        self._setup_session_store(session_store)
        
        # Transform user config to internal format
        if not internal_config:
            self.internal_config = self._create_internal_config()
        
        # Create agent
        self._create_agent()
        
        print(f"🚀 OmniAgent '{self.name}' initialized successfully!")
        print(f"📁 Server config saved to: servers_config.json")
        if self.session_store:
            print(f"💾 Session store enabled with max context: {self.session_store.max_context_tokens}")
        
        # Show tool information
        self._show_tool_info()
    
    def _show_tool_info(self):
        """Show information about available tools"""
        mcp_count = len(self.mcp_tools) if self.mcp_tools else 0
        local_count = len(self.local_tools.get_available_tools()) if self.local_tools else 0
        
        print(f"🔧 Tools configured:")
        print(f"  • MCP Tools: {mcp_count}")
        print(f"  • Local Tools: {local_count}")
        
        if self.local_tools:
            print("  📋 Local tools available:")
            for tool in self.local_tools.get_available_tools():
                print(f"    - {tool['name']}: {tool['description']}")
    
    def _setup_session_store(self, session_store: Optional[InMemoryStore]):
        """Setup session store with proper configuration"""
        if session_store:
            # Use provided session store
            self.session_store = session_store
        else:
            # Create default session store with max context from model config
            max_context_tokens = 100000  # default
            if isinstance(self.model_config, dict):
                max_context_tokens = self.model_config.get("max_context_length", max_context_tokens)
            elif hasattr(self.model_config, 'max_context_length'):
                max_context_tokens = self.model_config.max_context_length
            
            self.session_store = InMemoryStore(
                max_context_tokens=max_context_tokens,
                debug=self.debug
            )
    
    def _create_internal_config(self) -> Dict[str, Any]:
        """Transform user configuration to internal format"""
        print(f"🔄 Transforming configuration for agent '{self.name}'...")
        
        # Prepare agent config with the agent name included
        agent_config_with_name = self._prepare_agent_config()
        
        internal_config = config_transformer.transform_config(
            model_config=self.model_config,
            mcp_tools=self.mcp_tools,
            agent_config=agent_config_with_name
        )
        
        # Save to hidden location
        self._save_config_hidden(internal_config)
        
        return internal_config
    
    def _prepare_agent_config(self) -> Dict[str, Any]:
        """Prepare agent config with the agent name included"""
        if self.agent_config:
            if isinstance(self.agent_config, dict):
                # Add agent name to the config
                agent_config_dict = self.agent_config.copy()
                agent_config_dict["agent_name"] = self.name
                return agent_config_dict
            else:
                # If it's already a dataclass, convert to dict
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
               
            }
    
    def _save_config_hidden(self, config: Dict[str, Any]):
        """Save config to hidden location only"""
        # Create hidden directory in project root
        hidden_dir = Path(".mcp_config")
        hidden_dir.mkdir(exist_ok=True)
        
        # Save config to hidden file only
        hidden_config_path = hidden_dir / "servers_config.json"
        self.config_transformer.save_config(config, str(hidden_config_path))
        
        print(f"📁 Config saved to: {hidden_config_path} (hidden from user)")
        print(f"🔒 servers_config.json is not visible in project root")
    
    def _create_agent(self):
        """Create the appropriate agent based on type"""
        # Initialize MCP client (only if MCP tools are provided)
        if self.mcp_tools:
            config = Configuration()
            self.mcp_client = MCPClient(config, debug=self.debug)
        else:
            self.mcp_client = None
            
        self.llm_connection = LLMConnection(Configuration())
        
        # Get agent config from internal config (which already has the name)
        agent_config_dict = self.internal_config["AgentConfig"]
        agent_settings = ReactAgentConfig(**agent_config_dict)
        
        # Create ReactAgent
        self.agent = ReactAgent(config=agent_settings)
    
    def _combine_available_tools(self) -> Dict[str, Any]:
        """Combine MCP tools and local tools into a single available_tools dict"""
        combined_tools = {}
        
        # Add MCP tools if available
        if self.mcp_client and self.mcp_client.available_tools:
            combined_tools.update(self.mcp_client.available_tools)
        
        # Add local tools if available
        if self.local_tools:
            local_tools_list = self.local_tools.get_available_tools()
            if local_tools_list:
                # Create a "local_tools" server entry
                combined_tools["local_tools"] = local_tools_list
        
        return combined_tools
    
    def generate_chat_id(self) -> str:
        """Generate a new chat ID for the session"""
        return f"omni_agent_{self.name}_{uuid.uuid4().hex[:8]}"
    
    async def run(self, query: str, chat_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the agent with a query and optional chat ID.
        
        Args:
            query: The user query
            chat_id: Optional chat ID for session continuity
            
        Returns:
            Dict containing response and chat_id
        """
        # Generate chat ID if not provided
        if not chat_id:
            chat_id = self.generate_chat_id()
            print(f"🆔 Generated new chat ID: {chat_id}")
        else:
            print(f"🆔 Using provided chat ID: {chat_id}")
        
        # Connect to MCP servers if MCP tools are configured
        if self.mcp_client and self.mcp_tools:
            await self.mcp_client.connect_to_servers()
        
        # Generate system prompt
        react_agent_prompt = generate_react_agent_prompt(
            current_date_time=date_time_func["format_date"]()
        )
        
        # Combine available tools from both MCP and local sources
        available_tools = self._combine_available_tools()
        
        # Prepare extra kwargs
        extra_kwargs = {
            "sessions": self.mcp_client.sessions if self.mcp_client else {},
            "available_tools": available_tools,
            "local_tools": self.local_tools,  # Pass local tools for execution
            "session_id": chat_id,
        }
        
        # Run the agent with memory object directly
        response = await self.agent._run(
            system_prompt=react_agent_prompt,
            query=query,
            llm_connection=self.llm_connection,
            add_message_to_history=self.session_store.store_message,
            message_history=self.session_store.get_messages,
            debug=self.debug,
            **extra_kwargs,
        )
        
        return {
            "response": response,
            "chat_id": chat_id,
            "agent_name": self.name
        }
    
    async def get_chat_history(self, chat_id: str) -> List[Dict[str, Any]]:
        """Get chat history for a specific chat ID"""
        if not self.session_store:
            return []
        
        return await self.session_store.get_messages(session_id=chat_id, agent_name=self.name)
    
    async def clear_chat_history(self, chat_id: Optional[str] = None):
        """Clear chat history for a specific chat ID or all history"""
        if not self.session_store:
            return
        
        if chat_id:
            await self.session_store.clear_memory(session_id=chat_id, agent_name=self.name)
            print(f"🧹 Cleared chat history for chat ID: {chat_id}")
        else:
            await self.session_store.clear_memory(agent_name=self.name)
            print(f"🧹 Cleared all chat history for agent: {self.name}")
    
    async def cleanup(self):
        """Clean up resources"""
        if self.mcp_client:
            await self.mcp_client.cleanup()
        
        # Clean up config files
        self._cleanup_config()
    
    def _cleanup_config(self):
        """Clean up the config files"""
        try:
            # Remove hidden directory only
            hidden_dir = Path(".mcp_config")
            if hidden_dir.exists():
                shutil.rmtree(hidden_dir)
                print("🧹 Hidden config files cleaned up")
        except Exception as e:
            print(f"Warning: Could not clean up config files: {e}")
    
    def get_config(self) -> Dict[str, Any]:
        """Get the current internal configuration"""
        return self.internal_config.copy()