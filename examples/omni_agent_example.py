#!/usr/bin/env python3
"""
Real-world example of how OmniAgent works with hidden config files and session management
Shows both dataclass and dictionary approaches for configuration.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from mcpomni_connect.omni_agent import OmniAgent
from mcpomni_connect.omni_agent.config import (
    ModelConfig,
    MCPToolConfig,
    TransportType,
    AgentConfig,
)
from mcpomni_connect.memory_store.memory_router import MemoryRouter

from mcpomni_connect.agents.tools.local_tools_registry import ToolRegistry


# 1. Create local tools registry
local_tools = ToolRegistry()


# 2. Define and register tools using decorators
@local_tools.register_tool(
    name="calculate_area",
    description="Calculate the area of a rectangle",
    inputSchema={
        "type": "object",
        "properties": {"length": {"type": "number"}, "width": {"type": "number"}},
        "required": ["length", "width"],
        "additionalProperties": False,
    },
)
def calculate_area(length: float, width: float) -> float:
    """Calculate area of a rectangle"""
    return length * width


@local_tools.register_tool(
    name="get_weather_info",
    description="Get weather information for a city",
    inputSchema={
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"],
        "additionalProperties": False,
    },
)
def get_weather_info(city: str) -> str:
    """Get weather info (simulated)"""
    return f"Weather in {city}: Sunny, 50°C"


@local_tools.register_tool(
    name="format_text",
    description="Format text in different styles",
    inputSchema={
        "type": "object",
        "properties": {
            "text": {"type": "string"},
            "style": {"type": "string", "default": "normal"},
        },
        "required": ["text"],
        "additionalProperties": False,
    },
)
def format_text(text: str, style: str = "normal") -> str:
    """Format text in different styles"""
    if style == "uppercase":
        return text.upper()
    elif style == "lowercase":
        return text.lower()
    elif style == "title":
        return text.title()
    else:
        return text


async def consume_events(agent, session_id):
    async for event in agent.stream_events(session_id):
        print(f"Event: {event.type} - {event.payload}")


async def example_session_management():
    """Example: Session management with chat IDs"""
    print("=" * 60)
    print("EXAMPLE: Session Management with Chat IDs")
    print("=" * 60)

    # Create agent with custom session store
    custom_memory = MemoryRouter(memory_store_type="redis")

    agent = OmniAgent(
        name="session_agent",
        system_instruction="You are a helpful assistant that can answer questions and help with tasks.",
        agent_config={
            "max_steps": 20,
            "tool_call_timeout": 60,
            "request_limit": 1000,
            "memory_config": {"mode": "token_budget", "value": 10000},
        },
        model_config={
            "provider": "openai",
            "model": "gpt-4.1",
            "max_context_length": 50000,
        },
        mcp_tools=[
            # {
            #     "name": "filesystem",
            #     "transport_type": "stdio",
            #     "command": "npx",
            #     "args": [
            #         "-y",
            #         "@modelcontextprotocol/server-filesystem",
            #         "/home/abiorh/Desktop",
            #         "/home/abiorh/ai/",
            #     ],
            # }
        ],
        local_tools=local_tools,
        memory_store=custom_memory,
    )

    print("✅ OmniAgent created with custom session store!")

    # Simulate a conversation with session ID management
    global_session_id = "1234567890"

    # # First message - will generate new chat ID
    # print("\n🤖 First message (new chat):")
    # result1 = await agent.run("Hello! My name is Alice.", global_session_id)
    # global_session_id = result1["session_id"]
    # print(f"Response: {result1['response']}")
    # print(f"Session ID: {global_session_id}")
    # # stream events create new task for this
    # asyncio.create_task(consume_events(agent, global_session_id))
    # # Second message - using same chat ID for continuity
    # print("\n🤖 Second message (same chat):")
    result2 = await agent.run(
        "what are you and what can you help me with",
        global_session_id,
    )
    print(f"Response: {result2['response']}")
    print(f"Session ID: {result2['session_id']}")

    # stream events
    # asyncio.create_task(consume_events(agent, global_session_id))
    # get_history = await agent.get_session_history(global_session_id)
    # print(f"History: {get_history}")

    # # Get chat history
    # print("\n📜 Chat History:")
    # history = await agent.get_chat_history(chat_id)
    # for i, msg in enumerate(history):
    #     print(f"  {i+1}. {msg['role']}: {msg['content']}")

    # New conversation with different chat ID
    # print("\n🤖 New conversation (different chat):")
    # result3 = await agent.run("list all the files in my current directory", global_session_id)
    # global_session_id = result3["session_id"]
    # print(f"Response: {result3['response']}")
    # print(f"New Session ID: {global_session_id}")
    # # stream events
    # asyncio.create_task(consume_events(agent, global_session_id))
    # # Clear specific chat history
    # print(f"\n🧹 Clearing chat history for: {chat_id}")
    # await agent.clear_chat_history(chat_id)

    # Verify history is cleared
    # history_after_clear = await agent.get_chat_history(chat_id)
    # print(f"History after clear: {len(history_after_clear)} messages")

    # get_history = await agent.get_session_history(global_session_id)
    # print(f"History: {get_history}")

    # Clean up
    await agent.cleanup()

    return agent


async def example_dataclass_approach():
    """Example: Using dataclasses for type safety and validation"""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Dataclass Approach (Recommended)")
    print("=" * 60)

    # Using dataclasses for better type safety and IDE support
    agent = OmniAgent(
        name="core",
        model_config=ModelConfig(
            provider="openai",
            model="gpt-4o",
            api_key="sk-...",
            temperature=0.7,
            max_tokens=4000,
            max_context_length=100000,
        ),
        mcp_tools=[
            MCPToolConfig(
                name="search",
                transport_type=TransportType.SSE,
                url="http://localhost:3000/mcp",
                headers={"Authorization": "Bearer token"},
                timeout=60,
            ),
            MCPToolConfig(
                name="database",
                transport_type=TransportType.STDIO,
                command="uvx",
                args=["mcp-server-database"],
            ),
        ],
        agent_config=AgentConfig(
            max_steps=20, tool_call_timeout=60, request_limit=1000
        ),
    )

    print("✅ OmniAgent created successfully with dataclasses!")
    print("🔒 Type safety and validation enabled")
    print("📁 Config files are hidden from user view")
    print(
        f"💾 Default session store with max context: {agent.session_store.max_context_tokens}"
    )

    # Show what files exist
    print("\n📂 Files in project root:")
    for file in Path(".").glob("*"):
        if file.is_file() and not file.name.startswith("."):
            print(f"   📄 {file.name}")
        elif file.is_dir() and file.name.startswith("."):
            print(f"   📁 {file.name}/ (hidden)")

    # Check if servers_config.json exists in hidden location
    hidden_config = Path(".mcp_config/servers_config.json")
    if hidden_config.exists():
        print("✅ servers_config.json is available in hidden location")

    # Clean up
    await agent.cleanup()

    return agent


async def example_dictionary_approach():
    """Example: Using dictionaries for simplicity"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Dictionary Approach (Simple)")
    print("=" * 60)

    # Using dictionaries for simplicity
    agent = OmniAgent(
        name="simple_agent",
        model_config={
            "provider": "anthropic",
            "model": "claude-3-sonnet",
            "api_key": "sk-ant-...",
            "temperature": 0.3,
            "max_context_length": 80000,
        },
        mcp_tools=[
            {
                "name": "analytics",
                "transport_type": "streamable_http",
                "url": "http://localhost:3001/mcp",
                "headers": {"X-API-Key": "analytics-key"},
                "timeout": 90,
            }
        ],
        agent_config={"max_steps": 15, "tool_call_timeout": 30},
    )

    print("✅ OmniAgent created successfully with dictionaries!")
    print("📝 Simple and flexible configuration")
    print("🔒 Config files are still hidden from user view")
    print(
        f"💾 Default session store with max context: {agent.session_store.max_context_tokens}"
    )

    # Clean up
    await agent.cleanup()

    return agent


