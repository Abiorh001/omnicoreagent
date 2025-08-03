from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
import os
from mcpomni_connect.utils import logger
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, timezone
from qdrant_client import models
from decouple import config
from mcpomni_connect.memory_store.memory_management.vector_db_base import VectorDBBase

# ==== 🔥 Warm up Qdrant client at module import ====
_qdrant_client = None
_qdrant_enabled = False
_qdrant_host = config("QDRANT_HOST", default=None)
_qdrant_port = config("QDRANT_PORT", default=None)

# Try to initialize Qdrant
if _qdrant_host and _qdrant_port:
    try:
        _qdrant_client = QdrantClient(host=_qdrant_host, port=_qdrant_port)
        _qdrant_enabled = True
        logger.debug("[Warmup] Qdrant client initialized successfully.")
    except Exception as e:
        logger.error(f"[Warmup] Failed to initialize Qdrant client: {e}")
        _qdrant_enabled = False
else:
    logger.warning(
        "[Warmup] QDRANT_HOST or QDRANT_PORT not set. Qdrant will be disabled."
    )


class QdrantVectorDB(VectorDBBase):
    """Qdrant vector database implementation."""

    def __init__(self, collection_name: str, **kwargs):
        """Initialize Qdrant vector database."""
        super().__init__(collection_name, **kwargs)

        self.qdrant_host = _qdrant_host
        self.qdrant_port = _qdrant_port

        if _qdrant_enabled:
            self.client = _qdrant_client
            self.enabled = True
            logger.debug(
                f"Initialized QdrantVectorDB for collection: {collection_name}"
            )
        else:
            self.enabled = False
            logger.warning(
                f"Qdrant not available. VectorDB operations will be disabled for collection: {collection_name}"
            )

    def _ensure_collection(self):
        """Ensure the collection exists, create if it doesn't."""
        if not self.enabled:
            logger.warning("Qdrant is not enabled. Cannot ensure collection.")
            return

        try:
            collections = self.client.get_collections().collections
            collection_names = [collection.name for collection in collections]

            if self.collection_name not in collection_names:
                # Get the actual vector size from the shared embedding module
                from mcpomni_connect.memory_store.memory_management.shared_embedding import (
                    NOMIC_VECTOR_SIZE,
                )

                actual_vector_size = NOMIC_VECTOR_SIZE

                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=actual_vector_size, distance=Distance.COSINE
                    ),
                )
                logger.debug(
                    f"Created new Qdrant collection: {self.collection_name} with vector size: {actual_vector_size}"
                )
            else:
                logger.debug(
                    f"Using existing Qdrant collection: {self.collection_name}"
                )
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant collection: {e}")
            raise

    def upsert_document(
        self, document: str, doc_id: str, metadata: Optional[Dict] = None
    ) -> bool:
        """Upsert a document (insert if new, update if exists)."""
        if not self.enabled:
            logger.warning("Qdrant is not enabled. Cannot upsert document.")
            return False

        try:
            # Ensure collection exists
            self._ensure_collection()

            # Prepare metadata
            if metadata is None:
                metadata = {}
            metadata["text"] = document
            metadata["timestamp"] = str(datetime.now())

            # Generate embedding with error handling
            try:
                vector = self.embed_text(document)
                logger.debug(f"Generated embedding of size: {len(vector)}")
            except Exception as e:
                logger.error(f"Failed to generate embedding for document: {e}")
                logger.error(f"Document preview: {document[:200]}...")
                return False

            # Create point
            point = models.PointStruct(id=doc_id, vector=vector, payload=metadata)

            # Upsert the point
            self.client.upsert(
                collection_name=self.collection_name, points=[point], wait=True
            )

            logger.debug(f"Successfully upserted memory to Qdrant: {doc_id}")

            return True
        except Exception as e:
            logger.error(f"Failed to upsert document to Qdrant: {e}")
            return False

    def query_collection(
        self, query: str, n_results: int, distance_threshold: float
    ) -> Any:
        """Query the collection for similar documents."""
        if not self.enabled:
            logger.warning("Qdrant is not enabled. Cannot query collection.")
            return "No relevant documents found"

        try:
            # Search for similar documents
            logger.debug(
                f"Querying Qdrant collection: {self.collection_name} with query: {query}"
            )
            search_result = self.client.query_points(
                collection_name=self.collection_name,
                query=self.embed_text(query),
                limit=n_results,
                with_payload=True,
            ).points

            logger.debug(f"Found {len(search_result)} raw results from Qdrant")

            if not search_result:
                return {
                    "documents": [],
                    "session_id": [],
                    "distances": [],
                    "metadatas": [],
                    "ids": [],
                }

            # Log all scores before filtering
            all_scores = [hit.score for hit in search_result]
            

            # Filter by distance threshold and format results
            filtered_results = [
                hit for hit in search_result if hit.score >= distance_threshold
            ]

            logger.debug(f"Found {len(filtered_results)} results after filtering")

            results = {
                "documents": [hit.payload["text"] for hit in filtered_results],
                "session_id": [
                    hit.payload.get("session_id", "") for hit in filtered_results
                ],
                "distances": [hit.score for hit in filtered_results],
                "metadatas": [hit.payload for hit in filtered_results],
                "ids": [hit.id for hit in filtered_results],
            }

            if len(results["documents"]) == 0:
                return "No relevant documents found"
            else:
                return results["documents"]

        except Exception as e:
            # Silently handle 404 errors (collection doesn't exist yet)
            if "404" in str(e) or "doesn't exist" in str(e):
                logger.debug(
                    f"Collection {self.collection_name} doesn't exist yet, returning empty results"
                )
                return "No relevant documents found"
            else:
                logger.error(f"Failed to query Qdrant: {e}")
                return "No relevant documents found"

    def delete_from_collection(
        self, doc_id: Optional[str] = None, where: Optional[Dict] = None
    ):
        """Delete document from the collection."""
        if not self.enabled:
            logger.warning("Qdrant is not enabled. Cannot delete from collection.")
            return

        try:
            if doc_id:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=models.PointIdsList(points=[doc_id]),
                )
                logger.debug(f"Successfully deleted document with ID: {doc_id}")
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
                logger.debug("Successfully deleted documents from Qdrant")
        except Exception as e:
            logger.error(f"Failed to delete document from Qdrant: {e}")
            raise

    async def add_to_collection_async(
        self, doc_id: str, document: str, metadata: Dict
    ) -> bool:
        """Async wrapper for adding to collection."""
        if not self.enabled:
            logger.warning("Qdrant is not enabled. Cannot add to collection.")
            return False

        try:
            # Ensure collection exists
            self._ensure_collection()

            # Prepare metadata with consistent timestamp
            current_time = datetime.now(timezone.utc)
            metadata["text"] = document
            metadata["timestamp"] = current_time.isoformat()

            # Generate embedding with error handling
            try:
                vector = self.embed_text(document)
            except Exception as e:
                return False

            # Create point
            point = models.PointStruct(id=doc_id, vector=vector, payload=metadata)

            # Upsert the point
            self.client.upsert(
                collection_name=self.collection_name, points=[point], wait=True
            )

            return True
        except Exception as e:
            return False

    async def query_collection_async(
        self, query: str, n_results: int, distance_threshold: float
    ) -> Dict[str, Any]:
        """Async wrapper for querying collection."""
        if not self.enabled:
            logger.warning("Qdrant is not enabled. Cannot query collection.")
            return {"documents": []}

        try:
            # Search for similar documents
            logger.debug(
                f"Async querying Qdrant collection: {self.collection_name} with query: {query}"
            )
            search_result = self.client.query_points(
                collection_name=self.collection_name,
                query=self.embed_text(query),
                limit=n_results,
                with_payload=True,
            ).points

            logger.debug(f"Found {len(search_result)} raw results from Qdrant")

            if not search_result:
                return {
                    "documents": [],
                    "session_id": [],
                    "distances": [],
                    "metadatas": [],
                    "ids": [],
                }

            # Log all scores before filtering
            all_scores = [hit.score for hit in search_result]
            

            # Filter by distance threshold and format results
            filtered_results = [
                hit for hit in search_result if hit.score >= distance_threshold
            ]

            logger.debug(f"Found {len(filtered_results)} results after filtering")

            results = {
                "documents": [hit.payload["text"] for hit in filtered_results],
                "session_id": [
                    hit.payload.get("session_id", "") for hit in filtered_results
                ],
                "distances": [hit.score for hit in filtered_results],
                "metadatas": [hit.payload for hit in filtered_results],
                "ids": [hit.id for hit in filtered_results],
            }

            return results

        except Exception as e:
            # Silently handle 404 errors (collection doesn't exist yet)
            if "404" in str(e) or "doesn't exist" in str(e):
                logger.debug(
                    f"Collection {self.collection_name} doesn't exist yet, returning empty results"
                )
                return {"documents": []}
            else:
                logger.error(f"Failed to query Qdrant: {e}")
                return {"documents": []}

    async def get_all_documents_async(self) -> Dict[str, Any]:
        """Get all documents from the collection without semantic search."""
        if not self.enabled:
            logger.warning("Qdrant is not enabled. Cannot get documents.")
            return {"documents": []}

        try:
            logger.debug(
                f"Getting all documents from Qdrant collection: {self.collection_name}"
            )

            # Use scroll to get all documents
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

            logger.debug(f"Found {len(points)} total documents in collection")

            if not points:
                return {
                    "documents": [],
                    "session_id": [],
                    "distances": [],
                    "metadatas": [],
                    "ids": [],
                }

            results = {
                "documents": [point.payload["text"] for point in points],
                "session_id": [point.payload.get("session_id", "") for point in points],
                "distances": [1.0] * len(points),  # All documents have perfect match
                "metadatas": [point.payload for point in points],
                "ids": [point.id for point in points],
            }

            return results

        except Exception as e:
            # Silently handle 404 errors (collection doesn't exist yet)
            if "404" in str(e) or "doesn't exist" in str(e):
                logger.debug(
                    f"Collection {self.collection_name} doesn't exist yet, returning empty results"
                )
                return {"documents": []}
            else:
                logger.error(f"Failed to get all documents from Qdrant: {e}")
                return {"documents": []}
