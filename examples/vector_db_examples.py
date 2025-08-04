#!/usr/bin/env python3
"""
Examples demonstrating vector database usage with the current system.
Shows how to use QdrantVectorDB and ChromaDBVectorDB for different use cases.
"""

import asyncio
import os
from datetime import datetime, timezone

from dotenv import load_dotenv

from mcpomni_connect.memory_store.memory_management.qdrant_vector_db import (
    QdrantVectorDB,
)
from mcpomni_connect.memory_store.memory_management.chromadb_vector_db import (
    ChromaDBVectorDB,
)
from mcpomni_connect.memory_store.memory_management.memory_manager import MemoryManager
from mcpomni_connect.memory_store.memory_management.shared_embedding import (
    is_vector_db_enabled,
    load_embed_model,
)
from mcpomni_connect.utils import logger


async def memory_example():
    """Example: Using MemoryManager for episodic memory operations."""
    print("=== Memory Operations Example ===")

    if not is_vector_db_enabled():
        print(
            "⚠️ Vector database is disabled. Set ENABLE_VECTOR_DB=True to use this feature."
        )
        return

    try:
        # Create memory manager for episodic memory
        memory_manager = MemoryManager(session_id="user_123", memory_type="episodic")

        if not memory_manager.vector_db or not memory_manager.vector_db.enabled:
            print("❌ Vector database not available. Check your configuration.")
            return

        # Add memory entries
        success = memory_manager.vector_db.upsert_document(
            document="User asked about Python programming and received help with async/await",
            doc_id="mem_001",
            metadata={
                "timestamp": "2024-01-15T10:30:00",
                "topic": "programming",
                "language": "python",
            },
        )

        if success:
            print("✅ Memory entry added successfully")
        else:
            print("❌ Failed to add memory entry")
            return

        # Query memory
        results = memory_manager.vector_db.query_documents(
            query="Python programming help", n_results=3
        )
        print(f"Memory query results: {len(results)} results found")
        for i, result in enumerate(results, 1):
            print(
                f"  {i}. Score: {result.get('score', 'N/A')}, Text: {result.get('document', '')[:100]}..."
            )

    except Exception as e:
        print(f"❌ Memory example error: {e}")
        logger.error(f"Memory example error: {e}")


async def tool_embeddings_example():
    """Example: Using ChromaDB directly for tool embeddings."""
    print("\n=== Tool Embeddings Example ===")

    if not is_vector_db_enabled():
        print(
            "⚠️ Vector database is disabled. Set ENABLE_VECTOR_DB=True to use this feature."
        )
        return

    try:
        # Create ChromaDB instance for tools
        tool_db = ChromaDBVectorDB("python_tools")

        if not tool_db.enabled:
            print("❌ ChromaDB not available. Check your installation.")
            return

        # Add tool embeddings
        tools = [
            {
                "name": "file_reader",
                "description": "Read and analyze text files",
                "function": "def read_file(path: str) -> str: ...",
            },
            {
                "name": "calculator",
                "description": "Perform mathematical calculations",
                "function": "def calculate(expression: str) -> float: ...",
            },
            {
                "name": "web_scraper",
                "description": "Scrape data from web pages",
                "function": "def scrape_url(url: str) -> dict: ...",
            },
        ]

        for tool in tools:
            document = f"{tool['description']}\n{tool['function']}"
            success = tool_db.upsert_document(
                document=document,
                doc_id=tool["name"],
                metadata={
                    "tool_name": tool["name"],
                    "category": "utility",
                    "language": "python",
                },
            )
            if success:
                print(f"✅ Added tool: {tool['name']}")

        # Semantic search for tools
        results = tool_db.query_documents(
            query="I need to read a file and do calculations", n_results=2
        )
        print(f"Tool search results: {len(results)} tools found")
        for i, result in enumerate(results, 1):
            print(
                f"  {i}. Tool: {result.get('metadata', {}).get('tool_name', 'Unknown')}"
            )
            print(f"     Score: {result.get('score', 'N/A')}")

    except Exception as e:
        print(f"❌ Tool embeddings example error: {e}")
        logger.error(f"Tool embeddings example error: {e}")


