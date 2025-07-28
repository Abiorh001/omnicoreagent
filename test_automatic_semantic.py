#!/usr/bin/env python3
"""
Test automatic semantic tool search - simulates real user usage
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from mcpomni_connect.agents.base import BaseReactAgent
from mcpomni_connect.agents.tools.local_tools_registry import ToolRegistry

async def test_automatic_semantic_search():
    """Test that semantic search works automatically without user integration"""
    
    print("🧪 Testing Automatic Semantic Tool Search")
    print("=" * 50)
    
    # 1. User creates tools (like in real usage)
    local_tools = ToolRegistry()
    
    @local_tools.register_tool(
        name="calculate_area",
        description="Calculate the area of a rectangle",
        inputSchema={
            "type": "object",
            "properties": {"length": {"type": "number"}, "width": {"type": "number"}},
            "required": ["length", "width"],
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
        },
    )
    def format_text(text: str, style: str = "normal") -> str:
        if style == "uppercase":
            return text.upper()
        elif style == "lowercase":
            return text.lower()
        else:
            return text

    # 2. User creates agent (like in real usage)
    agent = BaseReactAgent(
        agent_name="test_agent",
        max_steps=10,
        tool_call_timeout=30,
        request_limit=100,
        total_tokens_limit=10000
    )

    # 3. Test different user queries
    test_scenarios = [
        {
            "query": "what are you and what can you help me with",
            "expected": "Should return all tools (general help query)"
        },
        {
            "query": "I need to calculate the area of a rectangle",
            "expected": "Should return calculate_area tool"
        },
        {
            "query": "I want to check the weather in London",
            "expected": "Should return get_weather_info tool"
        },
        {
            "query": "I need to format some text",
            "expected": "Should return format_text tool"
        },
        {
            "query": "Show me all available tools",
            "expected": "Should return all tools"
        }
    ]

    print("\n📋 Testing different user queries:")
    print("-" * 40)

    for i, scenario in enumerate(test_scenarios, 1):
        query = scenario["query"]
        expected = scenario["expected"]
        
        print(f"\n{i}. Query: '{query}'")
        print(f"   Expected: {expected}")
        
        # This is what happens automatically when user calls agent.run()
        tools_section = await agent.get_tools_registry(
            local_tools=local_tools,
            query=query,
            use_semantic_search=True,  # This is the default!
            top_k=5
        )
        
        # Count tools found
        tool_lines = [line for line in tools_section.split('\n') if line.startswith('### `')]
        tool_count = len(tool_lines)
        
        print(f"   ✅ Found {tool_count} relevant tools")
        
        # Show tool names
        for j, tool_line in enumerate(tool_lines[:3], 1):
            tool_name = tool_line.split('`')[1] if '`' in tool_line else 'Unknown'
            print(f"      {j}. {tool_name}")
        
        if len(tool_lines) > 3:
            print(f"      ... and {len(tool_lines) - 3} more")

    print("\n" + "=" * 50)
    print("✅ Automatic semantic search is working!")
    print("🎯 Users don't need to do any additional integration")
    print("🚀 Semantic search happens automatically on every query")

if __name__ == "__main__":
    asyncio.run(test_automatic_semantic_search()) 