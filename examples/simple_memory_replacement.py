#!/usr/bin/env python3
"""
Simple Memory Replacement Example

Shows how to replace Redis memory with database memory in existing code.
This is the simplest way to add database persistence to your agents.
"""

import asyncio
from mcpomni_connect.memory import DatabaseSessionMemory, RedisShortTermMemory, InMemoryShortTermMemory


async def before_database_memory():
    """How you might have been using memory before."""
    print("=== BEFORE: Using Redis or In-Memory ===")
    
    # Old way - Redis memory
    redis_memory = RedisShortTermMemory(max_context_tokens=30000)
    
    # Or in-memory
    inmemory = InMemoryShortTermMemory(max_context_tokens=30000)
    
    # Store some messages
    await redis_memory.store_message("user", "Hello, I need help with Python")
    await redis_memory.store_message("assistant", "I'd be happy to help!")
    
    # Get messages for agent
    messages = await redis_memory.get_messages()
    print(f"Redis stored {len(messages)} messages")
    
    return redis_memory


async def after_database_memory():
    """How to use database memory - just replace the memory object!"""
    print("\n=== AFTER: Using Database Memory ===")
    
    # New way - Database memory (SAME INTERFACE!)
    db_memory = DatabaseSessionMemory(
        db_url="sqlite:///simple_example.db",  # Optional - defaults to SQLite
        max_context_tokens=30000
    )
    
    # Everything else stays exactly the same!
    await db_memory.store_message("user", "Hello, I need help with Python")
    await db_memory.store_message("assistant", "I'd be happy to help!")
    
    # Same method calls
    messages = await db_memory.get_messages()
    print(f"Database stored {len(messages)} messages")
    
    # Same additional methods
    await db_memory.save_message_history_to_file("backup.json")
    await db_memory.set_memory_config("token_budget", 5000)
    
    return db_memory


async def agent_integration_example():
    """How to use database memory with your agents."""
    print("\n=== AGENT INTEGRATION EXAMPLE ===")
    
    from mcpomni_connect.agents.tool_calling_agent import ToolCallingAgent
    from mcpomni_connect.agents.types import AgentConfig
    from mcpomni_connect.llm import LLMConnection
    
    # 1. Initialize database memory
    db_memory = DatabaseSessionMemory()  # Uses default SQLite
    
    # 2. Configure your agent (same as always)
    agent_config = AgentConfig(
        agent_name="my_agent",
        max_steps=10,
        mcp_enabled=True
    )
    
    # 3. Configure LLM (same as always)
    llm_config = {"provider": "openai", "model": "gpt-4o-mini"}
    llm_connection = LLMConnection(llm_config)
    
    # 4. Initialize agent (same as always)
    agent = ToolCallingAgent(config=agent_config)
    
    # 5. The ONLY difference - pass database memory functions:
    response = await agent.run(
        query="Help me with Python programming",
        chat_id="my_session",
        system_prompt="You are a helpful assistant",
        llm_connection=llm_connection,
        sessions={},
        server_names=[],
        tools_list=[],
        available_tools={},
        # 🔄 OLD WAY (Redis):
        # add_message_to_history=redis_memory.store_message,
        # message_history=redis_memory.get_messages,
        
        # ✅ NEW WAY (Database):
        add_message_to_history=db_memory.store_message,
        message_history=db_memory.get_messages,
    )
    
    print(f"Agent response: {response}")
    
    # Check persistence
    messages = await db_memory.get_messages()
    print(f"Agent conversation stored {len(messages)} messages in database")


async def production_config_example():
    """Production configuration example."""
    print("\n=== PRODUCTION CONFIGURATION ===")
    
    import os
    
    # Set environment variables for production
    os.environ.setdefault('DATABASE_URL', 'postgresql://user:pass@localhost/mcp_prod')
    os.environ.setdefault('LLM_API_KEY', 'your-api-key')
    
    # Initialize with production database
    db_memory = DatabaseSessionMemory(
        db_url=os.getenv('DATABASE_URL'),
        max_context_tokens=50000,  # Higher for production
        debug=False  # Turn off debug logs
    )
    
    print(f"Production database configured")
    print("Environment variables:")
    print(f"  DATABASE_URL: {os.getenv('DATABASE_URL')}")
    print(f"  Memory capacity: {db_memory.max_context_tokens} tokens")


async def main():
    """Run the examples."""
    print("Simple Database Memory Integration")
    print("=" * 50)
    
    # Show before/after comparison
    await before_database_memory()
    await after_database_memory()
    
    # Show agent integration
    await agent_integration_example()
    
    # Show production config
    await production_config_example()
    
    print("\n" + "=" * 50)
    print("🎯 SUMMARY:")
    print("""
    To replace Redis/In-Memory with Database memory:
    
    1. Replace this:
       memory = RedisShortTermMemory()
       
       With this:
       memory = DatabaseSessionMemory()
    
    2. Everything else stays the same!
       - Same method calls (store_message, get_messages)
       - Same agent integration
       - Same memory strategies
       - Same file operations
    
    3. Benefits you get:
       ✅ Persistent across restarts
       ✅ Full session tracking
       ✅ SQL database storage
       ✅ Production ready
       ✅ Better metadata support
    
    4. Configuration (optional):
       - Set DATABASE_URL environment variable
       - Supports PostgreSQL, MySQL, SQLite
       - Defaults to SQLite if not configured
    """)


if __name__ == "__main__":
    asyncio.run(main()) 