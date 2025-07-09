#!/usr/bin/env python3
"""
Programmatic Database Memory Usage (No CLI)

This example shows how to use DatabaseSessionMemory directly in your 
applications without the CLI interface.
"""

import asyncio
from mcpomni_connect.memory import DatabaseSessionMemory
from mcpomni_connect.agents.tool_calling_agent import ToolCallingAgent
from mcpomni_connect.agents.types import AgentConfig
from mcpomni_connect.llm import LLMConnection


async def example_direct_agent_usage():
    """Example: Using database memory directly with agents."""
    print("=== Direct Agent Usage with Database Memory ===")
    
    # Initialize database memory
    db_memory = DatabaseSessionMemory(
        db_url="sqlite:///agent_memory.db",
        max_context_tokens=20000,
        debug=True
    )
    
    # Initialize LLM connection (you'd configure this based on your setup)
    llm_config = {
        "provider": "openai",
        "model": "gpt-4o-mini", 
        "temperature": 0.7,
        "max_tokens": 2000
    }
    # llm_connection = LLMConnection(llm_config)  # Configure as needed
    
    # Configure agent
    agent_config = AgentConfig(
        agent_name="database_agent",
        tool_call_timeout=30,
        max_steps=10,
        request_limit=100,
        total_tokens_limit=50000,
        mcp_enabled=True
    )
    
    # Initialize agent
    agent = ToolCallingAgent(config=agent_config, debug=True)
    
    # Example conversation flow
    queries = [
        "Help me understand Python asyncio",
        "What are the best practices for async programming?",
        "Can you give me an example of using asyncio.gather()?"
    ]
    
    for query in queries:
        print(f"\nUser: {query}")
        
        # Store user message
        await db_memory.store_message("user", query, {"query_type": "programming"})
        
        # Simulate agent response (in real usage, you'd call the agent)
        response = f"This is a simulated response to: {query[:30]}..."
        
        # Store assistant response
        await db_memory.store_message("assistant", response, {"response_type": "helpful"})
        
        print(f"Assistant: {response}")
    
    # Retrieve conversation history
    messages = await db_memory.get_messages()
    print(f"\nStored {len(messages)} messages in database")
    
    return db_memory


async def example_custom_application():
    """Example: Custom application with database memory."""
    print("\n=== Custom Application Integration ===")
    
    class MyMCPApp:
        def __init__(self, db_url=None):
            self.memory = DatabaseSessionMemory(
                db_url=db_url or "sqlite:///my_app_memory.db",
                max_context_tokens=15000
            )
            self.session_active = True
            
        async def start_conversation(self, user_id=None):
            """Start a new conversation session."""
            if user_id:
                # You could customize session management here
                pass
            print("Conversation started with database memory")
            
        async def process_message(self, message, role="user", metadata=None):
            """Process and store a message."""
            await self.memory.store_message(role, message, metadata or {})
            
            # Get conversation context for processing
            context = await self.memory.get_messages()
            
            # Your business logic here
            response = f"Processed: {message[:50]}..."
            
            # Store response
            await self.memory.store_message("assistant", response, {"processed": True})
            
            return response
            
        async def get_conversation_summary(self):
            """Get a summary of the current conversation."""
            messages = await self.memory.get_messages()
            user_msgs = [m for m in messages if m['role'] == 'user']
            assistant_msgs = [m for m in messages if m['role'] == 'assistant']
            
            return {
                "total_messages": len(messages),
                "user_messages": len(user_msgs),
                "assistant_messages": len(assistant_msgs),
                "last_activity": messages[-1]['timestamp'] if messages else None
            }
            
        async def export_conversation(self, filename):
            """Export conversation to file."""
            await self.memory.save_message_history_to_file(filename)
            
        async def clear_session(self):
            """Clear current session."""
            await self.memory.clear_memory()
    
    # Usage example
    app = MyMCPApp()
    await app.start_conversation()
    
    # Simulate conversation
    await app.process_message("Hello, I need help with my project")
    await app.process_message("What technology stack do you recommend?")
    await app.process_message("I'm building a web API")
    
    # Get summary
    summary = await app.get_conversation_summary()
    print(f"Conversation summary: {summary}")
    
    # Export conversation
    await app.export_conversation("project_discussion.json")
    print("Conversation exported to project_discussion.json")
    
    return app


