#!/usr/bin/env python3
"""
Examples demonstrating the unified vector database interface for different use cases.
"""

import asyncio
from mcpomni_connect.memory_store.memory_management.vector_db_factory import (
    create_vector_db,
    create_memory_vector_db,
    create_tool_vector_db,
    create_document_vector_db,
    create_knowledge_vector_db,
    get_available_backends,
    is_backend_available,
)


async def memory_example():
    """Example: Using vector database for memory operations."""
    print("=== Memory Operations Example ===")

    # Create memory-specific vector database
    memory_db = create_memory_vector_db(
        session_id="user_123", memory_type="episodic", preferred_backend="auto"
    )

    # Add memory entries
    await memory_db.add_to_collection_async(
        doc_id="mem_001",
        document="User asked about Python programming and received help with async/await",
        metadata={
            "timestamp": "2024-01-15T10:30:00",
            "topic": "programming",
            "language": "python",
        },
    )

    # Query memory
    results = await memory_db.query_collection_async(
        query="Python programming help", n_results=3
    )
    print(f"Memory query results: {results}")


async def tool_embeddings_example():
    """Example: Using vector database for tool embeddings."""
    print("\n=== Tool Embeddings Example ===")

    # Create tool-specific vector database
    tool_db = create_tool_vector_db(
        collection_name="python_tools", preferred_backend="auto"
    )

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
        await tool_db.add_to_collection_async(
            doc_id=tool["name"],
            document=f"{tool['description']}\n{tool['function']}",
            metadata={
                "tool_name": tool["name"],
                "category": "utility",
                "language": "python",
            },
        )

    # Semantic search for tools
    results = await tool_db.query_collection_async(
        query="I need to read a file and do calculations", n_results=2
    )
    print(f"Tool search results: {results}")


async def document_storage_example():
    """Example: Using vector database for document storage."""
    print("\n=== Document Storage Example ===")

    # Create document-specific vector database
    doc_db = create_document_vector_db(
        collection_name="company_docs", preferred_backend="auto"
    )

    # Add documents
    documents = [
        {
            "id": "doc_001",
            "title": "Company Policy Manual",
            "content": "This document outlines our company policies...",
            "category": "policies",
        },
        {
            "id": "doc_002",
            "title": "Technical Architecture",
            "content": "Our system uses microservices architecture...",
            "category": "technical",
        },
        {
            "id": "doc_003",
            "title": "Employee Handbook",
            "content": "Welcome to our company. Here are the guidelines...",
            "category": "hr",
        },
    ]

    for doc in documents:
        await doc_db.add_to_collection_async(
            doc_id=doc["id"],
            document=f"{doc['title']}\n{doc['content']}",
            metadata={
                "title": doc["title"],
                "category": doc["category"],
                "type": "document",
            },
        )

    # Search documents
    results = await doc_db.query_collection_async(
        query="What are the company policies?", n_results=2
    )
    print(f"Document search results: {results}")


async def knowledge_base_example():
    """Example: Using vector database for knowledge base."""
    print("\n=== Knowledge Base Example ===")

    # Create knowledge-specific vector database
    kb_db = create_knowledge_vector_db(
        collection_name="ai_knowledge", preferred_backend="auto"
    )

    # Add knowledge entries
    knowledge_entries = [
        {
            "id": "kb_001",
            "topic": "Machine Learning",
            "content": "Machine learning is a subset of artificial intelligence...",
            "tags": ["AI", "ML", "algorithms"],
        },
        {
            "id": "kb_002",
            "topic": "Neural Networks",
            "content": "Neural networks are computing systems inspired by biological neurons...",
            "tags": ["AI", "deep_learning", "neural_networks"],
        },
        {
            "id": "kb_003",
            "topic": "Natural Language Processing",
            "content": "NLP enables computers to understand and process human language...",
            "tags": ["AI", "NLP", "language_processing"],
        },
    ]

    for entry in knowledge_entries:
        await kb_db.add_to_collection_async(
            doc_id=entry["id"],
            document=f"{entry['topic']}\n{entry['content']}",
            metadata={
                "topic": entry["topic"],
                "tags": entry["tags"],
                "type": "knowledge",
            },
        )

    # Query knowledge base
    results = await kb_db.query_collection_async(
        query="How do neural networks work?", n_results=2
    )
    print(f"Knowledge base results: {results}")


async def generic_vector_db_example():
    """Example: Using vector database for any purpose."""
    print("\n=== Generic Vector DB Example ===")

    # Create a generic vector database
    generic_db = create_vector_db(
        collection_name="my_custom_collection",
        preferred_backend="auto",
        purpose="custom",
        owner="user_123",
    )

    # Add any type of data
    await generic_db.add_to_collection_async(
        doc_id="item_001",
        document="This is some custom data that I want to store and search",
        metadata={
            "type": "custom",
            "created_by": "user_123",
            "tags": ["custom", "example"],
        },
    )

    # Search the data
    results = await generic_db.query_collection_async(query="custom data", n_results=1)
    print(f"Generic search results: {results}")


async def backend_info_example():
    """Example: Checking available backends."""
    print("\n=== Backend Information ===")

    # Get available backends
    backends = get_available_backends()
    print(f"Available backends: {backends}")

    # Check specific backends
    qdrant_available = is_backend_available("qdrant")
    chromadb_available = is_backend_available("chromadb")

    print(f"Qdrant available: {qdrant_available}")
    print(f"ChromaDB available: {chromadb_available}")


async def main():
    """Run all examples."""
    print("🚀 Vector Database Examples")
    print("=" * 50)

    try:
        # Check backend availability first
        await backend_info_example()

        # Run examples
        await memory_example()
        await tool_embeddings_example()
        await document_storage_example()
        await knowledge_base_example()
        await generic_vector_db_example()

        print("\n✅ All examples completed successfully!")

    except Exception as e:
        print(f"❌ Error running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
