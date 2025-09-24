from typing import Callable
from omnicoreagent.core.utils import (
    logger,
    is_vector_db_enabled,
    is_embedding_requirements_met,
)
from decouple import config


class BaseVectorDBHandler:
    def __init__(
        self,
        collection_name: str,
        memory_type: str,
        llm_connection: Callable,
        is_background: bool = False,
    ):
        self.collection_name = collection_name
        self.memory_type = memory_type
        self.llm_connection = llm_connection
        self.is_background = is_background
        self.vector_db = None

        self._init_vector_db()

    def _init_vector_db(self):
        if not is_vector_db_enabled():
            logger.debug("Vector database is disabled by configuration")
            return

        if not is_embedding_requirements_met():
            logger.error("Embedding requirements not met: EMBEDDING_API_KEY missing")
            return

        if not self.llm_connection:
            logger.error("LLM connection is required for vector DB")
            return

        provider = config("OMNI_MEMORY_PROVIDER", default=None)
        if not provider:
            logger.error("OMNI_MEMORY_PROVIDER is not set")
            return

        provider = provider.lower()

        try:
            if provider == "qdrant-remote":
                from omnicoreagent.core.memory_store.memory_management.qdrant_vector_db import (
                    QdrantVectorDB,
                )

                self.vector_db = QdrantVectorDB(
                    self.collection_name,
                    memory_type=self.memory_type,
                    is_background=self.is_background,
                    llm_connection=self.llm_connection,
                )

            elif provider == "mongodb-remote":
                from omnicoreagent.core.memory_store.memory_management.mongodb_vector_db import (
                    MongoDBVectorDB,
                )

                self.vector_db = MongoDBVectorDB(
                    self.collection_name,
                    memory_type=self.memory_type,
                    is_background=self.is_background,
                    llm_connection=self.llm_connection,
                )

            elif provider.startswith("chroma"):
                from omnicoreagent.core.memory_store.memory_management.chromadb_vector_db import (
                    ChromaDBVectorDB,
                )

                client_type = "remote" if provider == "chroma-remote" else "cloud"
                self.vector_db = ChromaDBVectorDB(
                    self.collection_name,
                    memory_type=self.memory_type,
                    client_type=client_type,
                    llm_connection=self.llm_connection,
                )

            if self.vector_db and self.vector_db.enabled:
                logger.debug(f"Using {provider} for {self.memory_type} memory")
                return
            else:
                logger.warning(f"{provider} not enabled or failed")
        except Exception as e:
            logger.warning(f"Failed to initialize {provider}: {e}")

        self.vector_db = None
