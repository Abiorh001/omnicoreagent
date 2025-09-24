import uuid
from datetime import datetime, timezone
from typing import List, Any, Callable, Optional, Tuple, Dict
from omnicoreagent.core.utils import (
    logger,
    is_vector_db_enabled,
    normalize_enriched_tool,
)
from decouple import config
import asyncio
import json


from omnicoreagent.core.memory_store.memory_management.base_vectordb_handler import (
    BaseVectorDBHandler,
)
from omnicoreagent.core.tools.semantic_tools.system_prompt import (
    tool_semantic_enricher_system_prompt,
)
from omnicoreagent.core.constants import MCP_TOOLS_REGISTRY
import math
import re
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import asyncio
import time

BATCH_SIZE = 10


@dataclass
class RetrievalConfig:
    """Configuration for BM25 retrieval parameters"""

    k1: float = 1.5
    b: float = 0.75


@dataclass
class ToolDocument:
    """Structured representation of a tool document"""

    tool_name: str
    tool_description: str
    tool_parameters: dict
    mcp_server_name: str
    tokens: List[str]
    raw_text: str

    def __post_init__(self):
        if not self.tokens:
            self.tokens = self._tokenize(self.raw_text)

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        if not text:
            return []
        return re.findall(r"\w+", text.lower())


