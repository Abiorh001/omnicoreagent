#!/usr/bin/env python3
"""
Complete Phase 2 Example - Demonstrating All Local Tools Features

This example showcases all the Phase 2 features of the local tools system:
- Tool Discovery
- Tool Templates
- Tool Composition
- Tool Caching
- Tool Monitoring
- Tool Security
- Tool SDK
- Tool Testing
- Tool Documentation
"""

import asyncio
import json
from pathlib import Path
from mcpomni_connect.agents.tools.local_tools_integration import (
    LocalToolsIntegration,
    setup_tool_ecosystem,
    get_ecosystem_status,
    run_tool_tests,
    generate_tool_docs,
    get_tool_insights
)
from mcpomni_connect.agents.tools.tool_sdk import tool_builder
from mcpomni_connect.agents.tools.tool_security import SecurityPolicy, SecurityLevel
from mcpomni_connect.omni_agent.agent import OmniAgent


async def demonstrate_phase2_features():
    """Demonstrate all Phase 2 features"""
    print("🚀 Phase 2 Complete Example - Local Tools Ecosystem")
    print("=" * 60)
    
    # Initialize the comprehensive local tools integration
    local_tools = LocalToolsIntegration()
    
    # 1. Setup Complete Tool Ecosystem
    print("\n1️⃣ Setting up complete tool ecosystem...")
    local_tools.setup_complete_tool_ecosystem()
    
    # 2. Tool Discovery
    print("\n2️⃣ Tool Discovery")
    print("-" * 30)
    
    # Discover tools from current directory
    discovered = local_tools.discover_tools_from_directory(".")
    print(f"Discovered {len(discovered)} potential tools from current directory")
    
    # Auto-register discovered tools
    registered_count = local_tools.auto_register_discovered_tools()
    print(f"Auto-registered {registered_count} tools")
    
    # 3. Tool Templates
    print("\n3️⃣ Tool Templates")
    print("-" * 30)
    
    # List available templates
    templates = local_tools.list_templates()
    print(f"Available templates: {', '.join(templates)}")
    
    # Load specific template
    data_tools_count = local_tools.load_template("data_processing")
    print(f"Loaded {data_tools_count} data processing tools")
    
    # 4. Custom Tool Creation with SDK
    print("\n4️⃣ Custom Tool Creation with SDK")
    print("-" * 30)
    
    @tool_builder.tool(
        name="custom_data_analyzer",
        description="Custom data analyzer with advanced features",
        version="1.0.0",
        author="Phase 2 Example",
        tags=["custom", "analysis", "data"],
        examples=[
            {
                "data": "[1, 2, 3, 4, 5]",
                "operation": "mean",
                "expected_result": "3.0"
            }
        ]
    )
    async def custom_data_analyzer(data: str, operation: str = "mean") -> str:
        """Custom data analyzer for demonstration"""
        try:
            numbers = json.loads(data)
            if operation == "mean":
                result = sum(numbers) / len(numbers)
            elif operation == "sum":
                result = sum(numbers)
            elif operation == "max":
                result = max(numbers)
            elif operation == "min":
                result = min(numbers)
            else:
                return f"Unknown operation: {operation}"
            
            return str(result)
        except Exception as e:
            return f"Error: {str(e)}"
    
    print("✅ Created custom tool: custom_data_analyzer")
    
    # 5. Tool Composition
    print("\n5️⃣ Tool Composition")
    print("-" * 30)
    
    # Create a data processing pipeline
    pipeline = local_tools.create_composition("data_pipeline")
    pipeline.add_step(
        tool_name="csv_to_json",
        parameters={"csv_data": "$input_data"},
        output_key="json_data"
    ).add_step(
        tool_name="filter_data",
        parameters={
            "data": "$json_data",
            "field": "age",
            "value": "25",
            "operator": "gt"
        },
        output_key="filtered_data"
    ).add_step(
        tool_name="custom_data_analyzer",
        parameters={
            "data": "$filtered_data",
            "operation": "mean"
        },
        output_key="analysis_result"
    )
    
    print("✅ Created data processing pipeline")
    
    # Register composition as a tool
    tool_name = local_tools.register_composition_as_tool("data_pipeline")
    print(f"✅ Registered composition as tool: {tool_name}")
    
    # 6. Tool Caching
    print("\n6️⃣ Tool Caching")
    print("-" * 30)
    
    # Set TTL for specific tools
    local_tools.set_tool_ttl("calculate", 3600)  # 1 hour
    local_tools.set_tool_ttl("fetch_url", 1800)  # 30 minutes
    
    # Get cache stats
    cache_stats = local_tools.get_cache_stats()
    print(f"Cache stats: {cache_stats}")
    
    # 7. Tool Monitoring
    print("\n7️⃣ Tool Monitoring")
    print("-" * 30)
    
    # Set performance alerts
    local_tools.set_performance_alert("fetch_url", 5.0)  # Alert if > 5s
    local_tools.set_performance_alert("calculate", 2.0)  # Alert if > 2s
    
    # Execute some tools to generate monitoring data
    print("Executing tools to generate monitoring data...")
    
    # Execute math tools
    await local_tools.execute_tool("add", {"a": 5, "b": 3})
    await local_tools.execute_tool("multiply", {"a": 4, "b": 6})
    await local_tools.execute_tool("calculate", {"expression": "2 + 2 * 3"})
    
    # Execute data processing tools
    csv_data = "name,age\nJohn,30\nJane,25\nBob,35"
    await local_tools.execute_tool("csv_to_json", {"csv_data": csv_data})
    
    # Get monitoring insights
    insights = local_tools.get_tool_usage_insights()
    print("Tool usage insights:")
    for insight in insights:
        print(f"  {insight}")
    
    # 8. Tool Security
    print("\n8️⃣ Tool Security")
    print("-" * 30)
    
    # Create security policy
    file_policy = SecurityPolicy(
        tool_name="read_text_file",
        security_level=SecurityLevel.HIGH,
        allowed_parameters={"file_path", "encoding"},
        parameter_validation={
            "file_path": lambda path: not path.startswith("/") and ".." not in path
        },
        rate_limit=10,
        require_authentication=True,
        audit_logging=True
    )
    
    local_tools.add_security_policy(file_policy)
    print("✅ Added security policy for file operations")
    
    # Set user context
    local_tools.set_user_context("demo_user", ["admin", "developer"])
    print("✅ Set user context for security checks")
    
    # 9. Tool Testing
    print("\n9️⃣ Tool Testing")
    print("-" * 30)
    
    # Run basic tests
    test_results = await local_tools.run_basic_tests()
    print(f"Test results: {test_results}")
    
    # Benchmark tools
    benchmark_results = await local_tools.benchmark_all_tools(iterations=10)
    print(f"Benchmark results: {benchmark_results}")
    
    # 10. Tool Documentation
    print("\n🔟 Tool Documentation")
    print("-" * 30)
    
    # Generate documentation
    docs = local_tools.generate_markdown_docs()
    print(f"Generated documentation ({len(docs)} characters)")
    
    # Generate JSON schema
    schema = local_tools.generate_json_schema()
    print(f"Generated JSON schema ({len(schema)} characters)")
    
    # 11. Integration with OmniAgent
    print("\n1️⃣1️⃣ Integration with OmniAgent")
    print("-" * 30)
    
    # Create OmniAgent with local tools
    model_config = {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "api_key": "your-api-key-here"
    }
    
    # Note: In a real scenario, you would provide actual MCP tools
    mcp_tools = []  # Empty for this example
    
    agent_config = {
        "agent_name": "Phase2DemoAgent",
        "tool_call_timeout": 30,
        "max_steps": 10
    }
    
    print("Creating OmniAgent with local tools integration...")
    print("Note: This is a demonstration - actual API key required for full execution")
    
    # 12. Ecosystem Status
    print("\n1️⃣2️⃣ Ecosystem Status")
    print("-" * 30)
    
    status = local_tools.get_ecosystem_status()
    print("Ecosystem Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Phase 2 demonstration complete!")
    return local_tools


