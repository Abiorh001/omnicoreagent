"""
Memory Management Package

This package provides advanced memory management functionality:
- Vector Database Management (Qdrant, MongoDB, ChromaDB)
- Memory Manager and Factory
- Background Memory Management
- Connection Management

Note: This package is for internal use, not for top-level imports.
"""

from .memory_manager import MemoryManager, MemoryManagerFactory
from .vector_db_base import VectorDBBase
from .qdrant_vector_db import QdrantVectorDB
from .mongodb_vector_db import MongoDBVectorDB
from .chromadb_vector_db import ChromaDBVectorDB, ChromaClientType
from .background_memory_management import BackgroundMemoryManager
from .connection_manager import VectorDBConnectionManager

__all__ = [
    "MemoryManager",
    "MemoryManagerFactory",
    "VectorDBBase",
    "QdrantVectorDB",
    "MongoDBVectorDB",
    "ChromaDBVectorDB",
    "ChromaClientType",
    "BackgroundMemoryManager",
    "VectorDBConnectionManager",
]