class ToolFallbackRetriever:
    """BM25-based tool retrieval fallback system (no caching)"""

    def __init__(self):
        self.config = RetrievalConfig()

    def tokenize(self, text: str) -> Tuple[str, ...]:
        if not text or not isinstance(text, str):
            return tuple()
        return tuple(re.findall(r"\w+", text.lower()))

    def _prepare_tool_document(self, tool: Dict[str, Any]) -> Optional[ToolDocument]:
        try:
            raw_tool = tool.get("raw_tool")
            enriched_tool = tool.get("enriched_tool")
            mcp_server_name = tool.get("mcp_server_name")
            tool_name = raw_tool.get("name", "")
            tool_description = raw_tool.get("description", "")
            tool_parameters = raw_tool.get("parameters", {})

            if not tool_name or not mcp_server_name:
                logger.warning(f"Tool missing required fields: {tool}")
                return None

            tokens = list(self.tokenize(enriched_tool))

            return ToolDocument(
                tool_name=tool_name,
                tool_description=tool_description,
                tool_parameters=tool_parameters,
                mcp_server_name=mcp_server_name,
                tokens=tokens,
                raw_text=enriched_tool,
            )
        except Exception as e:
            logger.error(f"Error preparing tool document: {e}, tool: {tool}")
            return None

    def _compute_idf_scores(self, documents: List[ToolDocument]) -> Dict[str, float]:
        if not documents:
            return {}

        N = len(documents)
        term_doc_freq = defaultdict(int)

        for doc in documents:
            unique_terms = set(doc.tokens)
            for term in unique_terms:
                term_doc_freq[term] += 1

        idf_scores = {}
        for term, df in term_doc_freq.items():
            idf_scores[term] = math.log((N - df + 0.5) / (df + 0.5) + 1)

        return idf_scores

    def bm25_score(
        self, query_tokens: List[str], documents: List[ToolDocument]
    ) -> List[Tuple[float, ToolDocument]]:
        if not query_tokens or not documents:
            return []

        N = len(documents)
        if N == 0:
            return []

        total_doc_length = sum(len(doc.tokens) for doc in documents)
        avgdl = total_doc_length / N if N > 0 else 0

        idf_scores = self._compute_idf_scores(documents)
        scored_docs = []

        for doc in documents:
            if not doc.tokens:
                scored_docs.append((0.0, doc))
                continue

            score = 0.0
            doc_len = len(doc.tokens)
            term_frequencies = Counter(doc.tokens)

            for query_term in query_tokens:
                if query_term not in idf_scores:
                    continue

                tf = term_frequencies.get(query_term, 0)
                if tf == 0:
                    continue

                idf = idf_scores[query_term]
                numerator = tf * (self.config.k1 + 1)
                denominator = tf + self.config.k1 * (
                    1
                    - self.config.b
                    + self.config.b * (doc_len / avgdl if avgdl > 0 else 1)
                )

                score += idf * (numerator / denominator)

            scored_docs.append((score, doc))

        return scored_docs

    async def fallback_tools(
        self,
        query: str,
        mcp_tools: Dict[str, Any],
        top_k: int,
        similarity_threshold: float,
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant tools using BM25 scoring as fallback"""
        start_time = time.time()

        if not query or not isinstance(query, str):
            return []
        stored_tools = MCP_TOOLS_REGISTRY
        if not stored_tools or not isinstance(stored_tools, dict):
            return []

        query = query.strip()
        if not query:
            return []

        try:
            # flatten all tool dicts from the stored tools
            all_tools = []
            mcp_server_names = []
            for server_name, tools in mcp_tools.items():
                mcp_server_names.append(server_name)
            for _, tool in stored_tools.items():
                stored_mcp_server_name = tool["mcp_server_name"]

                if stored_mcp_server_name.lower().strip() in mcp_server_names:
                    tool_data = {
                        "mcp_server_name": tool["mcp_server_name"],
                        "raw_tool": tool["raw_tool"],
                        "enriched_tool": tool["enriched_tool"],
                    }
                    all_tools.append(tool_data)
                else:
                    logger.info(
                        f"Mcp server of this tool: {tool['raw_tool']['name']} is not connected"
                    )

            documents = [self._prepare_tool_document(tool=tool) for tool in all_tools]
            documents = [doc for doc in documents if doc]

            if not documents:
                return []

            query_tokens = list(self.tokenize(query))
            if not query_tokens:
                return []

            scored_docs = self.bm25_score(query_tokens, documents)
            if not scored_docs:
                return []

            scored_docs = [
                (score, doc)
                for score, doc in scored_docs
                if score >= similarity_threshold
            ]
            scored_docs.sort(key=lambda x: x[0], reverse=True)
            top_docs = scored_docs[:top_k]

            results = []
            for score, doc in top_docs:
                results.append(
                    {
                        "mcp_server_name": doc.mcp_server_name,
                        "raw_tool": {
                            "name": doc.tool_name,
                            "description": doc.tool_description,
                            "parameters": doc.tool_parameters,
                        },
                    }
                )

            # logger.info(
            #     f"Retrieved {len(results)} tools for query '{query}' in {time.time() - start_time:.3f}s"
            # )
            return results

        except Exception as e:
            logger.error(f"Error in fallback_tools: {e}", exc_info=True)
            return []


class SemanticToolManager(BaseVectorDBHandler):
    """"""

    def __init__(
        self,
        llm_connection: Callable,
        memory_type: str = "semantic-tools",
        is_background: bool = False,
    ):
        """Initialize memory manager with automatic backend selection.

        Args:
            memory_type: Type of memory (semantic-tools)
            is_background: Whether this is for background processing
            llm_connection: LLM connection for embeddings
        """

        collection_name = f"{memory_type}"
        # initialize vector DB
        super().__init__(
            collection_name=collection_name,
            memory_type=memory_type,
            llm_connection=llm_connection,
            is_background=is_background,
        )
        self.llm_connection = llm_connection

    async def _process_tools_for_server(
        self,
        server_name: str,
        tools: List[Any],
        store_tool: Callable,
        tool_exists: Callable,
    ) -> List[dict]:
        """
        Process tools for a single MCP server in batches of BATCH_SIZE.
        Runs each tool in a batch concurrently.
        """
        total_tools = len(tools)
        results: List[dict] = []

        logger.info(f"[{server_name}] Starting enrichment of {total_tools} tools")

        async def process_tool(tool):
            try:
                # Handle dict or object tool
                name = getattr(tool, "name", None) or tool.get("name")
                name = str(name)
                description = getattr(tool, "description", None) or tool.get(
                    "description"
                )
                input_schema = (
                    getattr(tool, "inputSchema", None) or tool.get("inputSchema") or {}
                )
                args = (
                    input_schema.get("properties", {})
                    if isinstance(input_schema, dict)
                    else {}
                )
                # check if tool exist we continue
                tool_exist = await tool_exists(
                    tool_name=str(name), mcp_server_name=server_name
                )

                if tool_exist:
                    # add the tool to mcp_tool_registry
                    MCP_TOOLS_REGISTRY[name] = tool_exist

                    logger.info(f"this tool already exist: {name}")
                    return

                # Build raw payload
                tool_payload = {
                    "name": str(name),
                    "description": str(description),
                    "parameters": args,
                }

                user_content = json.dumps(tool_payload, ensure_ascii=False)

                llm_messages = [
                    {"role": "system", "content": tool_semantic_enricher_system_prompt},
                    {"role": "user", "content": user_content},
                ]

                resp = await self.llm_connection.llm_call(llm_messages)

                enriched: Optional[str] = None
                if resp and getattr(resp, "choices", None):
                    try:
                        enriched = resp.choices[0].message.content
                    except Exception:
                        enriched = str(resp)

                result = {
                    "mcp_server_name": server_name,
                    "raw_tool": tool_payload,
                    "enriched_tool": normalize_enriched_tool(enriched=enriched),
                    "error": None,
                }

                # Insert this tool
                document = {
                    "mcp_server_name": result["mcp_server_name"],
                    "raw_tool": result["raw_tool"],
                    "enriched_tool": result["enriched_tool"],
                }
                # insert the tool to mcp tool registry
                MCP_TOOLS_REGISTRY[name] = document
                await self.insert_tool(mcp_server_name=server_name, document=document)
                # store the tool data to disk
                await store_tool(
                    tool_name=name,
                    mcp_server_name=server_name,
                    raw_tool=result["raw_tool"],
                    enriched_tool=result["enriched_tool"],
                )

                return result

            except Exception as exc:
                logger.error(
                    f"[{server_name}] Error processing tool {getattr(tool, 'name', None)}: {exc}"
                )
                return {
                    "mcp_server_name": server_name,
                    "raw_tool": {
                        "tool_name": getattr(tool, "name", None),
                        "description": getattr(tool, "description", None),
                        "parameters": {},
                    },
                    "enriched_tool": None,
                    "error": str(exc),
                }

        for i in range(0, total_tools, BATCH_SIZE):
            batch = tools[i : i + BATCH_SIZE]
            batch_num = (i // BATCH_SIZE) + 1
            total_batches = (total_tools + BATCH_SIZE - 1) // BATCH_SIZE

            logger.info(
                f"[{server_name}] Processing batch {batch_num}/{total_batches} "
                f"({len(batch)} tools in this batch, concurrently)"
            )

            batch_results = await asyncio.gather(*[process_tool(t) for t in batch])
            results.extend(batch_results)

            logger.info(
                f"[{server_name}] Finished batch {batch_num}/{total_batches} "
                f"({len(results)}/{total_tools} tools processed so far)"
            )

        logger.info(f"[{server_name}] Completed enrichment of {total_tools} tools")
        return results

    async def batch_process_all_mcp_servers(
        self,
        mcp_tools: Dict[str, List[Any]],
        store_tool: Callable,
        tool_exists: Callable,
    ) -> Dict[str, List[dict]]:
        """
        Process all MCP servers concurrently with one global LLM connection.
        Args:
            mcp_tools: mapping of server_name -> list of tool objects/dicts
        Returns:
            mapping server_name -> list of per-tool results
        """
        logger.info(f"Starting enrichment for {len(mcp_tools)} MCP servers")

        tasks = {
            server_name: asyncio.create_task(
                self._process_tools_for_server(
                    server_name=server_name,
                    tools=tools,
                    store_tool=store_tool,
                    tool_exists=tool_exists,
                )
            )
            for server_name, tools in mcp_tools.items()
        }

        gathered = await asyncio.gather(*tasks.values(), return_exceptions=True)

        output: Dict[str, List[dict]] = {}
        for server_name, res in zip(tasks.keys(), gathered):
            if isinstance(res, Exception):
                logger.error(f"[{server_name}] Failed: {res}")
                output[server_name] = []
            else:
                output[server_name] = res

        logger.info("Completed enrichment for all MCP servers")
        return output

    async def insert_tool(self, mcp_server_name: str, document: dict):
        doc_id = str(uuid.uuid4())
        latest_timestamp_datetime = datetime.now(timezone.utc)

        self.vector_db.add_to_collection(
            document=document,
            metadata={
                "mcp_server_name": mcp_server_name,
                "memory_type": self.memory_type,
                "timestamp": latest_timestamp_datetime.isoformat(),
            },
            doc_id=doc_id,
        )

        logger.debug(f"[{mcp_server_name}] Stored tool with ID: {doc_id}")

    async def tools_retrieval(
        self, query: str, mcp_tools: dict, top_k: int, similarity_threshold: float
    ):
        mcp_server_names = []
        for server_name, _ in mcp_tools.items():
            mcp_server_names.append(server_name)
        tools_retrieved = await self.query_tool(
            query=query,
            n_results=top_k,
            similarity_threshold=similarity_threshold,
            mcp_server_names=mcp_server_names,
        )
        # If semantic search failed, use BM25 fallback
        if not tools_retrieved:
            retriever = ToolFallbackRetriever()
            results = await retriever.fallback_tools(
                query=query,
                mcp_tools=mcp_tools,
                top_k=top_k,
                similarity_threshold=similarity_threshold,
            )
            return results[:10] if results else []

        # Otherwise return semantic results
        return tools_retrieved[:10]

    async def query_tool(
        self,
        query: str,
        n_results: int,
        similarity_threshold: float,
        session_id: str = None,
        mcp_server_names: list[str] = None,
    ):
        if not self.vector_db or not self.vector_db.enabled:
            return []

        try:
            results = self.vector_db.query_collection(
                query=query,
                session_id=session_id,
                mcp_server_names=mcp_server_names,
                n_results=n_results,
                similarity_threshold=similarity_threshold,
            )

            if isinstance(results, dict) and "documents" in results:
                documents = results["documents"]
                for doc in documents:
                    del doc["enriched_tool"]

                return documents
            elif isinstance(results, list):
                return results
            else:
                return []
        except Exception as e:
            logger.error(f"Error querying {self.memory_type} memory: {e}")
            return []