async def example_mcp_client_integration():
    """Example: Integrating with core MCP client without CLI."""
    print("\n=== MCP Client Integration (No CLI) ===")
    
    from mcpomni_connect.client import MCPClient
    
    class DatabaseMemoryMCPClient:
        def __init__(self, servers_config, db_url=None):
            self.client = MCPClient(servers_config, debug=True)
            self.memory = DatabaseSessionMemory(
                db_url=db_url or "sqlite:///mcp_client_memory.db",
                max_context_tokens=30000
            )
            
        async def initialize(self):
            """Initialize MCP client and connect to servers."""
            await self.client.connect_to_servers()
            
        async def query_with_memory(self, query, store_in_memory=True):
            """Execute a query using MCP tools with database memory."""
            if store_in_memory:
                await self.memory.store_message("user", query)
            
            # Get conversation context
            conversation_history = await self.memory.get_messages()
            
            # Get available tools
            tools = []
            for server_name in self.client.server_names:
                session = self.client.sessions.get(server_name)
                if session:
                    server_tools = await session.list_tools()
                    tools.extend(server_tools.tools)
            
            # Process query with tools (simplified example)
            # In real implementation, you'd use your agent system here
            response = f"Processed query '{query}' with {len(tools)} available tools"
            
            if store_in_memory:
                await self.memory.store_message("assistant", response, {
                    "tools_available": len(tools),
                    "servers_connected": len(self.client.server_names)
                })
            
            return response
            
        async def get_memory_stats(self):
            """Get statistics about stored conversations."""
            messages = await self.memory.get_messages()
            last_active = await self.memory.get_last_active()
            
            return {
                "total_messages": len(messages),
                "last_active": last_active,
                "memory_type": "database",
                "session_id": self.memory.session_id
            }
            
        async def cleanup(self):
            """Clean up resources."""
            await self.client.cleanup()
    
    # Example usage (you'd need actual server config)
    servers_config = {
        "example-server": {
            "transport_type": "stdio",
            "command": "echo",  # Dummy command for example
            "args": ["Hello from MCP"]
        }
    }
    
    client = DatabaseMemoryMCPClient(servers_config)
    # await client.initialize()  # Uncomment when you have real servers
    
    # Simulate usage
    response = await client.query_with_memory("List available files in current directory")
    print(f"Response: {response}")
    
    stats = await client.get_memory_stats()
    print(f"Memory stats: {stats}")
    
    return client


async def example_batch_processing():
    """Example: Batch processing with database memory."""
    print("\n=== Batch Processing with Database Memory ===")
    
    db_memory = DatabaseSessionMemory(
        db_url="sqlite:///batch_processing.db",
        max_context_tokens=50000
    )
    
    # Simulate batch processing of queries
    batch_queries = [
        "Analyze this data: [1, 2, 3, 4, 5]",
        "Create a Python function to calculate mean",
        "What are the best practices for data analysis?",
        "How do I handle missing data in pandas?",
        "Show me an example of data visualization"
    ]
    
    results = []
    
    for i, query in enumerate(batch_queries, 1):
        # Store query
        await db_memory.store_message("user", query, {
            "batch_id": "batch_001",
            "query_number": i,
            "processing_type": "data_analysis"
        })
        
        # Simulate processing
        result = f"Batch result {i}: Processed '{query[:30]}...'"
        
        # Store result
        await db_memory.store_message("assistant", result, {
            "batch_id": "batch_001", 
            "result_number": i,
            "status": "completed"
        })
        
        results.append(result)
        print(f"Processed query {i}/{len(batch_queries)}")
    
    # Get batch summary
    all_messages = await db_memory.get_messages()
    batch_messages = [m for m in all_messages if m.get('metadata', {}).get('batch_id') == 'batch_001']
    
    print(f"\nBatch processing complete:")
    print(f"- Total messages in session: {len(all_messages)}")
    print(f"- Batch-specific messages: {len(batch_messages)}")
    print(f"- Results generated: {len(results)}")
    
    return results


async def main():
    """Run all examples."""
    print("Database Memory - Programmatic Usage Examples")
    print("=" * 60)
    
    # Direct agent usage
    db_memory1 = await example_direct_agent_usage()
    
    # Custom application
    app = await example_custom_application()
    
    # MCP client integration
    client = await example_mcp_client_integration()
    
    # Batch processing
    results = await example_batch_processing()
    
    print("\n" + "=" * 60)
    print("Key Integration Patterns:")
    print("""
    1. **Direct Agent Integration**:
       - Pass DatabaseSessionMemory to agents as add_message_to_history and message_history
       - Agents automatically use database for persistence
       
    2. **Custom Application Wrapper**:
       - Wrap DatabaseSessionMemory in your own application class
       - Add business logic while keeping database persistence
       
    3. **MCP Client Integration**:
       - Replace CLI memory management with direct database memory
       - Full control over session management and queries
       
    4. **Batch Processing**:
       - Use metadata to track batch operations
       - Persistent storage for long-running processes
    """)


if __name__ == "__main__":
    asyncio.run(main()) 