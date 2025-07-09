import asyncio
import json
import time
from typing import Any

import redis.asyncio as redis
from decouple import config

from mcpomni_connect.utils import (
    CLIENT_MAC_ADDRESS,
    logger,
)

# TODO: Add QDRANT DB episodic memory
# from qdrant_client import QdrantClient
# from qdrant_client.http import models
# from qdrant_client.http.models import Distance, VectorParams


class InMemoryShortTermMemory:
    """In memory short term memory"""

    def __init__(
        self,
        max_context_tokens: int = 30000,
        debug: bool = False,
    ) -> None:
        """Initialize memory storage.

        Args:
            max_context_tokens: Maximum tokens to keep in memory
            debug: Enable debug logging
        """
        self.max_context_tokens = max_context_tokens
        self.debug = debug
        self.short_term_limit = int(0.7 * max_context_tokens)
        self.agents_history: dict[str, list[dict[str, Any]]] = {}
        self.memory_config: dict[str, Any] = {
            "mode": "token_budget",  # default mode
            "value": self.short_term_limit,  # default token budget
        }

    def set_memory_config(self, mode: str, value: int = None) -> None:
        """Set global memory strategy.

        Args:
            mode: Memory mode ('sliding_window', 'token_budget')
            value: Optional value (e.g., window size or token limit)
        """
        valid_modes = {"sliding_window", "token_budget"}
        if mode.lower() not in valid_modes:
            raise ValueError(
                f"Invalid memory mode: {mode}. Must be one of {valid_modes}."
            )

        self.memory_config = {
            "mode": mode,
            "value": value,
        }

        if self.debug:
            logger.info(f"[Memory] Config set to: {self.memory_config}")

    async def truncate_message_history(
        self, agent_name: str, chat_id: str = None
    ) -> list[dict[str, Any]]:
        """Truncate message history to stay within token limits.

        Args:
            agent_name: Name of agent

        Returns:
            List of messages after truncation
        """
        logger.info(f"memory config: {self.memory_config}")
        try:
            if agent_name not in self.agents_history:
                self.agents_history[agent_name] = []
                return []

            messages = self.agents_history[agent_name]
            if chat_id is not None:
                messages = [
                    message for message in messages if message["chat_id"] == chat_id
                ]
            mode = self.memory_config.get("mode", "token_budget")
            value = self.memory_config.get("value")
            if mode.lower() == "sliding_window":
                messages = messages[-value:]

            elif mode.lower() == "token_budget":
                total_tokens = sum(len(str(msg["content"]).split()) for msg in messages)
                while value is not None and total_tokens > value and messages:
                    messages.pop(0)
                    total_tokens = sum(
                        len(str(msg["content"]).split()) for msg in messages
                    )

            return messages
        except Exception as e:
            logger.error(f"Failed to truncate message history: {e}")
            self.agents_history[agent_name] = []
            return []

    async def store_message(
        self,
        agent_name: str,
        role: str,
        content: str,
        metadata: dict | None = None,
        chat_id: str = None,
    ) -> None:
        """Store a message in memory.

        Args:
            agent_name: Name of agent
            role: Message role (e.g., 'user', 'assistant')
            content: Message content
            metadata: Optional metadata about the message
        """
        try:
            message = {
                "role": role,
                "content": content,
                "chat_id": chat_id,
                "timestamp": asyncio.get_running_loop().time(),
                "metadata": metadata or {},
            }

            if agent_name not in self.agents_history:
                self.agents_history[agent_name] = []
            self.agents_history[agent_name].append(message)

        except Exception as e:
            logger.error(f"Failed to store message: {e}")

    async def get_messages(
        self, agent_name: str, chat_id: str = None
    ) -> list[dict[str, Any]]:
        """Get messages from memory.

        Args:
            agent_name: Name of agent

        Returns:
            List of messages
        """
        try:
            if agent_name not in self.agents_history:
                self.agents_history[agent_name] = []
            messages = await self.truncate_message_history(
                agent_name=agent_name, chat_id=chat_id
            )
            return messages

        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            return []

    async def get_all_messages(self):
        try:
            messages = self.agents_history
            if messages:
                return messages
            return {}
        except Exception as e:
            logger.error(f"error getting messages: {e}")
            return {}

    async def clear_memory(self, agent_name: str = None) -> None:
        """Clear memory for an agent or all memory.

        Args:
            agent_name: Name of agent to clear (required for auto-agent mode)
        """
        try:
            if agent_name and agent_name in self.agents_history:
                del self.agents_history[agent_name]
            elif agent_name and agent_name not in self.agents_history:
                return
            else:
                self.agents_history = {}

        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")

    async def save_message_history_to_file(
        self, file_path: str, agent_name: str = None
    ) -> None:
        """Save message history to a file, appending to existing content.

        Args:
            file_path: Path to the file
            agent_name: Name of agent (if None, save all agents)
        """
        try:
            with open(file_path, "a") as f:
                # Add separator if file has content
                if f.tell() > 0:
                    f.write("\n\n")

                if agent_name:
                    messages = self.agents_history.get(agent_name, [])
                    if messages:
                        f.write(f"Agent: {agent_name}\n")
                        for message in messages:
                            f.write(f"{message['role']}: {message['content']}\n")
                else:
                    logger.info(
                        f"Saving messages for all agents: {self.agents_history}"
                    )
                    for agent, messages in self.agents_history.items():
                        if messages:
                            logger.info(f"Saving messages for agent: {agent}")
                            f.write(f"Agent: {agent}\n")
                            for message in messages:
                                f.write(f"{message['role']}: {message['content']}\n")
                            f.write("\n")
            if self.debug:
                logger.info(f"Message history saved to {file_path}")

        except Exception as e:
            logger.error(f"Failed to save message history: {e}")
            raise

    async def load_message_history_from_file(
        self, file_path: str, agent_name: str = None
    ) -> None:
        """Load message history from a file and store in in memory short term memory.

        Args:
            file_path: Path to the file
            agent_name: Name of agent (if specified, only load messages for this agent)
        """
        try:
            with open(file_path) as f:
                content = f.read()

                if "Agent:" in content:
                    sections = content.split("Agent:")
                    for section in sections[1:]:
                        lines = section.strip().split("\n")
                        current_agent = lines[0].strip()

                        # Skip if agent_name is specified and doesn't match current agent
                        if agent_name and current_agent != agent_name:
                            continue

                        messages = lines[1:]
                        for msg in messages:
                            if ":" in msg:
                                role, content = msg.split(":", 1)
                                await self.store_message(
                                    agent_name=current_agent,
                                    role=role.strip(),
                                    content=content.strip(),
                                )

            if self.debug:
                logger.info(f"Successfully loaded message history from {file_path}")

        except Exception as e:
            logger.error(f"Failed to load message history from file: {e}")


