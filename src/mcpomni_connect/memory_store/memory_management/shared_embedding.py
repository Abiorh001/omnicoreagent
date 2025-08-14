"""
Shared embedding model for vector database operations.
This module loads the embedding model only when enabled via config.
"""

import os
import re
from decouple import config
from mcpomni_connect.utils import logger

# Vector database feature flag
ENABLE_VECTOR_DB = config("ENABLE_VECTOR_DB", default=False, cast=bool)

# Default vector size fallback
NOMIC_VECTOR_SIZE = 768

# Internal shared model instance
_EMBED_MODEL = None


def _initialize_embedding_system():
    """Initialize the embedding system only when vector DB is enabled."""
    global _EMBED_MODEL, NOMIC_VECTOR_SIZE

    if not ENABLE_VECTOR_DB:
        logger.debug(
            "Vector database disabled - skipping embedding system initialization"
        )
        return

    try:
        # Force import and load the sentence transformer
        logger.debug("[Warmup] Loading sentence transformer model...")

        # Import SentenceTransformer
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            logger.error(
                "sentence_transformers not available - cannot initialize embedding system"
            )
            return

        if SentenceTransformer is None:
            logger.error("Failed to import SentenceTransformer")
            return

        # Load the model
        logger.debug("[Warmup] Initializing nomic-ai/nomic-embed-text-v1 model...")
        _EMBED_MODEL = SentenceTransformer(
            "nomic-ai/nomic-embed-text-v1", trust_remote_code=True
        )

        # Warm up the model with test embeddings
        logger.debug("[Warmup] Warming up embedding model...")
        test_embedding = _EMBED_MODEL.encode("test")
        NOMIC_VECTOR_SIZE = len(test_embedding)

        # Additional warm-up calls to eliminate first-call delay
        warmup_texts = [
            "short",
            "medium length text for testing",
            "this is a longer text that should help warm up the model completely",
        ]

        for text in warmup_texts:
            warmup_embedding = _EMBED_MODEL.encode(text)
            if len(warmup_embedding) != NOMIC_VECTOR_SIZE:
                raise ValueError(
                    f"Warm-up failed: expected {NOMIC_VECTOR_SIZE}, got {len(warmup_embedding)}"
                )

        logger.debug(
            f"[Warmup] Embedding model ready. Vector size: {NOMIC_VECTOR_SIZE}"
        )

    except Exception as e:
        logger.error(f"[Warmup] ❌ Failed to load embedding model: {e}")
        _EMBED_MODEL = None
        raise RuntimeError(f"Failed to initialize embedding system: {e}")


# Only initialize if vector DB is enabled
if ENABLE_VECTOR_DB:
    _initialize_embedding_system()


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
        logger.warning("Text truncated to 8192 characters for embedding")

    if not text or text.isspace() or len(text) < 5:
        return "default placeholder text for consistent embedding dimensions"

    return text


def is_vector_db_enabled() -> bool:
    """Check if vector database features are enabled."""
    return ENABLE_VECTOR_DB
