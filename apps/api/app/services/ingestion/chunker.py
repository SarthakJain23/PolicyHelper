import re
from typing import TypedDict
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import settings
from app.services.ingestion.parser import ParsedSection


class ChunkResult(TypedDict):
    chunk_index: int
    content: str
    metadata: dict


class PolicyChunker:
    """
    Hybrid Header-Aware and Recursive Character Chunker.
    Injects document context breadcrumbs into chunks to maintain policy context.
    """

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", "; ", ", ", " "],
        )

    def chunk_document(
        self,
        document_title: str,
        category: str,
        sections: list[ParsedSection],
    ) -> list[ChunkResult]:
        chunks: list[ChunkResult] = []
        chunk_idx = 0

        # Regex to detect policy section headers (e.g. "1.2 Paid Time Off", "Section 3: Eligibility", "## Parental Leave")
        header_pattern = re.compile(
            r"^(?:#{1,4}\s+|(?:\d+\.)+\d*\s+|section\s+\d+[:\.]?\s*)(.+)$",
            re.IGNORECASE | re.MULTILINE,
        )

        current_heading = "General Overview"

        for section in sections:
            # Check for header in text
            lines = section.content.splitlines()
            for line in lines:
                match = header_pattern.match(line.strip())
                if match:
                    current_heading = match.group(0).strip()
                    break

            # Create breadcrumb prefix
            breadcrumb = f"Document: {document_title} > Category: {category} > Section: {current_heading}"
            
            # Split section text
            raw_chunks = self.splitter.split_text(section.content)

            for raw_chunk in raw_chunks:
                clean_text = raw_chunk.strip()
                if not clean_text:
                    continue

                # Prepend breadcrumb to chunk text for vector embedding and retrieval context
                contextualized_text = f"[{breadcrumb}]\n{clean_text}"

                chunks.append(
                    ChunkResult(
                        chunk_index=chunk_idx,
                        content=contextualized_text,
                        metadata={
                            "document_title": document_title,
                            "category": category,
                            "section_header": current_heading,
                            "page_number": section.page_number,
                            "breadcrumb": breadcrumb,
                            "raw_snippet": clean_text[:300],
                        },
                    )
                )
                chunk_idx += 1

        return chunks
