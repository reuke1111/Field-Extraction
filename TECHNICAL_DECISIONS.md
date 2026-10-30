# Technical Decisions Document: Haqdarshak AI Scheme Extraction System

**Author:** Senior AI/ML Engineer  
**Role Context:** Haqdarshak AI/ML Hiring Assignment (Option A1: Field Extraction with Evidence)  
**Date:** 2026-10-30  

---

## 1. Executive Summary

Haqdarshak manages a repository of ~5,000 central and state government welfare schemes. Researchers currently spend extensive manual hours extracting core scheme attributes (Scheme name, Department, Benefits, Eligibility, Required documents, Application procedure, Deadline, Official link).

This prototype automates the first extraction pass while ensuring:
1. **Traceable Source Evidence:** Every extracted fact references exact verbatim quotation, page number, and source document metadata.
2. **Zero Hallucination Policy:** Missing information is recorded as `status="not_found"` with explicit explanations; never guessed or defaulted.
3. **Explicit Conflict Preservation:** Conflicting cross-source information (e.g., Department PDF ₹50,000 vs. Catalogue ₹40,000) is flagged and retained side-by-side rather than silently overwritten.
4. **Human-in-the-Loop Governance:** Approval requires verification of populated fields and resolution of conflicts.
5. **Measurable Field-Level Quality:** Automated evaluation against ground truth across English, Hindi, and Scanned formats.

---

## 2. Technology Stack Selection & Rationale

| Layer | Selected Technology | Alternatives Evaluated | Rationale for Selection |
|---|---|---|---|
| **Data Models & Schema** | **Pydantic v2** | `marshmallow`, `dataclasses`, `jsonschema` | Type safety, field-level validators, strict regex/number validation, JSON schema generation for LLM structured outputs. |
| **PDF Extraction** | **PyMuPDF (`fitz`) + `pypdf` adapter** | `pdfminer.six`, `pypdf2`, `pdfplumber` | PyMuPDF provides high-speed C-level text layout extraction and page rendering. A pure-Python `pypdf` fallback ensures zero-dependency operation across constrained enterprise Windows environments. |
| **OCR & Image Processing** | **Tesseract OCR (English + Hindi) with RapidOCR / Vision Adapter** | `easyocr`, `paddleocr` | PyTesseract is the industry standard for Devanagari (`hin`) and English (`eng`). Adapter pattern allows graceful diagnostics when Tesseract binary is absent on host. |
| **Language Detection** | **Unicode Script Analyzer (Devanagari vs Latin)** | `langdetect`, `fasttext` | Zero external neural weights; 100% deterministic classification for Hindi (`\u0900-\u097F`) vs English without runtime latency or false positives on mixed headers. |
| **Persistence** | **SQLite 3 (`sqlite3`)** | `PostgreSQL`, `MongoDB`, `DuckDB` | Embedded zero-configuration ACID storage, foreign key enforcement, restart persistence, zero network dependencies. |
| **User Interface** | **Streamlit** | `Gradio`, `Dash`, `FastAPI + React` | Rich multi-page layout, native dataframe widgets, file uploaders, and side-by-side diff viewers built rapidly with clean Python code. |
| **LLM Provider Abstraction** | **Unified `BaseLLMProvider` (Google Gemini + Mock Provider)** | `LangChain`, `LlamaIndex` | Clean, decoupled provider interface. Gemini 2.5 Flash / 1.5 Flash provides low cost and structured JSON schema enforcement. Built-in `MockProvider` enables 100% offline testing with deterministic responses. |
| **Evaluation Framework** | **Custom Field-Level Precision/Recall/F1 + Evidence Verifier** | Generic RAG Triad / BLEU / ROUGE | BLEU/ROUGE are inappropriate for exact entity extraction. Custom metrics measure exact match, normalized semantic match, evidence presence, and conflict detection recall. |

---

## 3. Rejected Alternatives & Technical Trade-Offs

### 3.1 Vector Databases & RAG Pipelines (Rejected)
* **Why evaluated:** RAG is commonly used for document question-answering.
* **Why rejected:** Scheme extraction is an exhaustive first-pass structured extraction over a discrete document (typically 2–10 pages), not a broad semantic search over 100,000 documents. Vector embeddings lose exact page offsets and introduce fuzzy boundary splitting. A page-aware sliding-window chunker with exact document citations is superior and avoids embedding model costs.

### 3.2 Heavy Frameworks (LangChain / LlamaIndex) (Rejected)
* **Why evaluated:** Provides pre-built chains and extractors.
* **Why rejected:** Heavy dependency chains introduce breaking API shifts, complex debugging trees, and high installation overhead. A lightweight, 50-line provider abstraction is transparent, maintainable, and directly inspectable.

### 3.3 Silent Conflict Resolution (Rejected)
* **Why evaluated:** Some systems pick the newest document or government source automatically.
* **Why rejected:** In welfare schemes, government circulars may specify base guidelines while state implementation orders or updated catalogues modify amounts. Overwriting either record causes researchers to lose critical historical context. Preserving conflict records with explicit source timestamps enables human experts to make informed decisions.

---

## 4. Key Architectural Safeguards

1. **Two-Stage Validation:**
   - Stage 1: LLM generates structured JSON adhering to the Pydantic schema.
   - Stage 2: Independent deterministic `EvidenceValidator` searches the original source page text to confirm the quotation is authentic. If not found, `evidence_valid` is set to `False` and approval is blocked.
2. **Deterministic Token & Cost Accounting:**
   - Model name and version are stored with each run.
   - Input/output tokens are tracked with real rates (Gemini Flash: \$0.075/1M input, \$0.30/1M output).
   - Mock runs are explicitly labelled `MOCK` with cost marked unavailable to prevent deceptive metrics.
