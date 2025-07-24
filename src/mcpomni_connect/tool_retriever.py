from qdrant_client import QdrantClient, models
from typing import List, Dict, Any


class ToolRetriever:
    def __init__(self):
        self.client = QdrantClient(":memory:")
        self.collection_name = "tools_collection"
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        # Ensure collection exists
        vector_size = self.client.get_embedding_size(self.model_name)
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=vector_size, distance=models.Distance.COSINE
            ),
            optimizers_config=models.OptimizersConfigDiff(memmap_threshold=20000),
            on_disk=True,
        )

    def upsert_tools(self, tools: List[Dict[str, Any]]):
        """
        Upsert tool embeddings into Qdrant using built-in model support.
        """
        docs = [
            models.Document(
                text=f"{tool['name']} {tool.get('description', '')} {tool.get('input_schema', '')} ",
                model=self.model_name,
            )
            for tool in tools
        ]
        payload = tools
        ids = [i for i, _ in enumerate(tools)]
        self.client.upload_collection(
            collection_name=self.collection_name,
            vectors=docs,
            ids=ids,
            payload=payload,
        )

    def query_tools(
        self, query: str, top_k: int = 20, all_tools: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query Qdrant for the top_k most relevant tools for the given query using built-in model support.
        Fallback to all_tools if no results are found.
        """
        query_doc = models.Document(text=query, model=self.model_name)
        search_result = self.client.query_points(
            collection_name=self.collection_name, query=query_doc, limit=top_k
        ).points
        if not search_result and all_tools is not None:
            return all_tools
        return [point.payload for point in search_result]
