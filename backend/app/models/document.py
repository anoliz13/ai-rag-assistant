from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
import enum
from typing import Optional


class DocumentStatus(str, enum.Enum):
    uploading = "uploading"
    extracting = "extracting"
    chunking = "chunking"
    embedding = "embedding"
    ready = "ready"
    failed = "failed"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(50))
    file_size: Mapped[int] = mapped_column(Integer)
    file_path: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(SAEnum(DocumentStatus), default=DocumentStatus.uploading)
    chunk_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=None)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
