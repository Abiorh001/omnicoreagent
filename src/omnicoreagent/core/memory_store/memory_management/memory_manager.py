import uuid
from datetime import datetime, timezone
from typing import List, Any, Callable, Optional, Tuple
from omnicoreagent.core.utils import (
    logger,
    is_vector_db_enabled,
    is_embedding_requirements_met,
    json_to_smooth_text,
    strip_comprehensive_narrative,
)
from decouple import config
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from omnicoreagent.core.memory_store.memory_management.system_prompts import (
    episodic_memory_constructor_system_prompt,
    long_term_memory_constructor_system_prompt,
)
from omnicoreagent.core.memory_store.memory_management.base_vectordb_handler import (
    BaseVectorDBHandler,
)

# Cache for recent summaries
_RECENT_SUMMARY_CACHE = {}
_CACHE_TTL = 1800  # 30 minutes TTL
_CACHE_LOCK = threading.RLock()


# Thread pool for background processing
_THREAD_POOL = None


def _initialize_memory_system():
    """Initialize the memory system only when vector DB is enabled."""
    global _THREAD_POOL

    if not is_vector_db_enabled():
        logger.debug("Vector database disabled - skipping memory system initialization")
        return

    # Create thread pool
    _THREAD_POOL = ThreadPoolExecutor(
        max_workers=4, thread_name_prefix="MemoryProcessor"
    )
    logger.debug("Memory system initialized with thread pool")


_initialize_memory_system()