async def document_storage_example():
    """Example: Using QdrantVectorDB for document storage."""
    print("\n=== Document Storage Example ===")

    if not is_vector_db_enabled():
        print(
            "⚠️ Vector database is disabled. Set ENABLE_VECTOR_DB=True to use this feature."
        )
        return

    try:
        # Create QdrantVectorDB instance for documents
        doc_db = QdrantVectorDB("company_docs")

        if not doc_db.enabled:
            print("❌ QdrantVectorDB not available. Trying ChromaDB...")
            doc_db = ChromaDBVectorDB("company_docs")
            if not doc_db.enabled:
                print("❌ No vector database available. Check your configuration.")
                return

        # Add documents
        documents = [
            {
                "id": "doc_001",
                "title": "Company Policy Manual",
                "content": "This document outlines our company policies for remote work, vacation time, and professional conduct.",
                "category": "policies",
            },
            {
                "id": "doc_002",
                "title": "Technical Architecture",
                "content": "Our system uses microservices architecture with Docker containers and Kubernetes orchestration.",
                "category": "technical",
            },
            {
                "id": "doc_003",
                "title": "Employee Handbook",
                "content": "Welcome to our company. Here are the guidelines for new employees including onboarding process.",
                "category": "hr",
            },
        ]

        for doc in documents:
            document_text = f"{doc['title']}\n{doc['content']}"
            success = doc_db.upsert_document(
                document=document_text,
                doc_id=doc["id"],
                metadata={
                    "title": doc["title"],
                    "category": doc["category"],
                    "type": "document",
                },
            )
            if success:
                print(f"✅ Added document: {doc['title']}")

        # Search documents
        results = doc_db.query_documents(
            query="What are the company policies?", n_results=2
        )
        print(f"Document search results: {len(results)} documents found")
        for i, result in enumerate(results, 1):
            title = result.get("metadata", {}).get("title", "Unknown")
            category = result.get("metadata", {}).get("category", "Unknown")
            print(f"  {i}. Document: {title} (Category: {category})")
            print(f"     Score: {result.get('score', 'N/A')}")

    except Exception as e:
        print(f"❌ Document storage example error: {e}")
        logger.error(f"Document storage example error: {e}")


