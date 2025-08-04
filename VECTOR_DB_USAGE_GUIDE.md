# Vector Database Usage Guide

## Overview

This guide shows you how to use the vector database abstraction directly for your tools and custom features, separate from the memory management system. The system provides automatic fallback between Qdrant and ChromaDB with a unified interface.

## Architecture

```
VectorDBBase (Abstract Base Class)
├── QdrantVectorDB (Concrete Implementation)
└── ChromaDBVectorDB (Concrete Implementation)

MemoryManager (High-level wrapper for memory operations)
├── Automatic backend selection
├── Memory-specific operations
└── Background processing
```

## Direct Vector Database Usage

### Core Methods Available

All vector database implementations provide these core methods:

#### 1. **Document Operations**
```python
# Upsert a document (insert if new, update if exists)
vector_db.upsert_document(document="Your text", doc_id="unique_id", metadata={"key": "value"})

# Delete documents
vector_db.delete_from_collection(doc_id="unique_id")
vector_db.delete_from_collection(where={"key": "value"})
```

#### 2. **Query Operations**
```python
# Query for similar documents
results = vector_db.query_collection(query="Your search query", n_results=5, distance_threshold=0.4)

# Async query
results = await vector_db.query_collection_async(query="Your search query", n_results=5, distance_threshold=0.7)
```

#### 3. **Async Operations**
```python
# Add document asynchronously
await vector_db.add_to_collection_async(doc_id="unique_id", document="Your text", metadata={"key": "value"})

# Query asynchronously
results = await vector_db.query_collection_async(query="Your search query")
```

## Creating Your Own Tool Class

### Option 1: Direct Vector Database Usage (Recommended for Tools)

```python
from mcpomni_connect.memory_store.memory_management.qdrant_vector_db import QdrantVectorDB
from mcpomni_connect.memory_store.memory_management.chromadb_vector_db import ChromaDBVectorDB

class MyVectorTool:
    def __init__(self, collection_name: str):
        # Try Qdrant first, fallback to ChromaDB
        try:
            self.vector_db = QdrantVectorDB(collection_name)
            if not self.vector_db.enabled:
                self.vector_db = ChromaDBVectorDB(collection_name)
        except Exception as e:
            self.vector_db = ChromaDBVectorDB(collection_name)
    
    def add_document(self, text: str, doc_id: str, metadata: dict = None):
        """Add a document to your collection."""
        if metadata is None:
            metadata = {}
        return self.vector_db.upsert_document(text, doc_id, metadata)
    
    def search_documents(self, query: str, n_results: int = 5):
        """Search for similar documents."""
        return self.vector_db.query_collection(query, n_results, distance_threshold=0.4)
    
    async def add_document_async(self, text: str, doc_id: str, metadata: dict = None):
        """Add document asynchronously."""
        if metadata is None:
            metadata = {}
        return await self.vector_db.add_to_collection_async(doc_id, text, metadata)
    
    async def search_documents_async(self, query: str, n_results: int = 5):
        """Search documents asynchronously."""
        return await self.vector_db.query_collection_async(query, n_results, distance_threshold=0.7)
    
    def delete_document(self, doc_id: str):
        """Delete a document."""
        self.vector_db.delete_from_collection(doc_id=doc_id)
```

### Option 2: Using MemoryManager (For Memory-Specific Operations)

```python
from mcpomni_connect.memory_store.memory_management.memory_manager import MemoryManager

class MyMemoryTool:
    def __init__(self, session_id: str):
        # Create memory manager with automatic backend selection
        self.memory_manager = MemoryManager(session_id, "custom_type")
    
    def add_document(self, text: str, doc_id: str):
        """Add a document using the memory manager."""
        return self.memory_manager.vector_db.upsert_document(text, doc_id)
    
    def search_documents(self, query: str):
        """Search using the memory manager."""
        return self.memory_manager.vector_db.query_collection(query, n_results=5)
    
    async def process_memory(self, messages: list, llm_connection):
        """Process memory using the memory manager."""
        return await self.memory_manager.process_conversation_memory(messages, llm_connection)
```

## Complete Tool Example

