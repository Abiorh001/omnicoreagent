#!/usr/bin/env python3
"""
Basic Tool Registry Example - Step by Step

This example shows the fundamental usage of the tool registry:
1. Register a tool using decorator
2. Execute the tool
3. See the results
"""

import asyncio
from mcpomni_connect.agents.tools.local_tools_registry import ToolRegistry

# Step 1: Create a tool registry
tool_registry = ToolRegistry()

# Step 2: Register tools using decorators
@tool_registry.register(
    name="add_numbers",
    description="Add two numbers together"
)
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

@tool_registry.register(
    name="multiply_numbers", 
    description="Multiply two numbers together"
)
def multiply_numbers(a: float, b: float) -> float:
    """Multiply two numbers together"""
    return a * b

@tool_registry.register(
    name="greet_person",
    description="Greet a person by name"
)
def greet_person(name: str, greeting: str = "Hello") -> str:
    """Greet someone with a custom message"""
    return f"{greeting}, {name}!"

# Step 3: List all registered tools
print("🔧 Registered Tools:")
for tool in tool_registry.list_tools():
    print(f"  • {tool.name}: {tool.description}")
print()

# Step 4: Execute tools
async def execute_tools():
    print("🚀 Executing Tools:")
    
    # Execute add_numbers
    result1 = await tool_registry.execute_tool("add_numbers", {"a": 5, "b": 3})
    print(f"add_numbers(5, 3) = {result1}")
    
    # Execute multiply_numbers
    result2 = await tool_registry.execute_tool("multiply_numbers", {"a": 4.5, "b": 2.0})
    print(f"multiply_numbers(4.5, 2.0) = {result2}")
    
    # Execute greet_person
    result3 = await tool_registry.execute_tool("greet_person", {"name": "Alice", "greeting": "Hi there"})
    print(f"greet_person('Alice', 'Hi there') = {result3}")
    
    # Execute with default parameter
    result4 = await tool_registry.execute_tool("greet_person", {"name": "Bob"})
    print(f"greet_person('Bob') = {result4}")

# Step 5: Get tool schemas (useful for integration)
print("📋 Tool Schemas:")
schemas = tool_registry.get_tool_schemas()
for tool_name, schema in schemas.items():
    print(f"\n{tool_name}:")
    print(f"  Description: {schema['description']}")
    print(f"  Parameters: {schema['inputSchema']}")

# Run the example
if __name__ == "__main__":
    print("🎯 Basic Tool Registry Example")
    print("=" * 40)
    
    # Execute all tools
    asyncio.run(execute_tools())
    
    print("\n✅ Example completed!") 