"""
Tests for OCR processing, language detection, and mixed page handling.
"""

from pathlib import Path
from core.ocr_engine import OCREngine
from core.pdf_extractor import PDFExtractor
from core.language_detector import detect_language

SAMPLE_DIR = Path("sample_documents")

def test_language_detection():
    english_text = "This scheme provides financial assistance of 50000 rupees to women entrepreneurs."
    hindi_text = "मुख्यमंत्री ग्रामीण हस्तशिल्प प्रोत्साहन योजना के तहत वित्तीय सहायता प्रदान की जाती है।"
    mixed_text = "योजना का नाम State Women Entrepreneurship Scheme है। आवेदन करें।"

    assert detect_language(english_text) == "en"
    assert detect_language(hindi_text) == "hi"
    assert detect_language(mixed_text) == "mixed"

def test_scanned_pdf_ocr_pipeline():
    extractor = PDFExtractor()
    doc_path = SAMPLE_DIR / "doc_c_scanned_scheme.pdf"
    assert doc_path.exists(), "Sample doc_c must exist"

    result = extractor.extract_document(str(doc_path))
    assert result["has_scanned_pages"] is True
    assert len(result["pages"]) >= 1

    page1 = result["pages"][0]
    assert page1["is_scanned"] is True
    assert page1["ocr_applied"] is True
    assert "KRISHI PROTSAHAN" in page1["text"].upper()
    assert "12,000" in page1["text"] or "12000" in page1["text"]

def test_ocr_engine_fallback_diagnostic():
    engine = OCREngine(tesseract_cmd="C:/invalid/path/tesseract.exe")
    assert not engine.tesseract_available
