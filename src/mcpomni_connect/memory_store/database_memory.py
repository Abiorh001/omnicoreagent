import asyncio
from mcpomni_connect.memory_store.base import AbstractMemoryStore
from mcpomni_connect.session.database_session import DatabaseSessionService
from mcpomni_connect.events.event import Event,EventContent
import time


class DatabaseMemory(AbstractMemoryStore):
    def __init__(self, db_url: str, session_id: str = None, app_name: str = None, user_id: str = None):
        """
        Initialize the database memory store and set up the database session service.
        If a session_id is provided, attempts to retrieve the session; otherwise, active_session is None.
        """
        self.db_url = db_url
        self.db_session = DatabaseSessionService(db_url=db_url)
        self.active_session = asyncio.run(
            self.db_session.get_session(session_id=session_id, app_name=app_name, user_id=user_id)
        )
        self.memory_config = {
            "mode": "sliding_window",
            "value": 10000
        }

    def set_memory_config(self, mode: str, value: int = None) -> None:
        """
        Placeholder for setting memory configuration (not implemented).
        """
        self.memory_config["mode"] = mode
        self.memory_config["value"] = value

    async def store_message(self, role: str, content,metadata: dict | None = None, session_id: str = None, app_name: str = None, user_id: str = None) -> None:
        """
        Store a message as an Event in the database for the current or newly created session.
        If no active session exists, create one first.
        """
        if not self.active_session:
            # Create a new session if one does not exist
            self.active_session = await self.db_session.create_session(app_name=app_name, user_id=user_id)
        # Store the event in the database
        await self.db_session.append_event(
            session=self.active_session, 
            event=Event(author=role, content=content, invocation_id=session_id, timestamp=time.time())
        )

    async def get_messages(self, user_id: str = None, app_name: str = None, session_id: str = None):
        """
        Retrieve all events/messages for a given session from the database.
        If session_id is not provided, use the active session's ID.
        Returns a list of Event objects (or an empty list if no session is found).
        """
        if not self.active_session:
            # Create a new session if one does not exist
            self.active_session = await self.db_session.create_session(app_name=app_name, user_id=user_id)
        sid = session_id or self.active_session.id
        session = await self.db_session.get_session(session_id=sid, app_name=app_name, user_id=user_id)
        events = session.events if session else []
        mode = self.memory_config.get("mode", "token_budget")
        value = self.memory_config.get("value")
        if mode.lower() == "sliding_window" and value is not None:
            events = events[-value:]
        elif mode.lower() == "token_budget" and value is not None:
            total_tokens = sum(len(str(event.content).split()) for event in events)
            while total_tokens > value and events:
                events.pop(0)
                total_tokens = sum(len(str(event.content).split()) for event in events)
        return events


    async def clear_memory(self, user_id: str = None, app_name: str = None, session_id: str = None) -> None:
        """
        Delete a session and all its events from the database.
        If session_id is not provided, deletes the active session and resets it to None.
        """
        sid = session_id or (self.active_session.id if self.active_session else None)
        if sid:
            await self.db_session.delete_session(session_id=sid, app_name=app_name, user_id=user_id)
            if not session_id:
                # Reset the active session if we deleted it
                self.active_session = None