class RedisShortTermMemory:
    """Redis short term memory."""

    REDIS_HOST = config("REDIS_HOST", default="localhost")
    REDIS_PORT = config("REDIS_PORT", default=6379)
    REDIS_DB = config("REDIS_DB", default=0)

    def __init__(
        self,
        redis_client: redis.Redis | None = None,
        max_context_tokens: int = 30000,
    ) -> None:
        """Initialize."""
        self._redis_client = redis_client or redis.Redis(
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            db=self.REDIS_DB,
            decode_responses=True,
        )
        self.SHORT_TERM_LIMIT = int(0.7 * max_context_tokens)
        self.client_id = CLIENT_MAC_ADDRESS
        self.in_memory_short_term_memory = InMemoryShortTermMemory(
            max_context_tokens=max_context_tokens
        )
        logger.info(
            f"Initialized RedisShortTermMemory with client ID: {self.client_id}"
        )

    async def store_message(self, role: str, content: str, metadata: dict = None):
        """Store a message in Redis with a timestamp using the client's MAC address as ID."""
        metadata = metadata or {}
        logger.info(f"Storing message for client {self.client_id}: {content}")

        key = f"mcp_memory:{self.client_id}"
        timestamp = time.time()

        message = {
            "role": role,
            "content": str(content),
            "metadata": self._serialize(metadata),
            "timestamp": timestamp,
        }

        # Store as a JSON string in Redis
        await self._redis_client.zadd(key, {json.dumps(message): timestamp})
        await self._redis_client.set(f"mcp_last_active:{self.client_id}", timestamp)
        # store to the in memory to act as current working memory which will be use for episodic memory
        await self.in_memory_short_term_memory.store_message(role, content, metadata)
        # Enforce the short term limit
        await self.enforce_short_term_limit()

    async def get_messages(self):
        """Retrieve messages for this client using the MAC address as ID."""
        key = f"mcp_memory:{self.client_id}"
        # enforce short term limit before retrieving messages
        await self.enforce_short_term_limit()
        messages = await self._redis_client.zrange(key, 0, -1)

        # Deserialize messages and reconstruct tool calls if necessary
        return [self._deserialize(json.loads(msg)) for msg in messages]

    def _serialize(self, data):
        """Convert any non-serializable data into a JSON-compatible format."""
        try:
            return json.dumps(data, default=lambda o: o.__dict__)
        except Exception as e:
            logger.error(f"Serialization failed: {e}")
            return json.dumps({"error": "Serialization failed"})

    def _deserialize(self, data):
        """Convert stored JSON strings back to their original format if needed."""
        try:
            if "metadata" in data:
                data["metadata"] = json.loads(data["metadata"])
            return data
        except Exception as e:
            logger.error(f"Deserialization failed: {e}")
            return data

    async def get_last_active(self):
        """Get last active timestamp for this client."""
        key = f"mcp_last_active:{self.client_id}"
        last_active = await self._redis_client.get(key)
        return float(last_active) if last_active else None

    async def enforce_short_term_limit(self):
        """Enforce short term limit on the number of tokens in the context window."""
        key = f"mcp_memory:{self.client_id}"
        messages = await self._redis_client.zrange(key, 0, -1, withscores=True)

        total_tokens = sum(len(msg[0].split()) for msg in messages)
        while total_tokens > self.SHORT_TERM_LIMIT and messages:
            oldest_msg = messages.pop(0)
            await self._redis_client.zrem(key, oldest_msg[0])
            total_tokens = sum(len(msg[0].split()) for msg in messages)

        logger.debug(
            f"Enforced short term limit: {total_tokens}/{self.SHORT_TERM_LIMIT} tokens"
        )

    async def clear_memory(self):
        """Clear the memory."""
        key = f"mcp_memory:{self.client_id}"
        await self._redis_client.delete(key)
        logger.info(f"Cleared memory for client {self.client_id}")

    async def save_message_history_to_file(self, file_path: str):
        """Save the message history to a file."""
        key = f"mcp_memory:{self.client_id}"
        messages = await self._redis_client.zrange(key, 0, -1)
        messages = [self._deserialize(json.loads(msg)) for msg in messages]
        with open(file_path, "w") as f:
            for message in messages:
                f.write(f"{message['role']}: {message['content']}\n")
        logger.info(f"Saved message history to {file_path}")


