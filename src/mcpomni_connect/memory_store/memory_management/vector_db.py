from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
import os
from mcpomni_connect.utils import logger
from typing import List, Dict, Any, Callable
import uuid
from datetime import datetime, timedelta
from qdrant_client import models
from sentence_transformers import SentenceTransformer
from mcpomni_connect.memory_store.memory_management.system_prompts import (
    episodic_memory_constructor_system_prompt,
    long_term_memory_constructor_system_prompt,
)
import time
import asyncio
import logging
import traceback

_RECENT_SUMMARY_CACHE = {}  # {(collection_name, memory_type): (summary, cache_time)}
_CACHE_TTL = 1800  # 30 minutes in seconds

# Eagerly load the embedding model at module import time
_EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")


def get_embed_model():
    return _EMBED_MODEL


class QdrantVectorDB:
    def __init__(self, session_id: str, memory_type: str):
        """Initialize Qdrant vector database with open-source embeddings.

        Args:
            session_id: Session ID for the collection
            memory_type: Type of memory (episodic, long_term)
        """
        self.client = QdrantClient(
            host=os.getenv("QDRANT_HOST"), port=os.getenv("QDRANT_PORT")
        )
        self.collection_name = f"{memory_type}_{session_id}"
        self.session_id = session_id
        self.memory_type = memory_type
        self._embed_model = get_embed_model()
        self._vector_size = 384
        logger.info(
            f"Initialized QdrantVectorDB for {memory_type} memory with session: {session_id} using all-MiniLM-L6-v2 (384-dim)"
        )

    def embed_text(self, text: str) -> list[float]:
        """Embed text using all-MiniLM-L6-v2 model."""
        try:
            embedding = self._embed_model.encode(text).tolist()
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding with SentenceTransformer: {e}")
            raise

    async def create_episodic_memory(
        self, message: str, llm_connection: Callable
    ) -> Dict:
        """Create an episodic memory from a conversation.

        Args:
            messages: The conversation messages to analyze
            llm_connection: The LLM connection to use for memory creation
        """
        try:
            llm_messages = []
            llm_messages.append(
                {"role": "system", "content": episodic_memory_constructor_system_prompt}
            )
            llm_messages.append({"role": "user", "content": message})
            response = await llm_connection.llm_call(llm_messages)
            if response and response.choices:
                return response.choices[0].message.content
            else:
                return None
        except Exception as e:
            logger.error(f"Failed to create episodic memory: {e}")
            raise

    async def create_long_term_memory(
        self, message: str, llm_connection: Callable
    ) -> Dict:
        """Create a long-term memory from a conversation.

        Args:
            messages: The conversation messages to analyze
            llm_connection: The LLM connection to use for memory creation
        """
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
        except Exception as e:
            logger.error(f"Failed to create long-term memory: {e}")
            raise

    def _ensure_collection(self):
        """Ensure the collection exists, create if it doesn't."""
        try:
            collections = self.client.get_collections().collections
            collection_names = [collection.name for collection in collections]

            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self._vector_size, distance=Distance.COSINE
                    ),
                )
                logger.info(
                    f"Created new Qdrant collection: {self.collection_name} with vector size: {self._vector_size}"
                )
            else:
                logger.info(f"Using existing Qdrant collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant collection: {e}")
            raise

    def add_to_collection(
        self, document: str, session_id: str, metadata: Dict = None, doc_id: str = None
    ):
        """Add a single document to the collection.

        Args:
            document: Text document to store
            session_id: Session ID
            metadata: Optional metadata dictionary
            doc_id: Optional document ID (will generate UUID if not provided)
        """
        try:
            if not doc_id:
                doc_id = str(uuid.uuid4())

            # Prepare metadata
            if metadata is None:
                metadata = {}
            metadata["text"] = document
            metadata["session_id"] = session_id
            metadata["timestamp"] = str(datetime.now())

            # Create point
            point = models.PointStruct(
                id=doc_id, vector=self.embed_text(document), payload=metadata
            )

            # Upsert point to collection (inserts if new, updates if exists)
            self.client.upsert(collection_name=self.collection_name, points=[point])
            logger.info(f"Successfully upserted document to Qdrant with ID: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add document to Qdrant: {e}")
            raise

    def upsert_document(
        self, document: str, session_id: str, doc_id: str, metadata: Dict = None
    ):
        """Upsert a document (insert if new, update if exists) using session_id as collection.

        Args:
            document: Text document to store/update
            session_id: Session ID (used as collection name)
            doc_id: Document ID (required for upsert)
            metadata: Optional metadata dictionary
        """
        try:
            # Prepare metadata
            if metadata is None:
                metadata = {}
            metadata["text"] = document
            metadata["session_id"] = session_id
            metadata["timestamp"] = str(datetime.now())

            # Create point
            point = models.PointStruct(
                id=doc_id, vector=self.embed_text(document), payload=metadata
            )

            # Upsert point to session collection
            self.client.upsert(collection_name=session_id, points=[point])
            logger.info(
                f"Successfully upserted document to session collection: {session_id} with ID: {doc_id}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to upsert document to session collection: {e}")
            raise

    def query_collection(
        self, query: str, n_results: int = 3, distance_threshold: float = 0.4
    ) -> Dict[str, Any]:
        """Query the collection.

        Args:
            query: The query text
            n_results: Number of results to return
            distance_threshold: Minimum similarity score

        Returns:
            Dict containing query results
        """
        try:
            # Search for similar documents
            logger.info(
                f"Querying collection: {self.collection_name} with query: {query}"
            )
            search_result = self.client.query_points(
                collection_name=self.collection_name,
                query=self.embed_text(query),
                limit=n_results,
                with_payload=True,
            ).points

            if not search_result:
                return {
                    "documents": [],
                    "session_id": [],
                    "distances": [],
                    "metadatas": [],
                    "ids": [],
                }

            # Filter by distance threshold and format results
            filtered_results = [
                hit for hit in search_result if hit.score >= distance_threshold
            ]

            results = {
                "documents": [hit.payload["text"] for hit in filtered_results],
                "session_id": [hit.payload["session_id"] for hit in filtered_results],
                "distances": [hit.score for hit in filtered_results],
                "metadatas": [hit.payload for hit in filtered_results],
                "ids": [hit.id for hit in filtered_results],
            }
            if len(results["documents"]) == 0:
                return "No relevant memory found"
            else:
                # filteer this corectly
                return results["documents"]
            logger.info(f"Retrieved {len(results['documents'])} results from Qdrant")
            return results
        except Exception as e:
            logger.error(f"Failed to query Qdrant: {e}")
            return "No relevant memory found"

    def delete_from_collection(self, doc_id: str = None, where: Dict = None):
        """Delete document from the collection.

        Args:
            doc_id: Document ID to delete
            where: Optional filter for deletion
        """
        try:
            if doc_id:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=models.PointIdsList(points=[doc_id]),
                )
                logger.info(f"Successfully deleted document with ID: {doc_id}")
            elif where:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=models.FilterSelector(
                        filter=models.Filter(
                            must=[
                                models.FieldCondition(
                                    key=key, match=models.MatchValue(value=value)
                                )
                                for key, value in where.items()
                            ]
                        )
                    ),
                )
                logger.info("Successfully deleted documents from Qdrant")
        except Exception as e:
            logger.error(f"Failed to delete document from Qdrant: {e}")
            raise

    def update_collection(
        self, document: str, session_id: str, doc_id: str, metadata: Dict = None
    ):
        """Update a single document in the collection.

        Args:
            document: Text document to update
            session_id: Session ID
            doc_id: Document ID to update (required)
            metadata: Optional metadata dictionary
        """
        if not doc_id:
            raise ValueError("doc_id is required for updating document")

        try:
            # Prepare metadata
            if metadata is None:
                metadata = {}
            metadata["text"] = document
            metadata["session_id"] = session_id
            metadata["timestamp"] = str(datetime.now())

            # Create point
            point = models.PointStruct(
                id=doc_id, vector=self.embed_text(document), payload=metadata
            )

            # Upsert point to collection
            self.client.upsert(collection_name=self.collection_name, points=[point])
            logger.info(f"Successfully updated document in Qdrant with ID: {doc_id}")
        except Exception as e:
            logger.error(f"Failed to update document in Qdrant: {e}")
            raise

    async def process_conversation_memory(
        self, messages: list, llm_connection: Callable
    ):
        """Process conversation memory only if 30min have passed since last summary. Summarize only new messages."""
        try:
            # Ensure collection exists (run in background)
            self._ensure_collection()
            # 1. Get the most recent summary (cached/scroll)
            most_recent = await self.get_most_recent_summary()
            last_end_time = None
            if most_recent and hasattr(most_recent, "payload"):
                last_end_time = most_recent.payload.get("end_time")
                if last_end_time and isinstance(last_end_time, str):
                    last_end_time = datetime.fromisoformat(last_end_time)
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
            # 2. Only proceed if at least 30min have passed since last summary
            if last_end_time is None:
                logger.info(
                    "No previous memory summary found (first run for this session). Proceeding to summarize all messages."
                )

            else:
                if (now - last_end_time).total_seconds() < 1800:
                    logger.info(f"Less than 30min since last memory summary, skipping.")
                    return
            # 3. Filter messages after last_end_time
            if last_end_time:
                logger.info(f"Last end time confirmed: {last_end_time}")
                # Only include messages with a valid timestamp greater than last_end_time
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
            # 4. Summarize and store
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
            self.invalidate_recent_summary_cache()
            logger.info(
                f"Successfully stored {self.memory_type} memory for session: {self.session_id}"
            )
        except Exception as e:
            logger.error(f"Error in background memory processing: {e}")

    async def _check_existing_memory(
        self, start_time: datetime, end_time: datetime
    ) -> bool:
        """Check if memory already exists for the given time period."""
        try:
            # Query for existing memories in the time range
            results = await self.query_collection_async(
                query=f"memory between {start_time.isoformat()} and {end_time.isoformat()}",
                n_results=1,
                distance_threshold=0.8,
            )

            # Check if any existing memories overlap with this time period
            for metadata in results.get("metadatas", []):
                existing_start = datetime.fromisoformat(metadata.get("start_time", ""))
                existing_end = datetime.fromisoformat(metadata.get("end_time", ""))

                # Check for overlap
                if start_time <= existing_end and end_time >= existing_start:
                    return True

            return False

        except Exception as e:
            logger.error(f"Error checking existing memory: {e}")
            return False

    def _format_conversation(self, messages: List[Any]) -> str:
        """Format conversation messages into a single text string, including metadata."""
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

    async def add_to_collection_async(
        self, doc_id: str, document: str, session_id: str, metadata: Dict
    ):
        """Async version of add_to_collection."""
        try:
            # Prepare rest of the metadata
            metadata["text"] = document
            metadata["session_id"] = session_id
            metadata["timestamp"] = str(datetime.now())

            # Create point
            point = models.PointStruct(
                id=doc_id, vector=self.embed_text(document), payload=metadata
            )

            # Upsert point to collection
            self.client.upsert(collection_name=self.collection_name, points=[point])
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
        """Async version of query_collection."""
        try:
            # Search for similar documents
            search_result = self.client.query_points(
                collection_name=self.collection_name,
                query=self.embed_text(query),
                limit=n_results,
                with_payload=True,
            ).points

            if not search_result:
                return {
                    "documents": [],
                    "session_id": [],
                    "distances": [],
                    "metadatas": [],
                    "ids": [],
                }

            # Filter by distance threshold and format results
            filtered_results = [
                hit for hit in search_result if hit.score >= distance_threshold
            ]

            results = {
                "documents": [hit.payload["text"] for hit in filtered_results],
                "session_id": [hit.payload["session_id"] for hit in filtered_results],
                "distances": [hit.score for hit in filtered_results],
                "metadatas": [hit.payload for hit in filtered_results],
                "ids": [hit.id for hit in filtered_results],
            }

            return results
        except Exception as e:
            logger.error(f"Failed to query collection: {e}")
            raise

    async def get_most_recent_summary(self) -> dict | None:
        """Fetch all points in the collection, return the most recent summary by end_time, with 30min cache."""
        cache_key = (self.collection_name, self.memory_type)
        now = time.time()
        # Check cache
        cached = _RECENT_SUMMARY_CACHE.get(cache_key)
        if cached:
            summary, cache_time = cached
            if now - cache_time < _CACHE_TTL:
                return summary
        # Not cached or expired, fetch all points
        points = []
        scroll_offset = None
        while True:
            batch_points, next_page_offset = self.client.scroll(
                collection_name=self.collection_name,
                limit=100,
                offset=scroll_offset,
                with_payload=True,
            )
            points.extend(batch_points)
            if not next_page_offset:
                break
            scroll_offset = next_page_offset
        if not points:
            _RECENT_SUMMARY_CACHE[cache_key] = (None, now)
            return None
        # Find most recent by end_time
        most_recent = max(points, key=lambda p: p.payload.get("end_time", ""))
        _RECENT_SUMMARY_CACHE[cache_key] = (most_recent, now)
        return most_recent

    def invalidate_recent_summary_cache(self):
        """Invalidate the cache for this collection/memory_type."""
        cache_key = (self.collection_name, self.memory_type)
        if cache_key in _RECENT_SUMMARY_CACHE:
            del _RECENT_SUMMARY_CACHE[cache_key]


async def fire_and_forget_memory_task(
    session_id, memory_type, validated_messages, llm_connection
):
    async def memory_task():
        try:
            db = QdrantVectorDB(session_id, memory_type)
            await db.process_conversation_memory(
                messages=validated_messages, llm_connection=llm_connection
            )
            logging.info(
                f"{memory_type} memory processing completed successfully for session {session_id}"
            )
        except Exception as e:
            logging.error(
                f"Error in {memory_type} memory processing for session {session_id}: {e}\n{traceback.format_exc()}"
            )

    task = asyncio.create_task(memory_task())

    def _handle_task_result(task):
        try:
            exc = task.exception()
            if exc:
                logging.error(
                    f"Background {memory_type} memory task error: {exc}", exc_info=exc
                )
        except asyncio.CancelledError:
            logging.warning(f"Background {memory_type} memory task was cancelled.")

    task.add_done_callback(_handle_task_result)
    return task