class MemoryManager(BaseVectorDBHandler):
    """Memory management operations ."""

    def __init__(
        self,
        agent_name: str,
        memory_type: str,
        is_background: bool = False,
        llm_connection: Callable = None,
    ):
        """Initialize memory manager with automatic backend selection.

        Args:
            agent_name: Name of the agent
            memory_type: Type of memory (episodic, long_term)
            is_background: Whether this is for background processing
            llm_connection: LLM connection for embeddings (optional)
        """

        # self.agent_name = agent_name
        # self.memory_type = memory_type
        # self.is_background = is_background
        # self.llm_connection = llm_connection

        # self.collection_name = collection_name

        collection_name = f"{agent_name}_{memory_type}"
        # initialize vector DB
        super().__init__(
            collection_name=collection_name,
            memory_type=memory_type,
            llm_connection=llm_connection,
            is_background=is_background,
        )
        self.agent_name = agent_name

        # # Check if vector database is enabled
        # if not is_vector_db_enabled():
        #     logger.debug("Vector database is disabled by configuration")
        #     self.vector_db = None
        #     return

        # # Check if embedding requirements are met
        # if not is_embedding_requirements_met():
        #     logger.error(
        #         "Vector database is enabled but no embedding API key is set. Please set EMBEDDING_API_KEY environment variable."
        #     )
        #     self.vector_db = None
        #     return

        # # Verify LLM connection is provided
        # if not self.llm_connection:
        #     logger.error(
        #         "LLM connection is required for vector database operations. Please provide llm_connection parameter."
        #     )
        #     self.vector_db = None
        #     return

        # logger.debug(
        #     "Embedding requirements met - using LLM-based embeddings via LiteLLM"
        # )

        # # Determine provider from config
        # provider = config("OMNI_MEMORY_PROVIDER", default=None)
        # if not provider:
        #     logger.error("OMNI_MEMORY_PROVIDER is not set in the environment")
        #     self.vector_db = None
        #     return

        # provider = provider.lower()

        # if provider == "qdrant-remote":
        #     try:
        #         # Import QdrantVectorDB when needed
        #         from omnicoreagent.core.memory_store.memory_management.qdrant_vector_db import (
        #             QdrantVectorDB,
        #         )

        #         self.vector_db = QdrantVectorDB(
        #             self.collection_name,
        #             memory_type=memory_type,
        #             is_background=self.is_background,
        #             llm_connection=self.llm_connection,
        #         )
        #         if self.vector_db.enabled:
        #             logger.debug(f"Using Qdrant for {memory_type} memory")
        #             return
        #         else:
        #             logger.warning("Qdrant not enabled")
        #     except Exception as e:
        #         logger.warning(f"Failed to initialize Qdrant (remote): {e}")

        # elif provider == "mongodb-remote":
        #     try:
        #         # Import MongoDBVectorDB when needed
        #         from omnicoreagent.core.memory_store.memory_management.mongodb_vector_db import (
        #             MongoDBVectorDB,
        #         )

        #         self.vector_db = MongoDBVectorDB(
        #             self.collection_name,
        #             memory_type=memory_type,
        #             is_background=self.is_background,
        #             llm_connection=self.llm_connection,
        #         )
        #         if self.vector_db.enabled:
        #             logger.debug(f"Using MongoDB for {memory_type} memory")
        #             return
        #         else:
        #             logger.warning("MongoDB not enabled")
        #     except Exception as e:
        #         logger.warning(f"Failed to initialize MongoDB (remote): {e}")

        # elif provider.startswith("chroma"):
        #     try:
        #         # Import ChromaDBVectorDB when needed
        #         from omnicoreagent.core.memory_store.memory_management.chromadb_vector_db import (
        #             ChromaDBVectorDB,
        #         )

        #         # Determine client type from provider
        #         if provider == "chroma-remote":
        #             client_type = "remote"
        #         elif provider == "chroma-cloud":
        #             client_type = "cloud"
        #         else:
        #             logger.error(f"Invalid ChromaDB provider: {provider}")
        #             raise RuntimeError(f"Invalid ChromaDB provider: {provider}")

        #         self.vector_db = ChromaDBVectorDB(
        #             self.collection_name,
        #             memory_type=memory_type,
        #             client_type=client_type,
        #             llm_connection=self.llm_connection,
        #         )
        #         if self.vector_db.enabled:
        #             logger.debug(
        #                 f"Using ChromaDB ({client_type}) for {memory_type} memory"
        #             )
        #             return
        #         else:
        #             logger.warning(f"ChromaDB ({client_type}) not enabled")
        #     except Exception as e:
        #         logger.warning(f"Failed to initialize ChromaDB ({client_type}): {e}")

        # logger.warning(
        #     f"Vector database provider '{provider}' failed - vector DB disabled"
        # )
        # self.vector_db = None

    async def create_episodic_memory(
        self, message: str, llm_connection: Callable
    ) -> Optional[str]:
        """Create an episodic memory from a conversation."""
        try:
            llm_messages = [
                {
                    "role": "system",
                    "content": episodic_memory_constructor_system_prompt,
                },
                {"role": "user", "content": message},
            ]

            # Use sync llm call for memory processing
            response = llm_connection.llm_call_sync(llm_messages)
            if response and response.choices:
                content = response.choices[0].message.content

                content = json_to_smooth_text(content=content)
                return content
            else:
                return None
        except Exception:
            return None

    async def create_long_term_memory(
        self, message: str, llm_connection: Callable
    ) -> Optional[str]:
        """Create a long-term memory from a conversation."""
        try:
            llm_messages = [
                {
                    "role": "system",
                    "content": long_term_memory_constructor_system_prompt,
                },
                {"role": "user", "content": message},
            ]

            response = llm_connection.llm_call_sync(llm_messages)

            if response and response.choices:
                content = response.choices[0].message.content
                content = strip_comprehensive_narrative(text=content)
                return content
            else:
                return None
        except Exception:
            return None

    def _format_conversation(self, messages: List[Any]) -> str:
        """Format conversation messages into a single text string."""
        formatted_messages = []
        for msg in messages:
            if hasattr(msg, "role") and hasattr(msg, "content"):
                # Pydantic model
                role = msg.role
                content = msg.content
                timestamp = getattr(msg, "timestamp", "")
                metadata = getattr(msg, "metadata", None)
            elif isinstance(msg, dict):
                # Dict fallback
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                timestamp = msg.get("timestamp", "")
                metadata = msg.get("metadata", None)
            else:
                continue
            meta_str = f" | metadata: {metadata}" if metadata else ""
            formatted_messages.append(f"[{timestamp}] {role}: {content}{meta_str}")
        return "\n".join(formatted_messages)

    def parse_iso_to_datetime(self, timestamp_str: str) -> Optional[datetime]:
        """
        Convert an ISO 8601 timestamp string to a UTC datetime object.
        """
        if not timestamp_str:
            return None
        if timestamp_str.endswith("Z"):
            timestamp_str = timestamp_str[:-1] + "+00:00"
        dt = datetime.fromisoformat(timestamp_str)

        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    async def get_last_procced_messages_timestamp(
        self, get_last_processed_messages: Callable, session_id: str
    ) -> Optional[datetime]:
        """Get the last processed messages timestamp"""
        if not self.vector_db or not self.vector_db.enabled:
            return None

        cache_key = (self.collection_name, self.memory_type, session_id)
        now = datetime.now(timezone.utc)

        # Check cache with TTL validation (thread-safe)
        with _CACHE_LOCK:
            cached = _RECENT_SUMMARY_CACHE.get(cache_key)
            logger.debug(
                f"Cache check for {self.memory_type}: {'HIT' if cached else 'MISS'}"
            )
            if cached:
                cached_last_timestamp, cached_time = cached
                cache_age = (now - cached_time).total_seconds()
                if cache_age < _CACHE_TTL:
                    logger.debug(
                        f"CACHE HIT for {self.memory_type} (age: {int(cache_age)}s, TTL: {_CACHE_TTL}s)"
                    )
                    if cached_last_timestamp:
                        return cached_last_timestamp
                else:
                    # Invalidate expired cache
                    del _RECENT_SUMMARY_CACHE[cache_key]
            else:
                logger.debug(f"No cache entry found for {self.memory_type}")

        try:
            last_timestamp_str = await get_last_processed_messages(
                session_id=session_id,
                agent_name=self.agent_name,
                memory_type=self.memory_type,
            )

            logger.debug(f"current last procced timestamp: {last_timestamp_str}")

            last_timestamp = None
            if last_timestamp_str:
                try:
                    last_timestamp = self.parse_iso_to_datetime(last_timestamp_str)
                except Exception as e:
                    logger.warning(f"Failed to parse last timestamp: Error: {e}")

            if not last_timestamp:
                with _CACHE_LOCK:
                    _RECENT_SUMMARY_CACHE[cache_key] = (None, now)
                return None

            # set the retrieved timestamp in cache
            with _CACHE_LOCK:
                _RECENT_SUMMARY_CACHE[cache_key] = (last_timestamp, now)
            return last_timestamp

        except Exception as e:
            logger.error(f"Error fetching most recent procced message timestamp: {e}")
            with _CACHE_LOCK:
                _RECENT_SUMMARY_CACHE[cache_key] = (None, now)
            return None

    def get_last_message_timestamp(self, messages: list) -> datetime:
        """
        Get the latest message timestamp (ISO format) from a list of messages.
        If no valid timestamps exist, return the current UTC time in ISO format.
        """
        valid_datetimes = []

        for m in messages:
            if hasattr(m, "timestamp") and m.timestamp is not None:
                try:
                    dt = self.parse_iso_to_datetime(timestamp_str=m.timestamp)
                    valid_datetimes.append(dt)
                except Exception:
                    continue

        if valid_datetimes:
            latest = max(valid_datetimes)
            return latest
        else:
            return datetime.now(timezone.utc)

    async def process_conversation_memory(
        self,
        session_id: str,
        messages: list,
        add_last_processed_messages: Callable,
        get_last_processed_messages: Callable,
        llm_connection: Callable,
    ):
        """Process conversation memory only if cache TTL has passed since last summary."""
        if not self.vector_db or not self.vector_db.enabled:
            logger.debug(
                f"Vector database is not enabled. Skipping memory operation for {self.memory_type}."
            )
            return

        try:
            # Ensure collection exists
            self.vector_db._ensure_collection()

            # Get last time we process the message for memory
            last_timestamp = await self.get_last_procced_messages_timestamp(
                get_last_processed_messages=get_last_processed_messages,
                session_id=session_id,
            )
            # get the last message stored in the messages
            latest_timestamp_datetime = self.get_last_message_timestamp(
                messages=messages
            )
            # Only proceed if at least cache TTL has passed since last summary
            if last_timestamp is None:
                logger.debug(
                    "No previous memory summary found, proceeding with all messages"
                )
            else:
                time_diff_seconds = (
                    latest_timestamp_datetime - last_timestamp
                ).total_seconds()
                logger.debug(
                    f"Time since last {self.memory_type} memory summary: {int(time_diff_seconds)} seconds"
                )

                if time_diff_seconds < _CACHE_TTL:
                    logger.debug(
                        f"Last {self.memory_type} memory summary was {int(time_diff_seconds)} seconds ago, which is less than the cache TTL of {_CACHE_TTL} seconds. Skipping summarization."
                    )
                    return

            # Filter messages after last_end_time
            if last_timestamp:
                messages_to_summarize = []
                # count lenght of message first before filter
                message_recieved = len(messages)
                logger.debug(
                    f"Total messages received: {message_recieved} since last summary at {last_timestamp.isoformat()}"
                )

                for m in messages:
                    msg_datetime = self.parse_iso_to_datetime(
                        timestamp_str=getattr(m, "timestamp")
                    )
                    if not msg_datetime:
                        continue
                    if msg_datetime > last_timestamp:
                        logger.debug(
                            f"Message to summarize timestamp: {msg_datetime}, last_timestamp: {last_timestamp}"
                        )
                        messages_to_summarize.append(m)
                logger.debug(
                    f"Messages to summarize after filtering the timestamp: {len(messages_to_summarize)}"
                )

            else:
                messages_to_summarize = messages

            if not messages_to_summarize:
                return
            # count message to ensure min is 15 before summarizing or return
            if len(messages_to_summarize) < 15:
                logger.debug(
                    f"Only {len(messages_to_summarize)} new messages since last summary, skipping summarization"
                )
                return
            # Summarize and store
            conversation_text = self._format_conversation(messages_to_summarize)

            if self.memory_type == "episodic":
                memory_content = await self.create_episodic_memory(
                    conversation_text, llm_connection
                )
            elif self.memory_type == "long_term":
                memory_content = await self.create_long_term_memory(
                    conversation_text, llm_connection
                )
            else:
                return

            if not memory_content or memory_content.strip() == "":
                return

            doc_id = str(uuid.uuid4())

            self.vector_db.add_to_collection(
                document=memory_content,
                metadata={
                    "session_id": session_id,
                    "memory_type": self.memory_type,
                    "timestamp": latest_timestamp_datetime.isoformat(),
                    "message_count": len(messages_to_summarize),
                    "agent_name": self.agent_name,
                },
                doc_id=doc_id,
            )

            logger.debug(f"Successfully stored memory document with ID: {doc_id}")
            # Update last processed message timestamp
            await add_last_processed_messages(
                session_id=session_id,
                agent_name=self.agent_name,
                timestamp=latest_timestamp_datetime.isoformat(),
                memory_type=self.memory_type,
            )

            with _CACHE_LOCK:
                _RECENT_SUMMARY_CACHE[
                    (self.collection_name, self.memory_type, session_id)
                ] = (
                    latest_timestamp_datetime,
                    datetime.now(timezone.utc),
                )

        except Exception:
            pass  # Silent background processing

    def query_memory(
        self,
        query: str,
        n_results: int,
        similarity_threshold: float,
        session_id: str = None,
        mcp_server_names: list[str] = None,
    ) -> List[str]:
        """Query memory for relevant information."""

        if not self.vector_db or not self.vector_db.enabled:
            return []

        try:
            results = self.vector_db.query_collection(
                query=query,
                session_id=session_id,
                mcp_server_names=mcp_server_names,
                n_results=n_results,
                similarity_threshold=similarity_threshold,
            )

            # logger.info(f"QUERY RESULTS HERE: {results}")
            if isinstance(results, dict) and "documents" in results:
                documents = results["documents"]
                return documents
            elif isinstance(results, list):
                return results
            else:
                return []
        except Exception as e:
            logger.error(f"Error querying {self.memory_type} memory: {e}")
            return []


class MemoryManagerFactory:
    """Factory for creating memory managers."""

    @staticmethod
    def create_both_memory_managers(
        agent_name: str,
        llm_connection: Callable = None,
    ) -> Tuple[Optional[MemoryManager], Optional[MemoryManager]]:
        """Create both episodic and long-term memory managers."""
        if not is_vector_db_enabled():
            logger.debug("Vector database disabled - skipping memory manager creation")
            return None, None
        episodic = MemoryManager(
            agent_name=agent_name, memory_type="episodic", llm_connection=llm_connection
        )
        long_term = MemoryManager(
            agent_name=agent_name,
            memory_type="long_term",
            llm_connection=llm_connection,
        )
        return episodic, long_term


def cleanup_memory_system():
    """Cleanup function to properly shutdown thread pool and clear cache."""
    logger.debug("Cleaning up memory management system")

    # Shutdown thread pool gracefully
    if _THREAD_POOL:
        _THREAD_POOL.shutdown(wait=True)

    # Clear cache
    with _CACHE_LOCK:
        _RECENT_SUMMARY_CACHE.clear()

    logger.debug("Memory system cleanup complete")
