import chromadb
from chromadb.config import Settings
import os
from mcpomni_connect.utils import logger
from typing import List, Dict, Any, Callable
import uuid
from datetime import datetime
from mcpomni_connect.memory_store.memory_management.system_prompts import (
    episodic_memory_constructor_system_prompt,
    long_term_memory_constructor_system_prompt,
)
from mcpomni_connect.memory_store.memory_management.shared_embedding import (
    get_embed_model,
    embed_text,
    NOMIC_VECTOR_SIZE,
)
import time
import asyncio
import logging
import traceback
import threading

# ==== 🔥 Get shared embedding model at module import ====
_EMBED_MODEL = get_embed_model()


def get_embed_model():
    return _EMBED_MODEL


class ChromaDBMemory:
    """ChromaDB-based memory store for local vector storage without external dependencies."""

    def __init__(self, session_id: str, memory_type: str):
        """Initialize ChromaDB memory store.

        Args:
            session_id: Session ID for the collection
            memory_type: Type of memory (episodic, long_term)
        """
        self.session_id = session_id
        self.memory_type = memory_type
        self.collection_name = f"{memory_type}_{session_id}"
        self._embed_model = get_embed_model()

        # Initialize ChromaDB client with local persistence
        try:
            # Create a local directory for ChromaDB data
            chroma_data_dir = os.path.join(os.getcwd(), ".chroma_db")
            os.makedirs(chroma_data_dir, exist_ok=True)

            self.chroma_client = chromadb.PersistentClient(
                path=chroma_data_dir,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                ),
            )

            # Get or create collection
            self.collection = self._get_or_create_collection()
            self.enabled = True
            logger.info(
                f"Initialized ChromaDB memory for {memory_type} memory with session: {session_id}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.enabled = False

    def _get_or_create_collection(self):
        """Get or create a collection with default embedding model."""
        try:
            logger.info(
                f"Getting or creating ChromaDB collection: {self.collection_name}"
            )
            collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={
                    "hnsw:space": "cosine",
                    "description": f"{self.memory_type} memory for session {self.session_id}",
                },
            )
            logger.info("Successfully initialized ChromaDB collection")
            return collection
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB collection: {e}")
            raise

    def embed_text(self, text: str) -> list[float]:
        """Embed text using shared nomic-ai/nomic-embed-text-v1 model."""
        return embed_text(text)

    async def create_episodic_memory(
        self, message: str, llm_connection: Callable
    ) -> Dict:
        """Create an episodic memory from a conversation."""
        try:
            # Temporarily disable LiteLLM logging to prevent async task warnings
            import litellm

            original_verbose = getattr(litellm, "verbose", None)
            litellm.verbose = False

            try:
                llm_messages = []
                llm_messages.append(
                    {
                        "role": "system",
                        "content": episodic_memory_constructor_system_prompt,
                    }
                )
                llm_messages.append({"role": "user", "content": message})
                response = await llm_connection.llm_call(llm_messages)
                if response and response.choices:
                    return response.choices[0].message.content
                else:
                    return None
            finally:
                # Restore original logging setting
                if original_verbose is not None:
                    litellm.verbose = original_verbose
        except Exception as e:
            logger.error(f"Failed to create episodic memory: {e}")
            raise

    async def create_long_term_memory(
        self, message: str, llm_connection: Callable
    ) -> Dict:
        """Create a long-term memory from a conversation."""
        try:
            # Temporarily disable LiteLLM logging to prevent async task warnings
            import litellm

            original_verbose = getattr(litellm, "verbose", None)
            litellm.verbose = False

            try:
                llm_messages = []
                llm_messages.append(
                    {
                        "role": "system",
                        "content": long_term_memory_constructor_system_prompt,
                    }
                )
                llm_messages.append({"role": "user", "content": message})
                response = await llm_connection.llm_call(llm_messages)
                if response and response.choices:
                    return response.choices[0].message.content
                else:
                    return None
            finally:
                # Restore original logging setting
                if original_verbose is not None:
                    litellm.verbose = original_verbose
        except Exception as e:
            logger.error(f"Failed to create long-term memory: {e}")
            raise

    def add_to_collection(
        self, document: str, session_id: str, metadata: Dict = None, doc_id: str = None
    ):
        """Add a single document to the collection."""
        try:
            if not self.enabled:
                logger.warning("ChromaDB is not enabled. Skipping memory operation.")
                return False

            if not doc_id:
                doc_id = str(uuid.uuid4())

            # Prepare metadata
            if metadata is None:
                metadata = {}
            metadata["text"] = document
            metadata["session_id"] = session_id
            metadata["timestamp"] = str(datetime.now())
            metadata["memory_type"] = self.memory_type

            # Add document to ChromaDB
            self.collection.add(
                documents=[document], metadatas=[metadata], ids=[doc_id]
            )
            logger.info(f"Successfully added document to ChromaDB with ID: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add document to ChromaDB: {e}")
            raise

    def query_collection(
        self, query: str, n_results: int = 3, distance_threshold: float = 0.4
    ) -> Dict[str, Any]:
        """Query the collection."""
        if not self.enabled:
            logger.warning("ChromaDB is not enabled. Skipping memory operation.")
            return "No relevant memory found"

        try:
            logger.info(
                f"Querying ChromaDB collection: {self.collection_name} with query: {query}"
            )

            # Query ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"],
            )

            if not results["documents"] or not results["documents"][0]:
                return "No relevant memory found"

            # Filter by distance threshold and format results
            documents = results["documents"][0]
            metadatas = results["metadatas"][0]
            distances = results["distances"][0]

            filtered_results = []
            for doc, meta, dist in zip(documents, metadatas, distances):
                if dist >= distance_threshold:
                    filtered_results.append(
                        {"document": doc, "metadata": meta, "distance": dist}
                    )

            if not filtered_results:
                return "No relevant memory found"

            # Return just the documents for compatibility
            return [result["document"] for result in filtered_results]

        except Exception as e:
            logger.error(f"Failed to query ChromaDB: {e}")
            return "No relevant memory found"

    async def add_to_collection_async(
        self, doc_id: str, document: str, session_id: str, metadata: Dict
    ):
        """Async wrapper for adding to collection."""
        if not self.enabled:
            logger.warning("ChromaDB is not enabled. Skipping memory operation.")
            return

        try:
            # Prepare metadata
            metadata["text"] = document
            metadata["session_id"] = session_id
            metadata["timestamp"] = str(datetime.now())
            metadata["memory_type"] = self.memory_type

            # Add document to ChromaDB
            self.collection.add(
                documents=[document], metadatas=[metadata], ids=[doc_id]
            )
            logger.info(
                f"Successfully stored {self.memory_type} memory with ID: {doc_id}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            raise

    async def query_collection_async(
        self, query: str, n_results: int = 5, distance_threshold: float = 0.70
    ) -> Dict[str, Any]:
        """Async wrapper for querying collection."""
        if not self.enabled:
            logger.warning("ChromaDB is not enabled. Skipping memory operation.")
            return {}

        try:
            # Query ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"],
            )

            if not results["documents"] or not results["documents"][0]:
                return {
                    "documents": [],
                    "session_id": [],
                    "distances": [],
                    "metadatas": [],
                    "ids": [],
                }

            # Filter by distance threshold and format results
            documents = results["documents"][0]
            metadatas = results["metadatas"][0]
            distances = results["distances"][0]

            filtered_results = []
            for doc, meta, dist in zip(documents, metadatas, distances):
                if dist >= distance_threshold:
                    filtered_results.append(
                        {"document": doc, "metadata": meta, "distance": dist}
                    )

            results = {
                "documents": [result["document"] for result in filtered_results],
                "session_id": [
                    result["metadata"]["session_id"] for result in filtered_results
                ],
                "distances": [result["distance"] for result in filtered_results],
                "metadatas": [result["metadata"] for result in filtered_results],
                "ids": [
                    result["metadata"].get("id", "") for result in filtered_results
                ],
            }

            return results
        except Exception as e:
            logger.error(f"Failed to query collection: {e}")
            raise

    async def process_conversation_memory(
        self, messages: list, llm_connection: Callable
    ):
        """Process conversation memory only if 30min have passed since last summary."""
        if not self.enabled:
            logger.warning("ChromaDB is not enabled. Skipping memory operation.")
            return

        try:
            # Get the most recent summary
            most_recent = await self.get_most_recent_summary()
            last_end_time = None

            if most_recent and "end_time" in most_recent:
                last_end_time = datetime.fromisoformat(most_recent["end_time"])

            now = datetime.now()
            valid_timestamps = [
                m.timestamp
                for m in messages
                if hasattr(m, "timestamp") and m.timestamp is not None
            ]

            if valid_timestamps:
                window_start = min(valid_timestamps)
            else:
                window_start = now

            # Only proceed if at least 30min have passed since last summary
            if last_end_time is None:
                logger.info(
                    "No previous memory summary found (first run for this session). Proceeding to summarize all messages."
                )
            else:
                if (now - last_end_time).total_seconds() < 1800:
                    logger.info(f"Less than 30min since last memory summary, skipping.")
                    return

            # Filter messages after last_end_time
            if last_end_time:
                logger.info(f"Last end time confirmed: {last_end_time}")
                messages_to_summarize = [
                    m
                    for m in messages
                    if hasattr(m, "timestamp")
                    and m.timestamp is not None
                    and datetime.fromtimestamp(m.timestamp) > last_end_time
                ]
            else:
                logger.info(
                    f"Last end time is None, proceeding to summarize all messages."
                )
                messages_to_summarize = messages

            if not messages_to_summarize:
                logger.info(f"No new messages to summarize for memory window.")
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
                logger.error(f"Unknown memory type: {self.memory_type}")
                return

            if not memory_content:
                logger.warning(f"Failed to construct {self.memory_type} memory")
                return

            doc_id = str(uuid.uuid4())
            logger.info(f"memory_content: {memory_content}")

            # Ensure window_start is a datetime before calling isoformat
            if isinstance(window_start, float):
                window_start = datetime.fromtimestamp(window_start)

            await self.add_to_collection_async(
                document=memory_content,
                session_id=self.session_id,
                metadata={
                    "memory_type": self.memory_type,
                    "start_time": window_start.isoformat() if window_start else None,
                    "end_time": now.isoformat(),
                    "message_count": len(messages_to_summarize),
                },
                doc_id=doc_id,
            )

            logger.info(
                f"Successfully stored {self.memory_type} memory for session: {self.session_id}"
            )

        except Exception as e:
            logger.error(f"Error in background memory processing: {e}")

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

    async def get_most_recent_summary(self) -> dict | None:
        """Get the most recent summary from the collection."""
        if not self.enabled:
            return None

        try:
            # Get all documents from the collection
            results = self.collection.get(
                include=["metadatas"],
                limit=1000,  # Adjust as needed
            )

            if not results["metadatas"]:
                return None

            # Find most recent by end_time
            most_recent = max(results["metadatas"], key=lambda x: x.get("end_time", ""))
            return most_recent

        except Exception as e:
            logger.error(f"Error getting most recent summary: {e}")
            return None

    async def query_both_memory_types(
        self,
        query: str,
        session_id: str,
        n_results: int = 3,
        distance_threshold: float = 0.5,
    ) -> tuple:
        """Query both long-term and episodic memory collections."""
        if not self.enabled:
            logger.warning("ChromaDB is not enabled. Skipping memory operation.")
            return (
                "No relevant long-term memory found",
                "No relevant episodic memory found",
            )

        try:
            long_term_result = "No relevant long-term memory found"
            episodic_result = "No relevant episodic memory found"

            # Query long-term memory collection
            try:
                long_term_collection = self.chroma_client.get_collection(
                    name=f"long_term_{session_id}"
                )
                long_term_results = long_term_collection.query(
                    query_texts=[query], n_results=n_results, include=["documents"]
                )

                if long_term_results["documents"] and long_term_results["documents"][0]:
                    long_term_result = long_term_results["documents"][0]
            except Exception as e:
                logger.warning(f"Failed to query long-term memory collection: {e}")

            # Query episodic memory collection
            try:
                episodic_collection = self.chroma_client.get_collection(
                    name=f"episodic_{session_id}"
                )
                episodic_results = episodic_collection.query(
                    query_texts=[query], n_results=n_results, include=["documents"]
                )

                if episodic_results["documents"] and episodic_results["documents"][0]:
                    episodic_result = episodic_results["documents"][0]

            except Exception as e:
                logger.warning(f"Failed to query episodic memory collection: {e}")

            return long_term_result, episodic_result

        except Exception as e:
            logger.error(f"Error in query_both_memory_types: {e}")
            return (
                "No relevant long-term memory found",
                "No relevant episodic memory found",
            )