async def knowledge_base_example():
    """Example: Using MemoryManager for long-term knowledge storage."""
    print("\n=== Knowledge Base Example ===")

    if not is_vector_db_enabled():
        print(
            "⚠️ Vector database is disabled. Set ENABLE_VECTOR_DB=True to use this feature."
        )
        return

    try:
        # Create memory manager for long-term knowledge
        kb_memory = MemoryManager(session_id="ai_knowledge", memory_type="long_term")

        if not kb_memory.vector_db or not kb_memory.vector_db.enabled:
            print("❌ Vector database not available. Check your configuration.")
            return

        # Add knowledge entries
        knowledge_entries = [
            {
                "id": "kb_001",
                "topic": "Machine Learning",
                "content": "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.",
                "tags": ["AI", "ML", "algorithms"],
            },
            {
                "id": "kb_002",
                "topic": "Neural Networks",
                "content": "Neural networks are computing systems inspired by biological neurons that can recognize patterns and make decisions through interconnected layers.",
                "tags": ["AI", "deep_learning", "neural_networks"],
            },
            {
                "id": "kb_003",
                "topic": "Natural Language Processing",
                "content": "NLP enables computers to understand, interpret, and generate human language in a valuable way for various applications.",
                "tags": ["AI", "NLP", "language_processing"],
            },
        ]

        for entry in knowledge_entries:
            document_text = f"{entry['topic']}\n{entry['content']}"
            success = kb_memory.vector_db.upsert_document(
                document=document_text,
                doc_id=entry["id"],
                metadata={
                    "topic": entry["topic"],
                    "tags": entry["tags"],
                    "type": "knowledge",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            if success:
                print(f"✅ Added knowledge: {entry['topic']}")

        # Query knowledge base
        results = kb_memory.vector_db.query_documents(
            query="How do neural networks work?", n_results=2
        )
        print(f"Knowledge base results: {len(results)} entries found")
        for i, result in enumerate(results, 1):
            topic = result.get("metadata", {}).get("topic", "Unknown")
            tags = result.get("metadata", {}).get("tags", [])
            print(f"  {i}. Topic: {topic}")
            print(f"     Tags: {', '.join(tags) if tags else 'None'}")
            print(f"     Score: {result.get('score', 'N/A')}")

    except Exception as e:
        print(f"❌ Knowledge base example error: {e}")
        logger.error(f"Knowledge base example error: {e}")


async def generic_vector_db_example():
    """Example: Using ChromaDB for custom data storage."""
    print("\n=== Generic Vector DB Example ===")

    if not is_vector_db_enabled():
        print(
            "⚠️ Vector database is disabled. Set ENABLE_VECTOR_DB=True to use this feature."
        )
        return

    try:
        # Create a generic ChromaDB instance
        generic_db = ChromaDBVectorDB("my_custom_collection")

        if not generic_db.enabled:
            print("❌ ChromaDB not available. Check your installation.")
            return

        # Add any type of data
        custom_data = [
            {
                "id": "item_001",
                "content": "This is some custom data that I want to store and search for semantic similarity",
                "category": "general",
            },
            {
                "id": "item_002",
                "content": "Another piece of information about machine learning and artificial intelligence",
                "category": "technical",
            },
            {
                "id": "item_003",
                "content": "User preferences and settings for the application configuration",
                "category": "config",
            },
        ]

        for item in custom_data:
            success = generic_db.upsert_document(
                document=item["content"],
                doc_id=item["id"],
                metadata={
                    "type": "custom",
                    "category": item["category"],
                    "created_by": "user_123",
                    "tags": ["custom", "example"],
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            if success:
                print(f"✅ Added custom item: {item['id']}")

        # Search the data
        results = generic_db.query_documents(query="custom data storage", n_results=2)
        print(f"Generic search results: {len(results)} items found")
        for i, result in enumerate(results, 1):
            category = result.get("metadata", {}).get("category", "Unknown")
            print(f"  {i}. Category: {category}")
            print(f"     Score: {result.get('score', 'N/A')}")
            print(f"     Content: {result.get('document', '')[:80]}...")

    except Exception as e:
        print(f"❌ Generic vector DB example error: {e}")
        logger.error(f"Generic vector DB example error: {e}")


async def backend_info_example():
    """Example: Checking vector database configuration and availability."""
    print("\n=== Backend Information ===")

    try:
        # Check if vector DB is enabled
        enabled = is_vector_db_enabled()
        print(f"Vector database enabled: {enabled}")

        if not enabled:
            print(
                "💡 To enable vector databases, set ENABLE_VECTOR_DB=True in your environment"
            )
            return

        # Check Qdrant configuration
        qdrant_host = os.getenv("QDRANT_HOST")
        qdrant_port = os.getenv("QDRANT_PORT")
        print(f"Qdrant configuration: Host={qdrant_host}, Port={qdrant_port}")

        # Test Qdrant availability
        try:
            qdrant_db = QdrantVectorDB("test_qdrant")
            qdrant_available = qdrant_db.enabled
            print(f"Qdrant available: {qdrant_available}")
        except Exception as e:
            print(f"Qdrant available: False (Error: {e})")

        # Test ChromaDB availability
        try:
            chroma_db = ChromaDBVectorDB("test_chroma")
            chromadb_available = chroma_db.enabled
            print(f"ChromaDB available: {chromadb_available}")
        except Exception as e:
            print(f"ChromaDB available: False (Error: {e})")

        # Show embedding model info
        try:
            load_embed_model()
            print("✅ Embedding model loaded successfully")
        except Exception as e:
            print(f"❌ Embedding model error: {e}")

    except Exception as e:
        print(f"❌ Backend info error: {e}")
        logger.error(f"Backend info error: {e}")


async def main():
    """Run all vector database examples."""
    print("🚀 Vector Database Examples")
    print("=" * 50)

    # Load environment variables
    load_dotenv()

    try:
        # Check backend availability first
        await backend_info_example()

        # Only run examples if vector DB is enabled
        if is_vector_db_enabled():
            print("\n🔄 Running vector database examples...")

            # Run examples
            await memory_example()
            await tool_embeddings_example()
            await document_storage_example()
            await knowledge_base_example()
            await generic_vector_db_example()

            print("\n✅ All examples completed successfully!")
            print("\n📋 Summary:")
            print("   • Memory operations with MemoryManager")
            print("   • Tool embeddings with ChromaDB")
            print("   • Document storage with QdrantVectorDB/ChromaDB fallback")
            print("   • Knowledge base with long-term memory")
            print("   • Generic vector database usage")
        else:
            print("\n⚠️ Vector database examples skipped (ENABLE_VECTOR_DB=False)")
            print("💡 To run examples, set ENABLE_VECTOR_DB=True in your environment")
            print("   Also ensure you have either:")
            print("   • ChromaDB installed: pip install chromadb")
            print("   • Qdrant configured: Set QDRANT_HOST and QDRANT_PORT")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        logger.error(f"Vector DB examples error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
