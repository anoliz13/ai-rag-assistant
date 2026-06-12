import json
import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas import ChatRequest
from app.services.retriever import RetrieverService
from app.services.llm import LLMService

router = APIRouter()
retriever = RetrieverService()
llm = LLMService()


@router.post("")
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    stmt = text("SELECT id FROM sessions WHERE id = :id")
    result = await db.execute(stmt, {"id": request.session_id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Session not found")

    contexts = await retriever.retrieve(request.message, request.document_ids)
    source_data = [
        {
            "chunk_id": c.chunk_id,
            "document_id": c.document_id,
            "content": c.content,
            "score": c.score,
            "page_number": c.page_number,
        }
        for c in contexts
    ]

    history_stmt = text("SELECT role, content FROM messages WHERE session_id = :sid ORDER BY created_at ASC")
    history_result = await db.execute(history_stmt, {"sid": request.session_id})
    history = [{"role": r[0], "content": r[1]} for r in history_result.fetchall()]

    async def generate():
        full_answer = ""
        async for chunk in llm.stream_chat(request.message, source_data, history):
            full_answer += chunk
            yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"

        msg_id = str(uuid.uuid4())
        await db.execute(text("""
            INSERT INTO messages (id, session_id, role, content, sources)
            VALUES (:id, :sid, :role, :content, :sources)
        """), {
            "id": msg_id,
            "sid": request.session_id,
            "role": "assistant",
            "content": full_answer,
            "sources": json.dumps(source_data) if source_data else None,
        })

        await db.execute(text("""
            INSERT INTO messages (id, session_id, role, content)
            VALUES (:id, :sid, :role, :content)
        """), {
            "id": str(uuid.uuid4()),
            "sid": request.session_id,
            "role": "user",
            "content": request.message,
        })

        await db.commit()
        yield f"data: {json.dumps({'type': 'done', 'sources': source_data})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