def process_both_memory_types_threaded_chroma(
    session_id, validated_messages, llm_connection
):
    """Process both episodic and long-term memory in ChromaDB using threaded operations."""
    try:
        logger.info(
            f"Starting ChromaDB threaded memory processing for session {session_id}"
        )

        # Process episodic memory in a separate thread
        def episodic_task():
            try:
                episodic_db = ChromaDBMemory(
                    session_id=session_id, memory_type="episodic"
                )
                if episodic_db.enabled:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(
                            episodic_db.process_conversation_memory(
                                validated_messages, llm_connection
                            )
                        )
                        logger.info(
                            f"ChromaDB episodic memory processing completed for session {session_id}"
                        )
                    finally:
                        loop.close()
                else:
                    logger.warning(
                        f"ChromaDB episodic memory processing skipped for session {session_id}"
                    )
            except Exception as e:
                logger.error(
                    f"Error in ChromaDB episodic memory processing for session {session_id}: {e}\n{traceback.format_exc()}"
                )

        # Process long-term memory in a separate thread
        def long_term_task():
            try:
                long_term_db = ChromaDBMemory(
                    session_id=session_id, memory_type="long_term"
                )
                if long_term_db.enabled:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(
                            long_term_db.process_conversation_memory(
                                validated_messages, llm_connection
                            )
                        )
                        logger.info(
                            f"ChromaDB long-term memory processing completed for session {session_id}"
                        )
                    finally:
                        loop.close()
                else:
                    logger.warning(
                        f"ChromaDB long-term memory processing skipped for session {session_id}"
                    )
            except Exception as e:
                logger.error(
                    f"Error in ChromaDB long-term memory processing for session {session_id}: {e}\n{traceback.format_exc()}"
                )

        # Start both tasks in separate threads
        episodic_thread = threading.Thread(target=episodic_task, daemon=True)
        long_term_thread = threading.Thread(target=long_term_task, daemon=True)

        episodic_thread.start()
        long_term_thread.start()

        logger.info(
            f"ChromaDB memory processing threads started for session {session_id}"
        )

    except Exception as e:
        logger.error(
            f"Error in ChromaDB threaded memory processing for session {session_id}: {e}\n{traceback.format_exc()}"
        )


def fire_and_forget_memory_processing_chroma(
    session_id, validated_messages, llm_connection
):
    """Fire and forget ChromaDB memory processing using threading."""
    memory_thread = threading.Thread(
        target=process_both_memory_types_threaded_chroma,
        args=(session_id, validated_messages, llm_connection),
        daemon=True,
    )
    memory_thread.start()
    logger.info(
        f"ChromaDB fire and forget memory processing started for session {session_id}"
    )
    return memory_thread
