#!/usr/bin/env python3
"""
Simple test to demonstrate local tools integration with OmniAgent
Shows how the @register_local_tool decorator automatically makes tools available
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from mcpomni_connect.omni_agent.agent import OmniAgent
from mcpomni_connect.agents.tools.local_tools_integration import register_local_tool, local_tools


# Register tools using the decorator - these will be automatically available
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


@register_local_tool(
    name="calculate_area",
    description="Calculate the area of a rectangle"
)
def calculate_area(length: float, width: float) -> float:
    """Calculate area of a rectangle"""
    return length * width


async def test_omniagent_with_local_tools():
    """Test OmniAgent with local tools"""
    print("🚀 Testing OmniAgent with Local Tools")
    print("=" * 50)
    
    # Show what tools are registered
    print("📋 Registered Local Tools:")
    available_tools = local_tools.get_available_tools()
    for tool in available_tools:
        print(f"  🔧 {tool['name']}: {tool['description']}")
    
    print(f"\n✅ Found {len(available_tools)} registered tools")
    
    # Create OmniAgent with local tools
    # Note: local_tools is just the instance of LocalToolsIntegration
    agent = OmniAgent(
        name="LocalToolsAgent",
        model_config={
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "api_key": "your-api-key-here"  # Replace with real key for actual testing
        },
        mcp_tools=[],  # No MCP tools, only local tools
        local_tools=local_tools,  # This is the LocalToolsIntegration instance
        agent_config={
            "agent_name": "LocalToolsAgent",
            "tool_call_timeout": 30,
            "max_steps": 10
        }
    )
    
    print("\n✅ OmniAgent created with local tools!")
    print("🔧 Local tools are automatically available to the agent")
    
    # Show available tools in the agent
    print("\n📋 Tools available to OmniAgent:")
    agent_tools = agent.get_available_tools()
    for tool in agent_tools:
        print(f"  🔧 {tool['name']}: {tool['description']}")
    
    # Test direct tool execution (without running the agent)
    print("\n🧪 Testing Direct Tool Execution:")
    
    result1 = await local_tools.execute_tool("add_numbers", {"a": 15, "b": 27})
    print(f"add_numbers(15, 27) = {result1}")
    
    result2 = await local_tools.execute_tool("multiply_numbers", {"a": 8, "b": 9})
    print(f"multiply_numbers(8, 9) = {result2}")
    
    result3 = await local_tools.execute_tool("greet_person", {"name": "Alice"})
    print(f"greet_person('Alice') = {result3}")
    
    result4 = await local_tools.execute_tool("calculate_area", {"length": 10, "width": 5})
    print(f"calculate_area(10, 5) = {result4}")
    
    print("\n✅ All direct tool executions successful!")
    
    # Note: To actually test the agent with queries, you need a real API key
    print("\n💡 To test agent queries, replace 'your-api-key-here' with a real API key")
    print("Example queries the agent could handle:")
    print("  • 'What is 15 + 27?'")
    print("  • 'Calculate the area of a rectangle with length 10 and width 5'")
    print("  • 'Greet Alice'")
    print("  • 'Multiply 8 and 9'")
    
    # Clean up
    await agent.cleanup()
    
    return agent


async def demonstrate_decorator_approach():
    """Demonstrate how the decorator approach works"""
    print("\n" + "=" * 50)
    print("DECORATOR APPROACH EXPLANATION")
    print("=" * 50)
    
    print("1️⃣ Register tools with @register_local_tool decorator:")
    print("   @register_local_tool(name='tool_name', description='...')")
    print("   def tool_function(...): ...")
    
    print("\n2️⃣ Tools are automatically added to global local_tools instance")
    print("   from mcpomni_connect.agents.tools.local_tools_integration import local_tools")
    
    print("\n3️⃣ Pass local_tools to OmniAgent:")
    print("   agent = OmniAgent(..., local_tools=local_tools)")
    
    print("\n4️⃣ Agent automatically has access to all registered tools!")
    print("   No need to manually register or manage tool lists")
    
    print("\n✅ Benefits:")
    print("   • Simple decorator syntax")
    print("   • Automatic tool discovery")
    print("   • No manual tool management")
    print("   • Global tool registry")
    print("   • Easy to add new tools")


async def main():
    """Run the test"""
    try:
        await test_omniagent_with_local_tools()
        await demonstrate_decorator_approach()
        
        print("\n🎉 Local tools integration is working perfectly!")
        print("The @register_local_tool decorator automatically makes tools available to OmniAgent")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 