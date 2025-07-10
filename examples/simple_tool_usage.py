#!/usr/bin/env python3
"""
Simple Tool Usage - The Basics

This shows the absolute basics:
1. Register a tool
2. Execute it
3. That's it!
"""

from mcpomni_connect.agents.tools.local_tools_registry import ToolRegistry

# 1. Create registry
registry = ToolRegistry()

# 2. Register a tool (this is what you do)
@registry.register(
    name="add",
    description="Add two numbers"
)
def add(a: int, b: int) -> int:
    return a + b

# 3. Execute the tool (this is how you use it)
async def main():
    result = await registry.execute_tool("add", {"a": 5, "b": 3})
    print(f"Result: {result}")  # Output: Result: 8

# Run it
import asyncio
asyncio.run(main()) 