import os
from enum import Enum
from mcpomni_connect.utils import logger
from decouple import config
import chromadb
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from mcpomni_connect.memory_store.memory_management.vector_db_base import VectorDBBase


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

                self.chroma_client = chromadb.CloudClient(
                    tenant=cloud_tenant,
                    database=cloud_database,
                    api_key=cloud_api_key,
                )
                logger.debug(
                    f"ChromaDB Cloud client initialized for tenant: {cloud_tenant}"
                )

            elif client_type == ChromaClientType.REMOTE:
                # Remote HTTP client
                chroma_host = config("CHROMA_HOST", default="localhost")
                chroma_port = config("CHROMA_PORT", default=8000, cast=int)
                logger.debug(
                    f"ChromaDB Remote client initialized for host: {chroma_host} and port: {chroma_port}"
                )
                self.chroma_client = chromadb.HttpClient(
                    host=chroma_host,
                    port=chroma_port,
                    ssl=False,
                )
            else:
                logger.error(f"❌ Unsupported ChromaDB client type: {client_type}")
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

    def query_collection(
        self, query: str, n_results: int, distance_threshold: float
    ) -> Dict[str, Any]:
        """for querying collection."""
        if not self.enabled:
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
