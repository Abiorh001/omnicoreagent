#!/usr/bin/env python3
"""
Test script to verify local tools integration with updated base agent
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from mcpomni_connect.agents.tools.local_tools_integration import register_local_tool, get_local_tools, execute_local_tool, local_tools
from mcpomni_connect.agents.tools.tools_handler import LocalToolHandler, LocalToolExecutor


# Register some test tools
@register_local_tool(
    name="add_numbers",
    description="Add two numbers together"
)
def add_numbers(a: int, b: int) -> int:
    """Add two numbers
    
    Args:
        a: First number
        b: Second number
    
    Returns:
        Sum of the two numbers
    """
    return a + b


@register_local_tool(
    name="greet",
    description="Greet someone by name"
)
def greet(name: str) -> str:
    """Greet someone by name
    
    Args:
        name: Name to greet
    
    Returns:
        Greeting message
    """
    return f"Hello, {name}!"


async def test_local_tool_handler():
    """Test the LocalToolHandler"""
    print("🧪 Testing LocalToolHandler")
    print("=" * 40)
    
    # Use the global local_tools instance
    handler = LocalToolHandler(local_tools)
    
    # Test validation
    tool_data = '{"tool": "add_numbers", "parameters": {"a": 5, "b": 3}}'
    validation_result = await handler.validate_tool_call_request(tool_data, {})
    
    print(f"Validation result: {validation_result}")
    assert validation_result.get("action") == True
    assert validation_result.get("tool_name") == "add_numbers"
    
    # Test tool execution
    result = await handler.call("add_numbers", {"a": 5, "b": 3})
    print(f"Tool execution result: {result}")
    assert result == 8
    
    print("✅ LocalToolHandler tests passed!")


async def test_local_tool_executor():
    """Test the LocalToolExecutor"""
    print("\n🧪 Testing LocalToolExecutor")
    print("=" * 40)
    
    # Use the global local_tools instance
    executor = LocalToolExecutor(local_tools, "greet")
    
    # Mock add_message_to_history function
    async def mock_add_message(agent_name, role, content, metadata=None, session_id=None):
        print(f"Mock message added: {role} - {content}")
    
    # Test execution
    result = await executor.execute(
        agent_name="test_agent",
        tool_args={"name": "World"},
        tool_name="greet",
        tool_call_id="test-123",
        add_message_to_history=mock_add_message,
        session_id="test_session"
    )
    
    print(f"Executor result: {result}")
    assert "Hello, World!" in result
    
    print("✅ LocalToolExecutor tests passed!")


async def test_tool_discovery():
    """Test tool discovery and registration"""
    print("\n🧪 Testing Tool Discovery")
    print("=" * 40)
    
    # Get available tools
    tools = get_local_tools()
    print(f"Found {len(tools)} registered tools:")
    for tool in tools:
        print(f"  🔧 {tool['name']}: {tool['description']}")
    
    # Test tool execution
    result = await execute_local_tool("add_numbers", {"a": 10, "b": 20})
    print(f"add_numbers(10, 20) = {result}")
    assert result == 30
    
    result = await execute_local_tool("greet", {"name": "Alice"})
    print(f"greet('Alice') = {result}")
    assert result == "Hello, Alice!"
    
    print("✅ Tool discovery tests passed!")


async def main():
    """Run all tests"""
    print("🚀 Testing Local Tools Integration with Updated Base Agent")
    print("=" * 60)
    
    try:
        await test_local_tool_handler()
        await test_local_tool_executor()
        await test_tool_discovery()
        
        print("\n🎉 All tests passed! Local tools integration is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 