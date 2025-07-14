import abc
from typing import Any
from typing import Optional

from pydantic import BaseModel, Field

from ..events.event import Event
from .session import Session
from .state import State


class GetSessionConfig(BaseModel):
    """The configuration of getting a session."""

    num_recent_events: Optional[int] = None
    after_timestamp: Optional[float] = None


class ListSessionsResponse(BaseModel):
    """The response of listing sessions.

    The events and states are not set within each Session object.
    """

    sessions: list[Session] = Field(default_factory=list)


class BaseSessionService(abc.ABC):
    """Base class for session services.

    The service provides a set of methods for managing sessions and events.
    """

    @abc.abstractmethod
    async def create_session(
        self,
        *,
        app_name: str,
        user_id: str,
        state: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Session:
        """Creates a new session.

        Args:
            app_name: the name of the app.
            user_id: the id of the user.
            state: the initial state of the session.
            session_id: the client-provided id of the session. If not provided, a
                generated ID will be used.

        Returns:
            session: The newly created session instance.
        """

    @abc.abstractmethod
    async def get_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        config: Optional[GetSessionConfig] = None,
    ) -> Optional[Session]:
        """Gets a session."""

    @abc.abstractmethod
    async def list_sessions(
        self, *, app_name: str, user_id: str
    ) -> ListSessionsResponse:
        """Lists all the sessions."""

    @abc.abstractmethod
    async def delete_session(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> None:
        """Deletes a session."""

    async def append_event(self, session: Session, event: Event) -> Event:
        """Appends an event to a session object."""
        if event.partial:
            return event
        self._BaseSessionService__update_session_state(session, event)
        session.events.append(event)
        return event

    def _BaseSessionService__update_session_state(
        self, session: Session, event: Event
    ) -> None:
        """Updates the session state based on the event."""
        if not event.actions or not event.actions.state_delta:
            return
        for key, value in event.actions.state_delta.items():
            if key.startswith(State.TEMP_PREFIX):
                continue
            session.state.update({key: value})
