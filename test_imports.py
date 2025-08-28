#!/usr/bin/env python3
"""
Test file to verify that all imports work correctly after fixing __init__.py files.
"""


def test_top_level_imports():
    """Test top-level imports from omnicoreagent"""
    try:
        from omnicoreagent import OmniAgent, ToolRegistry, ReactAgent

        print("✅ Top-level imports work: OmniAgent, ToolRegistry, ReactAgent")
        return True
    except ImportError as e:
        print(f"❌ Top-level import failed: {e}")
        return False


def test_logger_import():
    """Test logger import from omnicoreagent"""
    try:
        from omnicoreagent import logger

        print("✅ Logger import works: logger")
        return True
    except ImportError as e:
        print(f"❌ Logger import failed: {e}")
        return False


def test_background_agent_imports():
    """Test background agent imports from omnicoreagent"""
    try:
        from omnicoreagent import (
            BackgroundOmniAgent,
            BackgroundAgentManager,
            TaskRegistry,
            APSchedulerBackend,
            BackgroundTaskScheduler,
        )

        print(
            "✅ Background agent imports work: BackgroundOmniAgent, BackgroundAgentManager, TaskRegistry, APSchedulerBackend, BackgroundTaskScheduler"
        )
        return True
    except ImportError as e:
        print(f"❌ Background agent import failed: {e}")
        return False


def test_deep_imports():
    """Test deep imports from omnicoreagent.core"""
    try:
        from omnicoreagent.core.tools import ToolRegistry, Tool

        print("✅ Deep imports work: ToolRegistry, Tool")
        return True
    except ImportError as e:
        print(f"❌ Deep import failed: {e}")
        return False


def test_agent_imports():
    """Test agent imports"""
    try:
        from omnicoreagent.core.agents import ReactAgent, OrchestratorAgent

        print("✅ Agent imports work: ReactAgent, OrchestratorAgent")
        return True
    except ImportError as e:
        print(f"❌ Agent import failed: {e}")
        return False


def test_memory_imports():
    """Test memory imports"""
    try:
        from omnicoreagent.core.memory_store import MemoryRouter

        print("✅ Memory imports work: MemoryRouter")
        return True
    except ImportError as e:
        print(f"❌ Memory import failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testing OmniCoreAgent imports...")
    print("=" * 50)

    success = True
    success &= test_top_level_imports()
    success &= test_logger_import()
    success &= test_background_agent_imports()
    success &= test_deep_imports()
    success &= test_agent_imports()
    success &= test_memory_imports()

    print("=" * 50)
    if success:
        print("🎉 All imports work correctly!")
    else:
        print("💥 Some imports failed!")