# class ChromaDBMemory:
#     def __init__(self, name: str, description: str):
#         self.chroma_client = chromadb.HttpClient(host="localhost", port=8000)
#         self.collection = self._get_or_create_collection(name, description)

#     def _get_or_create_collection(self, name: str, description: str):
#         """Get or create a collection with default embedding model."""
#         try:

#             logger.info(f"Getting or creating collection: {name}")
#             collection = self.chroma_client.get_or_create_collection(
#                 name=name,
#                 metadata={
#                     "hnsw:space": "cosine",
#                     "description": description

#                 }
#             )
#             logger.info("Successfully initialized ChromaDB collection")
#             return collection
#         except Exception as e:
#             logger.error(f"Failed to initialize ChromaDB collection: {e}")
#             raise

#     def add_to_collection(self, documents: list[str], metadatas: list[dict] = None, ids: list[str] = None):
#         """Add documents to the collection using ChromaDB's internal embedding model.

#         Args:
#             collection: The ChromaDB collection
#             documents: List of text documents to store
#             metadatas: Optional list of metadata dictionaries
#             ids: Optional list of document IDs
#         """
#         try:
#             # Add documents to ChromaDB
#             self.collection.add(
#                 documents=documents,
#                 metadatas=metadatas if metadatas else None,
#                 ids=ids if ids else None
#             )
#             logger.info(f"Successfully added {len(documents)} documents to ChromaDB")
#         except Exception as e:
#             logger.error(f"Failed to add documents to ChromaDB: {e}")
#             raise

