from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from mcpomni_connect.utils import logger, is_vector_db_enabled
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

        # Check if vector DB is enabled
        if not is_vector_db_enabled():
            self._embed_model = None
            self._vector_size = NOMIC_VECTOR_SIZE
            self.enabled = False
        else:
            try:
                self._embed_model = get_embed_model()
                self._vector_size = NOMIC_VECTOR_SIZE
                self.enabled = True
            except Exception as e:
                logger.warning(f"Failed to initialize embedding model: {e}")
                self._embed_model = None
                self.enabled = False

        for key, value in kwargs.items():
            setattr(self, key, value)

    def embed_text(self, text: str) -> List[float]:
        """Embed text using shared nomic-ai/nomic-embed-text-v1 model."""
        if not is_vector_db_enabled():
            raise RuntimeError("Vector database is disabled by configuration")
        return embed_text(text)

    @abstractmethod
    def _ensure_collection(self):
        """Ensure the collection exists, create if it doesn't."""
        raise NotImplementedError

    @abstractmethod
    def add_to_collection(self, doc_id: str, document: str, metadata: Dict) -> bool:
        """for adding to collection."""
        raise NotImplementedError

    @abstractmethod
    def query_collection(
        self, query: str, n_results: int, distance_threshold: float
    ) -> Dict[str, Any]:
        """for querying collection."""
        raise NotImplementedError