```python
import asyncio
from mcpomni_connect.memory_store.memory_management.qdrant_vector_db import QdrantVectorDB
from mcpomni_connect.memory_store.memory_management.chromadb_vector_db import ChromaDBVectorDB

class DocumentSearchTool:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        # Automatic fallback: Qdrant → ChromaDB
        try:
            self.vector_db = QdrantVectorDB(collection_name)
            if not self.vector_db.enabled:
                self.vector_db = ChromaDBVectorDB(collection_name)
        except Exception as e:
            self.vector_db = ChromaDBVectorDB(collection_name)
    
    def add_document(self, content: str, doc_id: str, metadata: dict = None):
        """Add a document to the collection."""
        if metadata is None:
            metadata = {}
        
        success = self.vector_db.upsert_document(
            document=content,
            doc_id=doc_id,
            metadata=metadata
        )
        
        if success:
            print(f"✅ Document {doc_id} added successfully")
        else:
            print(f"❌ Failed to add document {doc_id}")
        
        return success
    
    def search_documents(self, query: str, n_results: int = 5):
        """Search for similar documents."""
        if not self.vector_db.enabled:
            print("❌ Vector database not enabled")
            return []
        
        results = self.vector_db.query_collection(
            query=query,
            n_results=n_results,
            distance_threshold=0.4
        )
        return results
    
    async def search_documents_async(self, query: str, n_results: int = 5):
        """Search documents asynchronously."""
        if not self.vector_db.enabled:
            print("❌ Vector database not enabled")
            return []
        
        results = await self.vector_db.query_collection_async(
            query=query,
            n_results=n_results,
            distance_threshold=0.7
        )
        return results
    
    def delete_document(self, doc_id: str):
        """Delete a document."""
        if not self.vector_db.enabled:
            print("❌ Vector database not enabled")
            return
        
        self.vector_db.delete_from_collection(doc_id=doc_id)
        print(f"🗑️ Document {doc_id} deleted")
    
    def get_collection_info(self):
        """Get information about the collection."""
        return {
            "collection_name": self.collection_name,
            "enabled": self.vector_db.enabled,
            "backend": type(self.vector_db).__name__
        }

# Usage Example
async def main():
    # Create document search tool
    doc_tool = DocumentSearchTool("my_documents")
    
    # Add documents
    doc_tool.add_document(
        content="This is a sample document about machine learning and AI",
        doc_id="doc_001",
        metadata={"category": "AI", "author": "John Doe", "tags": ["machine learning", "AI"]}
    )
    
    doc_tool.add_document(
        content="Another document about data science and analytics techniques",
        doc_id="doc_002",
        metadata={"category": "Data Science", "author": "Jane Smith", "tags": ["data science", "analytics"]}
    )
    
    # Search documents
    results = doc_tool.search_documents("machine learning")
    print("Search results:", results)
    
    # Async search
    async_results = await doc_tool.search_documents_async("data science")
    print("Async search results:", async_results)
    
    # Get collection info
    info = doc_tool.get_collection_info()
    print("Collection info:", info)
    
    # Delete a document
    doc_tool.delete_document("doc_001")

if __name__ == "__main__":
    asyncio.run(main())
```

## Tool Integration Example

```python
class KnowledgeBaseTool:
    def __init__(self, collection_name: str):
        # Initialize vector database
        try:
            self.vector_db = QdrantVectorDB(collection_name)
            if not self.vector_db.enabled:
                self.vector_db = ChromaDBVectorDB(collection_name)
        except Exception as e:
            self.vector_db = ChromaDBVectorDB(collection_name)
    
    def store_knowledge(self, question: str, answer: str, category: str = "general"):
        """Store Q&A pair in knowledge base."""
        doc_id = f"qa_{hash(question)}"
        metadata = {
            "type": "qa_pair",
            "category": category,
            "question": question,
            "timestamp": datetime.now().isoformat()
        }
        
        content = f"Q: {question}\nA: {answer}"
        return self.vector_db.upsert_document(content, doc_id, metadata)
    
    def find_similar_questions(self, query: str, n_results: int = 3):
        """Find similar questions in knowledge base."""
        results = self.vector_db.query_collection(
            query=query,
            n_results=n_results,
            distance_threshold=0.6
        )
        return results
    
    async def find_similar_questions_async(self, query: str, n_results: int = 3):
        """Find similar questions asynchronously."""
        results = await self.vector_db.query_collection_async(
            query=query,
            n_results=n_results,
            distance_threshold=0.6
        )
        return results

# Usage in your application
kb_tool = KnowledgeBaseTool("knowledge_base")

# Store knowledge
kb_tool.store_knowledge(
    "How do I install Python?",
    "You can install Python from python.org or use package managers like apt, brew, or conda.",
    "programming"
)

# Find similar questions
similar = kb_tool.find_similar_questions("How to set up Python?")
print("Similar questions:", similar)
```

## Key Benefits for Tools

1. **Standalone Usage**: Use vector DB directly without memory management overhead
2. **Automatic Fallback**: Qdrant → ChromaDB if Qdrant is unavailable
3. **Unified Interface**: Same methods work with both backends
4. **Async Support**: Both sync and async operations available
5. **Tool-Specific**: Focus on your tool's functionality, not memory operations

## Configuration

The system automatically detects your vector database configuration:

- **Qdrant**: Set `QDRANT_HOST` and `QDRANT_PORT` environment variables
- **ChromaDB**: Automatically uses local storage in `.chroma_db` directory

## Error Handling

```python
try:
    result = vector_db.upsert_document("text", "id")
    if not result:
        print("Vector DB operation failed")
except Exception as e:
    print(f"Error: {e}")
```

## Best Practices for Tools

1. **Use direct vector DB classes** for tool-specific operations
2. **Check enabled state** - verify `vector_db.enabled` before operations
3. **Use async methods** for better performance in async contexts
4. **Provide meaningful metadata** for better document organization
5. **Handle fallback gracefully** - both Qdrant and ChromaDB should work

## Available Methods Summary

| Method | Sync | Async | Description |
|--------|------|-------|-------------|
| `upsert_document()` | ✅ | ❌ | Add/update document |
| `query_collection()` | ✅ | ❌ | Search documents |
| `delete_from_collection()` | ✅ | ❌ | Delete documents |
| `add_to_collection_async()` | ❌ | ✅ | Async add document |
| `query_collection_async()` | ❌ | ✅ | Async search documents |

## When to Use Each Approach

- **Use Direct Vector DB** (QdrantVectorDB/ChromaDBVectorDB): For tools, document search, knowledge bases, custom features
- **Use MemoryManager**: For memory-specific operations, conversation history, episodic/long-term memory

This abstraction makes it easy to build your own vector database-powered tools while maintaining clean, reusable code! 