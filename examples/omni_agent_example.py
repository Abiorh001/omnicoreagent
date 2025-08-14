#!/usr/bin/env python3
"""
Comprehensive OmniAgent Example - Demonstrates all features and capabilities.
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

from mcpomni_connect.omni_agent import OmniAgent
from mcpomni_connect.memory_store.memory_router import MemoryRouter
from mcpomni_connect.events.event_router import EventRouter
from mcpomni_connect.agents.tools.local_tools_registry import ToolRegistry
from mcpomni_connect.utils import logger


async def create_comprehensive_tool_registry() -> ToolRegistry:
    """Create a comprehensive tool registry with various tool types."""
    tool_registry = ToolRegistry()

    # Mathematical tools
    @tool_registry.register_tool("calculate_area")
    def calculate_area(length: float, width: float) -> str:
        """Calculate the area of a rectangle."""
        area = length * width
        return f"Area of rectangle ({length} x {width}): {area} square units"

    @tool_registry.register_tool("calculate_perimeter")
    def calculate_perimeter(length: float, width: float) -> str:
        """Calculate the perimeter of a rectangle."""
        perimeter = 2 * (length + width)
        return f"Perimeter of rectangle ({length} x {width}): {perimeter} units"

    # Text processing tools
    @tool_registry.register_tool("format_text")
    def format_text(text: str, style: str = "normal") -> str:
        """Format text in different styles."""
        if style == "uppercase":
            return text.upper()
        elif style == "lowercase":
            return text.lower()
        elif style == "title":
            return text.title()
        elif style == "reverse":
            return text[::-1]
        else:
            return text

    @tool_registry.register_tool("word_count")
    def word_count(text: str) -> str:
        """Count words in text."""
        words = text.split()
        return f"Word count: {len(words)} words"

    # System information tools
    @tool_registry.register_tool("system_info")
    def get_system_info() -> str:
        """Get basic system information."""
        import platform
        import time

        info = f"""System Information:
• OS: {platform.system()} {platform.release()}
• Architecture: {platform.machine()}
• Python Version: {platform.python_version()}
• Current Time: {time.strftime("%Y-%m-%d %H:%M:%S")}"""
        return info

    # Data analysis tools
    @tool_registry.register_tool("analyze_numbers")
    def analyze_numbers(numbers: str) -> str:
        """Analyze a list of numbers."""
        try:
            num_list = [float(x.strip()) for x in numbers.split(",")]
            if not num_list:
                return "No numbers provided"

            total = sum(num_list)
            average = total / len(num_list)
            minimum = min(num_list)
            maximum = max(num_list)

            return f"""Number Analysis:
• Count: {len(num_list)} numbers
• Sum: {total}
• Average: {average:.2f}
• Min: {minimum}
• Max: {maximum}"""
        except Exception as e:
            return f"Error analyzing numbers: {str(e)}"

    # File system tools
    @tool_registry.register_tool("list_directory")
    def list_directory(path: str = ".") -> str:
        """List contents of a directory."""
        import os

        try:
            if not os.path.exists(path):
                return f"Directory {path} does not exist"

            items = os.listdir(path)
            files = [item for item in items if os.path.isfile(os.path.join(path, item))]
            dirs = [item for item in items if os.path.isdir(os.path.join(path, item))]

            return f"""Directory: {path}
