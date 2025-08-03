from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from mcpomni_connect.utils import logger
from mcpomni_connect.memory_store.memory_management.shared_embedding import (
    get_embed_model,
    embed_text,
    NOMIC_VECTOR_SIZE,
)


class VectorDBBase(ABC):
    """Base class for vector database operations - CORE OPERATIONS ONLY."""

    def __init__(self, collection_name: str, **kwargs):
        """Initialize vector database with collection name.
        Args:
            collection_name: Name of the collection/namespace
            **kwargs: Additional parameters
        """
        self.collection_name = collection_name
        self._embed_model = get_embed_model()
        self._vector_size = NOMIC_VECTOR_SIZE
        self.enabled = False
        for key, value in kwargs.items():
            setattr(self, key, value)

    def embed_text(self, text: str) -> List[float]:
        """Embed text using shared nomic-ai/nomic-embed-text-v1 model."""
        return embed_text(text)

    @abstractmethod
    def _ensure_collection(self):
        """Ensure the collection exists, create if it doesn't."""
        pass

    @abstractmethod
    def upsert_document(
        self, document: str, doc_id: str, metadata: Optional[Dict] = None
    ) -> bool:
        """Upsert a document (insert if new, update if exists)."""
        pass

    @abstractmethod
    def query_collection(
        self, query: str, n_results: int, distance_threshold: float
    ) -> Any:
        """Query the collection for similar documents."""
        pass

    @abstractmethod
    def delete_from_collection(
        self, doc_id: Optional[str] = None, where: Optional[Dict] = None
    ):
        """Delete document from the collection."""
        pass

    @abstractmethod
    async def add_to_collection_async(
        self, doc_id: str, document: str, metadata: Dict
    ) -> bool:
        """Async wrapper for adding to collection."""
        pass

    @abstractmethod
    async def query_collection_async(
        self, query: str, n_results: int, distance_threshold: float
    ) -> Dict[str, Any]:
        """Async wrapper for querying collection."""
        pass
