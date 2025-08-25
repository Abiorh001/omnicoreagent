import json
from datetime import datetime, timezone
from typing import Any
import uuid
from sqlalchemy import String, Text, DateTime, create_engine, func, inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.types import TypeDecorator
from sqlalchemy.ext.mutable import MutableDict
from mcpomni_connect.utils import logger, utc_now_str

DEFAULT_MAX_KEY_LENGTH = 128
DEFAULT_MAX_VARCHAR_LENGTH = 256


class DynamicJSON(TypeDecorator):
    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return value


class Base(DeclarativeBase):
    pass


class StorageMessage(Base):
    __tablename__ = "messages"
    id: Mapped[str] = mapped_column(
        String(DEFAULT_MAX_KEY_LENGTH),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    session_id: Mapped[str] = mapped_column(String(DEFAULT_MAX_KEY_LENGTH))
    role: Mapped[str] = mapped_column(String(DEFAULT_MAX_VARCHAR_LENGTH))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # ISO 8601 string for portability
    timestamp: Mapped[str] = mapped_column(
        String(50), default=lambda: datetime.now(timezone.utc).isoformat()
    )
    msg_metadata: Mapped[dict[str, Any]] = mapped_column(
        MutableDict.as_mutable(DynamicJSON), default={}
    )


class LastProcessedMessage(Base):
    __tablename__ = "last_processed_messages"
    id: Mapped[str] = mapped_column(
        String(DEFAULT_MAX_KEY_LENGTH),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    session_id: Mapped[str] = mapped_column(String(DEFAULT_MAX_KEY_LENGTH))
    agent_name: Mapped[str] = mapped_column(String(DEFAULT_MAX_VARCHAR_LENGTH))
    memory_type: Mapped[str] = mapped_column(String(DEFAULT_MAX_VARCHAR_LENGTH))
    timestamp: Mapped[str] = mapped_column()
    last_processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class DatabaseMessageStore:
    """
    Database-backed message store for storing, retrieving, and clearing messages by session.
    """

    def __init__(self, db_url: str, **kwargs: Any):
        try:
            db_engine = create_engine(db_url, **kwargs)
        except Exception as e:
            raise ValueError(
                f"Failed to create database engine for URL '{db_url}'"
            ) from e
        self.db_engine = db_engine
        self.database_session_factory = sessionmaker(bind=self.db_engine)

        # Check if tables exist before creating them
        inspector = inspect(self.db_engine)
        existing_tables = inspector.get_table_names()

        if (
            "messages" not in existing_tables
            or "last_processed_messages" not in existing_tables
        ):
            Base.metadata.create_all(self.db_engine)

        self.memory_config: dict[str, Any] = {}

    def set_memory_config(self, mode: str, value: int = None) -> None:
        valid_modes = {"sliding_window", "token_budget"}
        if mode.lower() not in valid_modes:
            raise ValueError(
                f"Invalid memory mode: {mode}. Must be one of {valid_modes}."
            )
        self.memory_config = {"mode": mode, "value": value}

    async def store_message(
        self,
        role: str,
        content: str,
        metadata: dict | None = None,
        session_id: str = None,
    ) -> None:
        try:
            if metadata is None:
                metadata = {}
            with self.database_session_factory() as session_factory:
                message = StorageMessage(
                    session_id=session_id,
                    role=role,
                    content=content,
                    msg_metadata=metadata,
                )
                session_factory.add(message)
                session_factory.commit()
        except Exception as e:
            logger.error(f"Failed to store message: {e}")

    async def get_messages(
        self, session_id: str = None, agent_name: str | None = None
    ) -> list[dict[str, Any]]:
        logger.info(f"get memory config: {self.memory_config}")
        try:
            with self.database_session_factory() as session_factory:
                query = session_factory.query(StorageMessage).filter(
                    StorageMessage.session_id == session_id
                )
                messages = query.order_by(StorageMessage.timestamp.asc()).all()
                result = [
                    {
                        "role": m.role,
                        "content": m.content,
                        "session_id": m.session_id,
                        "timestamp": m.timestamp.timestamp()
                        if isinstance(m.timestamp, datetime)
                        else m.timestamp,
                        "msg_metadata": m.msg_metadata,
                    }
                    for  m in messages
                ]
                mode = self.memory_config.get("mode", "token_budget")
                value = self.memory_config.get("value")
                if mode.lower() == "sliding_window" and value is not None:
                    result = result[-value:]
                elif mode.lower() == "token_budget" and value is not None:
                    total_tokens = sum(
                        len(str(msg["content"]).split()) for msg in result
                    )
                    while total_tokens > value and result:
                        result.pop(0)
                        total_tokens = sum(
                            len(str(msg["content"]).split()) for msg in result
                        )
                if agent_name:
                    result = [
                        msg
                        for msg in result
                        if msg["msg_metadata"].get("agent_name") == agent_name
                    ]
                return result
        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            return []

    async def set_last_processed_messages(
        self, session_id: str, agent_name: str, timestamp: float, memory_type: str
    ) -> None:
        try:
            with self.database_session_factory() as session_factory:
                existing = (
                    session_factory.query(LastProcessedMessage)
                    .filter(
                        LastProcessedMessage.session_id == session_id,
                        LastProcessedMessage.agent_name == agent_name,
                        LastProcessedMessage.memory_type == memory_type,
                    )
                    .first()
                )
                if existing:
                    existing.agent_name = agent_name
                    existing.memory_type = memory_type
                    existing.timestamp = timestamp
                else:
                    new_entry = LastProcessedMessage(
                        session_id=session_id,
                        agent_name=agent_name,
                        memory_type=memory_type,
                        timestamp=timestamp,
                    )
                    session_factory.add(new_entry)
                session_factory.commit()
        except Exception as e:
            logger.error(f"Failed to set last processed: {e}")

    async def get_last_processed_messages(
        self, session_id: str, agent_name: str, memory_type: str
    ) -> Any:
        try:
            with self.database_session_factory() as session_factory:
                entry = (
                    session_factory.query(LastProcessedMessage)
                    .filter(
                        LastProcessedMessage.session_id == session_id,
                        LastProcessedMessage.agent_name == agent_name,
                        LastProcessedMessage.memory_type == memory_type,
                    )
                    .first()
                )
                if entry:
                    return entry.timestamp
                return None
        except Exception as e:
            logger.error(f"Failed to get last processed: {e}")
            return None

    async def clear_memory(
        self, session_id: str = None, agent_name: str = None
    ) -> None:
        try:
            with self.database_session_factory() as session_factory:
                if session_id and agent_name:
                    # Clear messages for specific agent in specific session
                    query = session_factory.query(StorageMessage).filter(
                        StorageMessage.session_id == session_id,
                        StorageMessage.msg_metadata.contains(
                            {"agent_name": agent_name}
                        ),
                    )
                    query.delete()
                elif session_id:
                    # Clear all messages for specific session
                    query = session_factory.query(StorageMessage).filter(
                        StorageMessage.session_id == session_id
                    )
                    query.delete()
                elif agent_name:
                    # Clear messages for specific agent across all sessions
                    query = session_factory.query(StorageMessage).filter(
                        StorageMessage.msg_metadata.contains({"agent_name": agent_name})
                    )
                    query.delete()
                else:
                    # Clear all messages
                    session_factory.query(StorageMessage).delete()
                session_factory.commit()
        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")