• Files: {len(files)} ({files[:5]}{"..." if len(files) > 5 else ""})
• Directories: {len(dirs)} ({dirs[:5]}{"..." if len(dirs) > 5 else ""})"""
        except Exception as e:
            return f"Error listing directory: {str(e)}"

    logger.info("Created comprehensive ToolRegistry with 7 tools")
    return tool_registry


async def demonstrate_memory_management(agent: OmniAgent):
    """Demonstrate memory management capabilities."""

    logger.info("\n" + "=" * 60)
    logger.info("DEMONSTRATING MEMORY MANAGEMENT")
    logger.info("=" * 60)

    session_id = "memory_demo_session"

    # 1. Store messages and demonstrate memory
    logger.info("\n🧠 Testing Memory Storage:")

    # First conversation
    result1 = await agent.run(
        "Hello! My name is Alice and I'm a software engineer.", session_id
    )
    logger.info(f"✅ Stored message 1: {result1['response'][:100]}...")

    # Second conversation with memory recall
    result2 = await agent.run("What's my name and what do I do?", session_id)
    logger.info(f"✅ Memory recall: {result2['response'][:100]}...")

    # 2. Get session history
    logger.info("\n📜 Session History:")
    history = await agent.get_session_history(session_id)
    logger.info(f"   Total messages in session: {len(history)}")
    for i, msg in enumerate(history[-3:], 1):  # Show last 3 messages
        logger.info(
            f"   {i}. {msg.get('role', 'unknown')}: {msg.get('content', '')[:50]}..."
        )

    # 3. Test memory with different session
    logger.info("\n🔄 Testing Memory Isolation:")
    new_session_id = "different_session"
    result3 = await agent.run("What's my name?", new_session_id)
    logger.info(f"   New session response: {result3['response'][:100]}...")

    # 4. Clear memory
    logger.info("\n🧹 Clearing Memory:")
    await agent.clear_session_history(session_id)
    logger.info("   ✅ Memory cleared for session")

    # Verify memory is cleared
    history_after_clear = await agent.get_session_history(session_id)
    logger.info(f"   Messages after clear: {len(history_after_clear)}")


async def demonstrate_event_streaming(agent: OmniAgent):
    """Demonstrate event streaming capabilities."""

    logger.info("\n" + "=" * 60)
    logger.info("DEMONSTRATING EVENT STREAMING")
    logger.info("=" * 60)

    session_id = "event_demo_session"

    # 1. Show event store information
    logger.info("\n📡 Event Store Information:")
    logger.info(f"   Event store type: {agent.get_event_store_type()}")
    logger.info(f"   Event store available: {agent.is_event_store_available()}")
    logger.info(f"   Event store info: {agent.get_event_store_info()}")

    # 2. Demonstrate event store switching
    logger.info("\n🔄 Event Store Switching:")
    logger.info("   Switching to Redis Streams...")
    agent.switch_event_store("redis_stream")
    logger.info(f"   New event store type: {agent.get_event_store_type()}")

    # Switch back to in-memory
    logger.info("   Switching back to In-Memory...")
    agent.switch_event_store("in_memory")
    logger.info(f"   Current event store type: {agent.get_event_store_type()}")

    # 3. Stream events in real-time
    logger.info("\n🎯 Real-time Event Streaming:")

    async def stream_events():
        event_count = 0
        async for event in agent.stream_events(session_id):
            event_count += 1
            logger.info(
                f"   📡 Event {event_count}: {event.type} - {str(event.payload)[:100]}..."
            )

            # Stop after 5 events to avoid infinite loop
            if event_count >= 5:
                logger.info("   ✅ Received 5 events, stopping stream")
                break

    # Start event streaming
    streaming_task = asyncio.create_task(stream_events())

    # Run agent to generate events
    await agent.run(
        "Calculate the area of a rectangle with length 10 and width 5", session_id
    )

    # Wait for events
    await asyncio.sleep(2)

    # Cancel streaming
    streaming_task.cancel()
    try:
        await streaming_task
    except asyncio.CancelledError:
        pass

    # 4. Get stored events
    logger.info("\n📋 Stored Events:")
    events = await agent.get_events(session_id)
    logger.info(f"   Total events stored: {len(events)}")
    for i, event in enumerate(events[:3], 1):
        logger.info(f"   {i}. {event.type}: {str(event.payload)[:80]}...")


async def demonstrate_tool_orchestration(agent: OmniAgent):
    """Demonstrate tool orchestration capabilities."""

    logger.info("\n" + "=" * 60)
    logger.info("DEMONSTRATING TOOL ORCHESTRATION")
    logger.info("=" * 60)

    session_id = "tool_demo_session"

    # 1. Test mathematical tools
    logger.info("\n🔢 Mathematical Tools:")
    result1 = await agent.run(
        "Calculate the area and perimeter of a rectangle with length 15 and width 8",
        session_id,
    )
    logger.info(f"   ✅ Math tools: {result1['response'][:100]}...")

    # 2. Test text processing tools
    logger.info("\n📝 Text Processing Tools:")
    result2 = await agent.run(
        "Format the text 'hello world' in uppercase and count the words", session_id
    )
    logger.info(f"   ✅ Text tools: {result2['response'][:100]}...")

    # 3. Test system information tools
    logger.info("\n💻 System Information Tools:")
    result3 = await agent.run("Get system information", session_id)
    logger.info(f"   ✅ System tools: {result3['response'][:100]}...")

    # 4. Test data analysis tools
    logger.info("\n📊 Data Analysis Tools:")
    result4 = await agent.run("Analyze the numbers: 10, 25, 15, 30, 20", session_id)
    logger.info(f"   ✅ Data analysis: {result4['response'][:100]}...")

    # 5. Test file system tools
    logger.info("\n📁 File System Tools:")
    result5 = await agent.run("List the contents of the current directory", session_id)
    logger.info(f"   ✅ File system: {result5['response'][:100]}...")

    # 6. Test complex tool combinations
    logger.info("\n🔄 Complex Tool Combinations:")
    result6 = await agent.run(
        "Calculate the area of a rectangle with length 12 and width 6, then format the result in uppercase",
        session_id,
    )
    logger.info(f"   ✅ Complex tools: {result6['response'][:100]}...")


async def demonstrate_session_management(agent: OmniAgent):
    """Demonstrate session management capabilities."""

    logger.info("\n" + "=" * 60)
    logger.info("DEMONSTRATING SESSION MANAGEMENT")
    logger.info("=" * 60)

    # 1. Test automatic session ID generation
    logger.info("\n🆔 Automatic Session ID Generation:")
    result1 = await agent.run(
        "Hello! I'm Bob, a data scientist.", None
    )  # No session_id provided
    session_id1 = result1["session_id"]
    logger.info(f"   ✅ Generated session ID: {session_id1}")
    logger.info(f"   Response: {result1['response'][:100]}...")

    # 2. Test session continuity
    logger.info("\n🔄 Session Continuity:")
    result2 = await agent.run("What's my name and profession?", session_id1)
    logger.info(f"   ✅ Session continuity: {result2['response'][:100]}...")

    # 3. Test multiple sessions
    logger.info("\n📋 Multiple Sessions:")
    session_id2 = "custom_session_123"
    result3 = await agent.run("Hello! I'm Carol, a teacher.", session_id2)
    logger.info(f"   ✅ Custom session ID: {session_id2}")
    logger.info(f"   Response: {result3['response'][:100]}...")

    # 4. Test session isolation
    logger.info("\n🔒 Session Isolation:")
    result4 = await agent.run("What's my name?", session_id2)
    logger.info(f"   ✅ Session isolation: {result4['response'][:100]}...")

    # 5. Test session history for different sessions
    logger.info("\n📜 Session History Comparison:")
    history1 = await agent.get_session_history(session_id1)
    history2 = await agent.get_session_history(session_id2)
    logger.info(f"   Session {session_id1}: {len(history1)} messages")
    logger.info(f"   Session {session_id2}: {len(history2)} messages")


async def demonstrate_advanced_features(agent: OmniAgent):
    """Demonstrate advanced OmniAgent features."""

    logger.info("\n" + "=" * 60)
    logger.info("DEMONSTRATING ADVANCED FEATURES")
    logger.info("=" * 60)

    session_id = "advanced_demo_session"

    # 1. Test XML-based reasoning
    logger.info("\n🤖 XML-Based Reasoning:")
    result1 = await agent.run(
        "I need to calculate the area of a rectangle with length 20 and width 10, then format the result in title case. Please think through this step by step.",
        session_id,
    )
    logger.info(f"   ✅ XML reasoning: {result1['response'][:150]}...")

    # 2. Test memory-aware responses
    logger.info("\n🧠 Memory-Aware Responses:")
    await agent.run(
        "My favorite color is blue and I love programming in Python.", session_id
    )
    result2 = await agent.run("What are my preferences?", session_id)
    logger.info(f"   ✅ Memory-aware: {result2['response'][:100]}...")

    # 3. Test tool error handling
    logger.info("\n⚠️ Tool Error Handling:")
    result3 = await agent.run(
        "Calculate the area of a rectangle with invalid dimensions", session_id
    )
    logger.info(f"   ✅ Error handling: {result3['response'][:100]}...")

    # 4. Test complex multi-step reasoning
    logger.info("\n🔄 Complex Multi-Step Reasoning:")
    result4 = await agent.run(
        "I have a list of numbers: 5, 15, 25, 35. Please analyze them, calculate the area of a rectangle with the average as length and 5 as width, then format the result in uppercase.",
        session_id,
    )
    logger.info(f"   ✅ Multi-step reasoning: {result4['response'][:150]}...")


async def demonstrate_configuration_management(agent: OmniAgent):
    """Demonstrate configuration management capabilities."""

    logger.info("\n" + "=" * 60)
    logger.info("DEMONSTRATING CONFIGURATION MANAGEMENT")
    logger.info("=" * 60)

    # 1. Show current configuration
    logger.info("\n⚙️ Current Configuration:")
    logger.info(f"   Agent name: {agent.name}")
    logger.info(f"   System instruction: {agent.system_instruction[:100]}...")
    logger.info(f"   Debug mode: {agent.debug}")
    logger.info(f"   Memory store type: {agent.memory_store.get_memory_store_info()}")
    logger.info(f"   Event store type: {agent.get_event_store_type()}")

    # 2. Show hidden config structure
    logger.info("\n📁 Hidden Configuration Structure:")
    hidden_dir = Path(".mcp_config")
    if hidden_dir.exists():
        logger.info(f"   ✅ Hidden directory exists: {hidden_dir}")
        for file in hidden_dir.glob("*"):
            logger.info(f"   📄 {file.name}")
    else:
        logger.info("   ❌ Hidden directory not found")

    # 3. Test configuration switching
    logger.info("\n🔄 Configuration Switching:")
    logger.info("   Switching event store to Redis Streams...")
    agent.switch_event_store("redis_stream")
    logger.info(f"   New event store: {agent.get_event_store_type()}")

    logger.info("   Switching back to In-Memory...")
    agent.switch_event_store("in_memory")
    logger.info(f"   Current event store: {agent.get_event_store_type()}")


async def main():
    """Main function demonstrating all OmniAgent capabilities."""

    logger.info("🚀 Starting Comprehensive OmniAgent Example")
    logger.info("=" * 60)

    # Load environment variables
    load_dotenv()

    # Check for required environment variables
    if not os.getenv("LLM_API_KEY"):
        logger.error("❌ LLM_API_KEY environment variable not found!")
        logger.error("Please set it in your .env file:")
        logger.error("LLM_API_KEY=your_api_key_here")
        return

    try:
        # 1. Initialize components
        logger.info("\n📦 Initializing Components...")

        # Create memory and event routers
        memory_store = MemoryRouter(memory_store_type="in_memory")
        event_router = EventRouter(event_store_type="in_memory")

        # Create comprehensive tool registry
        tool_registry = await create_comprehensive_tool_registry()

        # Create OmniAgent with all features
        agent = OmniAgent(
            name="comprehensive_demo_agent",
            system_instruction="You are a comprehensive AI assistant with access to mathematical, text processing, system information, data analysis, and file system tools. You can perform complex calculations, format text, analyze data, and provide system information. Always use the appropriate tools for the task and provide clear, helpful responses.",
            model_config={
                "provider": "openai",  # Change to your preferred provider
                "model": "gpt-4.1",  # Use valid model name
                "temperature": 0.7,
                "max_context_length": 3000,
            },
            mcp_tools=[
                {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        str(Path.home()),  # Use user's home directory
                        str(Path.cwd()),  # Use current working directory
                    ],
                }
            ],
            local_tools=tool_registry,
            agent_config={
                "max_steps": 15,
                "tool_call_timeout": 60,
                "request_limit": 1000,
                "memory_config": {"mode": "token_budget", "value": 10000},
            },
            memory_store=memory_store,
            event_router=event_router,
            debug=True,
        )

        logger.info("✅ OmniAgent created with all features")

        # 2. Demonstrate all capabilities
        await demonstrate_memory_management(agent)
        await demonstrate_event_streaming(agent)
        await demonstrate_tool_orchestration(agent)
        await demonstrate_session_management(agent)
        await demonstrate_advanced_features(agent)
        await demonstrate_configuration_management(agent)

        # 3. Final demonstration
        logger.info("\n" + "=" * 60)
        logger.info("FINAL COMPREHENSIVE DEMONSTRATION")
        logger.info("=" * 60)

        final_session = "final_demo_session"

        # Complex multi-step task
        logger.info("\n🎯 Complex Multi-Step Task:")
        final_result = await agent.run(
            "I want to: 1) Calculate the area of a rectangle with length 25 and width 12, "
            "2) Format the result in uppercase, 3) Count the words in the formatted result, "
            "4) Get system information, and 5) List the current directory. "
            "Please perform all these tasks and provide a comprehensive summary.",
            final_session,
        )

        logger.info(
            f"✅ Final comprehensive result: {final_result['response'][:200]}..."
        )

        # 4. Show final statistics
        logger.info("\n📊 Final Statistics:")
        final_history = await agent.get_session_history(final_session)
        final_events = await agent.get_events(final_session)

        logger.info("   Total sessions created: 6")
        logger.info(f"   Total messages in final session: {len(final_history)}")
        logger.info(f"   Total events in final session: {len(final_events)}")
        logger.info("   Tools available: 7")
        logger.info(f"   Memory store: {memory_store.get_memory_store_info()}")
        logger.info(f"   Event store: {agent.get_event_store_info()}")

        # 5. Cleanup
        logger.info("\n🧹 Cleaning up...")
        try:
            await agent.cleanup()
            logger.info("✅ Agent cleanup completed")
        except Exception as e:
            logger.warning(f"⚠️ Cleanup warning: {e}")

        logger.info("✅ Comprehensive OmniAgent Example completed successfully!")
        logger.info(
            "📋 Summary: Demonstrated memory management, event streaming, tool orchestration,"
        )
        logger.info(
            "           session management, advanced features, and configuration management."
        )

    except Exception as e:
        logger.error(f"❌ Error in main: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
