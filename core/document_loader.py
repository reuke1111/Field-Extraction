"""
Document Loader module.
Handles validation, hashing, ingestion, page extraction, OCR routing, and repository persistence.
"""

import hashlib
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from models.source import SourceMetadata
from core.pdf_extractor import PDFExtractor
from core.language_detector import detect_language
from database.repository import Repository

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB

class DocumentLoader:
    def __init__(self, repository: Optional[Repository] = None, pdf_extractor: Optional[PDFExtractor] = None):
        self.repository = repository or Repository()
        self.pdf_extractor = pdf_extractor or PDFExtractor()

    def calculate_sha256(self, file_path: str) -> str:
        """
        Calculates SHA-256 hash of a file.
        """
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def load_pdf(
        self,
        file_path: str,
        source_id: Optional[str] = None,
        source_type: str = "government_pdf",
        source_url: Optional[str] = None,
        captured_at: Optional[str] = None
    ) -> SourceMetadata:
        """
        Ingests a PDF document through the full extraction pipeline.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_size = path.stat().st_size
        if file_size > MAX_FILE_SIZE_BYTES:
            raise ValueError(f"File size exceeds maximum allowed ({MAX_FILE_SIZE_BYTES} bytes): {file_size}")

        if path.suffix.lower() != ".pdf":
            raise ValueError(f"Unsupported file type '{path.suffix}'. Only .pdf is allowed.")

        # Hash calculation
        sha256_hash = self.calculate_sha256(str(path))

        # Check if already ingested
        existing = self.repository.get_document_by_hash(sha256_hash)
        if existing and not source_id:
            return existing

        # Assign unique document ID if not provided
        if not source_id:
            doc_count = len(self.repository.list_documents())
            source_id = f"DOC-{doc_count + 1:03d}"

        # Extract pages and run OCR if necessary
        extraction_result = self.pdf_extractor.extract_document(str(path))
        pages = extraction_result["pages"]
        total_pages = extraction_result["total_pages"]
        has_scanned = extraction_result["has_scanned_pages"]
        ocr_method = extraction_result["ocr_method"]
        warnings = list(extraction_result["warnings"])

        # Detect overall document language from combined text
        combined_text = "\n".join([p["text"] for p in pages])
        detected_lang = detect_language(combined_text)

        captured_date = captured_at or datetime.now(timezone.utc).strftime("%Y-%m-%d")

        metadata = SourceMetadata(
            source_id=source_id,
            filename=path.name,
            file_type="pdf",
            file_size_bytes=file_size,
            sha256_hash=sha256_hash,
            source_type=source_type,
            source_url=source_url,
            captured_at=captured_date,
            detected_language=detected_lang,
            total_pages=total_pages,
            has_scanned_pages=has_scanned,
            ocr_method=ocr_method,
            warnings=warnings
        )

        # Persist to database
        self.repository.save_document(metadata, pages)
        return metadata
