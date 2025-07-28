#!/usr/bin/env python3
"""
Simple test to verify event streaming works with background agents.
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
from mcpomni_connect.events.base import Event, EventType
from mcpomni_connect.utils import logger


async def test_event_streaming():
    """Test event streaming with background agents."""

    logger.info("🧪 Testing Event Streaming")
    logger.info("=" * 40)

    try:
        # 1. Initialize components
        memory_store = MemoryRouter(memory_store_type="in_memory")
        event_router = EventRouter(event_store_type="in_memory")

        # 2. Create manager
        manager = BackgroundAgentManager(
            memory_store=memory_store, event_router=event_router
        )

        # 3. Test direct event emission
        logger.info("📡 Testing direct event emission...")
        test_session_id = "test_session_123"

        # Emit a test event
        test_event = Event(
            type=EventType.AGENT_MESSAGE,
            payload={"message": "Test event from direct emission"},
            agent_name="test_agent",
        )

        await event_router.append(session_id=test_session_id, event=test_event)
        logger.info("✅ Emitted test event")

        # 4. Test event streaming
        logger.info("📡 Testing event streaming...")

        async def stream_test_events():
            event_count = 0
            async for event in event_router.stream(session_id=test_session_id):
                event_count += 1
                logger.info(
                    f"📡 Received event {event_count}: {event.type} - {event.payload}"
                )

                if event_count >= 1:
                    logger.info("✅ Successfully received test event")
                    break

        # Start streaming task
        streaming_task = asyncio.create_task(stream_test_events())

        # Wait for event
        await asyncio.sleep(2)

        # Cancel streaming
        streaming_task.cancel()
        try:
            await streaming_task
        except asyncio.CancelledError:
            pass

        # 5. Test background agent event streaming
        logger.info("\n🤖 Testing background agent event streaming...")

        # Create simple tool registry
        tool_registry = ToolRegistry()

        @tool_registry.register_tool("test_tool")
        def test_tool() -> str:
            return "Test tool executed successfully!"

        # Create background agent
        agent_config = {
            "agent_id": "test_background_agent",
            "system_instruction": "You are a test agent. Use the test_tool when asked.",
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
                "max_steps": 3,
                "tool_call_timeout": 30,
                "request_limit": 1000,
                "memory_config": {"mode": "token_budget", "value": 5000},
            },
            "interval": 5,  # Run every 5 seconds
            "max_retries": 1,
            "retry_delay": 5,
            "debug": True,
            "task_config": {
                "query": "Use the test_tool and report the result.",
                "description": "Test task",
            },
        }

        # Create agent
        result = manager.create_agent(agent_config)
        agent_id = result["agent_id"]
        session_id = result["session_id"]

        logger.info(f"✅ Created agent: {agent_id}")
        logger.info(f"   Session ID: {session_id}")

        # Start manager
        manager.start()

        # Monitor events
        async def monitor_background_events():
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
                            f"📡 Background Event {event_count}: {event.type} - {event.payload}"
                        )

                        if event_count >= 3:
                            logger.info("✅ Received 3 background events")
                            break

            except Exception as e:
                logger.error(f"❌ Background event monitoring error: {e}")

        # Start monitoring
        monitoring_task = asyncio.create_task(monitor_background_events())

        # Wait for events
        logger.info("⏰ Waiting for background agent events (15 seconds)...")
        await asyncio.sleep(15)

        # Cancel monitoring
        monitoring_task.cancel()
        try:
            await monitoring_task
        except asyncio.CancelledError:
            pass

        # Show status
        status = manager.get_agent_status(agent_id)
        if status:
            logger.info(f"\n📊 Agent Status:")
            logger.info(f"   Running: {status['is_running']}")
            logger.info(f"   Run Count: {status['run_count']}")
            logger.info(f"   Error Count: {status['error_count']}")

        # Shutdown
        manager.shutdown()

        logger.info("✅ Event streaming test completed successfully!")

    except Exception as e:
        logger.error(f"❌ Event streaming test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_event_streaming())
