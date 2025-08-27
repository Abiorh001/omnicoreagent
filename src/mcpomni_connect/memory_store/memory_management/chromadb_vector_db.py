from enum import Enum
from mcpomni_connect.utils import logger
from decouple import config
import chromadb
from typing import Dict, Any
from mcpomni_connect.memory_store.memory_management.vector_db_base import VectorDBBase
from mcpomni_connect.memory_store.memory_management.connection_manager import (
    get_connection_manager,
)


class ChromaClientType(Enum):
    """Enumeration for ChromaDB client types"""

    REMOTE = "remote"
    CLOUD = "cloud"


class ChromaDBVectorDB(VectorDBBase):
    """ChromaDB vector database implementation."""

    def __init__(
        self,
        collection_name: str,
        client_type: ChromaClientType = ChromaClientType.REMOTE,
        **kwargs,
    ):
        """Initialize ChromaDB vector database ."""
        super().__init__(collection_name, **kwargs)

        self.is_background = kwargs.get("is_background", False)

        if isinstance(client_type, str):
            try:
                client_type = ChromaClientType(client_type.lower())
            except ValueError:
                logger.warning(
                    f"Invalid client_type '{client_type}', defaulting to REMOTE"
                )
                client_type = ChromaClientType.REMOTE

        # Initialize ChromaDB client based on type
        try:
            logger.debug(
                f"Initializing ChromaDB for {collection_name} with client_type: {client_type.value}"
            )

            if client_type == ChromaClientType.CLOUD:
                # Cloud client
                cloud_tenant = config("CHROMA_TENANT", default=None)
                cloud_database = config("CHROMA_DATABASE", default=None)
                cloud_api_key = config("CHROMA_API_KEY", default=None)

                if not all([cloud_tenant, cloud_database, cloud_api_key]):
                    logger.error(
                        "ChromaDB Cloud requires CHROMA_TENANT, CHROMA_DATABASE, and CHROMA_API_KEY"
                    )
                    self.enabled = False
                    return

                if self.is_background:
                    # Background processing gets fresh connections - no pooling to avoid interference
                    self.chroma_client = chromadb.CloudClient(
                        tenant=cloud_tenant,
                        database=cloud_database,
                        api_key=cloud_api_key,
                    )
                    self.connection_manager = (
                        None  # No connection manager for background
                    )
                    logger.debug(
                        f"Background ChromaDBVectorDB created fresh connection for: {collection_name}"
                    )
                else:
                    # Main thread gets pooled connections
                    self.connection_manager = get_connection_manager()
                    self.chroma_client = (
                        self.connection_manager.get_chromadb_connection(
                            client_type="cloud",
                            tenant=cloud_tenant,
                            database=cloud_database,
                            api_key=cloud_api_key,
                        )
                    )
                    if self.chroma_client is None:
                        logger.warning("Failed to get ChromaDB connection from pool")
                        self.enabled = False
                        return
                    logger.debug(
                        f"ChromaDBVectorDB using pooled connection for: {collection_name}"
                    )

                logger.debug(
                    f"ChromaDB Cloud client initialized for tenant: {cloud_tenant}"
                )

            elif client_type == ChromaClientType.REMOTE:
                # Remote HTTP client
                chroma_host = config("CHROMA_HOST", default="localhost")
                chroma_port = config("CHROMA_PORT", default=8000, cast=int)

                if self.is_background:
                    self.chroma_client = chromadb.HttpClient(
                        host=chroma_host,
                        port=chroma_port,
                        ssl=False,
                    )
                    self.connection_manager = None
                    logger.debug(
                        f"Background ChromaDBVectorDB created fresh connection for: {collection_name}"
                    )
                else:
                    self.connection_manager = get_connection_manager()
                    self.chroma_client = (
                        self.connection_manager.get_chromadb_connection(
                            client_type="remote", host=chroma_host, port=chroma_port
                        )
                    )
                    if self.chroma_client is None:
                        logger.warning("Failed to get ChromaDB connection from pool")
                        self.enabled = False
                        return
                    logger.debug(
                        f"ChromaDBVectorDB using pooled connection for: {collection_name}"
                    )

                logger.debug(
                    f"ChromaDB Remote client initialized for host: {chroma_host} and port: {chroma_port}"
                )
            else:
                logger.error(f"Unsupported ChromaDB client type: {client_type}")
                self.enabled = False
                return

            # Get or create collection
            self.collection = self._ensure_collection()
            self.enabled = True
            logger.debug(
                f"ChromaDB initialized successfully for collection: {collection_name}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.enabled = False

    def __del__(self):
        """Cleanup method to release connection back to pool."""
        try:
            # Only release if we have a connection manager
            if (
                hasattr(self, "connection_manager")
                and self.connection_manager is not None
            ):
                self.connection_manager.release_connection("chromadb")
        except Exception:
            # Ignore errors during cleanup
            pass

    def _ensure_collection(self):
        """Ensure the collection exists, create if it doesn't."""
        try:
            collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"type": "memory"},
            )
            return collection
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB collection: {e}")
            raise

    def add_to_collection(self, doc_id: str, document: str, metadata: Dict) -> bool:
        """for adding to collection."""
        if not self.enabled:
            logger.warning(
                "ChromaDB is not available or enabled. Cannot add to collection."
            )
            return False

        try:
            metadata["text"] = document

            # Add document to ChromaDB
            self.collection.add(
                documents=[document], metadatas=[metadata], ids=[doc_id]
            )

            return True
        except Exception:
            return False

    def query_collection(
        self, query: str, session_id: str, n_results: int, similarity_threshold: float
    ) -> Dict[str, Any]:
        """for querying collection."""
        if not self.enabled:
            logger.warning(
                "ChromaDB is not available or enabled. Cannot query collection."
            )
            return {
                "documents": [],
                "scores": [],
                "metadatas": [],
                "ids": [],
            }

        try:
            # Query ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"],
                where={"session_id": session_id},
            )

            if not results["documents"] or not results["documents"][0]:
                return {
                    "documents": [],
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
                # Convert distance to similarity score
                score = 1 - dist
                if score >= similarity_threshold:
                    filtered_results.append(
                        {"document": doc, "metadata": meta, "score": score}
                    )

            results = {
                "documents": [result["document"] for result in filtered_results],
                "scores": [result["score"] for result in filtered_results],
                "metadatas": [result["metadata"] for result in filtered_results],
                "ids": [
                    result["metadata"].get("id", "") for result in filtered_results
                ],
            }

            return results
        except Exception as e:
            logger.error(f"Failed to query ChromaDB: {e}")
            raise
