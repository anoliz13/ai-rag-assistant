from typing import Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.config import settings


class ChunkResult:
    def __init__(self, content: str, chunk_index: int, page_number: Optional[int] = None):
        self.content = content
        self.chunk_index = chunk_index
        self.page_number = page_number


class ChunkerService:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""],
            length_function=len,
        )

    def chunk(self, text: str, page_numbers: Optional[list[int]] = None) -> list[ChunkResult]:
        chunks = self.splitter.split_text(text)
        results: list[ChunkResult] = []
        for i, content in enumerate(chunks):
            page = page_numbers[min(i, len(page_numbers) - 1)] if page_numbers else None
            results.append(ChunkResult(content=content, chunk_index=i, page_number=page))
        return results
