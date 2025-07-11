from typing import Dict, Any, List, Optional, Union, Callable
import json
import asyncio
from dataclasses import dataclass
from .local_tools_registry import ToolRegistr
from .tools_handler import MCPToolHandler, LocalToolHandler, ToolExecutor


@dataclass
class ToolInfo:
    """Unified tool information"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    source: str  # "mcp" or "local"
    server_name: Optional[str] = None  # For MCP tools
    function: Optional[Callable] = None  # For local tools


class UnifiedToolManager:
    """
    Unified tool manager that provides a seamless interface for both MCP and local tools.
    
    This manager allows you to:
    - Register and use local Python functions as tools
    - Access MCP tools from connected servers
    - Execute tools regardless of their source
    - Get unified tool listings and schemas
    - Handle tool conflicts (MCP tools take priority)
    """
    
    def __init__(self):
        self.local_tools = LocalToolsIntegration()
        self.mcp_tools: Dict[str, List[Any]] = {}
        self.mcp_sessions: Dict[str, Any] = {}
        self._tool_cache: Dict[str, ToolInfo] = {}
        
    # === Local Tools Management ===
    
    def register_tool(self, tool_name: str, tool_function: callable, description: str = None, schema: Dict[str, Any] = None):
        """Register a local Python function as a tool"""
        self.local_tools.register_tool(tool_name, tool_function, description, schema)
        self._update_tool_cache()
        
    def register_tool_decorator(self, name: str = None, description: str = "", schema: Dict[str, Any] = None):
        """Decorator for registering local tools"""
        def decorator(func):
            tool_name = name or func.__name__
            self.register_tool(tool_name, func, description, schema)
            return func
        return decorator
    
    # === MCP Tools Management ===
    
    def set_mcp_tools(self, mcp_tools: Dict[str, List[Any]], sessions: Dict[str, Any]):
        """Set MCP tools and sessions from connected servers"""
        self.mcp_tools = mcp_tools
        self.mcp_sessions = sessions
        self._update_tool_cache()
        
    def add_mcp_server(self, server_name: str, tools: List[Any], session: Any):
        """Add a single MCP server's tools"""
        self.mcp_tools[server_name] = tools
        self.mcp_sessions[server_name] = session
        self._update_tool_cache()
        
    # === Unified Tool Access ===
    
    def get_all_tools(self) -> List[ToolInfo]:
        """Get all available tools (MCP and local)"""
        return list(self._tool_cache.values())
    
    def get_tool(self, tool_name: str) -> Optional[ToolInfo]:
        """Get a specific tool by name"""
        return self._tool_cache.get(tool_name.lower())
    
    def list_tool_names(self) -> List[str]:
        """Get list of all available tool names"""
        return list(self._tool_cache.keys())
    
    def get_tools_by_source(self, source: str) -> List[ToolInfo]:
        """Get tools filtered by source ('mcp' or 'local')"""
        return [tool for tool in self._tool_cache.values() if tool.source == source]
    
    def get_mcp_tools(self) -> List[ToolInfo]:
        """Get only MCP tools"""
        return self.get_tools_by_source("mcp")
    
    def get_local_tools(self) -> List[ToolInfo]:
        """Get only local tools"""
        return self.get_tools_by_source("local")
    
    # === Tool Execution ===
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute a tool regardless of its source (MCP or local)"""
        tool_info = self.get_tool(tool_name)
        if not tool_info:
            raise ValueError(f"Tool '{tool_name}' not found")
            
        if tool_info.source == "mcp":
            return await self._execute_mcp_tool(tool_info, parameters)
        else:
            return await self._execute_local_tool(tool_info, parameters)
    
    async def _execute_mcp_tool(self, tool_info: ToolInfo, parameters: Dict[str, Any]) -> Any:
        """Execute an MCP tool"""
        if not tool_info.server_name or tool_info.server_name not in self.mcp_sessions:
            raise ValueError(f"MCP server '{tool_info.server_name}' not available")
            
        session = self.mcp_sessions[tool_info.server_name]["session"]
        result = await session.call_tool(tool_info.name, parameters)
        
        # Normalize result
        if hasattr(result, 'content'):
            return result.content
        return str(result)
    
    async def _execute_local_tool(self, tool_info: ToolInfo, parameters: Dict[str, Any]) -> Any:
        """Execute a local tool"""
        return await self.local_tools.execute_tool(tool_info.name, parameters)
    
    # === Tool Schema and Documentation ===
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get schema for a specific tool"""
        tool_info = self.get_tool(tool_name)
        if tool_info:
            return {
                "name": tool_info.name,
                "description": tool_info.description,
                "inputSchema": tool_info.input_schema,
                "source": tool_info.source,
                "server_name": tool_info.server_name
            }
        return None
    
    def get_all_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get schemas for all tools"""
        schemas = {}
        for tool_info in self._tool_cache.values():
            schemas[tool_info.name] = self.get_tool_schema(tool_info.name)
        return schemas
    
    def get_tools_for_llm(self) -> List[Dict[str, Any]]:
        """Get tools in format suitable for LLM function calling"""
        tools = []
        for tool_info in self._tool_cache.values():
            tools.append({
                "type": "function",
                "function": {
                    "name": tool_info.name,
                    "description": tool_info.description,
                    "parameters": tool_info.input_schema,
                },
            })
        return tools
    
    # === Tool Validation ===
    
    async def validate_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a tool call request"""
        tool_info = self.get_tool(tool_name)
        if not tool_info:
            return {
                "valid": False,
                "error": f"Tool '{tool_name}' not found"
            }
        
        # Basic parameter validation
        if not isinstance(parameters, dict):
            return {
                "valid": False,
                "error": "Parameters must be a dictionary"
            }
        
        return {
            "valid": True,
            "tool_info": tool_info
        }
    
    # === Internal Methods ===
    
    def _update_tool_cache(self):
        """Update the internal tool cache"""
        self._tool_cache.clear()
        
        # Add MCP tools first (they take priority)
        for server_name, tools in self.mcp_tools.items():
            for tool in tools:
                if hasattr(tool, 'name'):
                    tool_info = ToolInfo(
                        name=tool.name,
                        description=getattr(tool, 'description', ''),
                        input_schema=getattr(tool, 'inputSchema', {}),
                        source="mcp",
                        server_name=server_name
                    )
                    self._tool_cache[tool.name.lower()] = tool_info
        
        # Add local tools (won't override MCP tools with same name)
        local_tools_list = self.local_tools.get_available_tools()
        for tool_data in local_tools_list:
            tool_name = tool_data['name']
            if tool_name.lower() not in self._tool_cache:  # Don't override MCP tools
                tool_info = ToolInfo(
                    name=tool_name,
                    description=tool_data['description'],
                    input_schema=tool_data['inputSchema'],
                    source="local",
                    function=self.local_tools.tool_registry.get_tool(tool_name).function if self.local_tools.tool_registry.get_tool(tool_name) else None
                )
                self._tool_cache[tool_name.lower()] = tool_info
    
    # === Utility Methods ===
    
    def get_tool_summary(self) -> Dict[str, Any]:
        """Get a summary of all available tools"""
        mcp_count = len(self.get_mcp_tools())
        local_count = len(self.get_local_tools())
        total_count = len(self._tool_cache)
        
        return {
            "total_tools": total_count,
            "mcp_tools": mcp_count,
            "local_tools": local_count,
            "sources": {
                "mcp": [tool.server_name for tool in self.get_mcp_tools()],
                "local": "local_registry"
            }
        }
    
    def clear_cache(self):
        """Clear the tool cache and rebuild it"""
        self._update_tool_cache()
    
    def has_tool(self, tool_name: str) -> bool:
        """Check if a tool exists"""
        return tool_name.lower() in self._tool_cache
    
    def get_tool_source(self, tool_name: str) -> Optional[str]:
        """Get the source of a tool ('mcp' or 'local')"""
        tool_info = self.get_tool(tool_name)
        return tool_info.source if tool_info else None 