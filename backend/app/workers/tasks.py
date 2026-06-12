import uuid
import json
import asyncio
from celery import Task
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.workers.celery_app import celery_app
from app.core.config import settings
from app.models.document import DocumentStatus


engine = create_async_engine(settings.database_url, echo=False, pool_size=5)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class AsyncTask(Task):
    abstract = True

    def run(self, *args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._run(*args, **kwargs))
        finally:
            loop.close()

    async def _run(self, *args, **kwargs):
        raise NotImplementedError


def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, base=AsyncTask, max_retries=3, default_retry_delay=10)
async def process_document(self, document_id: str, file_bytes: bytes, file_type: str, file_path: str):
    from app.services.extractor import ExtractorService
    from app.services.chunker import ChunkerService
    from app.services.embedder import EmbedderService

    extractor = ExtractorService()
    chunker = ChunkerService()
    embedder = EmbedderService()

    async with async_session() as db:
        try:
            await _update_status(db, document_id, DocumentStatus.extracting)
            result = extractor.extract(file_bytes, file_type)
            text = result.text
            page_numbers = result.pages

            if not text.strip():
                raise ValueError("No text could be extracted from the document")

            await _update_status(db, document_id, DocumentStatus.chunking)
            chunks = chunker.chunk(text, page_numbers)

            await _update_status(db, document_id, DocumentStatus.embedding)
            chunk_texts = [c.content for c in chunks]
            embeddings = await embedder.embed_batch(chunk_texts)

            await _store_chunks(db, document_id, chunks, embeddings)
            await _update_status(db, document_id, DocumentStatus.ready, chunk_count=len(chunks))

        except Exception as e:
            await _update_status(db, document_id, DocumentStatus.failed, error=str(e))
            raise


async def _update_status(db: AsyncSession, doc_id: str, status: DocumentStatus, chunk_count: int = None, error: str = None):
    stmt = text("""
        UPDATE documents
        SET status = :status,
            chunk_count = :chunk_count,
            error_message = :error,
            updated_at = NOW()
        WHERE id = :id
    """)
    await db.execute(stmt, {
        "id": doc_id,
        "status": status.value,
        "chunk_count": chunk_count,
        "error": error,
    })
    await db.commit()


async def _store_chunks(db: AsyncSession, doc_id: str, chunks, embeddings: list[list[float]]):
    for chunk, embedding in zip(chunks, embeddings):
        stmt = text("""
            INSERT INTO chunks (id, document_id, content, chunk_index, page_number, token_count, embedding)
            VALUES (:id, :document_id, :content, :chunk_index, :page_number, :token_count, :embedding::vector)
        """)
        await db.execute(stmt, {
            "id": str(uuid.uuid4()),
            "document_id": doc_id,
            "content": chunk.content,
            "chunk_index": chunk.chunk_index,
            "page_number": chunk.page_number,
            "token_count": len(chunk.content.split()),
            "embedding": json.dumps(embedding),
        })
    await db.commit()
