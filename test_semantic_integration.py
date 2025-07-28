#!/usr/bin/env python3
"""
Test semantic tool search integration with OmniAgent-like flow
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from mcpomni_connect.agents.base import BaseReactAgent
from mcpomni_connect.agents.tools.local_tools_registry import ToolRegistry

# Mock LLM connection for testing
class MockLLMConnection:
    async def llm_call(self, messages):
        # Mock response that would trigger tool search
        return type('Response', (), {
            'choices': [type('Choice', (), {
                'message': type('Message', (), {
                    'content': 'I can help you with various tasks. Let me show you the available tools.'
                })()
            })()]
        })()

# Mock message history
async def mock_message_history(agent_name, session_id):
    return []

# Mock add message to history
async def mock_add_message_to_history(role, content, session_id=None, metadata=None):
    pass

async def test_semantic_integration():
    """Test semantic tool search with OmniAgent-like flow"""
    
    # Create local tools registry (like in the example)
    local_tools = ToolRegistry()
    
    # Register tools (like in the example)
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
        if style == "uppercase":
            return text.upper()
        elif style == "lowercase":
            return text.lower()
        elif style == "title":
            return text.title()
        else:
            return text

    # Create agent (like OmniAgent would)
    agent = BaseReactAgent(
        agent_name="test_agent",
        max_steps=10,
        tool_call_timeout=30,
        request_limit=100,
        total_tokens_limit=10000
    )

    # Test different queries
    test_queries = [
        "what are you and what can you help me with",
        "I need to calculate something",
        "I want to check the weather",
        "I need to format some text",
        "Show me all available tools"
    ]

    print("Testing semantic tool search integration...")
    print("=" * 60)

    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 40)
        
        # Get tools using semantic search (like OmniAgent would)
        tools_section = await agent.get_tools_registry(
            local_tools=local_tools,
            query=query,
            use_semantic_search=True,
            top_k=5
        )
        
        # Count tools found
        tool_count = len([line for line in tools_section.split('\n') if line.startswith('### `')])
        print(f"Relevant tools found: {tool_count}")
        
        # Show first few lines of tools section
        lines = tools_section.split('\n')
        tool_lines = [line for line in lines if line.startswith('### `')]
        for i, tool_line in enumerate(tool_lines[:3], 1):
            tool_name = tool_line.split('`')[1] if '`' in tool_line else 'Unknown'
            print(f"  {i}. {tool_name}")
        
        if len(tool_lines) > 3:
            print(f"  ... and {len(tool_lines) - 3} more tools")

    print("\n" + "=" * 60)
    print("Integration test completed!")

if __name__ == "__main__":
    asyncio.run(test_semantic_integration()) 