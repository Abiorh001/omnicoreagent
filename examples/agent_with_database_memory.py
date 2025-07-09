#!/usr/bin/env python3
"""
Direct Agent Integration with Database Memory (No CLI)

This shows exactly how to use your agents with database memory 
programmatically, the same way the CLI does it internally.
"""

import asyncio
from mcpomni_connect.memory import DatabaseSessionMemory
from mcpomni_connect.agents.tool_calling_agent import ToolCallingAgent
from mcpomni_connect.agents.types import AgentConfig
from mcpomni_connect.llm import LLMConnection


async def example_tool_calling_agent_with_database():
    """Example showing exactly how CLI integrates database memory with agents."""
    
    # 1. Initialize database memory (same as CLI does)
    db_memory = DatabaseSessionMemory(
        db_url="sqlite:///my_agent_session.db",
        max_context_tokens=30000,
        debug=True
    )
    
    # 2. Configure your LLM connection
    llm_config = {
        "provider": "openai",  # or "groq", "anthropic", etc.
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_tokens": 2000,
        "max_context_length": 30000
    }
    llm_connection = LLMConnection(llm_config)
    
    # 3. Configure agent (same as CLI does)
    agent_config = AgentConfig(
        agent_name="tool_calling_agent",
        tool_call_timeout=30,
        max_steps=15,
        request_limit=1000,
        total_tokens_limit=100000,
        mcp_enabled=True
    )
    
    # 4. Initialize agent
    agent = ToolCallingAgent(config=agent_config, debug=True)
    
    # 5. Run agent with database memory - THIS IS THE KEY PART
    query = "Help me analyze some data and create a Python script"
    
    # This is exactly how the CLI calls the agent:
    response = await agent.run(
        query=query,
        chat_id="my_session_001",  # Your session identifier
        system_prompt="You are a helpful AI assistant with access to tools.",
        llm_connection=llm_connection,
        sessions={},  # MCP sessions (empty for this example)
        server_names=[],  # MCP server names
        tools_list=[],  # Available tools
        available_tools={},  # Tool metadata
        # HERE'S THE DATABASE MEMORY INTEGRATION:
        add_message_to_history=db_memory.store_message,  # Uses database storage
        message_history=db_memory.get_messages,  # Gets from database
    )
    
    print(f"Agent response: {response}")
    
    # 6. Check what was stored
    messages = await db_memory.get_messages()
    print(f"\nStored {len(messages)} messages in database:")
    for msg in messages[-3:]:  # Show last 3 messages
        print(f"  {msg['role']}: {msg['content'][:100]}...")
    
    return db_memory, agent


async def example_react_agent_with_database():
    """Example with ReAct Agent (for non-function-calling LLMs)."""
    
    from mcpomni_connect.agents.react_agent import ReactAgent
    
    # Initialize database memory
    db_memory = DatabaseSessionMemory(
        db_url="sqlite:///react_agent_session.db",
        max_context_tokens=25000
    )
    
    # Configure LLM for ReAct agent
    llm_config = {
        "provider": "groq",  # Example: Groq often used for ReAct
        "model": "llama-3.1-8b-instant",
        "temperature": 0.1,
        "max_tokens": 1500
    }
    llm_connection = LLMConnection(llm_config)
    
    # Configure ReAct agent
    agent_config = AgentConfig(
        agent_name="react_agent",
        tool_call_timeout=30,
        max_steps=10,
        request_limit=500,
        total_tokens_limit=50000,
        mcp_enabled=True
    )
    
    # Initialize ReAct agent
    react_agent = ReactAgent(config=agent_config)
    
    # Run ReAct agent with database memory
    system_prompt = "You are a helpful assistant that can use tools to help users."
    query = "Find information about Python best practices"
    
    response = await react_agent._run(
        system_prompt=system_prompt,
        query=query,
        llm_connection=llm_connection,
        # Database memory integration:
        add_message_to_history=db_memory.store_message,
        message_history=db_memory.get_messages,
        debug=True,
        # Additional ReAct-specific parameters:
        sessions={},
        available_tools={},
        is_generic_agent=True,
        chat_id="react_session_001"
    )
    
    print(f"ReAct Agent response: {response}")
    return db_memory


