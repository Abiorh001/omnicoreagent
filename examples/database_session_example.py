#!/usr/bin/env python3
"""
Example usage of DatabaseSessionService for session and event management.

This example demonstrates:
1. Creating a database session service
2. Creating and managing sessions
3. Working with events
4. State management across different scopes (app, user, session)
"""

import asyncio
import time
from typing import Dict, Any

from mcpomni_connect.session.database_session import DatabaseSessionService
from mcpomni_connect.events.event import Event, EventActions
from mcpomni_connect.session._session_util import UserContent, AssistantContent


async def main():
    """Demonstrate DatabaseSessionService usage."""
    
    # 1. Initialize the database session service
    # Using SQLite for this example (file-based database)
    db_url = "sqlite:///./session_example.db"
    session_service = DatabaseSessionService(db_url)
    
    print("✅ Database session service initialized")
    
    # 2. Create a new session
    app_name = "mcp_omni_connect"
    user_id = "user123"
    
    # Create session with initial state
    initial_state = {
        "user:name": "John Doe",  # User-scoped state
        "app:version": "1.0.0",   # App-scoped state
        "session_id": "demo_session",  # Session-scoped state
        "temp:cache": "temporary_data"  # Temporary state (won't be persisted)
    }
    
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        state=initial_state
    )
    
    print(f"✅ Created session: {session.id}")
    print(f"   State keys: {list(session.state.keys())}")
    
    # 3. Create and append events
    print("\n📝 Adding events to session...")
    
    # User message event
    user_event = Event(
        invocation_id="inv_001",
        author="user",
        content=UserContent(text="Hello, can you help me with some tasks?"),
        actions=EventActions(
            state_delta={"last_user_message": "Hello, can you help me with some tasks?"}
        )
    )
    
    await session_service.append_event(session, user_event)
    print(f"   Added user event: {user_event.id[:8]}...")
    
    # Assistant response event
    assistant_event = Event(
        invocation_id="inv_002", 
        author="assistant",
        content=AssistantContent(text="Hello! I'd be happy to help you with your tasks. What do you need assistance with?"),
        actions=EventActions(
            state_delta={"last_assistant_message": "Hello! I'd be happy to help you with your tasks."}
        )
    )
    
    await session_service.append_event(session, assistant_event)
    print(f"   Added assistant event: {assistant_event.id[:8]}...")
    
    # 4. Retrieve the session and check events
    print("\n🔍 Retrieving session...")
    retrieved_session = await session_service.get_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session.id
    )
    
    if retrieved_session:
        print(f"   Session ID: {retrieved_session.id}")
        print(f"   Number of events: {len(retrieved_session.events)}")
        print(f"   State keys: {list(retrieved_session.state.keys())}")
        
        # Display events
        for i, event in enumerate(retrieved_session.events):
            print(f"   Event {i+1}: {event.author} - {event.content}")
    
    # 5. List all sessions for the user
    print("\n📋 Listing all sessions...")
    sessions_response = await session_service.list_sessions(
        app_name=app_name,
        user_id=user_id
    )
    
    print(f"   Found {len(sessions_response.sessions)} session(s):")
    for s in sessions_response.sessions:
        print(f"   - {s.id} (last updated: {s.last_update_time})")
    
    # 6. Create another session to demonstrate multi-session handling
    print("\n🆕 Creating second session...")
    session2 = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        state={"session_name": "Second Session", "app:version": "1.0.1"}
    )
    
    print(f"   Created second session: {session2.id}")
    
    # List sessions again
    sessions_response = await session_service.list_sessions(
        app_name=app_name,
        user_id=user_id
    )
    print(f"   Now have {len(sessions_response.sessions)} session(s)")
    
    # 7. Clean up - delete the sessions
    print("\n🧹 Cleaning up...")
    await session_service.delete_session(app_name, user_id, session.id)
    await session_service.delete_session(app_name, user_id, session2.id)
    
    print("   Deleted both sessions")
    
    # Verify cleanup
    sessions_response = await session_service.list_sessions(
        app_name=app_name,
        user_id=user_id
    )
    print(f"   Remaining sessions: {len(sessions_response.sessions)}")
    
    print("\n✨ Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main()) 