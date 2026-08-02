from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Dict, Any

class SupabaseVectorService:
    """
    Handles pgvector Cosine similarity search directly in Supabase Postgres
    """
    async def search_similar_products(self, session: AsyncSession, vector: List[float], limit: int = 10, threshold: float = 0.70) -> List[Dict[str, Any]]:
        vector_str = f"[{','.join(map(str, vector))}]"
        
        query = text("""
            SELECT id, title, brand, main_image_url, 
                   1 - (embedding <=> :vector::vector) AS similarity_score
            FROM master_products
            WHERE embedding IS NOT NULL AND (1 - (embedding <=> :vector::vector)) >= :threshold
            ORDER BY embedding <=> :vector::vector ASC
            LIMIT :limit;
        """)
        
        res = await session.execute(query, {
            "vector": vector_str,
            "threshold": threshold,
            "limit": limit
        })
        
        rows = res.fetchall()
        return [
            {
                "master_id": str(row.id),
                "title": row.title,
                "brand": row.brand,
                "main_image_url": row.main_image_url,
                "similarity_score": float(row.similarity_score)
            }
            for row in rows
        ]

supabase_vector_service = SupabaseVectorService()
