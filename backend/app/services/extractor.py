import io
from typing import Optional
import fitz
from docx import Document as DocxDocument
import csv
import chardet


class ExtractionResult:
    def __init__(self, text: str, pages: Optional[list[int]] = None):
        self.text = text
        self.pages = pages or []


class ExtractorService:
    @staticmethod
    def extract(file_bytes: bytes, file_type: str) -> ExtractionResult:
        extractors = {
            "application/pdf": ExtractorService._extract_pdf,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ExtractorService._extract_docx,
            "text/plain": ExtractorService._extract_txt,
            "text/csv": ExtractorService._extract_csv,
            "text/markdown": ExtractorService._extract_txt,
            "text/x-markdown": ExtractorService._extract_txt,
        }
        extractor = extractors.get(file_type)
        if not extractor:
            raise ValueError(f"Unsupported file type: {file_type}")
        return extractor(file_bytes)

    @staticmethod
    def _extract_pdf(file_bytes: bytes) -> ExtractionResult:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        texts: list[str] = []
        pages: list[int] = []
        for page_num, page in enumerate(doc, 1):
            text = page.get_text().strip()
            if text:
                texts.append(text)
                pages.append(page_num)
        doc.close()
        return ExtractionResult("\n\n".join(texts), pages)

    @staticmethod
    def _extract_docx(file_bytes: bytes) -> ExtractionResult:
        doc = DocxDocument(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return ExtractionResult("\n\n".join(paragraphs))

    @staticmethod
    def _extract_txt(file_bytes: bytes) -> ExtractionResult:
        encoding = chardet.detect(file_bytes)["encoding"] or "utf-8"
        text = file_bytes.decode(encoding, errors="replace")
        return ExtractionResult(text)

    @staticmethod
    def _extract_csv(file_bytes: bytes) -> ExtractionResult:
        encoding = chardet.detect(file_bytes)["encoding"] or "utf-8"
        content = file_bytes.decode(encoding, errors="replace")
        reader = csv.reader(io.StringIO(content))
        rows = []
        for row in reader:
            rows.append(", ".join(row))
        return ExtractionResult("\n".join(rows))
