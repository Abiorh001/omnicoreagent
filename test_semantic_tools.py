#!/usr/bin/env python3
"""
Test script for semantic tool search functionality
"""

import asyncio
from src.mcpomni_connect.agents.base import BaseReactAgent

async def test_semantic_tool_search():
    """Test the semantic tool search functionality"""
    
    # Create a test agent
    agent = BaseReactAgent(
        agent_name="test_agent",
        max_steps=10,
        tool_call_timeout=30,
        request_limit=100,
        total_tokens_limit=10000
    )
    
    # Mock tools data
    mcp_tools = {
        "file_server": [
            type('Tool', (), {
                'name': 'read_file',
                'description': 'Read contents of a file from the filesystem',
                'inputSchema': {
                    'properties': {
                        'path': {'type': 'string', 'description': 'Path to the file'}
                    }
                }
            })(),
            type('Tool', (), {
                'name': 'write_file', 
                'description': 'Write content to a file on the filesystem',
                'inputSchema': {
                    'properties': {
                        'path': {'type': 'string', 'description': 'Path to the file'},
                        'content': {'type': 'string', 'description': 'Content to write'}
                    }
                }
            })()
        ],
        "web_server": [
            type('Tool', (), {
                'name': 'http_get',
                'description': 'Make an HTTP GET request to fetch data from a URL',
                'inputSchema': {
                    'properties': {
                        'url': {'type': 'string', 'description': 'URL to fetch'}
                    }
                }
            })()
        ]
    }
    
    # Test queries
    test_queries = [
        "I need to read a file",
        "I want to make an HTTP request",
        "I need to write data to a file",
        "Show me all tools"
    ]
    
    print("Testing semantic tool search...")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 30)
        
        # Get tools using semantic search
        tools_section = await agent.get_tools_registry(
            mcp_tools=mcp_tools,
            query=query,
            use_semantic_search=True,
            top_k=5
        )
        
        print(f"Relevant tools found: {len(tools_section.split('###')) - 1}")
        print("Tools section:")
        print(tools_section[:500] + "..." if len(tools_section) > 500 else tools_section)
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(test_semantic_tool_search()) 