#!/usr/bin/env python3
"""
Simplified Local Tools Example - Demonstrating Core Features

This example showcases the essential local tools features:
- Tool Registry
- Tool Integration
- Tool Monitoring
- Tool Security
"""

import asyncio
import json
from pathlib import Path
from mcpomni_connect.agents.tools.local_tools_integration import (
    LocalToolsIntegration,
    setup_tool_ecosystem,
    get_ecosystem_status,
    get_tool_insights
)
from mcpomni_connect.agents.tools.tool_security import SecurityPolicy, SecurityLevel
from mcpomni_connect.omni_agent.agent import OmniAgent


async def demonstrate_core_features():
    """Demonstrate core local tools features"""
    print("🚀 Simplified Local Tools Example - Core Features")
    print("=" * 60)
    
    # Initialize the simplified local tools integration
    local_tools = LocalToolsIntegration()
    
    # 1. Setup Basic Tool Ecosystem
    print("\n1️⃣ Setting up basic tool ecosystem...")
    local_tools.setup_basic_tool_ecosystem()
    
    # 2. Register some tools
    print("\n2️⃣ Registering Tools")
    print("-" * 30)
    
    @local_tools.register_tool(
        name="calculate",
        description="Perform mathematical calculations"
    )
    def calculate(operation: str, a: float, b: float) -> float:
        """Perform basic mathematical operations"""
        operations = {
            "add": lambda x, y: x + y,
            "subtract": lambda x, y: x - y,
            "multiply": lambda x, y: x * y,
            "divide": lambda x, y: x / y if y != 0 else "Error: Division by zero"
        }
        
        if operation not in operations:
            return f"Error: Unknown operation '{operation}'"
        
        return operations[operation](a, b)
    
    @local_tools.register_tool(
        name="greet",
        description="Greet someone by name"
    )
    def greet(name: str) -> str:
        """Greet someone by name"""
        return f"Hello, {name}! Nice to meet you!"
    
    @local_tools.register_tool(
        name="validate_email",
        description="Validate email address format"
    )
    def validate_email(email: str) -> dict:
        """Validate email address format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid = bool(re.match(pattern, email))
        
        return {
            "email": email,
            "is_valid": is_valid,
            "message": "Valid email" if is_valid else "Invalid email format"
        }
    
    print(f"Registered {len(local_tools.list_tool_names())} tools")
    
    # 3. Tool Security
    print("\n3️⃣ Tool Security")
    print("-" * 30)
    
    # Add security policies
    admin_policy = SecurityPolicy(
        name="admin_policy",
        level=SecurityLevel.ADMIN,
        allowed_tools=["calculate", "greet", "validate_email"],
        required_roles=["admin"]
    )
    
    user_policy = SecurityPolicy(
        name="user_policy", 
        level=SecurityLevel.USER,
        allowed_tools=["calculate", "greet"],
        required_roles=["user"]
    )
    
    local_tools.add_security_policy(admin_policy)
    local_tools.add_security_policy(user_policy)
    
    # Set user context
    local_tools.set_user_context("alice", ["user"])
    
    print("Security policies configured")
    
    # 4. Test Tool Execution
    print("\n4️⃣ Testing Tool Execution")
    print("-" * 30)
    
    # Test calculations
    result1 = await local_tools.execute_tool("calculate", {"operation": "add", "a": 10, "b": 20})
    print(f"calculate(add, 10, 20) = {result1}")
    
    result2 = await local_tools.execute_tool("greet", {"name": "World"})
    print(f"greet('World') = {result2}")
    
    result3 = await local_tools.execute_tool("validate_email", {"email": "test@example.com"})
    print(f"validate_email('test@example.com') = {result3}")
    
    # 5. Tool Monitoring
    print("\n5️⃣ Tool Monitoring")
    print("-" * 30)
    
    # Get monitoring summary
    monitoring_summary = local_tools.get_monitoring_summary()
    print(f"Total tool executions: {monitoring_summary.get('total_executions', 0)}")
    print(f"Success rate: {monitoring_summary.get('success_rate', 0):.1f}%")
    
    # Get insights
    insights = local_tools.get_tool_usage_insights()
    print("Usage insights:")
    for insight in insights:
        print(f"  {insight}")
    
    # 6. Integration with OmniAgent
    print("\n6️⃣ OmniAgent Integration")
    print("-" * 30)
    
    # Create OmniAgent with local tools
    agent = OmniAgent(
        name="LocalToolsAgent",
        model_config={
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "api_key": "your-api-key-here"  # Replace with real key
        },
        mcp_tools=[],  # No MCP tools
        local_tools=local_tools,  # Local tools integration
        agent_config={
            "agent_name": "LocalToolsAgent",
            "tool_call_timeout": 30,
            "max_steps": 10
        }
    )
    
    print("✅ OmniAgent created with local tools!")
    
    # Show available tools
    tools = local_tools.get_available_tools()
    print(f"Available tools: {len(tools)}")
    for tool in tools:
        print(f"  🔧 {tool['name']}: {tool['description']}")
    
    # 7. Ecosystem Status
    print("\n7️⃣ Ecosystem Status")
    print("-" * 30)
    
    status = local_tools.get_ecosystem_status()
    print(f"Tools registered: {status['tools_registered']}")
    print(f"Monitoring active: {'Yes' if status['monitoring_summary'] else 'No'}")
    print(f"Security configured: {'Yes' if status['security_report'] else 'No'}")
    
    # Clean up
    await agent.cleanup()
    
    print("\n🎉 Core features demonstration complete!")


async def main():
    """Run the demonstration"""
    try:
        await demonstrate_core_features()
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print("✅ Tool Registry - Simple function registration")
        print("✅ Tool Integration - Seamless OmniAgent integration") 
        print("✅ Tool Monitoring - Usage tracking and insights")
        print("✅ Tool Security - Access control and policies")
        print("\nThe local tools system is now focused and streamlined!")
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 