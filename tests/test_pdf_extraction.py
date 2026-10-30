"""
Tests for PDF extraction, page preservation, and digital text extraction.
"""

import pytest
from pathlib import Path
from core.pdf_extractor import PDFExtractor


SAMPLE_DIR = Path("sample_documents")

def test_extract_english_digital_pdf():
    extractor = PDFExtractor()
    doc_path = SAMPLE_DIR / "doc_a_english_scheme.pdf"
    assert doc_path.exists(), "Sample doc_a must exist"

    result = extractor.extract_document(str(doc_path))
    assert result["total_pages"] == 2, "Document A should have 2 pages"
    assert not result["has_scanned_pages"], "Document A is digital"
    assert len(result["pages"]) == 2

    page1_text = result["pages"][0]["text"]
    assert "STATE WOMEN ENTREPRENEURSHIP" in page1_text
    assert "50,000" in page1_text or "50000" in page1_text

    page2_text = result["pages"][1]["text"]
    assert "2026-12-31" in page2_text

def test_extract_hindi_digital_pdf():
    extractor = PDFExtractor()
    doc_path = SAMPLE_DIR / "doc_b_hindi_scheme.pdf"
    assert doc_path.exists(), "Sample doc_b must exist"

    result = extractor.extract_document(str(doc_path))
    assert result["total_pages"] == 2
    page1_text = result["pages"][0]["text"]
    # Verify Devanagari text is extracted
    assert "हस्तशिल्प" in page1_text or "योजना" in page1_text

def test_missing_file_raises_error():
    extractor = PDFExtractor()
    with pytest.raises(FileNotFoundError):
        extractor.extract_document("sample_documents/non_existent.pdf")
