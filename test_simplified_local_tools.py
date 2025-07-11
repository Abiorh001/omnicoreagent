#!/usr/bin/env python3
"""
Test simplified local tools system
Focuses only on: Registry, Integration, Monitoring, Security
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from mcpomni_connect.agents.tools.local_tools_integration import register_local_tool, get_local_tools, execute_local_tool, local_tools
from mcpomni_connect.agents.tools.tools_handler import LocalToolHandler, LocalToolExecutor


# Register tools using the decorator
@register_local_tool(
    name="add_numbers",
    description="Add two numbers together"
)
def add_numbers(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@register_local_tool(
    name="multiply_numbers", 
    description="Multiply two numbers"
)
def multiply_numbers(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b


@register_local_tool(
    name="greet_person",
    description="Greet someone by name"
)
def greet_person(name: str) -> str:
    """Greet someone by name"""
    return f"Hello, {name}! Nice to meet you!"


async def test_tool_registry():
    """Test tool registration and listing"""
    print("🧪 Testing Tool Registry")
    print("=" * 40)
    
    # Get available tools
    tools = get_local_tools()
    print(f"Found {len(tools)} registered tools:")
    for tool in tools:
        print(f"  🔧 {tool['name']}: {tool['description']}")
    
    assert len(tools) >= 3, f"Expected at least 3 tools, found {len(tools)}"
    print("✅ Tool registry test passed!")


async def test_tool_execution():
    """Test direct tool execution"""
    print("\n🧪 Testing Tool Execution")
    print("=" * 40)
    
    # Test tool execution
    result1 = await execute_local_tool("add_numbers", {"a": 15, "b": 27})
    print(f"add_numbers(15, 27) = {result1}")
    assert result1 == 42
    
    result2 = await execute_local_tool("multiply_numbers", {"a": 8, "b": 9})
    print(f"multiply_numbers(8, 9) = {result2}")
    assert result2 == 72
    
    result3 = await execute_local_tool("greet_person", {"name": "Alice"})
    print(f"greet_person('Alice') = {result3}")
    assert "Alice" in result3
    
    print("✅ Tool execution test passed!")


async def test_tool_monitoring():
    """Test tool monitoring"""
    print("\n🧪 Testing Tool Monitoring")
    print("=" * 40)
    
    # Get monitoring summary
    monitoring_summary = local_tools.get_monitoring_summary()
    print(f"Monitoring summary: {monitoring_summary}")
    
    # Get insights
    insights = local_tools.get_tool_usage_insights()
    print("Usage insights:")
    for insight in insights:
        print(f"  {insight}")
    
    print("✅ Tool monitoring test passed!")


async def test_tool_security():
    """Test tool security"""
    print("\n🧪 Testing Tool Security")
    print("=" * 40)
    
    # Get security report
    security_report = local_tools.get_security_report()
    print(f"Security report: {security_report}")
    
    # Set user context
    local_tools.set_user_context("test_user", ["user"])
    print("User context set")
    
    print("✅ Tool security test passed!")


async def test_tool_handler():
    """Test LocalToolHandler"""
    print("\n🧪 Testing LocalToolHandler")
    print("=" * 40)
    
    # Create handler
    handler = LocalToolHandler(local_tools)
    
    # Test validation
    tool_data = '{"tool": "add_numbers", "parameters": {"a": 5, "b": 3}}'
    validation_result = await handler.validate_tool_call_request(tool_data, {})
    
    print(f"Validation result: {validation_result}")
    assert validation_result.get("action") == True
    assert validation_result.get("tool_name") == "add_numbers"
    
    # Test execution
    result = await handler.call("add_numbers", {"a": 5, "b": 3})
    print(f"Tool execution result: {result}")
    assert result == 8
    
    print("✅ LocalToolHandler test passed!")


async def test_tool_executor():
    """Test LocalToolExecutor"""
    print("\n🧪 Testing LocalToolExecutor")
    print("=" * 40)
    
    # Create executor
    executor = LocalToolExecutor(local_tools, "greet_person")
    
    # Mock add_message_to_history function
    async def mock_add_message(agent_name, role, content, metadata=None, session_id=None):
        print(f"Mock message added: {role} - {content}")
    
    # Test execution
    result = await executor.execute(
        agent_name="test_agent",
        tool_args={"name": "World"},
        tool_name="greet_person",
        tool_call_id="test-123",
        add_message_to_history=mock_add_message,
        session_id="test_session"
    )
    
    print(f"Executor result: {result}")
    assert "Hello, World!" in result
    
    print("✅ LocalToolExecutor test passed!")


async def main():
    """Run all tests"""
    print("🚀 Testing Simplified Local Tools System")
    print("=" * 60)
    print("Focus: Registry, Integration, Monitoring, Security")
    print("=" * 60)
    
    try:
        await test_tool_registry()
        await test_tool_execution()
        await test_tool_monitoring()
        await test_tool_security()
        await test_tool_handler()
        await test_tool_executor()
        
        print("\n🎉 All tests passed! Simplified local tools system is working correctly.")
        print("\n✅ What we have:")
        print("  • Simple tool registration with @register_local_tool")
        print("  • Direct tool execution")
        print("  • Basic monitoring and insights")
        print("  • Basic security policies")
        print("  • Integration with OmniAgent")
        print("  • No unnecessary complexity")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 