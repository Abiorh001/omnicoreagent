"""
Background Agent System for Self-Flying Automation.

This module provides a comprehensive system for creating and managing
background agents that can execute tasks automatically.
"""

from .background_agents import BackgroundOmniAgent
from .background_agent_manager import BackgroundAgentManager
from .task_registry import TaskRegistry
from .scheduler_backend import APSchedulerBackend
from .base import BackgroundTaskScheduler

__all__ = [
    "BackgroundOmniAgent",
    "BackgroundAgentManager",
    "TaskRegistry",
    "APSchedulerBackend",
    "BackgroundTaskScheduler",
]
