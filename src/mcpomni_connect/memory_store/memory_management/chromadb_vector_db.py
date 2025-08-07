import os
from enum import Enum
from mcpomni_connect.utils import logger

# Try to import ChromaDB with proper error handling
try:
    import chromadb
    from chromadb.config import Settings

    CHROMADB_AVAILABLE = True
except ImportError as e:
    logger.error(f"ChromaDB not available: {e}")
    logger.warning("Install ChromaDB with: pip install chromadb")
    CHROMADB_AVAILABLE = False
    chromadb = None
    Settings = None
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from mcpomni_connect.memory_store.memory_management.vector_db_base import VectorDBBase
from decouple import config

# ==== 🔥 Warm up ChromaDB client at module import ====
_chroma_client = None
_chroma_enabled = False
_warmed_collections = {}  # Cache for pre-created collections


def _initialize_chromadb():
    """Initialize and warm up ChromaDB client with aggressive pre-loading."""
    global _chroma_client, _chroma_enabled
    if not CHROMADB_AVAILABLE:
        return

    try:
        logger.debug("[Warmup] Starting ChromaDB warmup")

        # Create warm-up directory
        chroma_warmup_dir = os.path.join(os.getcwd(), ".chroma_warmup")
        os.makedirs(chroma_warmup_dir, exist_ok=True)

        # Create a lightweight client for warmup with optimized settings
        _chroma_client = chromadb.PersistentClient(
            path=chroma_warmup_dir,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )

        # Pre-create a test collection to warm up the entire pipeline
        try:
            test_collection = _chroma_client.get_or_create_collection(
                name="warmup_test_collection",
                metadata={"description": "Warmup collection"},
            )
            # Add a tiny test document to warm up embedding pipeline
            test_collection.add(
                documents=["warmup test document"],
                ids=["warmup_id"],
                metadatas=[{"type": "warmup"}],
            )
            logger.debug("[Warmup] Test collection and embedding pipeline warmed up")
        except Exception as e:
            logger.debug(f"[Warmup] Test collection warmup failed (non-critical): {e}")

        _chroma_enabled = True
        logger.debug("[Warmup] ChromaDB client and pipeline initialized successfully")
    except Exception as e:
        logger.warning(f"[Warmup] Failed to initialize ChromaDB client: {e}")
        _chroma_enabled = False


def _should_warmup_chromadb():
    """Check if we should warm up ChromaDB."""
    from decouple import config

    memory_provider = config("OMNI_MEMORY_PROVIDER", default=None)

    if not memory_provider or memory_provider == "chroma-local":
        return True
    elif memory_provider == "qdrant-remote":
        try:
            # Quick test if Qdrant is actually reachable
            from qdrant_client import QdrantClient

            qdrant_host = config("QDRANT_HOST", default=None)
            qdrant_port = config("QDRANT_PORT", default=None)

            test_client = QdrantClient(host=qdrant_host, port=qdrant_port)
            test_client.get_collections()  # Quick health check
            logger.debug("[Warmup] Qdrant is available, skipping ChromaDB warmup")
            return False
        except Exception:
            logger.debug(
                "[Warmup] Qdrant not reachable, will warm up ChromaDB as fallback"
            )
            return True
    else:
        logger.debug("[Warmup] No Qdrant configured, warming up ChromaDB")
        return True


# Smart initialization - only if Qdrant is not available
if CHROMADB_AVAILABLE and _should_warmup_chromadb():
    _initialize_chromadb()
else:
    logger.debug(
        "[Warmup] ChromaDB warmup skipped (Qdrant available or ChromaDB unavailable)"
    )


class ChromaClientType(Enum):
    """Enumeration for ChromaDB client types."""
    LOCAL = "local"
    REMOTE = "remote"
    CLOUD = "cloud"

