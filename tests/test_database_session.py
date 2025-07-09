import pytest
import pytest_asyncio
import asyncio
from typing import Dict, Any

from mcpomni_connect.session.database_session import DatabaseSessionService
from mcpomni_connect.events.event import Event, EventActions
from mcpomni_connect.session._session_util import UserContent


@pytest_asyncio.fixture
async def session_service():
    """Create a test database session service using in-memory SQLite."""
    db_url = "sqlite:///:memory:"
    service = DatabaseSessionService(db_url)
    return service


@pytest.mark.asyncio
async def test_create_session(session_service):
    """Test creating a new session."""
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user",
        state={"test_key": "test_value"}
    )
    
    assert session.app_name == "test_app"
    assert session.user_id == "test_user"
    assert session.id is not None
    assert "test_key" in session.state
    assert session.state["test_key"] == "test_value"


@pytest.mark.asyncio
async def test_get_session(session_service):
    """Test retrieving a session."""
    # Create a session
    created_session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user",
        state={"initial": "data"}
    )
    
    # Retrieve the session
    retrieved_session = await session_service.get_session(
        app_name="test_app",
        user_id="test_user",
        session_id=created_session.id
    )
    
    assert retrieved_session is not None
    assert retrieved_session.id == created_session.id
    assert retrieved_session.app_name == "test_app"
    assert retrieved_session.user_id == "test_user"


@pytest.mark.asyncio
async def test_append_event(session_service):
    """Test adding events to a session."""
    # Create a session
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    # Create an event
    event = Event(
        invocation_id="test_invocation",
        author="test_user",
        content=UserContent(text="Hello test"),
        actions=EventActions(state_delta={"message_count": 1})
    )
    
    # Append the event
    result_event = await session_service.append_event(session, event)
    
    assert result_event.id == event.id
    assert result_event.author == "test_user"
    
    # Retrieve session and check event was added
    updated_session = await session_service.get_session(
        app_name="test_app",
        user_id="test_user", 
        session_id=session.id
    )
    
    assert len(updated_session.events) == 1
    assert updated_session.events[0].author == "test_user"


@pytest.mark.asyncio
async def test_list_sessions(session_service):
    """Test listing sessions for a user."""
    # Create multiple sessions
    session1 = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    session2 = await session_service.create_session(
        app_name="test_app", 
        user_id="test_user"
    )
    
    # List sessions
    response = await session_service.list_sessions(
        app_name="test_app",
        user_id="test_user"
    )
    
    assert len(response.sessions) == 2
    session_ids = [s.id for s in response.sessions]
    assert session1.id in session_ids
    assert session2.id in session_ids


@pytest.mark.asyncio
async def test_delete_session(session_service):
    """Test deleting a session."""
    # Create a session
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    # Verify it exists
    retrieved = await session_service.get_session(
        app_name="test_app",
        user_id="test_user",
        session_id=session.id
    )
    assert retrieved is not None
    
    # Delete the session
    await session_service.delete_session(
        app_name="test_app",
        user_id="test_user",
        session_id=session.id
    )
    
    # Verify it's deleted
    deleted_session = await session_service.get_session(
        app_name="test_app",
        user_id="test_user",
        session_id=session.id
    )
    assert deleted_session is None


@pytest.mark.asyncio 
async def test_state_management(session_service):
    """Test app, user, and session state management."""
    # Create session with different state scopes
    initial_state = {
        "app:global_setting": "value1",
        "user:preference": "value2", 
        "session_data": "value3",
        "temp:cache": "temporary"
    }
    
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user",
        state=initial_state
    )
    
    # The temp: prefixed state should not be persisted in the merged state
    # but app: and user: prefixed states should be managed separately
    assert "app:global_setting" in session.state
    assert "user:preference" in session.state
    assert "session_data" in session.state
    # temp: data is not persisted in final state
    assert "temp:cache" not in session.state 