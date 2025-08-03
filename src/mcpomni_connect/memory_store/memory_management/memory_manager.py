import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Callable, Optional, Tuple
from mcpomni_connect.utils import logger
from decouple import config
import time
import asyncio
import logging
import traceback
import threading
import litellm
from concurrent.futures import ThreadPoolExecutor
from mcpomni_connect.memory_store.memory_management.system_prompts import (
    episodic_memory_constructor_system_prompt,
    long_term_memory_constructor_system_prompt,
)

# Import both vector database implementations
from mcpomni_connect.memory_store.memory_management.qdrant_vector_db import (
    QdrantVectorDB,
)
from mcpomni_connect.memory_store.memory_management.chromadb_vector_db import (
    ChromaDBVectorDB,
)

# Cache for recent summaries
_RECENT_SUMMARY_CACHE = {}
_CACHE_TTL = 1800  # 30 minutes
_CACHE_LOCK = threading.RLock()  # Thread-safe cache access

# Thread pool for background processing
_THREAD_POOL = ThreadPoolExecutor(max_workers=4, thread_name_prefix="MemoryProcessor")


class MemoryManager:
    """Memory management operations with automatic fallback between Qdrant and ChromaDB."""

    def __init__(self, session_id: str, memory_type: str):
        """Initialize memory manager with automatic backend selection.

        Args:
            session_id: Session ID for the collection
            memory_type: Type of memory (episodic, long_term)
        """
        self.session_id = session_id
        self.memory_type = memory_type
        self.collection_name = f"{memory_type}_{session_id}"

        # Check Qdrant availability
        qdrant_host = config("QDRANT_HOST", default=None)
        qdrant_port = config("QDRANT_PORT", default=None)

        # Try Qdrant first
        if qdrant_host and qdrant_port:
            try:
                self.vector_db = QdrantVectorDB(
                    self.collection_name, session_id=session_id, memory_type=memory_type
                )
                if self.vector_db.enabled:
                    logger.debug(f"Using Qdrant for {memory_type} memory")
                    return
            except Exception as e:
                logger.warning(f"Failed to initialize Qdrant: {e}")

        # Fallback to ChromaDB
        try:
            self.vector_db = ChromaDBVectorDB(
                self.collection_name, session_id=session_id, memory_type=memory_type
            )

            if self.vector_db.enabled:
                logger.debug(f"Using ChromaDB for {memory_type} memory")
            else:
                logger.warning(
                    f"Both Qdrant and ChromaDB are disabled for {memory_type} memory"
                )
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.vector_db = None
            logger.warning(
                f"Vector database completely disabled for {memory_type} memory"
            )

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

            # Use sync call for memory processing
            response = llm_connection.llm_call_sync(llm_messages)
            if response and response.choices:
                content = response.choices[0].message.content

                return content
            else:
                return None
        except Exception as e:
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

            # Use sync call for memory processing
            response = llm_connection.llm_call_sync(llm_messages)

            if response and response.choices:
                content = response.choices[0].message.content

                return content
            else:
                return None
        except Exception as e:
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

    def _extract_end_time(self, metadata):
        """Extract end_time from metadata regardless of DB backend."""
        try:
            if hasattr(metadata, "payload"):
                # Qdrant format
                end_time = metadata.payload.get("end_time")
                logger.debug(f"📅 Extracted end_time from Qdrant payload: {end_time}")
                return end_time
            elif isinstance(metadata, dict):
                # ChromaDB format or generic dict
                end_time = metadata.get("end_time")
                logger.debug(f"📅 Extracted end_time from dict: {end_time}")
                return end_time
            else:
                logger.warning(f"❌ Unknown metadata format: {type(metadata)}")
                return None
        except Exception as e:
            logger.error(f"❌ Error extracting end_time: {e}")
            return None

    def _ensure_utc_datetime(self, timestamp):
        """Ensure message timestamp is a valid UTC timezone-aware datetime."""
        if timestamp is None:
            return datetime.now(timezone.utc)

        # If it's already a datetime object (Message objects now use timezone-aware datetimes)
        if isinstance(timestamp, datetime):
            # If timezone-aware, convert to UTC
            if timestamp.tzinfo is not None:
                return timestamp.astimezone(timezone.utc)
            # If naive, assume it's UTC and add timezone info
            else:
                return timestamp.replace(tzinfo=timezone.utc)

        # If it's a timestamp (float/int), convert to UTC timezone-aware datetime
        try:
            return datetime.fromtimestamp(timestamp, tz=timezone.utc)
        except (ValueError, OverflowError, OSError):
            return datetime.now(timezone.utc)

    async def process_conversation_memory(
        self, messages: list, llm_connection: Callable
    ):
        """Process conversation memory only if 30min have passed since last summary."""
        if not self.vector_db or not self.vector_db.enabled:
            logger.debug(
                f"Vector database is not enabled. Skipping memory operation for {self.memory_type}."
            )
            return

        try:
            # Ensure collection exists
            self.vector_db._ensure_collection()

            # Get the most recent summary
            most_recent = await self.get_most_recent_summary()
            last_end_time = None

            if most_recent:
                # Extract end_time using universal helper method
                last_end_time = self._extract_end_time(most_recent)

                if last_end_time and isinstance(last_end_time, str):
                    try:
                        # Handle various ISO formats and ensure UTC timezone
                        if last_end_time.endswith("Z"):
                            last_end_time = last_end_time.replace("Z", "+00:00")
                        last_end_time = datetime.fromisoformat(last_end_time)
                        # Ensure it's timezone-aware UTC
                        last_end_time = self._ensure_utc_datetime(last_end_time)

                    except Exception as e:
                        logger.error(f"Failed to parse last_end_time: {e}")
                        last_end_time = None
            else:
                last_end_time = None

            now = datetime.now(timezone.utc)

            # Extract and validate timestamps, converting to UTC datetimes
            valid_timestamps = []
            for m in messages:
                if hasattr(m, "timestamp") and m.timestamp is not None:
                    utc_dt = self._ensure_utc_datetime(m.timestamp)
                    valid_timestamps.append(utc_dt.timestamp())

            if valid_timestamps:
                window_start = min(valid_timestamps)
                window_start_dt = datetime.fromtimestamp(window_start, tz=timezone.utc)

            else:
                window_start = now
                window_start_dt = now

            # Only proceed if at least 30min have passed since last summary
            if last_end_time is None:
                logger.debug(
                    "No previous memory summary found, proceeding with all messages"
                )
            else:
                time_diff_seconds = (now - last_end_time).total_seconds()
                time_diff_minutes = time_diff_seconds / 60

                if time_diff_seconds < 1800:  # 30 minutes = 1800 seconds
                    logger.debug(
                        f"Less than 30min since last summary ({time_diff_minutes:.1f} min), skipping"
                    )
                    return
                else:
                    logger.debug(f"More than 30min since last summary, proceeding")

            # Filter messages after last_end_time
            if last_end_time:
                messages_to_summarize = []

                for m in messages:
                    msg_datetime = self._ensure_utc_datetime(
                        getattr(m, "timestamp", None)
                    )
                    if msg_datetime > last_end_time:
                        messages_to_summarize.append(m)

            else:
                messages_to_summarize = messages

            if not messages_to_summarize:
                logger.debug("No new messages to summarize for memory window")
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

            # window_start_dt is already properly set above as UTC datetime

            await self.vector_db.add_to_collection_async(
                document=memory_content,
                metadata={
                    "memory_type": self.memory_type,
                    "start_time": window_start_dt.isoformat()
                    if window_start_dt
                    else None,
                    "end_time": now.isoformat(),
                    "message_count": len(messages_to_summarize),
                    "universal_query": "memory_document",  # Universal query field for reliable retrieval
                },
                doc_id=doc_id,
            )

            self.invalidate_recent_summary_cache()

        except Exception as e:
            pass  # Silent background processing

    async def get_most_recent_summary(self) -> Optional[Dict]:
        """Get the most recent summary using universal query field."""
        if not self.vector_db or not self.vector_db.enabled:
            return None

        cache_key = (self.collection_name, self.memory_type)
        now = datetime.utcnow()

        # Check cache with TTL validation (thread-safe)
        with _CACHE_LOCK:
            cached = _RECENT_SUMMARY_CACHE.get(cache_key)
            if cached:
                cached_data, cached_time = cached
                if (now - cached_time).total_seconds() < _CACHE_TTL:
                    logger.info(
                        f"📋 Returning cached summary for {self.memory_type} (age: {int((now - cached_time).total_seconds())}s)"
                    )
                    return cached_data
                else:
                    logger.info(
                        f"📋 Cache expired for {self.memory_type} (age: {int((now - cached_time).total_seconds())}s), invalidating and refreshing"
                    )
                    # Invalidate expired cache
                    del _RECENT_SUMMARY_CACHE[cache_key]

        # Use universal query field to get all memory documents
        try:
            logger.debug(
                f"🔍 Querying with universal query field for {self.memory_type}"
            )

            results = await self.vector_db.query_collection_async(
                query="memory_document",  # Universal query field
                n_results=50,
                distance_threshold=0.01,
            )

            if not results or not results.get("metadatas"):
                logger.debug(f"📋 No documents found for {self.memory_type}")
                with _CACHE_LOCK:
                    _RECENT_SUMMARY_CACHE[cache_key] = (None, now)
                return None

            # Sort by end_time to get most recent
            valid_metadatas = []
            for metadata in results["metadatas"]:
                end_time_str = metadata.get("end_time")
                if end_time_str:
                    try:
                        # Handle various ISO formats and ensure UTC timezone
                        if end_time_str.endswith("Z"):
                            end_time_str = end_time_str.replace("Z", "+00:00")
                        end_time = datetime.fromisoformat(end_time_str)
                        # Ensure it's timezone-aware UTC
                        end_time = self._ensure_utc_datetime(end_time)
                        valid_metadatas.append((metadata, end_time))
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to parse end_time: {end_time_str}")
                        continue

            if not valid_metadatas:
                logger.debug(f"📋 No valid end_time found for {self.memory_type}")
                with _CACHE_LOCK:
                    _RECENT_SUMMARY_CACHE[cache_key] = (None, now)
                return None

            # Get most recent
            most_recent_metadata, most_recent_time = max(
                valid_metadatas, key=lambda x: x[1]
            )

            with _CACHE_LOCK:
                _RECENT_SUMMARY_CACHE[cache_key] = (most_recent_metadata, now)
            return most_recent_metadata

        except Exception as e:
            logger.error(f"❌ Error fetching most recent summary: {e}")
            with _CACHE_LOCK:
                _RECENT_SUMMARY_CACHE[cache_key] = (None, now)
            return None

    def invalidate_recent_summary_cache(self):
        """Invalidate the cache for this collection/memory_type."""
        cache_key = (self.collection_name, self.memory_type)
        with _CACHE_LOCK:
            if cache_key in _RECENT_SUMMARY_CACHE:
                del _RECENT_SUMMARY_CACHE[cache_key]

    async def query_memory(
        self, query: str, n_results: int, distance_threshold: float
    ) -> List[str]:
        """Query memory for relevant information."""
        if not self.vector_db or not self.vector_db.enabled:
            return []

        try:
            results = await self.vector_db.query_collection_async(
                query=query, n_results=n_results, distance_threshold=distance_threshold
            )

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


