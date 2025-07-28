#!/usr/bin/env python3
"""
Simple test script for semantic tool search functionality
"""

import asyncio
from src.mcpomni_connect.tool_retriever import ToolRetriever

async def test_semantic_tool_search():
    """Test the semantic tool search functionality"""
    
    # Create tool retriever
    tool_retriever = ToolRetriever()
    
    # Mock tools data
    mock_tools = [
        {
            "md": "### `read_file`\nRead contents of a file from the filesystem\n\n**Parameters:**\n| Name | Type | Description |\n|------|------|-------------|\n| `path` | `string` | Path to the file |",
            "server": "file_server",
            "type": "mcp"
        },
        {
            "md": "### `write_file`\nWrite content to a file on the filesystem\n\n**Parameters:**\n| Name | Type | Description |\n|------|------|-------------|\n| `path` | `string` | Path to the file |\n| `content` | `string` | Content to write |",
            "server": "file_server", 
            "type": "mcp"
        },
        {
            "md": "### `http_get`\nMake an HTTP GET request to fetch data from a URL\n\n**Parameters:**\n| Name | Type | Description |\n|------|------|-------------|\n| `url` | `string` | URL to fetch |",
            "server": "web_server",
            "type": "mcp"
        },
        {
            "md": "### `database_query`\nExecute a SQL query on the database\n\n**Parameters:**\n| Name | Type | Description |\n|------|------|-------------|\n| `query` | `string` | SQL query to execute |",
            "server": "database_server",
            "type": "mcp"
        }
    ]
    
    # Index the tools
    print("Indexing tools...")
    for tool in mock_tools:
        tool_retriever.upsert_markdown_tool(tool["md"])
    
    # Test queries
    test_queries = [
        "I need to read a file",
        "I want to make an HTTP request", 
        "I need to write data to a file",
        "I need to query the database",
        "Show me all tools"
    ]
    
    print("Testing semantic tool search...")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 30)
        
        # Get relevant tools using semantic search
        relevant_tools = tool_retriever.query_tools(
            query=query,
            top_k=3,
            all_tools=mock_tools
        )
        
        print(f"Relevant tools found: {len(relevant_tools)}")
        for i, tool in enumerate(relevant_tools, 1):
            print(f"{i}. Server: {tool['server']}")
            print(f"   Tool: {tool['md'].split('`')[1] if '`' in tool['md'] else 'Unknown'}")
            print()
    
    print("=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(test_semantic_tool_search()) 