class ChromaDBVectorDB(VectorDBBase):
    """ChromaDB vector database implementation."""

    def __init__(self, collection_name: str, client_type: ChromaClientType = ChromaClientType.LOCAL, **kwargs):
        """Initialize ChromaDB vector database."""
        super().__init__(collection_name, **kwargs)

        # Check if ChromaDB is available first
        if not CHROMADB_AVAILABLE:
            logger.error(f"❌ ChromaDB not available for collection: {collection_name}")
            logger.warning("🔧 Install ChromaDB with: pip install chromadb")
            self.enabled = False
            return

        if isinstance(client_type, str):
            try:
                client_type = ChromaClientType(client_type.lower())
            except ValueError:
                logger.warning(f"Invalid client_type '{client_type}', defaulting to LOCAL")
                client_type = ChromaClientType.LOCAL

        # Initialize ChromaDB client based on type
        try:
            logger.debug(f"Initializing ChromaDB for {collection_name} with client_type: {client_type.value}")

            if client_type == ChromaClientType.CLOUD:
                # Cloud client
                cloud_tenant = config("CHROMA_TENANT", default=None)
                cloud_database = config("CHROMA_DATABASE", default=None)
                cloud_api_key = config("CHROMA_API_KEY", default=None)
                
                if not all([cloud_tenant, cloud_database, cloud_api_key]):
                    logger.error("ChromaDB Cloud requires CHROMA_CLOUD_TENANT, CHROMA_CLOUD_DATABASE, and CHROMA_CLOUD_API_KEY")
                    self.enabled = False
                    return
                
                self.chroma_client = chromadb.CloudClient(
                    tenant=cloud_tenant,
                    database=cloud_database,
                    api_key=cloud_api_key,
                )
                logger.debug(f"ChromaDB Cloud client initialized for tenant: {cloud_tenant}")
                
            elif client_type == ChromaClientType.REMOTE:
                # Remote HTTP client
                chroma_host = config("CHROMA_HOST", default="localhost")
                chroma_port = config("CHROMA_PORT", default=8000, cast=int)
                
                self.chroma_client = chromadb.HttpClient(
                    host=chroma_host,
                    port=chroma_port,
                    ssl=False,
                )
            elif client_type == ChromaClientType.LOCAL:
                # Local persistent client
                chroma_data_dir = os.path.join(os.getcwd(), ".chroma_db")
                os.makedirs(chroma_data_dir, exist_ok=True)

                # Check if we should do lazy warmup (if not done at startup)
                global _chroma_enabled, _chroma_client
                if not _chroma_enabled and CHROMADB_AVAILABLE:
                    logger.debug("Doing lazy ChromaDB warmup (not done at startup)")
                    try:
                        _initialize_chromadb()
                    except Exception as e:
                        logger.warning(f"Lazy ChromaDB warmup failed: {e}")

                # Use warmed-up client patterns for maximum speed
                if _chroma_enabled and _chroma_client:
                    # Create client with minimal overhead (ChromaDB is already warmed up)
                    self.chroma_client = chromadb.PersistentClient(
                        path=chroma_data_dir,
                        settings=Settings(
                            anonymized_telemetry=False,
                            allow_reset=True,
                        ),
                    )
                else:
                    # Standard client creation
                    self.chroma_client = chromadb.PersistentClient(path=chroma_data_dir)

            # Get or create collection

            self.collection = self._ensure_collection()
            self.enabled = True
            logger.debug(
                f"ChromaDB initialized successfully for collection: {collection_name}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.enabled = False

    def _ensure_collection(self):
        """Ensure the collection exists, create if it doesn't."""
        try:
            # Fast collection creation leveraging warmup
            if _chroma_enabled:
                # Since ChromaDB is warmed up, collection creation should be fast
                collection = self.chroma_client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"type": "memory"},  # Ultra-minimal metadata
                )
            else:
                # Fallback to basic collection creation
                collection = self.chroma_client.get_or_create_collection(
                    name=self.collection_name
                )
            return collection
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB collection: {e}")
            raise

    def upsert_document(
        self, document: str, doc_id: str, metadata: Optional[Dict] = None
    ) -> bool:
        """Upsert a document (insert if new, update if exists)."""
        if not CHROMADB_AVAILABLE or not self.enabled:
            logger.warning(
                "ChromaDB is not available or enabled. Cannot upsert document."
            )
            return False

        try:
            # Prepare metadata with consistent timestamp
            if metadata is None:
                metadata = {}
            current_time = datetime.now(timezone.utc)
            metadata["text"] = document
            metadata["timestamp"] = current_time.isoformat()

            # Add document to ChromaDB
            self.collection.add(
                documents=[document], metadatas=[metadata], ids=[doc_id]
            )
            logger.debug(
                f"Successfully upserted document to ChromaDB with ID: {doc_id}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to upsert document to ChromaDB: {e}")
            raise

    def query_collection(
        self, query: str, n_results: int, distance_threshold: float
    ) -> Any:
        """Query the collection for similar documents."""
        if not CHROMADB_AVAILABLE or not self.enabled:
            logger.warning(
                "ChromaDB is not available or enabled. Cannot query collection."
            )
            return "No relevant documents found"

        try:
            logger.debug(
                f"Querying ChromaDB collection: {self.collection_name} with query: {query}"
            )

            # Query the collection
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"],
            )

            if not results or not results["documents"] or not results["documents"][0]:
                return "No relevant documents found"

            # Filter by distance threshold
            documents = results["documents"][0]
            distances = results["distances"][0]
            metadatas = results["metadatas"][0]

            # Filter results by distance threshold
            filtered_results = []
            for doc, dist, meta in zip(documents, distances, metadatas):
                if (
                    dist <= distance_threshold
                ):  # ChromaDB uses distance, lower is better
                    filtered_results.append(doc)

            if not filtered_results:
                return "No relevant documents found"
            else:
                return filtered_results

        except Exception as e:
            # Silently handle collection not found errors
            if "not found" in str(e).lower() or "doesn't exist" in str(e).lower():
                logger.debug(
                    f"Collection {self.collection_name} doesn't exist yet, returning empty results"
                )
                return "No relevant documents found"
            else:
                logger.error(f"Failed to query ChromaDB: {e}")
                return "No relevant documents found"

    def delete_from_collection(
        self, doc_id: Optional[str] = None, where: Optional[Dict] = None
    ):
        """Delete document from the collection."""
        if not self.enabled:
            logger.warning("ChromaDB is not enabled. Cannot delete from collection.")
            return

        try:
            if doc_id:
                self.collection.delete(ids=[doc_id])

            elif where:
                # ChromaDB doesn't support complex where clauses like Qdrant
                # We can only delete by IDs or metadata filters
                logger.warning("ChromaDB delete with where clause not fully supported")
        except Exception as e:
            logger.error(f"Failed to delete document from ChromaDB: {e}")
            raise

    async def add_to_collection_async(
        self, doc_id: str, document: str, metadata: Dict
    ) -> bool:
        """Async wrapper for adding to collection."""
        if not CHROMADB_AVAILABLE or not self.enabled:
            logger.warning(
                "ChromaDB is not available or enabled. Cannot add to collection."
            )
            return False

        try:
            # Prepare metadata with consistent timestamp
            current_time = datetime.now(timezone.utc)
            metadata["text"] = document
            metadata["timestamp"] = current_time.isoformat()

            # Add document to ChromaDB
            self.collection.add(
                documents=[document], metadatas=[metadata], ids=[doc_id]
            )

            return True
        except Exception:
            return False

    async def query_collection_async(
        self, query: str, n_results: int, distance_threshold: float
    ) -> Dict[str, Any]:
        """Async wrapper for querying collection."""
        if not CHROMADB_AVAILABLE or not self.enabled:
            logger.warning(
                "ChromaDB is not available or enabled. Cannot query collection."
            )
            return {
                "documents": [],
                "session_id": [],
                "distances": [],
                "metadatas": [],
                "ids": [],
            }

        try:
            # Query ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"],
            )

            if not results["documents"] or not results["documents"][0]:
                return {
                    "documents": [],
                    "session_id": [],
                    "distances": [],
                    "metadatas": [],
                    "ids": [],
                }

            # Filter by distance threshold and format results
            documents = results["documents"][0]
            metadatas = results["metadatas"][0]
            distances = results["distances"][0]

            filtered_results = []
            for doc, meta, dist in zip(documents, metadatas, distances):
                if dist >= distance_threshold:
                    filtered_results.append(
                        {"document": doc, "metadata": meta, "distance": dist}
                    )

            results = {
                "documents": [result["document"] for result in filtered_results],
                "session_id": [
                    result["metadata"].get("session_id", "")
                    for result in filtered_results
                ],
                "distances": [result["distance"] for result in filtered_results],
                "metadatas": [result["metadata"] for result in filtered_results],
                "ids": [
                    result["metadata"].get("id", "") for result in filtered_results
                ],
            }

            return results
        except Exception as e:
            logger.error(f"Failed to query ChromaDB: {e}")
            raise
