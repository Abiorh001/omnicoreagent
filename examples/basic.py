#!/usr/bin/env python3
"""
Basic OmniAgent Example

This example shows how to create a simple agent using the OmniAgent class.
Demonstrates the basic setup and usage patterns for MCP agents.
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

from mcpomni_connect.omni_agent import OmniAgent
from mcpomni_connect.memory_store.memory_router import MemoryRouter
from mcpomni_connect.events.event_router import EventRouter
from mcpomni_connect.utils import logger


class BasicAgent:
    """A simple agent using OmniAgent with in-memory storage."""

    def __init__(self):
        """Initialize the basic agent with simple configuration."""

        # Create memory and event routers
        self.memory_store = MemoryRouter(memory_store_type="mongodb")
        self.event_router = EventRouter(event_store_type="in_memory")

        # Create the OmniAgent
        self.agent = OmniAgent(
            name="basic_agent",
            system_instruction="""You are a helpful AI assistant.
            You can help with various tasks including answering questions,
            providing explanations, and using available tools to assist users.
            Always be friendly, helpful, and accurate in your responses.""",
            model_config={
                "provider": "openai",  # Change to your preferred provider
                "model": "gpt-4o",
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
                "request_limit": 0,  # 0 = unlimited (production mode)
                "total_tokens_limit": 0,  # 0 = unlimited (production mode)
                "memory_results_limit": 5,  # Number of memory results to retrieve
                "memory_similarity_threshold": 0.5,  # Similarity threshold for memory filtering
            },
            memory_store=self.memory_store,
            event_router=self.event_router,
            debug=True,
        )

    async def run_query(self, query: str, session_id: str = None) -> dict:
        """Process a user query and return the agent's response.

        Args:
            query: User's query/message
            session_id: Optional session ID (auto-generated if not provided)

        Returns:
            Dict with response and session_id
        """
        try:
            logger.info(f"Processing query: {query[:50]}...")

            # Run the agent
            result = await self.agent.run(query, session_id)

            logger.info(f"Response generated for session: {result['session_id']}")
            return result

        except Exception as e:
            logger.error(f"Failed to process query: {e}")
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "session_id": session_id or "error_session",
            }

    async def get_session_history(self, session_id: str) -> list[dict]:
        """Get the conversation history for a specific session."""
        try:
            return await self.agent.get_session_history(session_id)
        except Exception as e:
            logger.error(f"Failed to get session history: {e}")
            return []

    async def clear_session_memory(self, session_id: str) -> None:
        """Clear memory for a specific session."""
        try:
            await self.agent.clear_session_history(session_id)
            logger.info(f"Cleared memory for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to clear session memory: {e}")

    def get_agent_info(self) -> dict:
        """Get information about the agent configuration."""
        return {
            "agent_name": self.agent.name,
            "memory_store_type": "in_memory",
            "memory_store_info": self.memory_store.get_memory_store_info(),
            "event_store_type": self.agent.get_event_store_type(),
            "debug_mode": self.agent.debug,
        }


async def interactive_chat():
    """Interactive chat interface with basic agent."""

    # Load environment variables
    load_dotenv()

    # Check for required environment variables
    if not os.getenv("LLM_API_KEY"):
        print("❌ LLM_API_KEY environment variable not found!")
        print("Please set it in your .env file:")
        print("LLM_API_KEY=your_api_key_here")
        return

    # Initialize basic agent
    agent = BasicAgent()

    try:
        print("🤖 Basic Agent initialized")
        print("💬 Start chatting! Commands: 'quit', 'history', 'clear', 'info'")
        print("-" * 50)

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
                    info = agent.get_agent_info()
                    print("\n📊 Agent Info:")
                    for key, value in info.items():
                        print(f"  {key}: {value}")
                    print()
                    continue

                if not user_input:
                    continue

                # Process query
                print("🤖 Agent is thinking...")
                result = await agent.run_query(user_input, current_session_id)

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


async def demonstrate_basic_usage():
    """Demonstrate basic agent usage with example queries."""

    print("\n" + "=" * 50)
    print("DEMONSTRATING BASIC AGENT USAGE")
    print("=" * 50)

    # Initialize agent
    agent = BasicAgent()

    # Example session
    session_id = "demo_session"

    # Example queries
    queries = [
        "Hello! Can you introduce yourself?",
        "What's the weather like today?",
        "Can you help me understand what you can do?",
        "What files are in my home directory?",
    ]

    print(f"🔄 Processing {len(queries)} example queries...")

    for i, query in enumerate(queries, 1):
        print(f"\n💬 Query {i}: {query}")

        try:
            result = await agent.run_query(query, session_id)
            print(f"✅ Agent: {result['response'][:150]}...")

        except Exception as e:
            print(f"❌ Error: {e}")

    # Show session summary
    history = await agent.get_session_history(session_id)
    print("\n📊 Session Summary:")
    print(f"  Total messages: {len(history)}")
    print(f"  Session ID: {session_id}")


async def main():
    """Main function demonstrating basic agent capabilities."""

    print("🚀 Basic Agent Example")
    print("=" * 50)

    try:
        # 1. Run basic usage demonstration
        await demonstrate_basic_usage()

        # 2. Interactive chat (optional)
        print("\n" + "=" * 50)
        print("Would you like to try interactive chat? (y/n)")
        response = input().strip().lower()

        if response in ["y", "yes"]:
            await interactive_chat()
        else:
            print("✅ Basic example completed!")

    except Exception as e:
        print(f"❌ Error in main: {e}")


if __name__ == "__main__":
    asyncio.run(main())
