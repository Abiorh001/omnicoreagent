#!/usr/bin/env python3
"""
Test script to verify background agent session ID and event streaming fixes.
"""

import asyncio
import sys
import os
from typing import Dict, Any

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from mcpomni_connect.omni_agent.background_agent.background_agent_manager import (
    BackgroundAgentManager,
)
from mcpomni_connect.memory_store.memory_router import MemoryRouter
from mcpomni_connect.events.event_router import EventRouter
from mcpomni_connect.agents.tools.local_tools_registry import ToolRegistry
from mcpomni_connect.utils import logger


async def create_simple_tool_registry() -> ToolRegistry:
    """Create a simple tool registry for testing."""
    tool_registry = ToolRegistry()

    @tool_registry.register_tool("simple_test")
    def simple_test() -> str:
        """Simple test tool that always works."""
        return "Test tool executed successfully!"

    logger.info("Created simple ToolRegistry")
    return tool_registry


async def test_background_agent():
    """Test background agent with fixed session ID handling."""

    logger.info("🧪 Testing Background Agent Session ID Fix")
    logger.info("=" * 50)

    try:
        # 1. Initialize components
        memory_store = MemoryRouter(memory_store_type="in_memory")
        event_router = EventRouter(event_store_type="in_memory")
        tool_registry = await create_simple_tool_registry()

        # 2. Create manager
        manager = BackgroundAgentManager(
            memory_store=memory_store, event_router=event_router
        )

        # 3. Create a simple agent
        agent_config = {
            "agent_id": "test_agent",
            "system_instruction": "You are a test agent. Use the simple_test tool when asked.",
            "model_config": {
                "model": "gpt-4.1",
                "temperature": 0.6,
                "provider": "openai",
                "top_p": 0.9,
                "max_context_length": 50000,
            },
            "mcp_tools": [],
            "local_tools": tool_registry,
            "agent_config": {
                "max_steps": 5,
                "tool_call_timeout": 30,
                "request_limit": 1000,
                "memory_config": {"mode": "token_budget", "value": 5000},
            },
            "interval": 10,  # Run every 10 seconds for quick testing
            "max_retries": 1,
            "retry_delay": 5,
            "debug": True,
            "task_config": {
                "query": "Use the simple_test tool and report the result.",
                "description": "Simple test task",
            },
        }

        # 4. Create agent
        logger.info("📦 Creating test agent...")
        result = manager.create_agent(agent_config)

        agent_id = result["agent_id"]
        session_id = result["session_id"]

        logger.info(f"✅ Created agent: {agent_id}")
        logger.info(f"   Session ID: {session_id}")
        logger.info(f"   Task Query: {result['task_query']}")

        # 5. Start manager
        logger.info("🚀 Starting manager...")
        manager.start()

        # 6. Set up event monitoring
        logger.info("📡 Setting up event monitoring...")

        async def monitor_events():
            try:
                agent = manager.get_agent(agent_id)
                if agent:
                    logger.info(
                        f"🎯 Monitoring events for {agent_id} (Session: {session_id})"
                    )
                    event_count = 0
                    async for event in agent.stream_events(session_id):
                        event_count += 1
                        logger.info(
                            f"📡 Event {event_count}: {event.type} - {event.payload}"
                        )

                        # Stop after 5 events to avoid infinite loop
                        if event_count >= 5:
                            logger.info("✅ Received 5 events, stopping monitoring")
                            break

            except Exception as e:
                logger.error(f"❌ Event monitoring error: {e}")

        # Start monitoring task
        monitoring_task = asyncio.create_task(monitor_events())

        # 7. Wait for events
        logger.info("⏰ Waiting for events (30 seconds)...")
        await asyncio.sleep(30)

        # 8. Cancel monitoring
        monitoring_task.cancel()
        try:
            await monitoring_task
        except asyncio.CancelledError:
            pass

        # 9. Show final status
        logger.info("\n📊 Final Status:")
        status = manager.get_agent_status(agent_id)
        if status:
            logger.info(f"   Running: {status['is_running']}")
            logger.info(f"   Run Count: {status['run_count']}")
            logger.info(f"   Error Count: {status['error_count']}")
            logger.info(f"   Last Run: {status['last_run']}")

        # 10. Shutdown
        logger.info("🛑 Shutting down...")
        manager.shutdown()

        logger.info("✅ Test completed successfully!")

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_background_agent())
