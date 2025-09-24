from qdrant_client.http import models as rest
from qdrant_client.models import VectorParams, Distance
from omnicoreagent.core.utils import logger
from typing import Dict, Any
from qdrant_client import models
from decouple import config
from omnicoreagent.core.memory_store.memory_management.vector_db_base import (
    VectorDBBase,
)
from omnicoreagent.core.memory_store.memory_management.connection_manager import (
    get_connection_manager,
)


class QdrantVectorDB(VectorDBBase):
    """Qdrant vector database implementation."""

    def __init__(self, collection_name: str, **kwargs):
        """Initialize Qdrant vector database."""
        super().__init__(collection_name, **kwargs)

        # Check if this is for background processing
        self.is_background = kwargs.get("is_background", False)

        # Get Qdrant configuration
        self.qdrant_host = config("QDRANT_HOST", default=None)
        self.qdrant_port = config("QDRANT_PORT", default=None)

        if self.qdrant_host and self.qdrant_port:
            try:
                if self.is_background:
                    # Background processing gets fresh connections - no pooling to avoid interference
                    from qdrant_client import QdrantClient

                    self.client = QdrantClient(
                        host=self.qdrant_host, port=self.qdrant_port
                    )
                    self.connection_manager = (
                        None  # No connection manager for background
                    )
                    logger.debug(
                        f"Background QdrantVectorDB created fresh connection for: {collection_name}"
                    )
                else:
                    # Main thread gets pooled connections
                    self.connection_manager = get_connection_manager()
                    self.client = self.connection_manager.get_qdrant_connection(
                        self.qdrant_host, self.qdrant_port
                    )
                    logger.debug(
                        f"QdrantVectorDB using pooled connection for: {collection_name}"
                    )

                self.enabled = self.client is not None
            except Exception as e:
                logger.error(f"Failed to initialize Qdrant connection: {e}")
                self.client = None
                self.enabled = False
        else:
            self.enabled = False
            self.client = None
            self.connection_manager = None
            logger.warning(
                f"QDRANT_HOST or QDRANT_PORT not set. Qdrant will be disabled for collection: {collection_name}"
            )

    def __del__(self):
        """Cleanup method to release connection back to pool."""
        try:
            # Only release if we have a connection manager
            if (
                hasattr(self, "connection_manager")
                and self.connection_manager is not None
            ):
                self.connection_manager.release_connection("qdrant")
        except Exception:
            # Ignore errors during cleanup
            pass

    def _ensure_collection(self):
        """Ensure the collection exists, create if it doesn't."""
        if not self.enabled:
            logger.warning("Qdrant is not enabled. Cannot ensure collection.")
            return
        actual_vector_size = self._get_embedding_dimensions()
        if not isinstance(actual_vector_size, int):
            raise ValueError(
                f"Vector size must be set before creating a collection. Got: {actual_vector_size}"
            )

        try:
            collections = self.client.get_collections().collections
            collection_names = [collection.name for collection in collections]

            if self.collection_name not in collection_names:
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
            # check the metadata to see if it has mcp_server_name key
            mcp_server_name = metadata.get("mcp_server_name", None)

            metadata["text"] = document

            # Generate embedding with error handling
            try:
                updated_document = None
                if not mcp_server_name:
                    updated_document = document
                else:
                    updated_document = document["enriched_tool"]
                vector = self.embed_text(updated_document)
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
        self,
        query: str,
        n_results: int,
        similarity_threshold: float,
        session_id: str = None,
        mcp_server_names: list[str] = None,
    ):
        if not self.enabled:
            return {"documents": []}

        try:
            # Build filter conditions
            must_conditions = []

            if session_id is not None:
                must_conditions.append(
                    rest.FieldCondition(
                        key="session_id", match=rest.MatchValue(value=session_id)
                    )
                )
            elif mcp_server_names:
                must_conditions.append(
                    rest.FieldCondition(
                        key="mcp_server_name",
                        match=rest.MatchAny(any=mcp_server_names),
                    )
                )

            # Only add Filter if there’s at least one condition
            query_filter = (
                rest.Filter(must=must_conditions) if must_conditions else None
            )

            search_result = self.client.query_points(
                collection_name=self.collection_name,
                query=self.embed_text(query),
                limit=n_results,
                with_payload=True,
                query_filter=query_filter,
            ).points

            filtered_results = [
                hit for hit in search_result if hit.score >= similarity_threshold
            ]

            return {
                "documents": [hit.payload["text"] for hit in filtered_results],
                "scores": [hit.score for hit in filtered_results],
                "metadatas": [hit.payload for hit in filtered_results],
                "ids": [hit.id for hit in filtered_results],
            }

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
