"""
OmniCoreAgent AI Framework

A comprehensive AI agent framework with MCP client capabilities.
"""

from .core.agents import (
    ReactAgent,
    OrchestratorAgent,
    SequentialAgent,
    ToolCallingAgent,
)
from .core.memory_store import MemoryRouter
from .core.llm import LLMConnection
from .core.events import EventRouter
from .core.database import DatabaseMessageStore
from .core.tools import ToolRegistry, Tool
from .core.utils import logger

# High-level interface
from .omni_agent.agent import OmniAgent
from .omni_agent.background_agent import (
    BackgroundOmniAgent,
    BackgroundAgentManager,
    TaskRegistry,
    APSchedulerBackend,
    BackgroundTaskScheduler,
)

# MCP Client (for advanced users)
from .mcp_omni_connect import MCPClient, Configuration, main

__all__ = [
    # Core Agents
    "ReactAgent",
    "OrchestratorAgent",
    "SequentialAgent",
    "ToolCallingAgent",
    # Core Components
    "MemoryRouter",
    "LLMConnection",
    "EventRouter",
    "DatabaseMessageStore",
    "ToolRegistry",
    "Tool",
    "logger",
    # High-level Interface
    "OmniAgent",
    "BackgroundOmniAgent",
    "BackgroundAgentManager",
    "TaskRegistry",
    "APSchedulerBackend",
    "BackgroundTaskScheduler",
    # MCP Client
    "MCPClient",
    "Configuration",
    "main",
]