def process_both_memory_types_threaded(session_id, validated_messages, llm_connection):
    """Process both episodic and long-term memory in a single threaded operation."""
    try:
        # Process episodic memory in a completely separate thread
        def episodic_task():
            try:
                episodic_manager = MemoryManager(
                    session_id=session_id, memory_type="episodic"
                )

                if episodic_manager.vector_db and episodic_manager.vector_db.enabled:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(
                            episodic_manager.process_conversation_memory(
                                validated_messages, llm_connection
                            )
                        )

                    finally:
                        loop.close()
            except Exception as e:
                pass  # Silent background processing

        # Process long-term memory in a completely separate thread
        def long_term_task():
            try:
                long_term_manager = MemoryManager(
                    session_id=session_id, memory_type="long_term"
                )

                if long_term_manager.vector_db and long_term_manager.vector_db.enabled:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(
                            long_term_manager.process_conversation_memory(
                                validated_messages, llm_connection
                            )
                        )
                    finally:
                        loop.close()
            except Exception as e:
                pass  # Silent background processing

        # Start both tasks in separate threads without waiting

        episodic_thread = threading.Thread(target=episodic_task, daemon=True)
        episodic_thread.start()

        long_term_thread = threading.Thread(target=long_term_task, daemon=True)
        long_term_thread.start()

    except Exception as e:
        pass  # Silent background processing


