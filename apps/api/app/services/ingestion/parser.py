import io
import tempfile
from pathlib import Path
from pypdf import PdfReader
import docx2txt


class ParsedSection:
    def __init__(self, content: str, page_number: int | None = None, heading: str | None = None):
        self.content = content
        self.page_number = page_number
        self.heading = heading


class DocumentParser:
    """Extracts text and page structure from multiple document formats."""

    @staticmethod
    def parse_pdf(file_bytes: bytes) -> list[ParsedSection]:
        sections: list[ParsedSection] = []
        reader = PdfReader(io.BytesIO(file_bytes))
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            text = text.strip()
            if text:
                sections.append(ParsedSection(content=text, page_number=page_num))
        return sections

    @staticmethod
    def parse_docx(file_bytes: bytes) -> list[ParsedSection]:
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            text = docx2txt.process(tmp_path) or ""
            text = text.strip()
            return [ParsedSection(content=text, page_number=1)] if text else []
        finally:
            if Path(tmp_path).exists():
                Path(tmp_path).unlink()

    @staticmethod
    def parse_text(file_bytes: bytes) -> list[ParsedSection]:
        text = file_bytes.decode("utf-8", errors="replace").strip()
        return [ParsedSection(content=text, page_number=1)] if text else []

    @classmethod
    def parse(cls, file_bytes: bytes, file_type: str) -> list[ParsedSection]:
        ext = file_type.lower().replace(".", "")
        if ext == "pdf":
            return cls.parse_pdf(file_bytes)
        elif ext in ["docx", "doc"]:
            return cls.parse_docx(file_bytes)
        else:
            return cls.parse_text(file_bytes)
