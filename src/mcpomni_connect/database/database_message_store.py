# File content already correct after previous rename and class update. from __future__ import annotations
import json
import logging
from datetime import datetime
from typing import Any
import uuid
from sqlalchemy import String, Text, DateTime, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.types import TypeDecorator
from sqlalchemy.ext.mutable import MutableDict

logger = logging.getLogger("mcpomni_connect." + __name__)

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
    timestamp: Mapped[float] = mapped_column(DateTime(), default=func.now())
    metadata: Mapped[dict[str, Any]] = mapped_column(
        MutableDict.as_mutable(DynamicJSON), default={}
    )


class DatabaseMessageStore:
    """
    Database-backed message store for storing, retrieving, and clearing messages by session and agent.
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
        Base.metadata.drop_all(self.db_engine)
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
                    timestamp=datetime.now(),
                    metadata=metadata,
                )
                session_factory.add(message)
                session_factory.commit()
        except Exception as e:
            logger.error(f"Failed to store message: {e}")

    async def get_messages(
        self, session_id: str = None, agent_name: str = None
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
                        "metadata": m.metadata,
                    }
                    for m in messages
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

                    def _get_agent_name_from_metadata(metadata):
                        if not metadata:
                            return None
                        if hasattr(metadata, "agent_name"):
                            return metadata.agent_name
                        if isinstance(metadata, dict):
                            return metadata.get("agent_name")
                        return None

                    result = [
                        msg
                        for msg in result
                        if _get_agent_name_from_metadata(msg.get("metadata"))
                        == agent_name
                    ]
                return result
        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            return []

    async def clear_memory(
        self, session_id: str = None, agent_name: str = None
    ) -> None:
        try:
            with self.database_session_factory() as session_factory:
                if session_id:
                    query = session_factory.query(StorageMessage).filter(
                        StorageMessage.session_id == session_id
                    )
                    if agent_name:
                        messages = query.all()
                        to_delete = [
                            m.id
                            for m in messages
                            if self._get_agent_name_from_metadata(m.metadata)
                            == agent_name
                        ]
                        for msg_id in to_delete:
                            session_factory.query(StorageMessage).filter(
                                StorageMessage.id == msg_id
                            ).delete()
                    else:
                        query.delete()
                elif agent_name:
                    messages = session_factory.query(StorageMessage).all()
                    to_delete = [
                        m.id
                        for m in messages
                        if self._get_agent_name_from_metadata(m.metadata) == agent_name
                    ]
                    for msg_id in to_delete:
                        session_factory.query(StorageMessage).filter(
                            StorageMessage.id == msg_id
                        ).delete()
                else:
                    session_factory.query(StorageMessage).delete()
                session_factory.commit()
        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")

    def _get_agent_name_from_metadata(self, metadata) -> str:
        if not metadata:
            return None
        if hasattr(metadata, "agent_name"):
            return metadata.agent_name
        if isinstance(metadata, dict):
            return metadata.get("agent_name")
        return None
