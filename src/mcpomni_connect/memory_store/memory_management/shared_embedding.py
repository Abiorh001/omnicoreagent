"""
Shared embedding model for vector database operations.
This module loads the embedding model once and provides it to both Qdrant and ChromaDB classes.
"""

from sentence_transformers import SentenceTransformer
from mcpomni_connect.utils import logger
import re

# Updated vector size for nomic-embed-text-v1 (latest version)
NOMIC_VECTOR_SIZE = 768  # This will be updated dynamically

# ==== 🔥 Eagerly load and warm up embedding model at module import ====
_EMBED_MODEL = None

try:
    _EMBED_MODEL = SentenceTransformer(
        "nomic-ai/nomic-embed-text-v1", trust_remote_code=True
    )
    # Get actual vector size from the model
    test_embedding = _EMBED_MODEL.encode("test")
    NOMIC_VECTOR_SIZE = len(test_embedding)
    logger.debug(
        f"[Warmup] Shared embedding model loaded. Vector size: {NOMIC_VECTOR_SIZE}"
    )
except Exception as e:
    logger.error(f"[Warmup] Failed to load shared embedding model: {e}")


def get_embed_model():
    """Get the shared embedding model instance."""
    return _EMBED_MODEL


def embed_text(text: str) -> list[float]:
    """Embed text using the shared nomic model with proper text cleaning."""
    try:
        if not _EMBED_MODEL:
            raise ValueError("Shared embedding model not loaded")

        # Clean the text first to avoid tensor dimension issues
        cleaned_text = clean_text_for_embedding(text)

        # Generate embedding
        embedding = _EMBED_MODEL.encode(cleaned_text)

        # Validate embedding size
        if len(embedding) != NOMIC_VECTOR_SIZE:
            logger.error(
                f"Embedding size mismatch: expected {NOMIC_VECTOR_SIZE}, got {len(embedding)}"
            )
            logger.error(f"Original text length: {len(text) if text else 0}")
            logger.error(f"Cleaned text length: {len(cleaned_text)}")
            raise ValueError(
                f"Embedding dim mismatch: got {len(embedding)}, expected {NOMIC_VECTOR_SIZE}"
            )

        return embedding.tolist()
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        if "cleaned_text" in locals():
            logger.error(f"Cleaned text preview: {cleaned_text[:200]}...")
        raise


def clean_text_for_embedding(text: str) -> str:
    """Clean and prepare text for embedding to avoid tensor dimension issues."""
    if not text or not isinstance(text, str):
        return "default placeholder text for empty content"

    # Remove or replace problematic characters
    text = re.sub(r"[^\w\s\.\,\!\?\:\;\-\(\)\[\]\{\}]", " ", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Ensure minimum length to avoid tensor dimension issues
    if len(text) < 10:
        text = f"content summary: {text} additional context for consistent embedding"

    # Truncate if too long (nomic-embed-text-v1 has a limit)
    if len(text) > 8192:
        text = text[:8192]
        logger.warning(f"Text truncated to 8192 characters for embedding")

    # Final check - ensure we have adequate content
    if not text or text.isspace() or len(text) < 5:
        return "default placeholder text for consistent embedding dimensions"

    return text