#     def query_collection(self, query: str, n_results: int = 5):
#         """Query the collection using ChromaDB's internal embedding model.

#         Args:
#             collection: The ChromaDB collection
#             query: The query text
#             n_results: Number of results to return

#         Returns:
#             dict: Query results containing documents, distances, and metadata
#         """
#         try:
#             results = self.collection.query(
#                 query_texts=[query],
#                 n_results=n_results
#             )
#             logger.debug(f"Retrieved {len(results['documents'][0])} results from ChromaDB")
#             return results
#         except Exception as e:
#             logger.error(f"Failed to query ChromaDB: {e}")
#             raise

#     def delete_from_collection(self, ids: list[str] = None, where: dict = None):
#         """Delete documents from the collection.

#         Args:
#             collection: The ChromaDB collection
#             ids: Optional list of document IDs to delete
#             where: Optional metadata filter for deletion
#         """
#         try:
#             self.collection.delete(
#                 ids=ids if ids else None,
#                 where=where if where else None
#             )
#             logger.info(f"Successfully deleted documents from ChromaDB")
#         except Exception as e:
#             logger.error(f"Failed to delete documents from ChromaDB: {e}")
#             raise

#     def update_collection(self, documents: list[str], metadatas: list[dict] = None, ids: list[str] = None):
#         """Update documents in the collection using ChromaDB's internal embedding model.

#         Args:
#             collection: The ChromaDB collection
#             documents: List of text documents to update
#             metadatas: Optional list of metadata dictionaries
#             ids: List of document IDs to update (required)
#         """
#         if not ids:
#             raise ValueError("IDs are required for updating documents")

#         try:
#             # Update documents in ChromaDB
#             self.collection.update(
#                 documents=documents,
#                 metadatas=metadatas if metadatas else None,
#                 ids=ids
#             )
#             logger.info(f"Successfully updated {len(documents)} documents in ChromaDB")
#         except Exception as e:
#             logger.error(f"Failed to update documents in ChromaDB: {e}")
#             raise


# class QdrantMemory:
#     def __init__(self, name: str, description: str):
#         """Initialize Qdrant memory storage.

#         Args:
#             name: Name of the collection
#             description: Description of the collection
#         """
#         self.client = QdrantClient(host=config("QDRANT_HOST", default="localhost"), port=config("QDRANT_PORT", default=6333))
#         self.collection_name = name
#         self.description = description
#         self._ensure_collection()

#     def _ensure_collection(self):
#         """Ensure the collection exists, create if it doesn't."""
#         try:
#             collections = self.client.get_collections().collections
#             collection_names = [collection.name for collection in collections]

#             if self.collection_name not in collection_names:
#                 self.client.create_collection(
#                     collection_name=self.collection_name,
#                     vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
#                 )
#                 logger.info(f"Created new Qdrant collection: {self.collection_name}")
#             else:
#                 logger.info(f"Using existing Qdrant collection: {self.collection_name}")
#         except Exception as e:
#             logger.error(f"Failed to initialize Qdrant collection: {e}")
#             raise

