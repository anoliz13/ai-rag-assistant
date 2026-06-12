import uuid
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas import (
    SessionCreate, SessionUpdate, SessionResponse, SessionListResponse,
    MessageResponse, MessageListResponse,
)

router = APIRouter()


@router.get("", response_model=SessionListResponse)
async def list_sessions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT id, title, document_ids, is_active, created_at, updated_at
        FROM sessions ORDER BY updated_at DESC
    """))
    rows = result.fetchall()
    sessions = [
        SessionResponse(id=r[0], title=r[1], document_ids=r[2], is_active=r[3], created_at=r[4], updated_at=r[5])
        for r in rows
    ]
    return SessionListResponse(sessions=sessions, total=len(sessions))


@router.post("", response_model=SessionResponse, status_code=201)
async def create_session(body: SessionCreate, db: AsyncSession = Depends(get_db)):
    session_id = str(uuid.uuid4())
    doc_ids = json.dumps(body.document_ids) if body.document_ids else None
    result = await db.execute(text("""
        INSERT INTO sessions (id, title, document_ids)
        VALUES (:id, :title, :doc_ids)
        RETURNING id, title, document_ids, is_active, created_at, updated_at
    """), {"id": session_id, "title": body.title, "doc_ids": doc_ids})
    row = result.fetchone()
    await db.commit()
    return SessionResponse(id=row[0], title=row[1], document_ids=row[2], is_active=row[3], created_at=row[4], updated_at=row[5])


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT id, title, document_ids, is_active, created_at, updated_at FROM sessions WHERE id = :id"), {"id": session_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse(id=row[0], title=row[1], document_ids=row[2], is_active=row[3], created_at=row[4], updated_at=row[5])


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(session_id: str, body: SessionUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        UPDATE sessions SET title = :title, updated_at = NOW()
        WHERE id = :id
        RETURNING id, title, document_ids, is_active, created_at, updated_at
    """), {"id": session_id, "title": body.title})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Session not found")
    await db.commit()
    return SessionResponse(id=row[0], title=row[1], document_ids=row[2], is_active=row[3], created_at=row[4], updated_at=row[5])


@router.delete("/{session_id}")
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    await db.execute(text("DELETE FROM sessions WHERE id = :id"), {"id": session_id})
    await db.commit()
    return {"message": "Session deleted"}


@router.get("/{session_id}/messages", response_model=MessageListResponse)
async def get_messages(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT id, session_id, role, content, sources, created_at
        FROM messages WHERE session_id = :sid ORDER BY created_at ASC
    """), {"sid": session_id})
    rows = result.fetchall()
    messages = [
        MessageResponse(id=r[0], session_id=r[1], role=r[2], content=r[3], sources=r[4], created_at=r[5])
        for r in rows
    ]
    return MessageListResponse(messages=messages, total=len(messages))


@router.get("/{session_id}/export")
async def export_session(session_id: str, format: str = "markdown", db: AsyncSession = Depends(get_db)):
    session_result = await db.execute(text("SELECT title FROM sessions WHERE id = :id"), {"id": session_id})
    session_row = session_result.fetchone()
    if not session_row:
        raise HTTPException(status_code=404, detail="Session not found")

    result = await db.execute(text("""
        SELECT role, content, created_at FROM messages
        WHERE session_id = :sid ORDER BY created_at ASC
    """), {"sid": session_id})
    messages = result.fetchall()

    md_lines = [f"# {session_row[0]}\n", f"*Exported: {__import__('datetime').datetime.utcnow().isoformat()}*\n"]
    for m in messages:
        role = "**You**" if m[0] == "user" else "**AI**"
        md_lines.append(f"\n### {role}\n{m[1]}\n")

    content = "\n".join(md_lines)

    if format == "pdf":
        headers = {"Content-Type": "application/pdf"}
    else:
        headers = {"Content-Type": "text/markdown", "Content-Disposition": f"attachment; filename=chat-{session_id[:8]}.md"}

    from fastapi.responses import Response
    return Response(content=content, headers=headers)
