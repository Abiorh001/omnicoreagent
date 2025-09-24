from abc import ABC, abstractmethod
from typing import List, Dict, Any
from omnicoreagent.core.utils import (
    logger,
    is_vector_db_enabled,
    is_embedding_requirements_met,
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

        self.llm_connection = kwargs.pop("llm_connection", None)

        # Check if vector DB is enabled
        if not is_vector_db_enabled():
            self._embed_model = None
            self._vector_size = None
            self.enabled = False
        else:
            # Check if embedding requirements are met
            if not is_embedding_requirements_met():
                logger.error(
                    "Vector database is enabled but no embedding API key is set"
                )
                self._embed_model = None
                self._vector_size = None
                self.enabled = False
            elif not self.llm_connection:
                logger.error(
                    "LLM connection is required for vector database operations"
                )
                self._embed_model = None
                self._vector_size = None
                self.enabled = False
            else:
                self._embed_model = None
                self._vector_size = None
                self.enabled = True
                logger.debug("Using LLM-based embedding via LiteLLM")

        for key, value in kwargs.items():
            setattr(self, key, value)

    def embed_text(self, text: str) -> List[float]:
        """Embed text using LLM connection via LiteLLM with smart chunking for long texts."""
        if not is_vector_db_enabled():
            raise RuntimeError("Vector database is disabled by configuration")

        if not is_embedding_requirements_met():
            raise RuntimeError(
                "Vector database is enabled but no embedding API key is set"
            )

        if not self.llm_connection:
            raise RuntimeError(
                "LLM connection is required for vector database operations"
            )

        if not text or not isinstance(text, str):
            raise ValueError("Text input must be a non-empty string")

        try:
            logger.debug(f"Attempting to embed text of length: {len(text)} characters")
            response = self.llm_connection.embedding_call_sync([text])

            if response is None:
                logger.warning(
                    "Embedding call returned None, this might be due to rate limits or temporary failure"
                )
                raise RuntimeError("Embedding service temporarily unavailable")

            return self._process_embedding_response(response)

        except Exception as e:
            error_msg = str(e).lower()

            if any(
                keyword in error_msg
                for keyword in ["token", "length", "too long", "exceed", "limit"]
            ):
                logger.info(
                    f"Text too long for single embedding, implementing smart chunking: {e}"
                )
                return self._embed_text_with_chunking(text)
            else:
                # Re-raise if it's not a token limit error
                logger.error(f"LLM embedding failed: {e}")
                raise RuntimeError(f"Failed to generate embedding: {e}")

    def _embed_text_with_chunking(self, text: str) -> List[float]:
        """Embed long text by splitting into 500-character chunks and processing."""
        try:
            # Split text into 500-character chunks
            chunk_size = 500
            chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
            logger.info(
                f"Split text into {len(chunks)} chunks of max {chunk_size} characters"
            )

            all_embeddings = []

            for i, chunk in enumerate(chunks):
                logger.debug(
                    f"Processing chunk {i + 1}/{len(chunks)}: {len(chunk)} characters"
                )

                try:
                    response = self.llm_connection.embedding_call_sync([chunk])

                    if response is None:
                        logger.warning(
                            f"Chunk {i + 1} embedding call returned None, this might be due to rate limits or temporary failure"
                        )
                        raise RuntimeError("Embedding service temporarily unavailable")

                    chunk_embedding = self._process_embedding_response(response)
                    all_embeddings.append(chunk_embedding)

                except Exception as chunk_error:
                    logger.error(f"Failed to embed chunk {i + 1}: {chunk_error}")
                    raise RuntimeError(f"Chunk {i + 1} embedding failed: {chunk_error}")

            if not all_embeddings:
                raise RuntimeError("All chunk embeddings failed")

            if self._vector_size is None:
                self._vector_size = len(all_embeddings[0])

            combined_embedding = []
            for i in range(self._vector_size):
                values = [emb[i] for emb in all_embeddings]
                combined_embedding.append(sum(values) / len(values))

            logger.debug(
                f"Successfully combined {len(all_embeddings)} chunk embeddings into single vector"
            )
            return combined_embedding

        except Exception as e:
            logger.error(f"Chunking-based embedding failed: {e}")
            raise RuntimeError(f"Failed to embed text with chunking: {e}")

    def _process_embedding_response(self, response) -> List[float]:
        """Process the embedding response and extract the embedding vector."""
        # Validate response structure
        if not response:
            raise RuntimeError("LLM embedding returned None response")

        if not hasattr(response, "data") or not response.data:
            raise RuntimeError("LLM embedding response missing data field")

        if not isinstance(response.data, list) or len(response.data) == 0:
            raise RuntimeError("LLM embedding response data is empty or invalid")

        embedding_data = response.data[0]

        # Extract embedding from response
        if isinstance(embedding_data, dict) and "embedding" in embedding_data:
            embedding = embedding_data["embedding"]
        elif hasattr(embedding_data, "embedding"):
            embedding = embedding_data.embedding
        else:
            raise RuntimeError("LLM embedding response missing embedding field")

        # If embedding is a string (base64), decode it
        if isinstance(embedding, str):
            try:
                import base64
                import numpy as np

                decoded = base64.b64decode(embedding)
                embedding = np.frombuffer(decoded, dtype=np.float32).tolist()
                logger.debug(
                    f"Converted base64 embedding to {len(embedding)} float values"
                )
            except Exception as e:
                logger.error(f"Failed to decode base64 embedding: {e}")
                raise RuntimeError(f"Failed to decode base64 embedding: {e}")

        if not isinstance(embedding, (list, tuple)) or len(embedding) == 0:
            raise RuntimeError("LLM embedding is not a valid numeric array")

        if self._vector_size is None:
            self._vector_size = len(embedding)
        elif self._vector_size != len(embedding):
            logger.warning(
                f"Embedding dimension mismatch: expected {self._vector_size}, got {len(embedding)}"
            )
            self._vector_size = len(embedding)

        return list(embedding)

    def _get_embedding_dimensions(self) -> int:
        """Get embedding dimensions from configuration - STRICT MODE."""
        if not self.llm_connection:
            raise ValueError("LLM connection is required to get embedding dimensions")

        if not hasattr(self.llm_connection, "embedding_config"):
            raise ValueError("LLM connection does not have embedding configuration")

        embedding_config = self.llm_connection.embedding_config
        if not embedding_config:
            raise ValueError("Embedding configuration is not available")

        if "dimensions" not in embedding_config:
            raise ValueError("Embedding configuration is missing 'dimensions' field")

        dimensions = embedding_config["dimensions"]
        if not isinstance(dimensions, int) or dimensions <= 0:
            raise ValueError(
                f"Invalid dimensions value: {dimensions}. Must be a positive integer."
            )

        return dimensions

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts efficiently with smart chunking for long texts."""
        if not texts:
            return []

        embeddings = []
        for text in texts:
            try:
                embedding = self.embed_text(text)
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Failed to embed text: {text[:50]}... Error: {e}")
                raise RuntimeError(f"Failed to embed text: {e}")

        return embeddings

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
        self,
        query: str,
        n_results: int,
        similarity_threshold: float,
        session_id: str,
        mcp_server_names: list[str],
    ) -> Dict[str, Any]:
        """for querying collection."""
        raise NotImplementedError
