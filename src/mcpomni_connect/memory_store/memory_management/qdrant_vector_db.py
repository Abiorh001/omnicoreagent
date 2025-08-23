from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from mcpomni_connect.utils import logger
from typing import Dict, Any, Optional
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
                actual_vector_size = self._vector_size

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

    def add_to_collection(self, doc_id: str, document: str, metadata: Dict) -> bool:
        """for adding to collection."""
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
            except Exception:
                return False

            # Create point
            point = models.PointStruct(id=doc_id, vector=vector, payload=metadata)

            # Upsert the point
            self.client.upsert(
                collection_name=self.collection_name, points=[point], wait=True
            )

            return True
        except Exception:
            return False

    def query_collection(
        self, query: str, n_results: int, distance_threshold: float
    ) -> Dict[str, Any]:
        """for querying collection."""
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
