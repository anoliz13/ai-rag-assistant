import pytest
from app.services.extractor import ExtractorService
from app.services.chunker import ChunkerService


class TestExtractor:
    def test_extract_txt(self):
        service = ExtractorService()
        result = service.extract(b"Hello World", "text/plain")
        assert result.text == "Hello World"
        assert result.pages == []

    def test_extract_csv(self):
        service = ExtractorService()
        result = service.extract(b"name,age\nAlice,30\nBob,25", "text/csv")
        assert "Alice" in result.text
        assert "30" in result.text

    def test_extract_docx_empty(self):
        service = ExtractorService()
        with pytest.raises(Exception):
            service.extract(b"invalid", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    def test_unsupported_type(self):
        service = ExtractorService()
        with pytest.raises(ValueError, match="Unsupported file type"):
            service.extract(b"test", "image/png")


class TestChunker:
    def setup_method(self):
        self.service = ChunkerService()

    def test_chunk_simple(self):
        text = "Hello World"
        chunks = self.service.chunk(text)
        assert len(chunks) == 1
        assert chunks[0].content == "Hello World"
        assert chunks[0].chunk_index == 0

    def test_chunk_long_text(self):
        text = "Word " * 500
        chunks = self.service.chunk(text)
        assert len(chunks) > 1

    def test_chunk_with_page_numbers(self):
        text = "Page1.\n\nPage2.\n\nPage3."
        chunks = self.service.chunk(text, [1, 2, 3])
        assert len(chunks) >= 1
        for chunk in chunks:
            assert chunk.page_number is not None

    def test_chunk_ordering(self):
        text = "First chunk. Second chunk. Third chunk." * 100
        chunks = self.service.chunk(text)
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i
