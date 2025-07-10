#!/usr/bin/env python3
"""
Test local tools integration
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from mcpomni_connect.agents.tools.local_tools_integration import register_local_tool, get_local_tools, execute_local_tool


# Register a test tool
@register_local_tool(
    name="test_tool",
    description="A simple test tool"
)
def test_tool(message: str, count: int = 1) -> str:
    """A simple test tool
    
    Args:
        message: Message to repeat
        count: Number of times to repeat (default: 1)
    
    Returns:
        Repeated message
    """
    return message * count


async def test_local_tools():
    """Test the local tools system"""
    print("🧪 Testing Local Tools Integration")
    print("=" * 40)
    
    # Show registered tools
    tools = get_local_tools()
    print(f"📋 Found {len(tools)} registered tools:")
    for tool in tools:
        print(f"  🔧 {tool['name']}: {tool['description']}")
    
    # Test tool execution
    print("\n⚡ Testing tool execution:")
    
    # Test with required parameters
    result1 = await execute_local_tool("test_tool", {"message": "Hello! "})
    print(f"test_tool('Hello! ') = {result1}")
    
    # Test with optional parameters
    result2 = await execute_local_tool("test_tool", {"message": "Hi! ", "count": 3})
    print(f"test_tool('Hi! ', 3) = {result2}")
    
    # Test with existing tools
    result3 = await execute_local_tool("add", {"a": 10, "b": 20})
    print(f"add(10, 20) = {result3}")
    
    result4 = await execute_local_tool("greet", {"name": "World"})
    print(f"greet('World') = {result4}")
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    asyncio.run(test_local_tools()) 