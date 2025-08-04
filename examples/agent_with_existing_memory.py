#!/usr/bin/env python3
"""
Agent with Database Memory

This example shows how to build an agent using the database memory store.
Demonstrates persistent memory across sessions using SQLite or PostgreSQL.
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

from mcpomni_connect.omni_agent import OmniAgent
from mcpomni_connect.memory_store.memory_router import MemoryRouter
from mcpomni_connect.events.event_router import EventRouter
from mcpomni_connect.utils import logger


class AgentWithDatabaseMemory:
    """An agent that uses database memory for persistent storage."""

    def __init__(self, db_url: str = "sqlite:///agent_database_memory.db"):
        """Initialize the agent with database memory.

        Args:
            db_url: Database URL (SQLite or PostgreSQL)
                   Examples:
                   - "sqlite:///agent_memory.db"
                   - "postgresql://user:password@localhost/dbname"
        """
        self.db_url = db_url

        # Set DATABASE_URL environment variable for MemoryRouter
        os.environ["DATABASE_URL"] = db_url

        # Create memory and event routers
        self.memory_store = MemoryRouter(memory_store_type="database")
        self.event_router = EventRouter(event_store_type="in_memory")

        # Create the OmniAgent with database memory
        self.agent = OmniAgent(
            name="database_memory_agent",
            system_instruction="""You are a helpful AI assistant with persistent memory.
            You can remember information across different conversation sessions.
            Use this memory to provide personalized and context-aware responses.
            Always check your memory for relevant past interactions before responding.""",
            model_config={
                "provider": "openai",  # Change to your preferred provider
                "model": "gpt-4",
                "temperature": 0.7,
                "max_context_length": 50000,
            },
            mcp_tools=[
                {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        str(Path.home()),  # Access user's home directory
                    ],
                }
            ],
            agent_config={
                "max_steps": 15,
                "tool_call_timeout": 60,
                "request_limit": 1000,
                "memory_config": {"mode": "token_budget", "value": 10000},
            },
            memory_store=self.memory_store,
            event_router=self.event_router,
            debug=True,
        )

    async def run_message(self, message: str, session_id: str = None) -> dict:
        """Process a user message and return the agent's response.

        Args:
            message: User's message
            session_id: Optional session ID (auto-generated if not provided)

        Returns:
            Dict with response and session_id
        """
        try:
            logger.info(f"Processing message: {message[:50]}...")

            # Run the agent
            result = await self.agent.run(message, session_id)

            logger.info(f"Agent response generated for session: {result['session_id']}")
            return result

        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "session_id": session_id or "error_session",
            }

    async def get_session_history(self, session_id: str) -> list[dict]:
        """Get the conversation history for a specific session.

        Args:
            session_id: Session identifier

        Returns:
            List of messages in the session
        """
        try:
            return await self.agent.get_session_history(session_id)
        except Exception as e:
            logger.error(f"Failed to get session history: {e}")
            return []

    async def clear_session_memory(self, session_id: str) -> None:
        """Clear memory for a specific session.

        Args:
            session_id: Session identifier
        """
        try:
            await self.agent.clear_session_history(session_id)
            logger.info(f"Cleared memory for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to clear session memory: {e}")

    async def get_all_sessions(self) -> list[str]:
        """Get a list of all session IDs in the database."""
        try:
            # Get messages and extract unique session IDs
            # This is a simplified approach - in a real app you might want
            # to implement this directly in the memory store
            sessions = set()
            # Note: This is a conceptual example - actual implementation
            # would depend on the memory store's capabilities
            return list(sessions)
        except Exception as e:
            logger.error(f"Failed to get all sessions: {e}")
            return []

    def get_database_info(self) -> dict:
        """Get information about the database memory store."""
        return {
            "database_url": self.db_url,
            "memory_store_type": "database",
            "memory_store_info": self.memory_store.get_memory_store_info(),
            "agent_name": self.agent.name,
            "debug_mode": self.agent.debug,
        }


async def interactive_chat():
    """Interactive chat interface with database memory."""

    # Load environment variables
    load_dotenv()

    # Check for required environment variables
    if not os.getenv("LLM_API_KEY"):
        print("❌ LLM_API_KEY environment variable not found!")
        print("Please set it in your .env file:")
        print("LLM_API_KEY=your_api_key_here")
        return

    # Initialize agent with database memory
    agent = AgentWithDatabaseMemory()

    try:
        print("🤖 Agent initialized with database memory")
        print("💾 Database:", agent.db_url)
        print(
            "💬 Start chatting! Commands: 'quit', 'history', 'clear', 'sessions', 'info'"
        )
        print("-" * 60)

        current_session_id = None

        # Interactive chat loop
        while True:
            try:
                user_input = input("You: ").strip()

                if user_input.lower() in ["quit", "exit", "bye"]:
                    print("👋 Goodbye!")
                    break

                if user_input.lower() == "history":
                    if current_session_id:
                        history = await agent.get_session_history(current_session_id)
                        print(f"\n📜 Session History ({current_session_id}):")
                        for entry in history[-10:]:  # Show last 10 messages
                            print(
                                f"  {entry.get('role', 'unknown')}: {entry.get('content', '')[:100]}..."
                            )
                    else:
                        print("No active session yet. Start a conversation first.")
                    print()
                    continue

                if user_input.lower() == "clear":
                    if current_session_id:
                        await agent.clear_session_memory(current_session_id)
                        print(f"🧹 Memory cleared for session: {current_session_id}")
                        current_session_id = None
                    else:
                        print("No active session to clear.")
                    continue

                if user_input.lower() == "info":
                    info = agent.get_database_info()
                    print("\n📊 Database Info:")
                    for key, value in info.items():
                        print(f"  {key}: {value}")
                    print()
                    continue

                if user_input.lower() == "sessions":
                    sessions = await agent.get_all_sessions()
                    print(f"\n📋 Available Sessions: {len(sessions)}")
                    for session in sessions[:10]:  # Show first 10
                        print(f"  - {session}")
                    print()
                    continue

                if not user_input:
                    continue

                # Process message
                print("🤖 Agent is thinking...")
                result = await agent.run_message(user_input, current_session_id)

                # Update current session ID
                current_session_id = result["session_id"]

                print(f"Agent: {result['response']}")
                print(f"Session: {current_session_id}")
                print()

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                continue

    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")


async def demonstrate_memory_persistence():
    """Demonstrate memory persistence across different sessions."""

    print("\n" + "=" * 60)
    print("DEMONSTRATING DATABASE MEMORY PERSISTENCE")
    print("=" * 60)

    # Initialize agent
    agent = AgentWithDatabaseMemory()

    # Session 1: Store some personal information
    session1 = "user_profile_session"
    print(f"\n📝 Session 1 ({session1}): Storing user information")

    result1 = await agent.run_message(
        "Hello! My name is Alice, I'm a software engineer from San Francisco, and I love working with Python and AI.",
        session1,
    )
    print(f"Agent: {result1['response'][:100]}...")

    # Session 2: Different session with same user
    session2 = "work_discussion_session"
    print(f"\n💼 Session 2 ({session2}): Work discussion")

    result2 = await agent.run_message(
        "Can you help me with a Python debugging problem? I'm getting a strange error.",
        session2,
    )
    print(f"Agent: {result2['response'][:100]}...")

    # Session 3: Return to first session
    print(f"\n🔄 Back to Session 1 ({session1}): Testing memory recall")

    result3 = await agent.run_message(
        "What do you remember about me? Where do I work and what languages do I use?",
        session1,
    )
    print(f"Agent: {result3['response'][:100]}...")

    # Show session histories
    print("\n📊 Memory Statistics:")
    history1 = await agent.get_session_history(session1)
    history2 = await agent.get_session_history(session2)

    print(f"  Session 1 messages: {len(history1)}")
    print(f"  Session 2 messages: {len(history2)}")
    print(f"  Total messages stored: {len(history1) + len(history2)}")


async def example_usage():
    """Example showing programmatic usage of the database memory agent."""

    print("\n" + "=" * 60)
    print("PROGRAMMATIC USAGE EXAMPLE")
    print("=" * 60)

    # Initialize agent
    agent = AgentWithDatabaseMemory()

    try:
        session_id = "example_session"

        # Process a series of messages
        messages = [
            "Hello! I'm a data scientist working on machine learning projects.",
            "Can you help me understand the difference between supervised and unsupervised learning?",
            "What about neural networks? How do they work?",
            "Thanks! Can you recommend some good Python libraries for ML?",
        ]

        print(f"🔄 Processing {len(messages)} messages in session: {session_id}")

        for i, message in enumerate(messages, 1):
            print(f"\n💬 Message {i}: {message[:50]}...")
            result = await agent.run_message(message, session_id)
            print(f"✅ Response generated: {result['response'][:80]}...")

        # Get conversation summary
        history = await agent.get_session_history(session_id)
        print("\n📊 Conversation completed:")
        print(f"  Total messages: {len(history)}")
        print(f"  Session ID: {session_id}")

        # Test memory recall
        print("\n🧠 Testing memory recall:")
        memory_test = await agent.run_message(
            "What did I tell you about my profession at the beginning of our conversation?",
            session_id,
        )
        print(f"Memory test result: {memory_test['response'][:100]}...")

    except Exception as e:
        print(f"❌ Error in example usage: {e}")


async def main():
    """Main function demonstrating all database memory features."""

    print("🚀 Database Memory Agent Examples")
    print("=" * 60)

    try:
        # 1. Run programmatic example
        await example_usage()

        # 2. Demonstrate memory persistence
        await demonstrate_memory_persistence()

        # 3. Interactive chat (optional)
        print("\n" + "=" * 60)
        print("Would you like to try interactive chat? (y/n)")
        response = input().strip().lower()

        if response in ["y", "yes"]:
            await interactive_chat()
        else:
            print("✅ Examples completed! Database memory is persistent across runs.")

    except Exception as e:
        print(f"❌ Error in main: {e}")


if __name__ == "__main__":
    asyncio.run(main())
