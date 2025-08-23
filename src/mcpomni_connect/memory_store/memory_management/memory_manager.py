import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Callable, Optional, Tuple
from mcpomni_connect.utils import logger, is_vector_db_enabled
from decouple import config
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from mcpomni_connect.memory_store.memory_management.system_prompts import (
    episodic_memory_constructor_system_prompt,
    long_term_memory_constructor_system_prompt,
)
from mcpomni_connect.memory_store.memory_management.shared_embedding import (
    load_embed_model,
)

# No more pre-loaded variables - everything imports when needed

# Cache for recent summaries
_RECENT_SUMMARY_CACHE = {}
_CACHE_TTL = 120  # 10 minutes (changed from 30 minutes for faster testing)
_CACHE_LOCK = threading.RLock()  # Thread-safe cache access

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


class MemoryManager:
    """Memory management operations with automatic fallback between Qdrant and ChromaDB."""

    def __init__(self, session_id: str, memory_type: str):
        """Initialize memory manager with automatic backend selection.

        Args:
            session_id: Session ID for the collection
            memory_type: Type of memory (episodic, long_term)
        """
        # No global variables needed anymore

        self.session_id = session_id
        self.memory_type = memory_type
        self.collection_name = f"{memory_type}_{session_id}"

        # Check if vector database is enabled
        if not is_vector_db_enabled():
            logger.debug("Vector database is disabled by configuration")
            self.vector_db = None
            return

        # Load embedding model once (shared across all instances)
        load_embed_model()

        # Determine provider from config
        provider = config("OMNI_MEMORY_PROVIDER", default=None)
        if not provider:
            logger.error("OMNI_MEMORY_PROVIDER is not set in the environment")
            self.vector_db = None
            return
        
        provider = provider.lower()

        # Try provider-specific initialization with sensible fallbacks
        if provider == "qdrant-remote":
            try:
                # Import QdrantVectorDB when needed
                from mcpomni_connect.memory_store.memory_management.qdrant_vector_db import (
                    QdrantVectorDB,
                )

                self.vector_db = QdrantVectorDB(
                    self.collection_name, session_id=session_id, memory_type=memory_type
                )
                if self.vector_db.enabled:
                    logger.debug(f"Using Qdrant for {memory_type} memory")
                    return
                else:
                    logger.warning("Qdrant not enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize Qdrant (remote): {e}")

        elif provider == "mongodb-remote":
            try:
                # Import MongoDBVectorDB when needed
                from mcpomni_connect.memory_store.memory_management.mongodb_vector_db import (
                    MongoDBVectorDB,
                )

                self.vector_db = MongoDBVectorDB(
                    self.collection_name, session_id=session_id, memory_type=memory_type
                )
                if self.vector_db.enabled:
                    logger.debug(f"Using MongoDB for {memory_type} memory")
                    return
                else:
                    logger.warning("MongoDB not enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize MongoDB (remote): {e}")

        elif provider.startswith("chroma"):
            try:
                # Import ChromaDBVectorDB when needed
                from mcpomni_connect.memory_store.memory_management.chromadb_vector_db import (
                    ChromaDBVectorDB,
                )

                # Determine client type from provider
                if provider == "chroma-remote":
                    client_type = "remote"
                elif provider == "chroma-cloud":
                    client_type = "cloud"
                else:
                    logger.error(f"Invalid ChromaDB provider: {provider}")
                    raise RuntimeError(f"Invalid ChromaDB provider: {provider}")

                self.vector_db = ChromaDBVectorDB(
                    self.collection_name,
                    session_id=session_id,
                    memory_type=memory_type,
                    client_type=client_type,
                )
                if self.vector_db.enabled:
                    logger.debug(f"Using ChromaDB ({client_type}) for {memory_type} memory")
                    return
                else:
                    logger.warning(f"ChromaDB ({client_type}) not enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize ChromaDB ({client_type}): {e}")

        # No fallback - if the configured provider fails, vector DB is disabled
        logger.warning(f"Vector database provider '{provider}' failed - vector DB disabled")
        self.vector_db = None

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

            # Use sync call for memory processing
            response = llm_connection.llm_call_sync(llm_messages)

            if response and response.choices:
                content = response.choices[0].message.content

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
        """Process conversation memory only if cache TTL has passed since last summary."""
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
                logger.info(f"🕐 Last summary end_time extracted: {last_end_time}")

                if last_end_time and isinstance(last_end_time, str):
                    try:
                        # Handle various ISO formats and ensure UTC timezone
                        if last_end_time.endswith("Z"):
                            last_end_time = last_end_time.replace("Z", "+00:00")
                        last_end_time = datetime.fromisoformat(last_end_time)
                        # Ensure it's timezone-aware UTC
                        last_end_time = self._ensure_utc_datetime(last_end_time)
                        logger.info(f"🕐 Parsed last_end_time: {last_end_time} (UTC)")
                    except Exception as e:
                        logger.error(f"Failed to parse last_end_time: {e}")
                        last_end_time = None
            else:
                logger.info("🕐 No previous memory summary found")
                last_end_time = None

            now = datetime.now(timezone.utc)
            logger.info(f"🕐 Current time: {now} (UTC)")

            # Extract and validate timestamps, converting to UTC datetimes
            valid_timestamps = []
            for m in messages:
                if hasattr(m, "timestamp") and m.timestamp is not None:
                    utc_dt = self._ensure_utc_datetime(m.timestamp)
                    valid_timestamps.append(utc_dt.timestamp())

            if valid_timestamps:
                window_start = min(valid_timestamps)
                window_start_dt = datetime.fromtimestamp(window_start, tz=timezone.utc)
                logger.info(f"🕐 Message window start: {window_start_dt} (UTC)")

            else:
                window_start = now
                window_start_dt = now
                logger.info(f"🕐 No valid message timestamps, using current time: {window_start_dt} (UTC)")

            # Only proceed if at least cache TTL has passed since last summary
            if last_end_time is None:
                logger.info(
                    "🕐 No previous memory summary found, proceeding with all messages"
                )
            else:
                time_diff_seconds = (now - last_end_time).total_seconds()
                time_diff_minutes = time_diff_seconds / 60
                cache_ttl_minutes = _CACHE_TTL / 60

                logger.info(f"🕐 Time since last summary: {time_diff_minutes:.1f} minutes")
                logger.info(f"🕐 Cache TTL threshold: {cache_ttl_minutes:.1f} minutes")

                if time_diff_seconds < _CACHE_TTL:
                    logger.info(
                        f"🕐 SKIPPING: Less than {cache_ttl_minutes:.1f}min since last summary ({time_diff_minutes:.1f} min)"
                    )
                    return
                else:
                    logger.info(f"🕐 PROCEEDING: More than {cache_ttl_minutes:.1f}min since last summary ({time_diff_minutes:.1f} min)")

            # Filter messages after last_end_time
            if last_end_time:
                messages_to_summarize = []
                total_messages = len(messages)

                for m in messages:
                    msg_datetime = self._ensure_utc_datetime(
                        getattr(m, "timestamp", None)
                    )
                    if msg_datetime > last_end_time:
                        messages_to_summarize.append(m)

                logger.info(f"🕐 Filtered {len(messages_to_summarize)}/{total_messages} messages after last_end_time: {last_end_time}")

            else:
                messages_to_summarize = messages
                logger.info(f"🕐 No last_end_time filter, processing all {len(messages)} messages")

            if not messages_to_summarize:
                logger.info("🕐 No new messages to summarize for memory window")
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
            new_end_time = now.isoformat()
            logger.info(f"💾 Storing new {self.memory_type} memory:")
            logger.info(f"💾   - Start time: {window_start_dt.isoformat() if window_start_dt else 'N/A'}")
            logger.info(f"💾   - End time: {new_end_time}")
            logger.info(f"💾   - Message count: {len(messages_to_summarize)}")
            logger.info(f"💾   - Next background indexing will run after: {(_CACHE_TTL/60):.1f} minutes")

            self.vector_db.add_to_collection(
                document=memory_content,
                metadata={
                    "memory_type": self.memory_type,
                    "start_time": window_start_dt.isoformat()
                    if window_start_dt
                    else None,
                    "end_time": new_end_time,
                    "message_count": len(messages_to_summarize),
                    "universal_query": "memory_document",  # Universal query field for reliable retrieval
                },
                doc_id=doc_id,
            )

            logger.info(f"💾 Successfully stored memory document with ID: {doc_id}")
            self.invalidate_recent_summary_cache()
            logger.info(f"💾 Invalidated cache for {self.memory_type} - next query will hit vector DB")

        except Exception:
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
            logger.debug(f"📋 Cache check for {self.memory_type}: {'HIT' if cached else 'MISS'}")
            if cached:
                cached_data, cached_time = cached
                cache_age = (now - cached_time).total_seconds()
                if cache_age < _CACHE_TTL:
                    logger.info(
                        f"📋 REDIS CACHE HIT for {self.memory_type} (age: {int(cache_age)}s, TTL: {_CACHE_TTL}s)"
                    )
                    if cached_data:
                        end_time_str = cached_data.get("end_time", "N/A")
                        logger.info(f"📋 Cached summary end_time: {end_time_str}")
                    return cached_data
                else:
                    logger.info(
                        f"📋 REDIS CACHE EXPIRED for {self.memory_type} (age: {int(cache_age)}s, TTL: {_CACHE_TTL}s), invalidating and refreshing"
                    )
                    # Invalidate expired cache
                    del _RECENT_SUMMARY_CACHE[cache_key]
            else:
                logger.debug(f"📋 No cache entry found for {self.memory_type}")

        # Use universal query field to get all memory documents
        try:
            logger.info(
                f"🔍 REDIS CACHE MISS - Querying vector DB for {self.memory_type}"
            )

            results = self.vector_db.query_collection(
                query="memory_document",  # Universal query field
                n_results=50,
                distance_threshold=0.01,
            )

            if not results or not results.get("metadatas"):
                logger.info(f"📋 No documents found for {self.memory_type}")
                with _CACHE_LOCK:
                    _RECENT_SUMMARY_CACHE[cache_key] = (None, now)
                return None

            # Debug: Show the actual results structure
            logger.info(f"📋 Raw results structure: {list(results.keys())}")
            logger.info(f"📋 Number of metadatas: {len(results.get('metadatas', []))}")
            logger.info(f"📋 Results: {results}")
            logger.info(f"📋 Metadatas: {results.get('metadatas', [])}")
            # Show first few metadata entries for debugging
            for i, metadata in enumerate(results["metadatas"][:3]):
                logger.info(f"📋 Metadata {i+1} keys: {list(metadata.keys())}")
                logger.info(f"📋 Metadata {i+1} end_time: {metadata.get('end_time', 'NOT_FOUND')}")
                logger.info(f"📋 Metadata {i+1} memory_type: {metadata.get('memory_type', 'NOT_FOUND')}")
                logger.info(f"📋 Metadata {i+1} raw content: {metadata}")

            # Sort by end_time to get most recent
            valid_metadatas = []
            for result in results["metadatas"]:
                # end_time and memory_type are now at the root level of each result
                end_time_str = result.get("end_time")
                memory_type = result.get("memory_type")
                
                logger.debug(f"📋 Checking result: {memory_type} - end_time: {end_time_str}")
                if end_time_str:
                    try:
                        # Handle various ISO formats and ensure UTC timezone
                        if end_time_str.endswith("Z"):
                            end_time_str = end_time_str.replace("Z", "+00:00")
                        end_time = datetime.fromisoformat(end_time_str)
                        # Ensure it's timezone-aware UTC
                        end_time = self._ensure_utc_datetime(end_time)
                        valid_metadatas.append((result, end_time))
                        logger.debug(f"📋 Valid end_time: {end_time_str} -> {end_time}")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to parse end_time: {end_time_str} - Error: {e}")
                        continue
                else:
                    logger.debug(f"📋 No end_time found in result: {memory_type}")

            if not valid_metadatas:
                logger.info(f"📋 No valid end_time found for {self.memory_type}")
                logger.info(f"📋 Total metadatas checked: {len(results['metadatas'])}")
                logger.info(f"📋 Valid metadatas with end_time: {len(valid_metadatas)}")
                with _CACHE_LOCK:
                    _RECENT_SUMMARY_CACHE[cache_key] = (None, now)
                return None

            # Get most recent
            most_recent_result, most_recent_time = max(
                valid_metadatas, key=lambda x: x[1]
            )
            
            # Debug: Show what's actually in the most recent result
            logger.info(f"📋 Most recent result keys: {list(most_recent_result.keys())}")
            logger.info(f"📋 Most recent summary found - end_time: {most_recent_result.get('end_time')}")
            logger.info(f"📋 Most recent summary found - memory_type: {most_recent_result.get('memory_type')}")

            with _CACHE_LOCK:
                _RECENT_SUMMARY_CACHE[cache_key] = (most_recent_result, now)
            return most_recent_result

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
                logger.info(f"🗑️ Invalidating cache for {self.memory_type} (key: {cache_key})")
                del _RECENT_SUMMARY_CACHE[cache_key]
            else:
                logger.debug(f"🗑️ Cache key {cache_key} not found for invalidation")

    def query_memory(
        self, query: str, n_results: int, distance_threshold: float
    ) -> List[str]:
        """Query memory for relevant information."""
        if not self.vector_db or not self.vector_db.enabled:
            return []

        try:
            results = self.vector_db.query_collection(
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
            except Exception:
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
            except Exception:
                pass  # Silent background processing

        # Start both tasks in separate threads without waiting

        episodic_thread = threading.Thread(target=episodic_task, daemon=True)
        episodic_thread.start()

        long_term_thread = threading.Thread(target=long_term_task, daemon=True)
        long_term_thread.start()

    except Exception:
        pass  # Silent background processing


def fire_and_forget_memory_processing(session_id, validated_messages, llm_connection):
    """Fire and forget memory processing using actual threading."""
    if not is_vector_db_enabled():
        return

    # Check if thread pool is available
    if _THREAD_POOL is None:
        logger.debug("Thread pool not initialized - skipping memory processing")
        return

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
        if not is_vector_db_enabled():
            logger.debug(
                "Vector database disabled - skipping episodic memory manager creation"
            )
            return None
        return MemoryManager(session_id, "episodic")

    @staticmethod
    def create_long_term_memory_manager(session_id: str) -> MemoryManager:
        """Create long-term memory manager."""
        if not is_vector_db_enabled():
            logger.debug(
                "Vector database disabled - skipping long-term memory manager creation"
            )
            return None
        return MemoryManager(session_id, "long_term")

    @staticmethod
    def create_both_memory_managers(
        session_id: str,
    ) -> Tuple[MemoryManager, MemoryManager]:
        """Create both episodic and long-term memory managers."""
        if not is_vector_db_enabled():
            logger.debug("Vector database disabled - skipping memory manager creation")
            return None, None
        episodic = MemoryManager(session_id, "episodic")
        long_term = MemoryManager(session_id, "long_term")
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
