"""
Source document model and metadata.
"""

from typing import Optional
from pydantic import BaseModel, Field

class SourceMetadata(BaseModel):
    source_id: str
    filename: str
    file_type: str = "pdf"
    file_size_bytes: int = 0
    sha256_hash: str
    source_type: str = "government_pdf"  # government_pdf, catalogue_listing, department_website
    source_url: Optional[str] = None
    captured_at: str  # YYYY-MM-DD
    detected_language: str = "en"  # en, hi, mixed
    total_pages: int = 1
    has_scanned_pages: bool = False
    ocr_method: Optional[str] = None  # pymupdf_digital, tesseract_ocr, synthetic_rendered_ocr
    warnings: list[str] = Field(default_factory=list)
