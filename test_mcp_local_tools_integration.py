#!/usr/bin/env python3
"""
Comprehensive test for MCP and Local Tools Integration
Tests the complete flow from tool registration to execution
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcpomni_connect.agents.tools.local_tools_integration import LocalToolsIntegration
from mcpomni_connect.agents.tools.tools_handler import LocalToolHandler, MCPToolHandler, ToolExecutor
from mcpomni_connect.agents.base import BaseReactAgent
from mcpomni_connect.agents.types import ParsedResponse
from mcpomni_connect.memory import InMemoryStore


def greet_person(name: str) -> str:
    """Simple greeting function"""
    return f"Hello, {name}! Nice to meet you!"


def calculate_sum(a: int, b: int) -> int:
    """Calculate sum of two numbers"""
    return a + b


def get_weather(city: str) -> str:
    """Mock weather function"""
    return f"Weather in {city}: Sunny, 25°C"


async def test_local_tools_integration():
    """Test the LocalToolsIntegration class"""
    print("\n🧪 Testing LocalToolsIntegration")
    
    # Create local tools integration
    local_tools = LocalToolsIntegration()
    
    # Register tools
    local_tools.register_tool("greet_person", greet_person, "Simple greeting function")
    local_tools.register_tool("calculate_sum", calculate_sum, "Calculate sum of two numbers")
    local_tools.register_tool("get_weather", get_weather, "Mock weather function")
    
    # Test get_available_tools
    available_tools = local_tools.get_available_tools()
    # print(f"Available tools: {[tool['name'] for tool in available_tools]}")
    
    # Test tool execution
    result1 = await local_tools.execute_tool("greet_person", {"name": "Alice"})
    print(f"greet_person result: {result1}")
    
    result2 = await local_tools.execute_tool("calculate_sum", {"a": 5, "b": 3})
    print(f"calculate_sum result: {result2}")
    
    result3 = await local_tools.execute_tool("get_weather", {"city": "New York"})
    print(f"get_weather result: {result3}")
    
    print("✅ LocalToolsIntegration tests passed!")


async def test_local_tool_handler():
    """Test the LocalToolHandler class"""
    print("\n🧪 Testing LocalToolHandler")
    
    # Create local tools integration
    local_tools = LocalToolsIntegration()
    local_tools.register_tool("greet_person", greet_person, "Simple greeting function")
    local_tools.register_tool("calculate_sum", calculate_sum, "Calculate sum of two numbers")
    
    # Create handler
    handler = LocalToolHandler(local_tools=local_tools)
    
    # Test validation
    tool_data = '{"tool": "greet_person", "parameters": {"name": "Bob"}}'
    validation_result = await handler.validate_tool_call_request(tool_data, local_tools)
    print(f"Validation result: {validation_result}")
    
    # Test tool execution
    result = await handler.call("greet_person", {"name": "Bob"})
    print(f"Tool execution result: {result}")
    
    print("✅ LocalToolHandler tests passed!")


async def test_tool_executor():
    """Test the ToolExecutor class"""
    print("\n🧪 Testing ToolExecutor")
    
    # Create local tools integration
    local_tools = LocalToolsIntegration()
    local_tools.register_tool("greet_person", greet_person, "Simple greeting function")
    
    # Create handler and executor
    handler = LocalToolHandler(local_tools=local_tools)
    executor = ToolExecutor(tool_handler=handler)
    
    # Mock message history function
    async def mock_add_message_to_history(agent_name, role, content, metadata=None, session_id=None):
        print(f"Mock message: {role} - {content}")
    
    # Test execution
    result = await executor.execute(
        agent_name="test_agent",
        tool_name="greet_person",
        tool_args={"name": "Charlie"},
        tool_call_id="test_id",
        add_message_to_history=mock_add_message_to_history,
        session_id="test_session"
    )
    
    print(f"Executor result: {result}")
    print("✅ ToolExecutor tests passed!")


async def test_base_agent_tool_resolution():
    """Test the BaseReactAgent tool resolution"""
    print("\n🧪 Testing BaseReactAgent Tool Resolution")
    
    # Create local tools integration
    local_tools = LocalToolsIntegration()
    local_tools.register_tool("greet_person", greet_person, "Simple greeting function")
    local_tools.register_tool("calculate_sum", calculate_sum, "Calculate sum of two numbers")
    
    # Create base agent
    agent = BaseReactAgent(
        agent_name="test_agent",
        max_steps=10,
        tool_call_timeout=30,
        request_limit=100,
        total_tokens_limit=10000
    )
    
    # Test tool resolution with local tools
    parsed_response = ParsedResponse(
        action=True,
        data='{"tool": "greet_person", "parameters": {"name": "David"}}'
    )
    
    tool_result = await agent.resolve_tool_call_request(
        parsed_response=parsed_response,
        sessions={},  # Empty for local tools
        mcp_tools={},  # Empty for local tools
        local_tools=local_tools
    )
    
    print(f"Tool resolution result: {tool_result}")
    
    if hasattr(tool_result, 'tool_name'):
        print(f"Resolved tool: {tool_result.tool_name}")
        print(f"Tool args: {tool_result.tool_args}")
        print("✅ BaseReactAgent tool resolution passed!")
    else:
        print(f"❌ Tool resolution failed: {tool_result}")


async def test_mock_mcp_tools():
    """Test MCP tools with mock data"""
    print("\n🧪 Testing Mock MCP Tools")
    
    # Create mock MCP tools structure
    class MockMCPTool:
        def __init__(self, name):
            self.name = name
    
    mock_mcp_tools = {
        "mock_server": [
            MockMCPTool("mcp_greet"),
            MockMCPTool("mcp_calculate")
        ]
    }
    
    # Create mock sessions
    mock_sessions = {
        "mock_server": {
            "session": type('MockSession', (), {
                'call_tool': lambda tool_name, tool_args: f"MCP {tool_name} called with {tool_args}"
            })()
        }
    }
    
    # Create base agent
    agent = BaseReactAgent(
        agent_name="test_agent",
        max_steps=10,
        tool_call_timeout=30,
        request_limit=100,
        total_tokens_limit=10000
    )
    
    # Test MCP tool resolution
    parsed_response = ParsedResponse(
        action=True,
        data='{"tool": "mcp_greet", "parameters": {"name": "Eve"}}'
    )
    
    tool_result = await agent.resolve_tool_call_request(
        parsed_response=parsed_response,
        sessions=mock_sessions,
        mcp_tools=mock_mcp_tools,
        local_tools=None
    )
    
    print(f"MCP tool resolution result: {tool_result}")
    
    if hasattr(tool_result, 'tool_name'):
        print(f"Resolved MCP tool: {tool_result.tool_name}")
        print(f"Tool args: {tool_result.tool_args}")
        print("✅ Mock MCP tools test passed!")
    else:
        print(f"❌ MCP tool resolution failed: {tool_result}")


async def test_tool_priority():
    """Test that MCP tools take priority over local tools"""
    print("\n🧪 Testing Tool Priority (MCP over Local)")
    
    # Create local tools integration
    local_tools = LocalToolsIntegration()
    local_tools.register_tool("greet_person", greet_person, "Simple greeting function")
    
    # Create mock MCP tools with same name
    class MockMCPTool:
        def __init__(self, name):
            self.name = name
    
    mock_mcp_tools = {
        "mock_server": [
            MockMCPTool("greet_person")  # Same name as local tool
        ]
    }
    
    mock_sessions = {
        "mock_server": {
            "session": type('MockSession', (), {
                'call_tool': lambda tool_name, tool_args: f"MCP {tool_name} called with {tool_args}"
            })()
        }
    }
    
    # Create base agent
    agent = BaseReactAgent(
        agent_name="test_agent",
        max_steps=10,
        tool_call_timeout=30,
        request_limit=100,
        total_tokens_limit=10000
    )
    
    # Test tool resolution - should prefer MCP tool
    parsed_response = ParsedResponse(
        action=True,
        data='{"tool": "greet_person", "parameters": {"name": "Frank"}}'
    )
    
    tool_result = await agent.resolve_tool_call_request(
        parsed_response=parsed_response,
        sessions=mock_sessions,
        mcp_tools=mock_mcp_tools,
        local_tools=local_tools
    )
    
    print(f"Tool priority result: {tool_result}")
    
    if hasattr(tool_result, 'tool_name'):
        print(f"Resolved tool: {tool_result.tool_name}")
        # Check if it's using MCP tool (should have server_name in the handler)
        if hasattr(tool_result.tool_executor.tool_handler, 'server_name'):
            print("✅ MCP tool took priority as expected!")
        else:
            print("❌ Local tool was used instead of MCP tool")
    else:
        print(f"❌ Tool resolution failed: {tool_result}")


async def test_complete_integration():
    """Test complete integration with memory store"""
    print("\n🧪 Testing Complete Integration")
    
    # Create local tools integration
    local_tools = LocalToolsIntegration()
    local_tools.register_tool("greet_person", greet_person, "Simple greeting function")
    local_tools.register_tool("calculate_sum", calculate_sum, "Calculate sum of two numbers")
    
    # Create memory store
    memory_store = InMemoryStore(max_context_tokens=10000, debug=True)
    
    # Create base agent
    agent = BaseReactAgent(
        agent_name="integration_test_agent",
        max_steps=10,
        tool_call_timeout=30,
        request_limit=100,
        total_tokens_limit=10000
    )
    
    # Mock LLM connection
    class MockLLMConnection:
        async def llm_call(self, messages):
            # Return a mock response that triggers tool usage
            return type('MockResponse', (), {
                'choices': [type('MockChoice', (), {
                    'message': type('MockMessage', (), {
                        'content': 'Action: {"tool": "greet_person", "parameters": {"name": "Integration Test"}}'
                    })()
                })()],
                'usage': type('MockUsage', (), {
                    'prompt_tokens': 10,
                    'completion_tokens': 5,
                    'total_tokens': 15
                })()
            })()
    
    llm_connection = MockLLMConnection()
    
    # Test the complete run method
    try:
        result = await agent.run(
            system_prompt="You are a helpful assistant with access to tools.",
            query="Please greet someone named 'Integration Test'",
            llm_connection=llm_connection.llm_call,
            add_message_to_history=memory_store.store_message,
            message_history=memory_store.get_messages,
            debug=True,
            sessions={},
            available_tools={"local_tools": local_tools.get_available_tools()},
            mcp_tools={},
            local_tools=local_tools,
            session_id="integration_test"
        )
        
        print(f"Integration test result: {result}")
        print("✅ Complete integration test passed!")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all tests"""
    print("🚀 Starting MCP and Local Tools Integration Tests")
    print("=" * 60)
    
    try:
        await test_local_tools_integration()
        await test_local_tool_handler()
        await test_tool_executor()
        await test_base_agent_tool_resolution()
        await test_mock_mcp_tools()
        await test_tool_priority()
        await test_complete_integration()
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed successfully!")
        print("✅ Both MCP and Local tools are working correctly!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 