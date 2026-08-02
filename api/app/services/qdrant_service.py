from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.config import settings
from typing import List, Dict, Any, Optional

class QdrantService:
    COLLECTION_NAME = "master_product_vectors"
    VECTOR_DIM = 512

    def __init__(self):
        try:
            self.client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT, timeout=5)
            self._ensure_collection()
        except Exception as e:
            print(f"Warning: Qdrant init deferred: {e}")
            self.client = None

    def _ensure_collection(self):
        if not self.client:
            return
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        if self.COLLECTION_NAME not in collection_names:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(size=self.VECTOR_DIM, distance=Distance.COSINE)
            )

    async def upsert_vector(self, master_id: str, vector: List[float], payload: Dict[str, Any]):
        if not self.client:
            return
        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=[
                PointStruct(
                    id=master_id,
                    vector=vector,
                    payload=payload
                )
            ]
        )

    async def search_similar(self, vector: List[float], limit: int = 10, score_threshold: float = 0.70) -> List[Dict[str, Any]]:
        if not self.client:
            return []
        search_result = self.client.search(
            collection_name=self.COLLECTION_NAME,
            query_vector=vector,
            limit=limit,
            score_threshold=score_threshold
        )
        return [
            {
                "master_id": point.id,
                "score": point.score,
                "payload": point.payload
            }
            for point in search_result
        ]

qdrant_service = QdrantService()
