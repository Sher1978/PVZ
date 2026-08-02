import meilisearch
from app.config import settings
from typing import List, Dict, Any, Optional

class MeiliService:
    INDEX_NAME = "products_index"

    def __init__(self):
        try:
            self.client = meilisearch.Client(settings.MEILISEARCH_HOST, settings.MEILI_MASTER_KEY)
            self.index = self.client.index(self.INDEX_NAME)
            self._ensure_index_settings()
        except Exception as e:
            print(f"Warning: Meilisearch init deferred: {e}")
            self.client = None
            self.index = None

    def _ensure_index_settings(self):
        if not self.index:
            return
        try:
            self.index.update_searchable_attributes(["title", "brand", "category_name", "description"])
            self.index.update_filterable_attributes(["brand", "category_id", "min_price", "platforms"])
            self.index.update_sortable_attributes(["min_price", "rating", "created_at"])
        except Exception as e:
            print(f"Warning updating Meilisearch settings: {e}")

    async def add_or_update_documents(self, documents: List[Dict[str, Any]]):
        if not self.index:
            return
        self.index.add_documents(documents)

    async def search(self, query: str, filter_query: Optional[str] = None, sort: Optional[List[str]] = None, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        if not self.index:
            return {"hits": [], "totalHits": 0}
        
        search_params = {
            "offset": (page - 1) * limit,
            "limit": limit
        }
        if filter_query:
            search_params["filter"] = filter_query
        if sort:
            search_params["sort"] = sort
            
        return self.index.search(query, search_params)

meili_service = MeiliService()
