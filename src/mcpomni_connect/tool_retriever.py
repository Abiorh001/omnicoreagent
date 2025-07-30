from qdrant_client import QdrantClient, models
from typing import List, Dict, Any
import hashlib
import logging

logger = logging.getLogger(__name__)


class ToolRetriever:
    def __init__(self):
        # Internal tool search optimization - no public API needed
        self.client = None
        self.collection_name = "tools_collection"
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.tools_storage = {}
        self._initialized = False
        
        # Initialize Qdrant client
        self._initialize_qdrant()
    
    def _initialize_qdrant(self):
        """Initialize Qdrant client and collection."""
        try:
            self.client = QdrantClient(":memory:")
            vector_size = self.client.get_embedding_size(self.model_name)
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size, distance=models.Distance.COSINE
                ),
                optimizers_config=models.OptimizersConfigDiff(memmap_threshold=20000),
                on_disk=True,
            )
            self._initialized = True
            logger.info(f"Successfully initialized Qdrant collection: {self.collection_name}")
        except ImportError:
            logger.warning("fastembed not available, using simple text matching")
            self.client = None
        except Exception as e:
            logger.warning(f"Qdrant initialization failed: {e}")
            self.client = None

    def upsert_tools(self, tool_md: str) -> None:
        """
        Upsert a single markdown-formatted tool description into Qdrant.
        
        Args:
            tool_md: Markdown-formatted tool description
        """
        try:
            # Generate a unique ID based on content hash
            unique_id = hashlib.md5(tool_md.encode()).hexdigest()[:8]
            
            # Store in simple dict if Qdrant is not available
            if not self.client:
                self.tools_storage[unique_id] = {
                    "content": tool_md,
                    "type": "markdown"
                }
                return
                
            doc = models.Document(
                text=tool_md,
                model=self.model_name,
            )
            payload = {"content": tool_md, "type": "markdown"}
            
            self.client.upload_collection(
                collection_name=self.collection_name,
                vectors=[doc],
                ids=[unique_id],
                payload=[payload],
            )
        except Exception as e:
            logger.warning(f"Failed to upsert markdown tool: {e}")

    def query_tools(
        self, query: str, top_k: int = 20, all_tools: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Semantic tool search - our core feature"""
        logger.info(f"ToolRetriever: Searching for query '{query}' with {len(all_tools or [])} tools")
        
        if not all_tools:
            logger.warning("ToolRetriever: No tools available")
            return []
        
        # Enhanced query processing for better semantic matching
        enhanced_query = self._enhance_query(query)
        logger.info(f"ToolRetriever: Enhanced query: '{enhanced_query}'")
        
        # Primary: Vector search (semantic)
        if self.client:
            try:
                query_doc = models.Document(text=enhanced_query, model=self.model_name)
                search_result = self.client.query_points(
                    collection_name=self.collection_name, query=query_doc, limit=top_k
                ).points
                
                if search_result:
                    # Fast lookup using content hash
                    content_to_tool = {tool.get("md", ""): tool for tool in all_tools}
                    relevant_tools = []
                    
                    for point in search_result:
                        payload = point.payload
                        if payload.get("type") == "markdown":
                            content = payload.get("content", "")
                            if content in content_to_tool:
                                relevant_tools.append(content_to_tool[content])
                    
                    if relevant_tools:
                        logger.info(f"ToolRetriever: Vector search found {len(relevant_tools)} relevant tools")
                        return relevant_tools
            except Exception as e:
                logger.warning(f"Vector search failed: {e}")
        
        # Fallback: Enhanced text search (still semantic-aware)
        logger.info("ToolRetriever: Using enhanced text search fallback")
        result = self._enhanced_text_search(enhanced_query, all_tools, top_k)
        logger.info(f"ToolRetriever: Text search found {len(result)} relevant tools")
        return result
    
    def _simple_text_search(self, query: str, all_tools: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
        """Fast text matching fallback - optimized for internal use"""
        if not all_tools:
            return []
        
        query_lower = query.lower()
        query_words = set(word for word in query_lower.split() if len(word) > 2)
        
        # Fast path for "show all" queries
        if any(word in query_lower for word in ["all", "show", "list", "every"]):
            return all_tools[:top_k]
        
        # Single pass scoring
        scored_tools = []
        for tool in all_tools:
            tool_md = tool.get("md", "")
            tool_lower = tool_md.lower()
            
            # Count matching words
            matches = sum(1 for word in query_words if word in tool_lower)
            if matches > 0:
                scored_tools.append((tool, matches))
        
        # Return top_k sorted by score
        scored_tools.sort(key=lambda x: x[1], reverse=True)
        return [tool for tool, score in scored_tools[:top_k]]
    
    def _enhance_query(self, query: str) -> str:
        """Enhance query with common tool-related keywords"""
        query_lower = query.lower()
        
        # Add tool-related keywords based on query content
        enhancements = []
        
        # File operations
        if any(word in query_lower for word in ["file", "read", "write", "create", "delete", "copy", "move"]):
            enhancements.extend(["file", "filesystem", "io"])
        
        # Web/HTTP operations
        if any(word in query_lower for word in ["http", "url", "web", "api", "request", "fetch"]):
            enhancements.extend(["http", "web", "api", "network"])
        
        # Database operations
        if any(word in query_lower for word in ["database", "sql", "query", "db", "table"]):
            enhancements.extend(["database", "sql", "query"])
        
        # System operations
        if any(word in query_lower for word in ["system", "process", "command", "execute", "run"]):
            enhancements.extend(["system", "process", "command"])
        
        # Math/calculation
        if any(word in query_lower for word in ["calculate", "math", "compute", "sum", "multiply"]):
            enhancements.extend(["math", "calculation", "compute"])
        
        # Text processing
        if any(word in query_lower for word in ["text", "string", "format", "parse", "extract"]):
            enhancements.extend(["text", "string", "format"])
        
        # If no specific enhancements, add general tool keywords
        if not enhancements:
            enhancements = ["tool", "function", "operation"]
        
        enhanced_query = query + " " + " ".join(enhancements)
        return enhanced_query
    
    def _enhanced_text_search(self, query: str, all_tools: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
        """Enhanced text search with better scoring and filtering"""
        if not all_tools:
            return []
        
        query_lower = query.lower()
        query_words = set(word for word in query_lower.split() if len(word) > 2)
        
        # Fast path for "show all" queries
        if any(word in query_lower for word in ["all", "show", "list", "every"]):
            return all_tools[:top_k]
        
        # Enhanced scoring with multiple criteria
        scored_tools = []
        for tool in all_tools:
            tool_md = tool.get("md", "")
            tool_lower = tool_md.lower()
            
            # Extract tool name for better matching
            tool_name = ""
            if "### `" in tool_md:
                tool_name = tool_md.split("### `")[1].split("`")[0].lower()
            
            score = 0
            
            # 1. Exact word matches (highest priority)
            exact_matches = sum(1 for word in query_words if word in tool_lower)
            score += exact_matches * 10
            
            # 2. Tool name matches (high priority)
            if tool_name:
                name_matches = sum(1 for word in query_words if word in tool_name)
                score += name_matches * 8
            
            # 3. Partial word matches (medium priority)
            partial_matches = 0
            for word in query_words:
                for tool_word in tool_lower.split():
                    if len(word) > 2 and (word in tool_word or tool_word in word):
                        partial_matches += 1
                        break
            score += partial_matches * 3
            
            # 4. Semantic similarity (low priority)
            # Check if query words appear in tool description
            description_matches = sum(1 for word in query_words if word in tool_lower)
            score += description_matches * 1
            
            if score > 0:
                scored_tools.append((tool, score))
        
        # If no matches found, return a subset of most commonly used tools
        if not scored_tools:
            logger.info("ToolRetriever: No scored tools found, returning common tools")
            # Return tools that are likely to be useful (file operations, basic tools)
            common_tools = []
            for tool in all_tools:
                tool_md = tool.get("md", "")
                tool_lower = tool_md.lower()
                
                # Prioritize common tool categories
                if any(keyword in tool_lower for keyword in ["file", "read", "write", "list", "get", "set"]):
                    common_tools.append((tool, 1))
                
                if len(common_tools) >= top_k:
                    break
            
            logger.info(f"ToolRetriever: Found {len(common_tools)} common tools")
            return [tool for tool, score in common_tools[:top_k]]
        
        # Return top_k sorted by score
        scored_tools.sort(key=lambda x: x[1], reverse=True)
        return [tool for tool, score in scored_tools[:top_k]]
    

