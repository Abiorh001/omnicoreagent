"""
Shared embedding model for vector database operations.
This module loads the embedding model once and provides it to both Qdrant and ChromaDB classes.
"""

from sentence_transformers import SentenceTransformer
from mcpomni_connect.utils import logger

NOMIC_VECTOR_SIZE = 768

# ==== 🔥 Eagerly load and warm up embedding model at module import ====
_EMBED_MODEL = None

try:
    _EMBED_MODEL = SentenceTransformer(
        "nomic-ai/nomic-embed-text-v1", trust_remote_code=True
    )
    _ = _EMBED_MODEL.encode("warmup")  # Force lazy-load model weights
    logger.info(
        "[Warmup] Shared embedding model 'nomic-ai/nomic-embed-text-v1' loaded successfully."
    )
except Exception as e:
    logger.error(f"[Warmup] Failed to load shared embedding model: {e}")


def get_embed_model():
    """Get the shared embedding model instance."""
    return _EMBED_MODEL


def embed_text(text: str) -> list[float]:
    """Embed text using the shared nomic-ai/nomic-embed-text-v1 model."""
    try:
        if not _EMBED_MODEL:
            raise ValueError("Shared embedding model not loaded")
        embedding = _EMBED_MODEL.encode(text).tolist()
        return embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise
