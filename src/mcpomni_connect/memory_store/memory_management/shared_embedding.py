"""
Shared embedding model for vector database operations.
This module loads the embedding model only when enabled via config.
"""

import re
from mcpomni_connect.utils import logger
from decouple import config

# Conditional import to avoid loading sentence_transformers when not needed
SentenceTransformer = None
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    pass

# Vector database feature flag
ENABLE_VECTOR_DB = config("ENABLE_VECTOR_DB", default=False, cast=bool)

# Default vector size fallback
NOMIC_VECTOR_SIZE = 768

# Internal shared model instance
_EMBED_MODEL = None

# Load immediately if enabled (like before)
if ENABLE_VECTOR_DB:
    try:
        if SentenceTransformer is not None:
            _EMBED_MODEL = SentenceTransformer(
                "nomic-ai/nomic-embed-text-v1", trust_remote_code=True
            )
            # Dynamically get actual vector size
            test_embedding = _EMBED_MODEL.encode("test")
            NOMIC_VECTOR_SIZE = len(test_embedding)
            logger.debug(
                f"[Warmup] Shared embedding model loaded. Vector size: {NOMIC_VECTOR_SIZE}"
            )
        else:
            logger.warning("sentence_transformers not available")
    except Exception as e:
        logger.error(f"[Warmup] Failed to load shared embedding model: {e}")
        _EMBED_MODEL = None


def load_embed_model():
    """Load the embedding model if enabled. Called manually during app startup."""
    # Model is already loaded at module level if enabled
    pass


def get_embed_model():
    """Get the shared embedding model instance, with safety check."""
    if not ENABLE_VECTOR_DB:
        raise RuntimeError("Vector database is disabled by configuration")
    if _EMBED_MODEL is None:
        raise RuntimeError("Embedding model not loaded. Call load_embed_model() first.")
    return _EMBED_MODEL


def embed_text(text: str) -> list[float]:
    """Embed text using the shared nomic model with proper text cleaning."""
    if not ENABLE_VECTOR_DB:
        raise RuntimeError("Vector database is disabled by configuration")

    if not _EMBED_MODEL:
        raise RuntimeError("Embedding model not loaded. Call load_embed_model() first.")

    try:
        cleaned_text = clean_text_for_embedding(text)
        embedding = _EMBED_MODEL.encode(cleaned_text)

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

    text = re.sub(r"[^\w\s\.\,\!\?\:\;\-\(\)\[\]\{\}]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    if len(text) < 10:
        text = f"content summary: {text} additional context for consistent embedding"

    if len(text) > 8192:
        text = text[:8192]
        logger.warning(f"Text truncated to 8192 characters for embedding")

    if not text or text.isspace() or len(text) < 5:
        return "default placeholder text for consistent embedding dimensions"

    return text


def is_vector_db_enabled() -> bool:
    """Check if vector database features are enabled."""
    return ENABLE_VECTOR_DB
