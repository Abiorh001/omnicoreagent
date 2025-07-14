#!/usr/bin/env python3
"""
Simple Agent with Database Memory

A simplified example showing how to build an agent with database memory.
"""

import asyncio
import uuid
from typing import Optional

from dotenv import load_dotenv

from mcpomni_connect.session.database_session import DatabaseSessionService
from mcpomni_connect.events.event import Event
from mcpomni_connect.session._session_util import UserContent, AssistantContent
from mcpomni_connect.utils import logger


class SimpleAgentWithMemory:
    """A simple agent that uses database memory for persistent conversations."""

    def __init__(self, db_url: str = "sqlite:///simple_agent_memory.db"):
        """Initialize the agent with database memory."""
        self.db_session_service = DatabaseSessionService(db_url=db_url)
        self.current_session = None

    async def start_conversation(
        self, app_name: str, user_id: str, session_id: Optional[str] = None
    ):
        """Start a new conversation or continue an existing one."""
        try:
            # Create or get existing session
            if session_id:
                self.current_session = await self.db_session_service.get_session(
                    app_name=app_name, user_id=user_id, session_id=session_id
                )
                if not self.current_session:
                    logger.warning(
                        f"Session {session_id} not found, creating new session"
                    )
                    session_id = None

            if not self.current_session:
                # Create new session
                session_id = session_id or f"session_{uuid.uuid4().hex[:8]}"
                self.current_session = await self.db_session_service.create_session(
                    app_name=app_name,
                    user_id=user_id,
                    session_id=session_id,
                    state={"conversation_count": 0},
                )
                logger.info(f"Created new session: {self.current_session.id}")
            else:
                logger.info(f"Continuing session: {self.current_session.id}")

            return self.current_session

        except Exception as e:
            logger.error(f"Failed to start conversation: {e}")
            raise

    async def process_message(self, user_message: str) -> str:
        """Process a user message and return a simple response."""
        try:
            if not self.current_session:
                raise ValueError("No active session. Call start_conversation() first.")

            # Create user event
            user_event = Event(
                id=f"event_{uuid.uuid4().hex[:8]}",
                invocation_id=f"inv_{uuid.uuid4().hex[:8]}",
                author="user",
                content=UserContent(text=user_message),
                timestamp=asyncio.get_event_loop().time(),
            )

            # Store user event in database
            await self.db_session_service.append_event(self.current_session, user_event)

            # Generate simple response
            agent_response = f"I received your message: '{user_message}'. This is a simple response from the agent with database memory."

            # Create assistant event
            assistant_event = Event(
                id=f"event_{uuid.uuid4().hex[:8]}",
                invocation_id=f"inv_{uuid.uuid4().hex[:8]}",
                author="assistant",
                content=AssistantContent(text=agent_response),
                timestamp=asyncio.get_event_loop().time(),
            )

            # Store assistant event in database
            await self.db_session_service.append_event(
                self.current_session, assistant_event
            )

            # Update conversation count
            self.current_session.state["conversation_count"] = (
                self.current_session.state.get("conversation_count", 0) + 1
            )

            return agent_response

        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"

    async def get_conversation_history(self) -> list[dict]:
        """Get the conversation history for the current session."""
        if not self.current_session:
            return []

        history = []
        for event in self.current_session.events:
            if event.content and hasattr(event.content, "text"):
                history.append(
                    {
                        "author": event.author,
                        "content": event.content.text,
                        "timestamp": event.timestamp,
                    }
                )

        return history

    async def close_session(self):
        """Close the current session."""
        self.current_session = None
        logger.info("Session closed")


async def interactive_chat():
    """Interactive chat interface with database memory."""

    # Load environment variables
    load_dotenv()

    # Initialize agent
    agent = SimpleAgentWithMemory()

    try:
        # Start conversation
        session = await agent.start_conversation(
            app_name="simple_chat", user_id="user_001"
        )

        print(f"🤖 Simple Agent initialized with session: {session.id}")
        print(f"📊 Conversation count: {session.state.get('conversation_count', 0)}")
        print(
            "💬 Start chatting! (type 'quit' to exit, 'history' to see conversation history)"
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
                        print(f"  {entry['author']}: {entry['content']}")
                    print()
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
    finally:
        await agent.close_session()


async def example_usage():
    """Example showing how to use the agent programmatically."""

    # Initialize agent
    agent = SimpleAgentWithMemory()

    try:
        # Start conversation
        session = await agent.start_conversation(
            app_name="example_app", user_id="user_001"
        )

        print(f"Session: {session.id}")

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

        # Close session
        await agent.close_session()

    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Main function to run the examples."""
    print("Simple Agent with Database Memory Examples")
    print("=" * 50)

    # Run interactive chat
    print("🚀 Starting interactive chat...")
    await interactive_chat()


if __name__ == "__main__":
    asyncio.run(main())
