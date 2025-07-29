#!/usr/bin/env python3
"""
Simple test for CLI initialization
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcpomni_connect.omni_agent.agent import OmniAgent
from mcpomni_connect.memory_store.memory_router import MemoryRouter
from mcpomni_connect.events.event_router import EventRouter
from mcpomni_connect.agents.tools.local_tools_registry import ToolRegistry


async def test_agent_creation():
    """Test basic agent creation."""
    print("🚀 Testing agent creation...")

    try:
        # Initialize routers
        memory_router = MemoryRouter("in_memory")
        event_router = EventRouter("in_memory")

        print("✅ Routers initialized")

        # Create tool registry
        tool_registry = ToolRegistry()
        print("✅ Tool registry created")

        # Create agent
        agent = OmniAgent(
            name="test_agent",
            system_instruction="You are a helpful AI assistant.",
            model_config={
                "provider": "openai",
                "model": "gpt-4.1",
                "temperature": 0.7,
                "max_context_length": 50000,
            },
            mcp_tools=[],
            local_tools=tool_registry,
            agent_config={
                "max_steps": 15,
                "tool_call_timeout": 60,
                "request_limit": 1000,
                "memory_config": {"mode": "token_budget", "value": 10000},
            },
            memory_store=memory_router,
            event_router=event_router,
            debug=True,
        )

        print("✅ Agent created successfully")

        # Test a simple run
        result = await agent.run("Hello", session_id="test_session")
        print(f"✅ Agent run successful: {result['response'][:100]}...")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_agent_creation())