async def demonstrate_tool_execution():
    """Demonstrate actual tool execution"""
    print("\n🛠️ Tool Execution Demonstration")
    print("=" * 40)
    
    local_tools = LocalToolsIntegration()
    local_tools.setup_complete_tool_ecosystem()
    
    # Execute various tools
    print("\nExecuting math tools...")
    result1 = await local_tools.execute_tool("add", {"a": 10, "b": 20})
    print(f"add(10, 20) = {result1}")
    
    result2 = await local_tools.execute_tool("multiply", {"a": 5, "b": 6})
    print(f"multiply(5, 6) = {result2}")
    
    print("\nExecuting data processing tools...")
    csv_data = "name,age,city\nJohn,30,NYC\nJane,25,LA\nBob,35,Chicago"
    result3 = await local_tools.execute_tool("csv_to_json", {"csv_data": csv_data})
    print(f"CSV to JSON conversion: {result3[:100]}...")
    
    print("\nExecuting custom tool...")
    result4 = await local_tools.execute_tool("custom_data_analyzer", {
        "data": "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]",
        "operation": "mean"
    })
    print(f"Custom data analyzer result: {result4}")
    
    print("\n✅ Tool execution demonstration complete!")


def demonstrate_documentation_generation():
    """Demonstrate documentation generation"""
    print("\n📚 Documentation Generation")
    print("=" * 40)
    
    local_tools = LocalToolsIntegration()
    local_tools.setup_complete_tool_ecosystem()
    
    # Generate all documentation formats
    docs = local_tools.generate_all_documentation()
    
    print("Generated documentation files:")
    for doc_type, content in docs.items():
        print(f"  • {doc_type}: {len(content)} characters")
    
    # Save documentation to files
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    with open(docs_dir / "tools_documentation.md", "w") as f:
        f.write(docs["markdown"])
    
    with open(docs_dir / "tools_schema.json", "w") as f:
        f.write(docs["json_schema"])
    
    print("✅ Documentation saved to docs/ directory")


async def main():
    """Main demonstration function"""
    print("🎯 MCPOmni Connect Phase 2 - Complete Local Tools Ecosystem")
    print("=" * 70)
    
    try:
        # Run main demonstration
        local_tools = await demonstrate_phase2_features()
        
        # Demonstrate tool execution
        await demonstrate_tool_execution()
        
        # Demonstrate documentation generation
        demonstrate_documentation_generation()
        
        print("\n🎉 All Phase 2 features demonstrated successfully!")
        print("\n📋 Summary of implemented features:")
        print("  ✅ Tool Discovery - Automatic tool detection")
        print("  ✅ Tool Templates - Pre-configured tool sets")
        print("  ✅ Tool Composition - Chain multiple tools")
        print("  ✅ Tool Caching - Result caching and optimization")
        print("  ✅ Tool Monitoring - Performance and usage tracking")
        print("  ✅ Tool Security - Access control and validation")
        print("  ✅ Tool SDK - Easy custom tool creation")
        print("  ✅ Tool Testing - Automated testing framework")
        print("  ✅ Tool Documentation - Auto-generated documentation")
        print("  ✅ OmniAgent Integration - Seamless agent integration")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 