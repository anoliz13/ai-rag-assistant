import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas import DocumentResponse, DocumentListResponse
from app.services.minio import MinioService
from app.workers.tasks import process_document
from app.models.document import DocumentStatus

router = APIRouter()
minio_service = MinioService()

ALLOWED_TYPES = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "text/plain": ".txt",
    "text/csv": ".csv",
    "text/markdown": ".md",
    "text/x-markdown": ".md",
}


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    file_bytes = await file.read()
    doc_id = str(uuid.uuid4())
    ext = ALLOWED_TYPES[file.content_type]
    object_name = f"{doc_id}{ext}"

    file_path = minio_service.upload_file(object_name, file_bytes, file.content_type)

    stmt = text("""
        INSERT INTO documents (id, filename, file_type, file_size, file_path, status)
        VALUES (:id, :filename, :file_type, :file_size, :file_path, :status)
        RETURNING id, filename, file_type, file_size, file_path, status, chunk_count, error_message, created_at, updated_at
    """)
    result = await db.execute(stmt, {
        "id": doc_id,
        "filename": file.filename,
        "file_type": file.content_type,
        "file_size": len(file_bytes),
        "file_path": object_name,
        "status": DocumentStatus.uploading.value,
    })
    row = result.fetchone()
    await db.commit()

    process_document.delay(doc_id, file_bytes, file.content_type, object_name)

    return DocumentResponse(
        id=row[0], filename=row[1], file_type=row[2], file_size=row[3],
        file_path=row[4], status=row[5], chunk_count=row[6],
        error_message=row[7], created_at=row[8], updated_at=row[9],
    )


@router.get("", response_model=DocumentListResponse)
async def list_documents(db: AsyncSession = Depends(get_db)):
    stmt = text("""
        SELECT id, filename, file_type, file_size, file_path, status, chunk_count, error_message, created_at, updated_at
        FROM documents ORDER BY created_at DESC
    """)
    result = await db.execute(stmt)
    rows = result.fetchall()
    documents = [
        DocumentResponse(
            id=r[0], filename=r[1], file_type=r[2], file_size=r[3],
            file_path=r[4], status=r[5], chunk_count=r[6],
            error_message=r[7], created_at=r[8], updated_at=r[9],
        ) for r in rows
    ]
    return DocumentListResponse(documents=documents, total=len(documents))


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, db: AsyncSession = Depends(get_db)):
    stmt = text("SELECT id, filename, file_type, file_size, file_path, status, chunk_count, error_message, created_at, updated_at FROM documents WHERE id = :id")
    result = await db.execute(stmt, {"id": document_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse(
        id=row[0], filename=row[1], file_type=row[2], file_size=row[3],
        file_path=row[4], status=row[5], chunk_count=row[6],
        error_message=row[7], created_at=row[8], updated_at=row[9],
    )


@router.delete("/{document_id}")
async def delete_document(document_id: str, db: AsyncSession = Depends(get_db)):
    stmt = text("SELECT file_path FROM documents WHERE id = :id")
    result = await db.execute(stmt, {"id": document_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")

    minio_service.delete_file(row[0])

    await db.execute(text("DELETE FROM documents WHERE id = :id"), {"id": document_id})
    await db.commit()
    return {"message": "Document deleted"}


@router.get("/{document_id}/preview")
async def preview_document(document_id: str, db: AsyncSession = Depends(get_db)):
    stmt = text("SELECT file_path, file_type FROM documents WHERE id = :id")
    result = await db.execute(stmt, {"id": document_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")

    file_bytes = minio_service.get_file(row[0])
    if not file_bytes:
        raise HTTPException(status_code=404, detail="File not found in storage")

    from fastapi.responses import Response
    return Response(content=file_bytes, media_type=row[1])
