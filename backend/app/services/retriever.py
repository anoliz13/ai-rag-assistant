import json
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.embedder import EmbedderService
from app.core.database import async_session
from typing import Optional


class RetrievalResult:
    def __init__(self, chunk_id: str, document_id: str, content: str, score: float, page_number: Optional[int] = None):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.content = content
        self.score = score
        self.page_number = page_number


class RetrieverService:
    def __init__(self):
        self.embedder = EmbedderService()

    async def retrieve(
        self, query: str, document_ids: Optional[list[str]] = None, top_k: int = 5, min_score: float = 0.5
    ) -> list[RetrievalResult]:
        query_embedding = await self.embedder.embed(query)
        embedding_json = json.dumps(query_embedding)

        async with async_session() as db:
            if document_ids:
                placeholders = ",".join(f"'{d}'" for d in document_ids)
                sql = text(f"""
                    SELECT c.id, c.document_id, c.content, c.page_number,
                           1 - (c.embedding <=> '{embedding_json}'::vector) AS score
                    FROM chunks c
                    WHERE c.document_id IN ({placeholders})
                      AND c.embedding IS NOT NULL
                    ORDER BY c.embedding <=> '{embedding_json}'::vector
                    LIMIT :top_k
                """)
            else:
                sql = text(f"""
                    SELECT c.id, c.document_id, c.content, c.page_number,
                           1 - (c.embedding <=> '{embedding_json}'::vector) AS score
                    FROM chunks c
                    WHERE c.embedding IS NOT NULL
                    ORDER BY c.embedding <=> '{embedding_json}'::vector
                    LIMIT :top_k
                """)

            result = await db.execute(sql, {"top_k": top_k})
            rows = result.fetchall()

            return [
                RetrievalResult(
                    chunk_id=row[0],
                    document_id=row[1],
                    content=row[2],
                    page_number=row[3],
                    score=float(row[4]),
                )
                for row in rows
                if float(row[4]) >= min_score
            ]
