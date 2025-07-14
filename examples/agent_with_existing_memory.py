#!/usr/bin/env python3
"""
Agent with Existing Database Memory

This example shows how to build an agent using the existing DatabaseSessionMemory class.
"""

import asyncio
import os

from dotenv import load_dotenv

from mcpomni_connect.memory import DatabaseSessionMemory
from mcpomni_connect.client import Configuration, MCPClient
from mcpomni_connect.llm import LLMConnection
from mcpomni_connect.agents.react_agent import ReactAgent
from mcpomni_connect.agents.types import AgentConfig
from mcpomni_connect.system_prompts import generate_react_agent_prompt
from mcpomni_connect.constants import date_time_func
from mcpomni_connect.utils import logger


class AgentWithExistingMemory:
    """An agent that uses the existing DatabaseSessionMemory class."""

    def __init__(self, db_url: str = "sqlite:///agent_existing_memory.db"):
        """Initialize the agent with existing database memory."""
        self.db_memory = DatabaseSessionMemory(db_url=db_url, debug=True)
        self.config = Configuration()
        self.client = MCPClient(self.config)
        self.llm_connection = LLMConnection(self.config)

        # Agent configuration
        self.agent_config = AgentConfig(
            agent_name="existing_memory_agent",
            tool_call_timeout=30,
            max_steps=15,
            request_limit=100,
            total_tokens_limit=1000000,
        )

    async def initialize(self):
        """Initialize the agent and connect to servers."""
        try:
            await self.client.connect_to_servers()
            logger.info("Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise

    async def process_message(
        self, user_message: str, agent_name: str = "default"
    ) -> str:
        """Process a user message and return the agent's response."""
        try:
            # Store user message in database memory
            await self.db_memory.store_message(
                agent_name=agent_name,
                role="user",
                content=user_message,
                metadata={"message_type": "user_input"},
            )

            # Generate agent response using ReactAgent
            agent_response = await self._generate_agent_response(
                user_message, agent_name
            )

            # Store agent response in database memory
            await self.db_memory.store_message(
                agent_name=agent_name,
                role="assistant",
                content=agent_response,
                metadata={"message_type": "agent_response"},
            )

            return agent_response

        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"

    async def _generate_agent_response(self, user_message: str, agent_name: str) -> str:
        """Generate agent response using ReactAgent."""
        try:
            # Create ReactAgent
            react_agent = ReactAgent(config=self.agent_config)

            # Generate system prompt
            system_prompt = generate_react_agent_prompt(
                current_date_time=date_time_func["format_date"]()
            )

            # Get conversation history from database memory
            message_history = await self.db_memory.get_messages(agent_name=agent_name)

            # Convert message history to the format expected by ReactAgent
            formatted_history = []
            for msg in message_history:
                formatted_history.append(
                    {"role": msg["role"], "content": msg["content"]}
                )

            # Run agent
            async def add_message_to_history(role, content, metadata=None, **kwargs):
                if metadata is None:
                    metadata = {}
                await self.db_memory.store_message(
                    agent_name=agent_name, role=role, content=content, metadata=metadata
                )

            async def get_message_history(**kwargs):
                return formatted_history

            response = await react_agent._run(
                system_prompt=system_prompt,
                query=user_message,
                llm_connection=self.llm_connection,
                add_message_to_history=add_message_to_history,
                message_history=get_message_history,
                debug=True,
                sessions=self.client.sessions,
                available_tools=self.client.available_tools,
                session_id=self.db_memory.session_id,
            )

            # Ensure response is never None
            if response is None:
                response = "I apologize, but I was unable to generate a response. Please try again."

            return response

        except Exception as e:
            logger.error(f"Failed to generate agent response: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"

    async def get_conversation_history(self, agent_name: str = "default") -> list[dict]:
        """Get the conversation history for the specified agent."""
        try:
            messages = await self.db_memory.get_messages(agent_name=agent_name)
            return messages
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []

    async def clear_memory(self):
        """Clear the database memory."""
        try:
            await self.db_memory.clear_memory()
            logger.info("Memory cleared successfully")
        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")

    async def get_last_active(self):
        """Get the last active timestamp."""
        try:
            return await self.db_memory.get_last_active()
        except Exception as e:
            logger.error(f"Failed to get last active: {e}")
            return None


async def interactive_chat():
    """Interactive chat interface with existing database memory."""

    # Load environment variables
    load_dotenv()

    # Check for required environment variables
    if not os.getenv("LLM_API_KEY"):
        print("❌ LLM_API_KEY environment variable not found!")
        print("Please set it in your .env file:")
        print("LLM_API_KEY=your_api_key_here")
        return

    # Initialize agent
    agent = AgentWithExistingMemory()

    try:
        # Initialize agent
        await agent.initialize()

        print("🤖 Agent initialized with existing DatabaseSessionMemory")
        print(
            "💬 Start chatting! (type 'quit' to exit, 'history' to see conversation history, 'clear' to clear memory)"
        )
        print("-" * 50)

        # Interactive chat loop
        while True:
            try:
                user_input = input("You: ").strip()

                if user_input.lower() in ["quit", "exit", "bye"]:
                    print("👋 Goodbye!")
                    break

                if user_input.lower() == "history":
                    history = await agent.get_conversation_history()
                    print("\n📜 Conversation History:")
                    for entry in history[-10:]:  # Show last 10 messages
                        print(f"  {entry['role']}: {entry['content']}")
                    print()
                    continue

                if user_input.lower() == "clear":
                    await agent.clear_memory()
                    print("🧹 Memory cleared!")
                    continue

                if not user_input:
                    continue

                # Process message
                print("🤖 Agent is thinking...")
                response = await agent.process_message(user_input)
                print(f"Agent: {response}")
                print()

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                continue

    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")


async def example_usage():
    """Example showing how to use the agent programmatically."""

    # Initialize agent
    agent = AgentWithExistingMemory()

    try:
        # Initialize
        await agent.initialize()

        # Process some messages
        messages = [
            "Hello! How are you today?",
            "Can you help me with Python programming?",
            "What's the difference between a list and a tuple?",
            "Thank you for your help!",
        ]

        for message in messages:
            print(f"\nUser: {message}")
            response = await agent.process_message(message)
            print(f"Agent: {response}")

        # Get conversation history
        history = await agent.get_conversation_history()
        print(f"\n📊 Total messages in conversation: {len(history)}")

        # Get last active time
        last_active = await agent.get_last_active()
        if last_active:
            print(f"🕒 Last active: {last_active}")

    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Main function to run the examples."""
    print("Agent with Existing Database Memory Examples")
    print("=" * 50)

    # Run interactive chat
    print("🚀 Starting interactive chat...")
    await interactive_chat()


if __name__ == "__main__":
    asyncio.run(main())