#     def add_to_collection(self, documents: List[str], conversation: str, metadatas: List[Dict] = None, ids: List[str] = None):
#         """Add documents to the collection.

#         Args:
#             documents: List of text documents to store
#             metadatas: Optional list of metadata dictionaries
#             ids: Optional list of document IDs
#         """
#         try:
#             if not ids:
#                 ids = [str(uuid.uuid4()) for _ in documents]

#             # Convert documents to points
#             points = []
#             for i, (doc, doc_id) in enumerate(zip(documents, ids)):
#                 metadata = metadatas[i] if metadatas else {}
#                 metadata["text"] = doc
#                 metadata["previous_conversation"] = conversation
#                 metadata["timestamp"] = str(datetime.now())

#                 points.append(models.PointStruct(
#                     id=doc_id,
#                     vector=embed_text(doc),
#                     payload=metadata
#                 ))

#             # Upsert points to collection
#             self.client.upsert(
#                 collection_name=self.collection_name,
#                 points=points
#             )
#             logger.info(f"Successfully added {len(documents)} documents to Qdrant")
#         except Exception as e:
#             logger.error(f"Failed to add documents to Qdrant: {e}")
#             raise

#     def query_collection(self, query: str, n_results: int = 5, distance_threshold: float = 0.70) -> Dict[str, Any]:
#         """Query the collection.

#         Args:
#             query: The query text
#             n_results: Number of results to return

#         Returns:
#             Dict containing query results
#         """
#         try:
#             # Search for similar documents
#             search_result = self.client.query_points(
#                 collection_name=self.collection_name,
#                 query=embed_text(query),
#                 limit=n_results,
#                 with_payload=True
#             ).points
#             if hasattr(search_result[0], "payload"):
#                 #logger.info(f"Search result: {search_result}")
#                 # format the results and filter by distance threshold if its greater than or equal to the threshold
#                 results = {
#                     "documents": [[hit.payload["text"] for hit in search_result if hit.score >= distance_threshold]],
#                     "previous_conversation": [[hit.payload["previous_conversation"] for hit in search_result if hit.score >= distance_threshold]],
#                     "distances": [[hit.score for hit in search_result if hit.score >= distance_threshold]],
#                     "metadatas": [[hit.payload for hit in search_result if hit.score >= distance_threshold]]
#                 }
#                 #logger.info(f" results distances: {results['distances']}")
#                 logger.info(f"Retrieved {len(results['documents'])} results from Qdrant")
#                 return results
#             else:
#                 logger.error(f"Failed to retrieve results from Qdrant: {search_result}")
#                 raise Exception(f"Failed to retrieve results from Qdrant: {search_result}")
#         except Exception as e:
#             logger.error(f"Failed to query Qdrant: {e}")
#             raise

#     def delete_from_collection(self, ids: List[str] = None, where: Dict = None):
#         """Delete documents from the collection.

#         Args:
#             ids: Optional list of document IDs to delete
#             where: Optional filter for deletion
#         """
#         try:
#             if ids:
#                 self.client.delete(
#                     collection_name=self.collection_name,
#                     points_selector=models.PointIdsList(
#                         points=ids
#                     )
#                 )
#             elif where:
#                 self.client.delete(
#                     collection_name=self.collection_name,
#                     points_selector=models.FilterSelector(
#                         filter=models.Filter(
#                             must=[
#                                 models.FieldCondition(
#                                     key=key,
#                                     match=models.MatchValue(value=value)
#                                 )
#                                 for key, value in where.items()
#                             ]
#                         )
#                     )
#                 )
#             logger.info("Successfully deleted documents from Qdrant")
#         except Exception as e:
#             logger.error(f"Failed to delete documents from Qdrant: {e}")
#             raise

