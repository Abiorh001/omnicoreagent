from pymongo.operations import SearchIndexModel
from bson.binary import Binary, BinaryVectorDtype
from omnicoreagent.core.utils import logger
from typing import Dict, Any
from decouple import config
from omnicoreagent.core.memory_store.memory_management.vector_db_base import (
    VectorDBBase,
)
from omnicoreagent.core.memory_store.memory_management.connection_manager import (
    get_connection_manager,
)


class MongoDBVectorDB(VectorDBBase):
    """MongoDB Atlas Vector Search implementation."""

    def __init__(self, collection_name: str, **kwargs):
        """Initialize MongoDB vector database."""
        super().__init__(collection_name, **kwargs)

        # Check if this is for background processing
        self.is_background = kwargs.get("is_background", False)

        # Get MongoDB configuration from environment
        self.mongodb_uri = config("MONGODB_URI", default=None)
        self.db_name = config("MONGODB_DB_NAME", default="omnicoreagent")
        self.collection_name = collection_name

        # MongoDB Atlas Vector Search specific settings
        self.similarity = "dotProduct"  # Default similarity metric
        self.dimensions = self._get_embedding_dimensions()  # Get dimensions from config
        self.quantization = "scalar"

        # Initialize MongoDB connection
        self.__init_connection()

    def __init_connection(self):
        """Initialize MongoDB connection and collection."""
        if self.mongodb_uri:
            try:
                if self.is_background:
                    # Background processing gets fresh connections - no pooling to avoid interference
                    from pymongo.mongo_client import MongoClient
                    from pymongo.server_api import ServerApi

                    self.client = MongoClient(
                        self.mongodb_uri, server_api=ServerApi("1")
                    )
                    self.db = self.client[self.db_name]
                    self.collection = self.db[self.collection_name]
                    self.connection_manager = (
                        None  # No connection manager for background
                    )
                    logger.debug(
                        f"Background MongoDBVectorDB created fresh connection for: {self.collection_name}"
                    )
                else:
                    # Main thread gets pooled connections
                    self.connection_manager = get_connection_manager()
                    self.client, self.db = (
                        self.connection_manager.get_mongodb_connection(
                            self.mongodb_uri, self.db_name
                        )
                    )
                    if self.client is not None and self.db is not None:
                        self.collection = self.db[self.collection_name]
                        logger.debug(
                            f"MongoDBVectorDB using pooled connection for: {self.collection_name}"
                        )
                    else:
                        logger.warning("Failed to get MongoDB connection from pool")
                        self.enabled = False
                        return

                self.enabled = True
                self._ensure_collection_and_index()

            except Exception as e:
                logger.error(f"Failed to initialize MongoDB connection: {e}")
                self.enabled = False
        else:
            logger.warning("MONGODB_URI not set. MongoDB will be disabled.")
            self.enabled = False

    def __del__(self):
        """Cleanup method to release connection back to pool."""
        try:
            # Only release if we have a connection manager
            if (
                hasattr(self, "connection_manager")
                and self.connection_manager is not None
            ):
                self.connection_manager.release_connection("mongodb")
        except Exception:
            # Ignore errors during cleanup
            pass

    def _ensure_collection(self):
        """Ensure the collection exists, create if it doesn't."""
        if not self.enabled:
            logger.warning("MongoDB is not enabled. Cannot ensure collection.")
            return

        try:
            # Check if collection exists
            if self.collection_name not in self.db.list_collection_names():
                self.db.create_collection(self.collection_name)
                logger.debug(f"Created new MongoDB collection: {self.collection_name}")

            # Create vector search index if it doesn't exist
            self._create_vector_search_index()

        except Exception as e:
            logger.error(f"Failed to initialize MongoDB collection: {e}")
            raise

    def _create_vector_search_index(self):
        """Create a vector search index for MongoDB Atlas."""
        try:
            # Generate index name
            index_name = f"idx_{self.db_name[:5]}_{self.collection_name[:5]}"

            # Check if vector search index already exists
            try:
                existing_indexes = list(self.collection.list_search_indexes())
                index_exists = any(
                    idx.get("name") == index_name for idx in existing_indexes
                )
                if index_exists:
                    logger.debug(f"Vector Search index '{index_name}' already exists")
                    return index_name
            except Exception as e:
                logger.warning(f"Could not check existing search indexes: {e}")

            # Create optimized index definition
            search_index_model = SearchIndexModel(
                definition={
                    "fields": [
                        {
                            "type": "vector",
                            "path": "embedding",
                            "numDimensions": self.dimensions,
                            "similarity": self.similarity,
                            "quantization": self.quantization,
                        },
                        {
                            "type": "filter",
                            "path": "text",  # Allow filtering by text content
                        },
                        {
                            "type": "filter",
                            "path": "session_id",  # Allow filtering by session_id
                        },
                        {
                            "type": "filter",
                            "path": "mcp_server_name",  # Allow filtering by mcp_server_name
                        },
                    ]
                },
                name=index_name,
                type="vectorSearch",
            )

            self.collection.create_search_index(model=search_index_model)
            logger.debug(f"Search index '{index_name}' creation submitted")
            return index_name

        except Exception as e:
            logger.error(f"Failed to create search index: {e}")
            return None

    def _ensure_collection_and_index(self):
        """Ensure the collection and index exist during initialization."""
        if not self.enabled:
            logger.warning("MongoDB is not enabled. Cannot ensure collection.")
            return

        try:
            # Check if collection exists
            if self.collection_name not in self.db.list_collection_names():
                self.db.create_collection(self.collection_name)
                logger.debug(f"Created new MongoDB collection: {self.collection_name}")

            # Create vector search index if it doesn't exist
            self.index_name = self._create_vector_search_index()

        except Exception as e:
            logger.error(f"Failed to initialize MongoDB collection and index: {e}")
            raise

    def _generate_bson_vector(self, vector, vector_dtype=BinaryVectorDtype.FLOAT32):
        """Convert float vector to BSON vector for MongoDB Atlas."""
        return Binary.from_vector(vector, vector_dtype)

    def add_to_collection(self, doc_id: str, document: str, metadata: Dict) -> bool:
        """for adding to collection."""
        if not self.enabled:
            logger.warning("MongoDB is not enabled. Cannot add to collection.")
            return False

        try:
            # Ensure collection exists
            self._ensure_collection()
            # check the metadata to see if it has mcp_server_name key
            mcp_server_name = metadata.get("mcp_server_name", None)

            metadata["text"] = document

            # Generate embedding with error handling
            try:
                updated_document = None
                if not mcp_server_name:
                    updated_document = document
                else:
                    updated_document = document["enriched_tool"]

                vector = self.embed_text(updated_document)
            except Exception:
                return False

            # Convert to BSON vector
            bson_vector = self._generate_bson_vector(vector)

            # Create document
            doc = {
                "_id": doc_id,
                "text": document,
                "embedding": bson_vector,
                **metadata,
            }

            # Upsert the document
            self.collection.replace_one({"_id": doc_id}, doc, upsert=True)

            return True
        except Exception:
            return False

    def query_collection(
        self,
        query: str,
        n_results: int,
        similarity_threshold: float,
        session_id: str = None,
        mcp_server_names: list[str] = None,
    ) -> Dict[str, Any]:
        """Query the collection with session_id or MCP server name filtering."""
        if not self.enabled:
            logger.warning("MongoDB is not enabled. Cannot query collection.")
            return {
                "documents": [],
                "session_id": [],
                "distances": [],
                "metadatas": [],
                "ids": [],
            }

        if session_id and mcp_server_names:
            raise ValueError(
                "Cannot filter by both session_id and mcp_server_names simultaneously."
            )

        try:
            query_embedding = self.embed_text(query)
            index_name = f"idx_{self.db_name[:5]}_{self.collection_name[:5]}"

            # Build filter dict
            filter_dict = {}
            if session_id:
                filter_dict["session_id"] = session_id
            elif mcp_server_names:
                filter_dict["mcp_server_name"] = {"$in": mcp_server_names}

            # Build vector search pipeline
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": index_name,
                        "queryVector": query_embedding,
                        "path": "embedding",
                        "limit": n_results,
                        "exact": True,
                        "filter": filter_dict,
                    }
                },
                {
                    "$project": {
                        "_id": 1,
                        "text": 1,
                        "score": {"$meta": "vectorSearchScore"},
                        "session_id": 1,
                        "timestamp": 1,
                        "memory_type": 1,
                        "mcp_server_name": 1,
                        "metadata": {
                            "$mergeObjects": [
                                "$metadata",
                                {
                                    "_id": "$_id",
                                    "session_id": "$session_id",
                                    "text": "$text",
                                    "timestamp": "$timestamp",
                                    "memory_type": "$memory_type",
                                    "mcp_server_name": "$mcp_server_name",
                                },
                            ]
                        },
                    }
                },
                {"$sort": {"score": -1}},
            ]

            results = list(self.collection.aggregate(pipeline))
            if not results:
                return {
                    "documents": [],
                    "session_id": [],
                    "mcp_server_name": [],
                    "distances": [],
                    "metadatas": [],
                    "ids": [],
                }

            # Filter by similarity threshold
            filtered_results = [
                r for r in results if r["score"] >= similarity_threshold
            ]

            return {
                "documents": [r["text"] for r in filtered_results],
                "session_id": [r.get("session_id", "") for r in filtered_results],
                "mcp_server_name": [
                    r.get("mcp_server_name", "") for r in filtered_results
                ],
                "scores": [r["score"] for r in filtered_results],
                "metadatas": [r["metadata"] for r in filtered_results],
                "ids": [r["_id"] for r in filtered_results],
            }

        except Exception as e:
            logger.error(f"Failed to query MongoDB: {e}")
            return {
                "documents": [],
                "session_id": [],
                "mcp_server_name": [],
                "distances": [],
                "metadatas": [],
                "ids": [],
            }
