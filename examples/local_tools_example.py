#!/usr/bin/env python3
"""
Example: Using Local Tools with OmniAgent
Shows how to register and use local Python functions as tools.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcpomni_connect.omni_agent import OmniAgent
from mcpomni_connect.agents.tools.local_tools_integration import register_local_tool, get_local_tools


# Register some local tools
@register_local_tool(
    name="calculate",
    description="Perform mathematical calculations"
)
def calculate(operation: str, a: float, b: float) -> float:
    """Perform basic mathematical operations
    
    Args:
        operation: The operation to perform (add, subtract, multiply, divide)
        a: First number
        b: Second number
    
    Returns:
        Result of the calculation
    """
    operations = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else "Error: Division by zero"
    }
    
    if operation not in operations:
        return f"Error: Unknown operation '{operation}'"
    
    return operations[operation](a, b)


@register_local_tool(
    name="format_text",
    description="Format text in different ways"
)
def format_text(text: str, style: str = "normal") -> str:
    """Format text in different styles
    
    Args:
        text: Text to format
        style: Formatting style (normal, uppercase, lowercase, title)
    
    Returns:
        Formatted text
    """
    styles = {
        "normal": lambda x: x,
        "uppercase": lambda x: x.upper(),
        "lowercase": lambda x: x.lower(),
        "title": lambda x: x.title()
    }
    
    if style not in styles:
        return f"Error: Unknown style '{style}'"
    
    return styles[style](text)


@register_local_tool(
    name="analyze_list",
    description="Analyze a list of numbers"
)
def analyze_list(numbers: list) -> dict:
    """Analyze a list of numbers and return statistics
    
    Args:
        numbers: List of numbers to analyze
    
    Returns:
        Dictionary with statistics (sum, average, min, max, count)
    """
    if not numbers:
        return {"error": "Empty list provided"}
    
    return {
        "sum": sum(numbers),
        "average": sum(numbers) / len(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "count": len(numbers)
    }


async def example_local_tools():
    """Example: Using OmniAgent with local tools"""
    print("=" * 60)
    print("EXAMPLE: Local Tools with OmniAgent")
    print("=" * 60)
    
    # Show registered local tools
    print("📋 Registered Local Tools:")
    local_tools = get_local_tools()
    for tool in local_tools:
        print(f"  🔧 {tool['name']}: {tool['description']}")
        print(f"     Schema: {tool['inputSchema']}")
        print()
    
    # Create OmniAgent with local tools
    agent = OmniAgent(
        name="local_tools_agent",
        model_config={
            "provider": "gemini",
            "model": "gemini-2.0-flash",
            "max_context_length": 30000
        },
        mcp_tools=[],  # No MCP tools, only local tools
        # Local tools will be automatically available
    )
    
    print("✅ OmniAgent created with local tools!")
    
    # Test the agent with local tool usage
    print("\n🤖 Testing Local Tools:")
    
    # Test calculation
    print("\n📊 Testing calculation:")
    result1 = await agent.run("Calculate 15 + 27 using the calculate tool")
    print(f"Response: {result1['response']}")
    
    # Test text formatting
    print("\n📝 Testing text formatting:")
    result2 = await agent.run("Format 'hello world' in uppercase using the format_text tool")
    print(f"Response: {result2['response']}")
    
    # Test list analysis
    print("\n📈 Testing list analysis:")
    result3 = await agent.run("Analyze the list [1, 5, 10, 15, 20] using the analyze_list tool")
    print(f"Response: {result3['response']}")
    
    # Test complex reasoning
    print("\n🧠 Testing complex reasoning:")
    result4 = await agent.run("I have a list of numbers [2, 4, 6, 8, 10]. Calculate the sum and then format 'the sum is' followed by the result in uppercase.")
    print(f"Response: {result4['response']}")
    
    # Clean up
    await agent.cleanup()
    
    return agent


async def example_custom_tools():
    """Example: Creating custom tools for specific use cases"""
    print("\n" + "=" * 60)
    print("EXAMPLE: Custom Tools for Specific Use Cases")
    print("=" * 60)
    
    # Register custom tools for a specific domain
    @register_local_tool(
        name="validate_email",
        description="Validate email address format"
    )
    def validate_email(email: str) -> dict:
        """Validate email address format
        
        Args:
            email: Email address to validate
        
        Returns:
            Dictionary with validation result
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid = bool(re.match(pattern, email))
        
        return {
            "email": email,
            "is_valid": is_valid,
            "message": "Valid email" if is_valid else "Invalid email format"
        }
    
    @register_local_tool(
        name="generate_password",
        description="Generate a secure password"
    )
    def generate_password(length: int = 12, include_symbols: bool = True) -> str:
        """Generate a secure password
        
        Args:
            length: Length of the password (default: 12)
            include_symbols: Include special symbols (default: True)
        
        Returns:
            Generated password
        """
        import random
        import string
        
        chars = string.ascii_letters + string.digits
        if include_symbols:
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        return ''.join(random.choice(chars) for _ in range(length))
    
    # Show new tools
    print("📋 New Custom Tools:")
    local_tools = get_local_tools()
    for tool in local_tools:
        if tool['name'] in ['validate_email', 'generate_password']:
            print(f"  🔧 {tool['name']}: {tool['description']}")
    
    # Create agent with custom tools
    agent = OmniAgent(
        name="custom_tools_agent",
        model_config={
            "provider": "gemini",
            "model": "gemini-2.0-flash",
            "max_context_length": 30000
        },
        mcp_tools=[]
    )
    
    print("\n✅ OmniAgent created with custom tools!")
    
    # Test custom tools
    print("\n🤖 Testing Custom Tools:")
    
    # Test email validation
    print("\n📧 Testing email validation:")
    result1 = await agent.run("Validate the email address 'user@example.com'")
    print(f"Response: {result1['response']}")
    
    # Test password generation
    print("\n🔐 Testing password generation:")
    result2 = await agent.run("Generate a secure password with 16 characters including symbols")
    print(f"Response: {result2['response']}")
    
    # Clean up
    await agent.cleanup()
    
    return agent


async def main():
    """Run all examples"""
    print("🚀 OmniAgent with Local Tools")
    print("This shows how to use local Python functions as tools\n")
    
    # Set up environment
    os.environ["LLM_API_KEY"] = "your-api-key-here"
    
    # Run examples
    await example_local_tools()
    await example_custom_tools()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("✅ Local tools can be easily registered with decorators")
    print("✅ Tools support both sync and async functions")
    print("✅ Automatic schema inference from function signatures")
    print("✅ Seamless integration with OmniAgent")
    print("✅ Support for default parameters and type hints")
    print("✅ Easy to create domain-specific tools")
    print("\nBenefits:")
    print("• No need to run external MCP servers for simple functions")
    print("• Faster execution for local operations")
    print("• Easy to test and debug")
    print("• Can use any Python library or function")
    print("• Perfect for prototyping and development")


if __name__ == "__main__":
    asyncio.run(main()) 