#     def update_collection(self, documents: List[str], conversation: str, metadatas: List[Dict] = None, ids: List[str] = None):
#         """Update documents in the collection.

#         Args:
#             documents: List of text documents to update
#             metadatas: Optional list of metadata dictionaries
#             ids: List of document IDs to update (required)
#         """
#         if not ids:
#             raise ValueError("IDs are required for updating documents")

#         try:
#             # Convert documents to points
#             points = []
#             for i, (doc, doc_id) in enumerate(zip(documents, ids)):
#                 metadata = metadatas[i] if metadatas else {}
#                 metadata["text"] = doc
#                 metadata["previous_conversation"] = conversation
#                 metadata["timestamp"] = str(datetime.now())
#                 logger.info(f"embedding text: {embed_text(doc)}")
#                 points.append(models.PointStruct(
#                     id=doc_id,
#                     vector=embed_text(doc),
#                     payload=metadata
#                 ))

#             # Upsert points to collection
#             self.client.upsert(
#                 collection_name=self.collection_name,
#                 points=points
#             )
#             logger.info(f"Successfully updated {len(documents)} documents in Qdrant")
#         except Exception as e:
#             logger.error(f"Failed to update documents in Qdrant: {e}")
#             raise

# class EpisodicMemory(QdrantMemory):
#     def __init__(self, name: str, description: str):
#         """Initialize episodic memory using Qdrant storage.

#         Args:
#             name: Name of the collection
#             description: Description of the collection
#         """
#         super().__init__(name, description)
#         self.EPISODIC_MEMORY_PROMPT = EPISODIC_MEMORY_PROMPT

#     async def create_episodic_memory(self, messages: List[Dict], llm_connection: Callable) -> Dict:
#         """Create an episodic memory from a conversation.

#         Args:
#             messages: The conversation messages to analyze
#             llm_connection: The LLM connection to use for memory creation

#         Returns:
#             Dict: The created memory
#         """
#         try:
#             llm_messages = []
#             llm_messages.append({"role": "system", "content": self.EPISODIC_MEMORY_PROMPT})
#             llm_messages.append({"role": "user", "content": str(messages)})
#             response = await llm_connection.llm_call(llm_messages)
#             if response and response.choices:
#                 logger.info(f"response: {response.choices[0].message.content}")
#                 memory = clean_json_response(response.choices[0].message.content)

#                 # Store the memory in Qdrant
#                 self.add_to_collection(
#                     documents=[memory],
#                     metadatas=[{
#                         "type": "episodic_memory",
#                     }],
#                     conversation=str(messages),
#                     ids=[str(uuid.uuid4())]
#                 )

#                 logger.debug(f"Successfully created episodic memory: {memory}")
#                 return memory

#             return None
#         except Exception as e:
#             logger.error(f"Failed to create episodic memory: {e}")
#             return None

#     async def retrieve_relevant_memories(self, query: str, n_results: int = 5) -> List[Dict]:
#         """Retrieve relevant episodic memories based on a query.

#         Args:
#             query: The query to search for relevant memories
#             n_results: Number of memories to retrieve

#         Returns:
#             List[Dict]: List of relevant memories
#         """
#         try:
#             final_results = []
#             results = self.query_collection(query, n_results)
#             if results and "documents" in results:
#                 documents = results.get("documents", [])
#                 # Flatten nested lists defensively
#                 flat_docs = []
#                 for item in documents:
#                     if isinstance(item, list):
#                         flat_docs.extend(item)
#                     else:
#                         flat_docs.append(item)

#                 # Parse each document safely
#                 for i, doc in enumerate(flat_docs):
#                     try:
#                         final_results.append(json.loads(doc))
#                     except (TypeError, json.JSONDecodeError) as e:
#                         logger.warning(f"Failed to parse document at index {i}: {doc} — Error: {e}")
#             logger.debug(f"length of final results: {len(final_results)}")
#             return final_results
#         except Exception as e:
#             logger.error(f"Failed to retrieve episodic memories: {e}")
#             return []


