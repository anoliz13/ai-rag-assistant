from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    status: str
    chunk_count: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int


class ChunkResponse(BaseModel):
    id: str
    document_id: str
    content: str
    chunk_index: int
    page_number: Optional[int] = None
    token_count: int


class ChatRequest(BaseModel):
    session_id: str
    message: str
    document_ids: Optional[list[str]] = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict[str, Any]]


class SessionCreate(BaseModel):
    title: str = "New Chat"
    document_ids: Optional[list[str]] = None


class SessionUpdate(BaseModel):
    title: str


class SessionResponse(BaseModel):
    id: str
    title: str
    document_ids: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SessionListResponse(BaseModel):
    sessions: list[SessionResponse]
    total: int


class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    sources: Optional[str] = None
    created_at: datetime


class MessageListResponse(BaseModel):
    messages: list[MessageResponse]
    total: int


class StatusResponse(BaseModel):
    status: str
    progress: float = 0.0
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    detail: str
