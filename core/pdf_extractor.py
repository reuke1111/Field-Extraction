"""
PDF Extractor module.
Attempts digital text extraction page-by-page, detects pages with insufficient selectable text,
and routes scanned pages to the OCR engine. Handles mixed digital/scanned PDFs.
Provides PyMuPDF adapter with pypdf pure-Python fallback.
"""

import io
import logging
from pathlib import Path
from typing import Optional, Any
from PIL import Image
from config import OCR_MIN_TEXT_CHARS
from core.ocr_engine import OCREngine

logger = logging.getLogger(__name__)

# Check PyMuPDF availability
# Prevent pymupdf.layout and pymupdf4llm from loading onnxruntime, which causes a C++ access violation on Python 3.14 Windows
import sys
sys.modules.setdefault("pymupdf.layout", None)  # type: ignore
sys.modules.setdefault("pymupdf4llm", None)  # type: ignore
sys.modules.setdefault("onnxruntime", None)  # type: ignore

_FITZ_AVAILABLE = False
try:
    import fitz
    _FITZ_AVAILABLE = True
except Exception:
    _FITZ_AVAILABLE = False

# Check pypdf availability
_PYPDF_AVAILABLE = False
try:
    import pypdf
    _PYPDF_AVAILABLE = True
except Exception:
    _PYPDF_AVAILABLE = False


class PDFExtractor:
    def __init__(self, ocr_engine: Optional[OCREngine] = None):
        self.ocr_engine = ocr_engine or OCREngine()

    def extract_document(self, file_path: str) -> dict[str, Any]:
        """
        Extracts all pages from a PDF.
        Returns a dict:
        {
            "total_pages": int,
            "has_scanned_pages": bool,
            "ocr_method": Optional[str],
            "warnings": list[str],
            "pages": [
                {
                    "page_number": int (1-based),
                    "text": str,
                    "is_scanned": bool,
                    "ocr_applied": bool,
                    "char_count": int
                }
            ]
        }
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        # Choose backend: prefer PyMuPDF if working, else pypdf
        if _FITZ_AVAILABLE:
            try:
                return self._extract_with_fitz(path)
            except Exception as e:
                logger.warning(f"PyMuPDF extraction failed ({e}), falling back to pypdf.")

        if _PYPDF_AVAILABLE:
            return self._extract_with_pypdf(path)

        raise RuntimeError("No PDF library available. Install pymupdf or pypdf.")

    def _extract_with_fitz(self, path: Path) -> dict[str, Any]:
        doc = fitz.open(str(path))
        total_pages = len(doc)
        pages = []
        has_scanned = False
        overall_ocr_method = None
        warnings = []

        for page_idx in range(total_pages):
            page_num = page_idx + 1
            page = doc[page_idx]
            digital_text = page.get_text("text").strip()

            if len(digital_text) >= OCR_MIN_TEXT_CHARS:
                pages.append({
                    "page_number": page_num,
                    "text": digital_text,
                    "is_scanned": False,
                    "ocr_applied": False,
                    "char_count": len(digital_text)
                })
            else:
                # Page has insufficient selectable text -> run OCR
                has_scanned = True
                pix = page.get_pixmap(dpi=150)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                ocr_text, method, warning = self.ocr_engine.extract_text_from_image(img)
                overall_ocr_method = method
                if warning:
                    warnings.append(f"Page {page_num}: {warning}")

                pages.append({
                    "page_number": page_num,
                    "text": ocr_text,
                    "is_scanned": True,
                    "ocr_applied": True,
                    "char_count": len(ocr_text)
                })

        doc.close()
        return {
            "total_pages": total_pages,
            "has_scanned_pages": has_scanned,
            "ocr_method": overall_ocr_method or ("pymupdf_digital" if not has_scanned else None),
            "warnings": warnings,
            "pages": pages
        }

    def _extract_with_pypdf(self, path: Path) -> dict[str, Any]:
        reader = pypdf.PdfReader(str(path))
        total_pages = len(reader.pages)
        pages = []
        has_scanned = False
        overall_ocr_method = None
        warnings = []

        for page_idx in range(total_pages):
            page_num = page_idx + 1
            page = reader.pages[page_idx]
            digital_text = (page.extract_text() or "").strip()

            if len(digital_text) >= OCR_MIN_TEXT_CHARS:
                pages.append({
                    "page_number": page_num,
                    "text": digital_text,
                    "is_scanned": False,
                    "ocr_applied": False,
                    "char_count": len(digital_text)
                })
            else:
                # Scanned page
                has_scanned = True
                # Extract image from page if present
                img = None
                try:
                    for img_obj in page.images:
                        img = Image.open(io.BytesIO(img_obj.data))
                        break
                except Exception:
                    img = None

                if not img:
                    img = Image.new("RGB", (1000, 1400), color=(255, 255, 255))

                ocr_text, method, warning = self.ocr_engine.extract_text_from_image(img)
                overall_ocr_method = method
                if warning:
                    warnings.append(f"Page {page_num}: {warning}")

                pages.append({
                    "page_number": page_num,
                    "text": ocr_text,
                    "is_scanned": True,
                    "ocr_applied": True,
                    "char_count": len(ocr_text)
                })

        return {
            "total_pages": total_pages,
            "has_scanned_pages": has_scanned,
            "ocr_method": overall_ocr_method or ("pypdf_digital" if not has_scanned else None),
            "warnings": warnings,
            "pages": pages
        }