class DatabaseSessionMemory:
    """Database-backed session memory using DatabaseSessionService."""

    def __init__(
        self,
        db_url: str = None,
        max_context_tokens: int = 30000,
        debug: bool = False,
    ) -> None:
        """Initialize database session memory.

        Args:
            db_url: Database URL (defaults to SQLite if not provided)
            max_context_tokens: Maximum tokens to keep in memory
            debug: Enable debug logging
        """
        from mcpomni_connect.session.database_session import DatabaseSessionService
        from mcpomni_connect.events.event import Event, EventActions
        from mcpomni_connect.session._session_util import UserContent, AssistantContent

        self.max_context_tokens = max_context_tokens
        self.debug = debug
        self.short_term_limit = int(0.7 * max_context_tokens)
        self.client_id = CLIENT_MAC_ADDRESS
        
       
        if not db_url:
            db_url = f"sqlite:///mcp_memory_{self.client_id}.db"
        
        self.db_service = DatabaseSessionService(db_url)
        self.app_name = "mcp_omni_connect"
        self.user_id = self.client_id
        self.session_id = None  
        
       
        self.Event = Event
        self.EventActions = EventActions  
        self.UserContent = UserContent
        self.AssistantContent = AssistantContent
        
       
        self.memory_config: dict[str, Any] = {
            "mode": "token_budget",  
            "value": self.short_term_limit,  
        }
        
      
        self.in_memory_short_term_memory = InMemoryShortTermMemory(
            max_context_tokens=max_context_tokens,
            debug=debug
        )
        
        logger.info(
            f"Initialized DatabaseSessionMemory with client ID: {self.client_id}, DB: {db_url}"
        )

    def set_memory_config(self, mode: str, value: int = None) -> None:
        """Set global memory strategy.

        Args:
            mode: Memory mode ('sliding_window', 'token_budget')
            value: Optional value (e.g., window size or token limit)
        """
        valid_modes = {"sliding_window", "token_budget"}
        if mode.lower() not in valid_modes:
            raise ValueError(
                f"Invalid memory mode: {mode}. Must be one of {valid_modes}."
            )

        self.memory_config = {
            "mode": mode,
            "value": value,
        }
        
       
        self.in_memory_short_term_memory.set_memory_config(mode, value)

        if self.debug:
            logger.info(f"[DatabaseMemory] Config set to: {self.memory_config}")

    async def _ensure_session(self):
        """Ensure we have an active session."""
        if not self.session_id:
            session = await self.db_service.create_session(
                app_name=self.app_name,
                user_id=self.user_id,
                state={"memory_type": "database", "client_id": self.client_id}
            )
            self.session_id = session.id
            logger.debug(f"Created database session: {self.session_id}")

    async def store_message(self, role: str, content: str, metadata: dict = None):
        """Store a message in the database with session management."""
        metadata = metadata or {}
        
        if self.debug:
            logger.info(f"Storing message for client {self.client_id}: {content}")

        await self._ensure_session()
        
        
        session = await self.db_service.get_session(
            app_name=self.app_name,
            user_id=self.user_id,
            session_id=self.session_id
        )
        
        if not session:
           
            self.session_id = None  
            await self._ensure_session()
            session = await self.db_service.get_session(
                app_name=self.app_name,
                user_id=self.user_id,
                session_id=self.session_id
            )

       
        if role.lower() == "user":
            event_content = self.UserContent(text=content)
        elif role.lower() in ["assistant", "system"]:
            event_content = self.AssistantContent(text=content)
        else:
            event_content = self.UserContent(text=content)  
        
        
        event = self.Event(
            invocation_id=f"msg_{time.time()}",
            author=role,
            content=event_content,
            actions=self.EventActions(
                state_delta={
                    "last_message": content,
                    "last_role": role,
                    "message_count": len(session.events) + 1,
                    **metadata
                }
            )
        )
        
       
        await self.db_service.append_event(session, event)
        
        
        await self.in_memory_short_term_memory.store_message(role, content, metadata)
        
        
        await self.enforce_short_term_limit()

    async def get_messages(self):
        """Retrieve messages from the database session."""
        await self._ensure_session()
        
       
        await self.enforce_short_term_limit()
        
        session = await self.db_service.get_session(
            app_name=self.app_name,
            user_id=self.user_id,
            session_id=self.session_id
        )
        
        if not session:
            return []
        
       
        messages = []
        for event in session.events:
            message = {
                "role": event.author,
                "content": event.content.text if hasattr(event.content, 'text') else str(event.content),
                "metadata": event.actions.state_delta if event.actions else {},
                "timestamp": event.timestamp,
            }
            messages.append(message)
        
        return messages

    async def get_last_active(self):
        """Get last active timestamp for this client."""
        await self._ensure_session()
        
        session = await self.db_service.get_session(
            app_name=self.app_name,
            user_id=self.user_id,
            session_id=self.session_id
        )
        
        if session:
            return session.last_update_time
        return None

    async def enforce_short_term_limit(self):
        """Enforce memory limits based on configured strategy."""
        await self._ensure_session()
        
        session = await self.db_service.get_session(
            app_name=self.app_name,
            user_id=self.user_id,
            session_id=self.session_id
        )
        
        if not session or not session.events:
            return
        
        mode = self.memory_config.get("mode", "token_budget")
        value = self.memory_config.get("value", self.short_term_limit)
        
        if mode == "sliding_window":
            
            if value and len(session.events) > value:
                
                logger.debug(f"Session has {len(session.events)} events, limit is {value}")
        
        elif mode == "token_budget":
          
            total_tokens = 0
            for event in session.events:
                if hasattr(event.content, 'text') and event.content.text:
                    total_tokens += len(event.content.text.split())
            
            if total_tokens > value:
                logger.debug(f"Token budget exceeded: {total_tokens}/{value} tokens")
               

        logger.debug(f"Memory limit check complete for session {self.session_id}")

    async def clear_memory(self):
        """Clear the memory by deleting the current session."""
        if self.session_id:
            try:
                await self.db_service.delete_session(
                    app_name=self.app_name,
                    user_id=self.user_id,
                    session_id=self.session_id
                )
                logger.info(f"Cleared database memory for client {self.client_id}")
            except Exception as e:
                logger.error(f"Failed to clear database memory: {e}")
            finally:
                self.session_id = None
        
        
        await self.in_memory_short_term_memory.clear_memory()

    async def get_all_messages(self, agent_name: str = None):
        """Get all messages, optionally filtered by agent."""
        messages = await self.get_messages()
        
        if agent_name:
           
            return [msg for msg in messages if msg.get("metadata", {}).get("agent_name") == agent_name]
        
        return messages

    async def save_message_history_to_file(self, filename: str, agent_name: str = None):
        """Save message history to a JSON file."""
        messages = await self.get_all_messages(agent_name)
        
        
        self.in_memory_short_term_memory.agents_history[agent_name or "default"] = [
            {
                "role": msg["role"],
                "content": msg["content"], 
                "metadata": msg.get("metadata", {})
            }
            for msg in messages
        ]
        
        await self.in_memory_short_term_memory.save_message_history_to_file(filename, agent_name)

    async def load_message_history_from_file(self, filename: str, agent_name: str = None):
        """Load message history from a JSON file."""
        
        await self.in_memory_short_term_memory.load_message_history_from_file(filename, agent_name)
        
        
        loaded_messages = self.in_memory_short_term_memory.agents_history.get(agent_name or "default", [])
        
        for msg in loaded_messages:
            await self.store_message(
                role=msg["role"],
                content=msg["content"],
                metadata=msg.get("metadata", {})
            )