async def example_orchestrator_agent_with_database():
    """Example with Orchestrator Agent for complex multi-step tasks."""
    
    from mcpomni_connect.agents.orchestrator import OrchestratorAgent
    from mcpomni_connect.agents.local_tools import AGENTS_REGISTRY
    
    # Initialize database memory
    db_memory = DatabaseSessionMemory(
        db_url="sqlite:///orchestrator_session.db",
        max_context_tokens=40000
    )
    
    # Configure LLM
    llm_config = {
        "provider": "openai",
        "model": "gpt-4o",  # Orchestrator works best with more capable models
        "temperature": 0.3,
        "max_tokens": 3000
    }
    llm_connection = LLMConnection(llm_config)
    
    # Configure orchestrator
    agent_config = AgentConfig(
        agent_name="orchestrator_agent", 
        tool_call_timeout=60,
        max_steps=20,
        request_limit=500,
        total_tokens_limit=80000,
        mcp_enabled=True
    )
    
    # Initialize orchestrator 
    orchestrator = OrchestratorAgent(
        config=agent_config,
        agents_registry=AGENTS_REGISTRY,
        current_date_time="2024-01-15 10:30:00",
        chat_id="orchestrator_session_001",
        debug=True
    )
    
   
    query = "Create a comprehensive data analysis pipeline"
    system_prompt = "You coordinate multiple agents to complete complex tasks."
    
    response = await orchestrator.run(
        query=query,
        sessions={},
        add_message_to_history=db_memory.store_message,
        llm_connection=llm_connection,
        available_tools={},
        message_history=db_memory.get_messages,
        orchestrator_system_prompt=system_prompt,
        tool_call_timeout=60,
        max_steps=20,
        request_limit=500,
        total_tokens_limit=80000
    )
    
    print(f"Orchestrator response: {response}")
    return db_memory


async def example_memory_strategies():
    """Example showing different memory strategies with agents."""
    
    db_memory = DatabaseSessionMemory(
        db_url="sqlite:///memory_strategies.db",
        max_context_tokens=20000
    )
    
    # Test different memory strategies
    strategies = [
        ("token_budget", 5000),
        ("sliding_window", 10),
        ("token_budget", 10000)
    ]
    
    for strategy, value in strategies:
        print(f"\n--- Testing {strategy} strategy with value {value} ---")
        
        # Set memory strategy
        db_memory.set_memory_config(strategy, value)
        
        # Simulate storing messages
        for i in range(15):
            await db_memory.store_message(
                "user", 
                f"This is test message {i+1} for {strategy} strategy",
                {"strategy": strategy, "value": value, "message_num": i+1}
            )
        
        # Check how many messages are retained
        messages = await db_memory.get_messages()
        print(f"Strategy {strategy}({value}): Retained {len(messages)} messages")
        
        # Clear for next test
        await db_memory.clear_memory()


async def example_production_setup():
    """Example showing production-ready setup."""
    
    import os
    from decouple import config
    
    # Production database configuration
    db_url = config('DATABASE_URL', default='sqlite:///production_mcp.db')
    
    # Initialize with production settings
    db_memory = DatabaseSessionMemory(
        db_url=db_url,
        max_context_tokens=50000,  # Higher limit for production
        debug=False  # Turn off debug in production
    )
    
    # Production LLM configuration
    llm_config = {
        "provider": config('LLM_PROVIDER', default='openai'),
        "model": config('LLM_MODEL', default='gpt-4o-mini'),
        "temperature": float(config('LLM_TEMPERATURE', default='0.7')),
        "max_tokens": int(config('LLM_MAX_TOKENS', default='2000')),
        "max_context_length": int(config('LLM_MAX_CONTEXT', default='50000'))
    }
    
    print("Production setup configured:")
    print(f"- Database: {db_url}")
    print(f"- LLM: {llm_config['provider']}/{llm_config['model']}")
    print(f"- Max context: {db_memory.max_context_tokens} tokens")
    
    return db_memory, llm_config


async def main():
    """Run all examples."""
    print("Database Memory + Agent Integration Examples")
    print("=" * 60)
    
    # Tool Calling Agent
    print("1. Tool Calling Agent with Database Memory")
    db_memory1, agent1 = await example_tool_calling_agent_with_database()
    
    # ReAct Agent  
    print("\n2. ReAct Agent with Database Memory")
    db_memory2 = await example_react_agent_with_database()
    
    # Orchestrator Agent
    print("\n3. Orchestrator Agent with Database Memory")
    db_memory3 = await example_orchestrator_agent_with_database()
    
    # Memory strategies
    print("\n4. Memory Strategies")
    await example_memory_strategies()
    
    # Production setup
    print("\n5. Production Setup")
    prod_memory, prod_config = await example_production_setup()
    
    print("\n" + "=" * 60)
    print("Integration Summary:")
    print("""
    🔑 KEY POINTS for using database memory without CLI:
    
    1. **Replace CLI memory functions**:
       add_message_to_history=db_memory.store_message
       message_history=db_memory.get_messages
    
    2. **Agent configuration stays the same**:
       - Same AgentConfig
       - Same LLMConnection
       - Same agent.run() calls
    
    3. **Automatic persistence**:
       - All conversations stored in database
       - Sessions survive application restarts
       - Full event tracking with metadata
    
    4. **Memory strategies work seamlessly**:
       - db_memory.set_memory_config(mode, value)
       - token_budget or sliding_window
       - Enforced automatically
    
    5. **Production ready**:
       - PostgreSQL, MySQL, SQLite support
       - Configurable via DATABASE_URL
       - ACID transactions
    """)


if __name__ == "__main__":
    asyncio.run(main()) 