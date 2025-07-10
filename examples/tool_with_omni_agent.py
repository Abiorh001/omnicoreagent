#!/usr/bin/env python3
"""
Tool Registry with OmniAgent - Real Usage

This shows how to:
1. Register tools
2. Use them with OmniAgent
3. Let the agent execute your tools
"""

import asyncio
from mcpomni_connect.agents.tools.local_tools_registry import ToolRegistry
from mcpomni_connect.agents.tools.local_tools_integration import LocalToolsIntegration
from mcpomni_connect.omni_agent.agent import OmniAgent

# 1. Create your tools
registry = ToolRegistry()

@registry.register(
    name="calculate_area",
    description="Calculate the area of a rectangle"
)
def calculate_area(length: float, width: float) -> float:
    """Calculate area of a rectangle"""
    return length * width

@registry.register(
    name="get_weather_info",
    description="Get weather information for a city"
)
def get_weather_info(city: str) -> str:
    """Get weather info (simulated)"""
    return f"Weather in {city}: Sunny, 25°C"

@registry.register(
    name="format_text",
    description="Format text in different styles"
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

# 2. Create local tools integration
local_tools = LocalToolsIntegration(registry)

# 3. Create OmniAgent with local tools
async def main():
    # Model configuration (you'll need a real API key)
    model_config = {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "api_key": "your-api-key-here"  # Replace with your key
    }
    
    # Agent configuration
    agent_config = {
        "agent_name": "ToolDemoAgent",
        "tool_call_timeout": 30,
        "max_steps": 10
    }
    
    # Create OmniAgent
    agent = OmniAgent(
        name="ToolDemoAgent",
        model_config=model_config,
        mcp_tools=[],  # No MCP tools, only local tools
        agent_config=agent_config
    )
    
    # Show available tools
    print("🔧 Available Tools:")
    tools = local_tools.get_available_tools()
    for tool in tools:
        print(f"  • {tool['name']}: {tool['description']}")
    
    print("\n💡 Try these queries with the agent:")
    print("  • 'Calculate the area of a rectangle with length 10 and width 5'")
    print("  • 'What's the weather like in London?'")
    print("  • 'Format the text HELLO WORLD in uppercase'")
    
    # Note: To actually run the agent, you need a valid API key
    print("\n⚠️  Note: Replace 'your-api-key-here' with a real API key to test the agent")

if __name__ == "__main__":
    asyncio.run(main()) 