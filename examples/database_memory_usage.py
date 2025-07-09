#!/usr/bin/env python3
"""
Database Memory Usage Example for MCPOmni Connect

This example demonstrates how to use the database memory system integrated 
with MCPOmni Connect for persistent conversation history and advanced
session management.

Features demonstrated:
1. Database memory configuration
2. Switching between memory types via CLI
3. Session persistence across restarts
4. Memory commands and history management
"""

import asyncio
import os
from mcpomni_connect.memory import DatabaseSessionMemory


async def example_standalone_database_memory():
    """Example of using DatabaseSessionMemory as a standalone component."""
    print("=== Standalone Database Memory Example ===")
    
    # Initialize database memory with SQLite
    db_memory = DatabaseSessionMemory(
        db_url="sqlite:///example_memory.db",
        max_context_tokens=10000,
        debug=True
    )
    
    # Store some sample messages
    await db_memory.store_message("user", "Hello, I need help with Python")
    await db_memory.store_message("assistant", "I'd be happy to help you with Python! What specific topic?")
    await db_memory.store_message("user", "I need to learn about async/await")
    await db_memory.store_message("assistant", "Async/await is used for asynchronous programming in Python...")
    
    # Retrieve messages
    messages = await db_memory.get_messages()
    print(f"\nStored {len(messages)} messages:")
    for msg in messages:
        print(f"  {msg['role']}: {msg['content'][:50]}...")
    
    # Save to file
    await db_memory.save_message_history_to_file("conversation_backup.json")
    print("\nConversation saved to conversation_backup.json")
    
    # Clear memory
    await db_memory.clear_memory()
    print("Memory cleared")


def example_cli_usage():
    """Example showing CLI commands for database memory usage."""
    print("\n=== CLI Usage Examples ===")
    
    cli_examples = """
    # Switch to database memory
    mcpomni_connect
    > /memory:database
    ✅ Memory persistence is now ENABLED using Database
    
    # Check current mode
    > /status
    🚀 MCPOmni Connect Status:
    - Mode: CHAT
    - Connected Servers: 2
    - Memory: ENABLED (Database SQLite)
    - Debug: OFF
    
    # Configure memory strategy
    > /memory_mode:token_budget:5000
    Memory mode set to 'token_budget' with value 5000.
    
    # Use the system normally - all conversations are automatically saved
    > How do I create a REST API in Python?
    [AI provides response with full conversation context]
    
    # View conversation history
    > /history
    [Shows all messages in current session]
    
    # Save conversation to file
    > /save_history:my_python_api_discussion.json
    Message history saved to my_python_api_discussion.json
    
    # Clear current session (creates new session)
    > /clear_history
    Message history cleared
    
    # Switch to different memory type
    > /memory:redis
    ✅ Memory persistence is now ENABLED using Redis
    
    # Cycle through memory types
    > /memory
    ✅ Memory persistence is now ENABLED using In-Memory
    
    > /memory  
    ✅ Memory persistence is now ENABLED using Redis
    
    > /memory
    ✅ Memory persistence is now ENABLED using Database
    """
    
    print(cli_examples)


def example_environment_configuration():
    """Example showing environment configuration options."""
    print("\n=== Environment Configuration Examples ===")
    
    config_examples = """
    # .env file configuration
    
    # Basic setup (uses SQLite by default)
    LLM_API_KEY=your_api_key_here
    
    # PostgreSQL database
    DATABASE_URL=postgresql://user:password@localhost:5432/mcp_sessions
    
    # MySQL database
    DATABASE_URL=mysql://user:password@localhost:3306/mcp_sessions
    
    # SQLite with custom path
    DATABASE_URL=sqlite:///custom/path/mcp_memory.db
    
    # Redis configuration (for Redis memory mode)
    REDIS_HOST=localhost
    REDIS_PORT=6379
    REDIS_DB=0
    
    # Example servers_config.json with database considerations
    {
        "AgentConfig": {
            "tool_call_timeout": 30,
            "max_steps": 15,
            "request_limit": 1000,
            "total_tokens_limit": 100000
        },
        "LLM": {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "temperature": 0.5,
            "max_tokens": 5000,
            "max_context_length": 30000
        },
        "mcpServers": {
            "filesystem": {
                "transport_type": "stdio",
                "command": "uvx",
                "args": ["mcp-server-filesystem", "/tmp"]
            }
        }
    }
    """
    
    print(config_examples)


def example_advanced_usage():
    """Example showing advanced database memory features."""
    print("\n=== Advanced Database Memory Features ===")
    
    advanced_examples = """
    Database Memory Advantages:
    
    1. **Full Session Tracking**:
       - Every conversation is stored as a session
       - Events include timestamps, metadata, and state changes
       - Sessions can be retrieved and analyzed later
    
    2. **State Management**:
       - App-level state (shared across all users)
       - User-level state (specific to user)
       - Session-level state (specific to conversation)
    
    3. **Memory Strategies**:
       - Token budget: Automatically manages context length
       - Sliding window: Keeps last N messages
       - Both work seamlessly with database storage
    
    4. **Cross-Session Persistence**:
       - Conversations survive application restarts
       - Multiple sessions can be maintained simultaneously
       - History can be queried and analyzed
    
    5. **Production Ready**:
       - Supports PostgreSQL, MySQL, SQLite
       - ACID transactions for data integrity
       - Efficient querying and indexing
    
    Example Workflow:
    
    # Day 1: Start a coding project discussion
    > /memory:database
    > I'm starting a new web application project
    
    # Day 2: Continue where you left off
    > /memory:database  # Same session continues automatically
    > What were we discussing about the web application?
    [AI remembers the full context from previous day]
    
    # Save important milestones
    > /save_history:project_day2_api_design.json
    
    # Analyze long-term patterns (via SQL queries on database)
    # Custom tools could be built to analyze conversation patterns
    """
    
    print(advanced_examples)


async def main():
    """Run all examples."""
    print("MCPOmni Connect Database Memory Integration Examples")
    print("=" * 60)
    
    # Standalone usage
    await example_standalone_database_memory()
    
    # CLI usage
    example_cli_usage()
    
    # Environment configuration
    example_environment_configuration()
    
    # Advanced features
    example_advanced_usage()
    
    print("\n=== Getting Started ===")
    print("""
    To get started with database memory:
    
    1. Install dependencies:
       pip install mcpomni-connect
    
    2. Optional: Set database URL in .env:
       DATABASE_URL=postgresql://user:pass@localhost/mcp_sessions
    
    3. Start MCPOmni Connect:
       mcpomni_connect
    
    4. Switch to database memory:
       > /memory:database
    
    5. Start chatting - everything is automatically saved!
    
    For more information, see: https://github.com/alidauda/mcp_omni_connect
    """)


if __name__ == "__main__":
    asyncio.run(main()) 