def show_hidden_config():
    """Show the hidden config structure"""
    print("\n" + "=" * 60)
    print("HIDDEN CONFIG STRUCTURE")
    print("=" * 60)

    hidden_dir = Path(".mcp_config")
    if hidden_dir.exists():
        print(f"📁 Hidden directory: {hidden_dir}")
        for file in hidden_dir.glob("*"):
            print(f"   📄 {file.name}")

        # Show config content
        config_file = hidden_dir / "servers_config.json"
        if config_file.exists():
            print("\n📋 Config content preview:")
            with open(config_file, "r") as f:
                import json

                config = json.load(f)
                print(f"   LLM: {config['LLM']['provider']} ({config['LLM']['model']})")
                print(f"   MCP Servers: {list(config['mcpServers'].keys())}")
                print(f"   Agent Config: {config['AgentConfig']}")
    else:
        print("❌ Hidden config directory not found")


async def main():
    """Run all examples"""
    print("🚀 OmniAgent with Hidden Config Files and Session Management")
    print("This shows both dataclass and dictionary approaches\n")

    # Set up environment
    os.environ["LLM_API_KEY"] = "sk-proj"  # Mock API key

    # Run examples
    await example_session_management()
    # await example_dataclass_approach()
    # await example_dictionary_approach()

    # Show hidden config structure
    show_hidden_config()

    # print("\n" + "=" * 60)
    # print("SUMMARY")
    # print("=" * 60)
    # print("✅ OmniAgent works with both dataclass and dictionary approaches")
    # print("✅ Config files are saved to .mcp_config/ (hidden directory)")
    # print("✅ MCPClient can find config in hidden location")
    # print("✅ Session management with chat IDs for conversation continuity")
    # print("✅ Automatic chat ID generation when not provided")
    # print("✅ Chat history retrieval and management")
    # print("✅ Users don't need to know about config file management")
    # print("✅ Cleanup removes all temporary files")
    # print("\nRecommendations:")
    # print("• Use dataclasses for production code (type safety)")
    # print("• Use dictionaries for quick prototyping")
    # print("• Provide custom session store for advanced memory management")
    # print("• Use chat IDs for conversation continuity")
    # print("• Both approaches hide implementation details")
    # print("• Both are compatible with existing MCPClient")


if __name__ == "__main__":
    asyncio.run(main())
