"""
OmniAgent Package

This package provides the high-level OmniAgent interface and background agent functionality.
"""

from .agent import OmniAgent
from .background_agent import (
    BackgroundOmniAgent,
    BackgroundAgentManager,
    TaskRegistry,
    APSchedulerBackend,
    BackgroundTaskScheduler,
)

__all__ = [
    "OmniAgent",
    "BackgroundOmniAgent",
    "BackgroundAgentManager",
    "TaskRegistry",
    "APSchedulerBackend",
    "BackgroundTaskScheduler",
]