def fire_and_forget_memory_processing(session_id, validated_messages, llm_connection):
    """Fire and forget memory processing using actual threading."""
    # Submit to thread pool and return immediately
    future = _THREAD_POOL.submit(
        process_both_memory_types_threaded,
        session_id,
        validated_messages,
        llm_connection,
    )
    return future


class MemoryManagerFactory:
    """Factory for creating memory managers."""

    @staticmethod
    def create_episodic_memory_manager(session_id: str) -> MemoryManager:
        """Create episodic memory manager."""
        return MemoryManager(session_id, "episodic")

    @staticmethod
    def create_long_term_memory_manager(session_id: str) -> MemoryManager:
        """Create long-term memory manager."""
        return MemoryManager(session_id, "long_term")

    @staticmethod
    def create_both_memory_managers(
        session_id: str,
    ) -> Tuple[MemoryManager, MemoryManager]:
        """Create both episodic and long-term memory managers."""
        episodic = MemoryManager(session_id, "episodic")
        long_term = MemoryManager(session_id, "long_term")
        return episodic, long_term


def cleanup_memory_system():
    """Cleanup function to properly shutdown thread pool and clear cache."""
    logger.debug("Cleaning up memory management system")

    # Shutdown thread pool gracefully
    _THREAD_POOL.shutdown(wait=True)

    # Clear cache
    with _CACHE_LOCK:
        _RECENT_SUMMARY_CACHE.clear()

    logger.debug("Memory system cleanup complete")
