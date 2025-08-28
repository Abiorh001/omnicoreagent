"""
Connection Manager for Vector Databases

This module provides a centralized connection management system for vector databases,
implementing connection pooling and reuse to optimize performance while maintaining
thread safety and isolation for background processing.
"""

import threading
from typing import Dict, Any
from contextlib import contextmanager
from omnicoreagent.core.utils import logger


class VectorDBConnectionManager:
    """
    Centralized connection manager for vector databases.

    Features:
    - Connection pooling and reuse
    - Thread-safe operations
    - Automatic connection cleanup
    - Background processing isolation support
    """

    _instance = None
    _lock = threading.RLock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._connections = {}
            self._connection_locks = {}
            logger.debug("VectorDBConnectionManager initialized")

    def _get_connection_key(
        self, provider: str, collection_name: str = None, background: bool = False
    ) -> str:
        """Generate a unique key for connection caching."""
        if background:
            # Background processing gets unique connections with UUID
            import uuid

            return f"{provider}_background_{uuid.uuid4().hex[:8]}"
        else:
            # Main thread gets pooled connections
            base_key = f"{provider}"
            if collection_name:
                base_key += f"_{collection_name}"
            return base_key

    def _get_or_create_qdrant_connection(self, host: str, port: int):
        """Get or create a Qdrant connection."""
        from qdrant_client import QdrantClient

        connection_key = self._get_connection_key("qdrant")

        with self._lock:
            if connection_key not in self._connections:
                try:
                    client = QdrantClient(host=host, port=port)
                    self._connections[connection_key] = {
                        "client": client,
                        "host": host,
                        "port": port,
                        "usage_count": 0,
                    }
                    logger.debug(
                        f"[ConnectionManager] Created new Qdrant connection: {connection_key} (host={host}:{port})"
                    )
                    logger.debug(
                        f"[ConnectionManager] Total connections: {len(self._connections)}"
                    )
                except Exception as e:
                    logger.error(
                        f"[ConnectionManager] Failed to create Qdrant connection: {e}"
                    )
                    return None
            else:
                logger.debug(
                    f"[ConnectionManager] Reusing existing Qdrant connection: {connection_key}"
                )

            connection = self._connections[connection_key]
            connection["usage_count"] += 1
            logger.debug(
                f"[ConnectionManager] Qdrant connection usage count: {connection_key} = {connection['usage_count']}"
            )
            return connection["client"]

    def _get_or_create_mongodb_connection(self, uri: str, db_name: str):
        """Get or create a MongoDB connection."""
        from pymongo.mongo_client import MongoClient
        from pymongo.server_api import ServerApi

        connection_key = self._get_connection_key("mongodb")

        with self._lock:
            if connection_key not in self._connections:
                try:
                    client = MongoClient(uri, server_api=ServerApi("1"))
                    db = client[db_name]
                    self._connections[connection_key] = {
                        "client": client,
                        "db": db,
                        "uri": uri,
                        "db_name": db_name,
                        "usage_count": 0,
                    }
                    logger.debug(
                        f"[ConnectionManager] Created new MongoDB connection: {connection_key} (db={db_name})"
                    )
                    logger.debug(
                        f"[ConnectionManager] Total connections: {len(self._connections)}"
                    )
                except Exception as e:
                    logger.error(
                        f"[ConnectionManager] Failed to create MongoDB connection: {e}"
                    )
                    return None, None
            else:
                logger.debug(
                    f"[ConnectionManager] Reusing existing MongoDB connection: {connection_key}"
                )

            connection = self._connections[connection_key]
            connection["usage_count"] += 1
            logger.debug(
                f"[ConnectionManager] MongoDB connection usage count: {connection_key} = {connection['usage_count']}"
            )
            return connection["client"], connection["db"]

    def _get_or_create_chromadb_connection(
        self,
        client_type: str,
        host: str = None,
        port: int = None,
        tenant: str = None,
        database: str = None,
        api_key: str = None,
    ):
        """Get or create a ChromaDB connection."""
        import chromadb

        connection_key = self._get_connection_key("chromadb")

        with self._lock:
            if connection_key not in self._connections:
                try:
                    if client_type == "cloud":
                        client = chromadb.CloudClient(
                            tenant=tenant,
                            database=database,
                            api_key=api_key,
                        )
                    elif client_type == "remote":
                        client = chromadb.HttpClient(
                            host=host,
                            port=port,
                            ssl=False,
                        )
                    else:
                        logger.error(
                            f"[ConnectionManager] Unsupported ChromaDB client type: {client_type}"
                        )
                        return None

                    self._connections[connection_key] = {
                        "client": client,
                        "client_type": client_type,
                        "host": host,
                        "port": port,
                        "tenant": tenant,
                        "database": database,
                        "usage_count": 0,
                    }
                    logger.debug(
                        f"[ConnectionManager] Created new ChromaDB connection: {connection_key} (type={client_type})"
                    )
                    logger.debug(
                        f"[ConnectionManager] Total connections: {len(self._connections)}"
                    )
                except Exception as e:
                    logger.error(
                        f"[ConnectionManager] Failed to create ChromaDB connection: {e}"
                    )
                    return None
            else:
                logger.debug(
                    f"[ConnectionManager] Reusing existing ChromaDB connection: {connection_key}"
                )

            connection = self._connections[connection_key]
            connection["usage_count"] += 1
            logger.debug(
                f"[ConnectionManager] ChromaDB connection usage count: {connection_key} = {connection['usage_count']}"
            )
            return connection["client"]

    def get_qdrant_connection(self, host: str, port: int):
        """Get a Qdrant connection from the pool."""
        return self._get_or_create_qdrant_connection(host, port)

    def get_mongodb_connection(self, uri: str, db_name: str):
        """Get a MongoDB connection from the pool."""
        return self._get_or_create_mongodb_connection(uri, db_name)

    def get_chromadb_connection(
        self,
        client_type: str,
        host: str = None,
        port: int = None,
        tenant: str = None,
        database: str = None,
        api_key: str = None,
    ):
        """Get a ChromaDB connection from the pool."""
        return self._get_or_create_chromadb_connection(
            client_type, host, port, tenant, database, api_key
        )

    def release_connection(self, provider: str):
        """Release a connection back to the pool."""
        connection_key = self._get_connection_key(provider)

        with self._lock:
            if connection_key in self._connections:
                connection = self._connections[connection_key]
                connection["usage_count"] = max(0, connection["usage_count"] - 1)
                logger.debug(
                    f"[ConnectionManager] Released {provider} connection: {connection_key}, new usage count: {connection['usage_count']}"
                )
            else:
                logger.warning(
                    f"[ConnectionManager] Tried to release non-existent connection: {connection_key}"
                )

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about current connections."""
        with self._lock:
            stats = {}
            for key, connection in self._connections.items():
                provider = key.split("_")[0]
                if provider not in stats:
                    stats[provider] = {"count": 0, "usage": 0}

                stats[provider]["count"] += 1
                stats[provider]["usage"] += connection["usage_count"]

            return stats

    def cleanup_all_connections(self):
        """Clean up all connections (typically called on app shutdown)."""
        with self._lock:
            for key, connection in list(self._connections.items()):
                try:
                    if "client" in connection:
                        if hasattr(connection["client"], "close"):
                            connection["client"].close()
                    logger.debug(f"Closed connection: {key}")
                except Exception as e:
                    logger.warning(f"Error closing connection {key}: {e}")

            self._connections.clear()
            logger.debug("All connections cleaned up")


# Global connection manager instance
_connection_manager = VectorDBConnectionManager()


def get_connection_manager():
    """Get the global connection manager instance."""
    return _connection_manager


@contextmanager
def managed_connection(provider: str):
    """
    Context manager for managed connections.

    Usage:
        with managed_connection("qdrant") as conn:
            # Use connection
            pass
        # Connection is automatically released
    """
    try:
        yield _connection_manager
    finally:
        _connection_manager.release_connection(provider)
