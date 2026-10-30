"""
Page 2: Document Upload & Ingestion Pipeline
"""

import os
import shutil
import tempfile
import streamlit as st
from datetime import datetime
from config import SAMPLE_DOCS_DIR
from core.document_loader import DocumentLoader
from core.extraction_engine import ExtractionEngine
from database.repository import Repository

def render_upload():
    st.title("📤 Document Ingestion & Extraction")
    st.markdown("Upload government scheme notification PDFs or test pre-built synthetic documents.")

    repo = Repository()
    loader = DocumentLoader(repository=repo)
    engine = ExtractionEngine(repository=repo)

    tab1, tab2 = st.tabs(["Upload New PDF", "Load Synthetic Test Documents"])

    with tab1:
        st.subheader("Upload Welfare Scheme PDF")
        uploaded_file = st.file_uploader("Select PDF file (Max 25MB)", type=["pdf"])

        col1, col2 = st.columns(2)
        with col1:
            source_name = st.text_input("Source Document Name / Label", placeholder="e.g. State Welfare Notification 2026")
            source_type = st.selectbox(
                "Source Type",
                ["government_pdf", "department_website", "catalogue_listing", "gazette_notification"]
            )
            captured_at = st.date_input("Capture Date", value=datetime.today()).strftime("%Y-%m-%d")

        with col2:
            source_url = st.text_input("Official Source URL (Optional)", placeholder="https://example.gov.invalid/scheme")
            lang_choice = st.selectbox("Language Option", ["Automatic Detection", "English (en)", "Hindi (hi)"])

        if uploaded_file is not None:
            if st.button("🚀 Process & Ingest Document", type="primary"):
                with st.spinner("Extracting text and running OCR pipeline..."):
                    # Write to temp file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(uploaded_file.getbuffer())
                        tmp_path = tmp.name

                    try:
                        # Ingest
                        meta = loader.load_pdf(
                            file_path=tmp_path,
                            source_type=source_type,
                            source_url=source_url if source_url else None,
                            captured_at=captured_at
                        )
                        st.success(f"Document Ingested! Source ID: `{meta.source_id}` (SHA-256: `{meta.sha256_hash[:16]}...`)")

                        if meta.warnings:
                            st.warning("Extraction Warnings:\n" + "\n".join([f"- {w}" for w in meta.warnings]))

                        # Run Extraction
                        with st.spinner("Executing grounded LLM extraction pass..."):
                            scheme = engine.extract_scheme(meta)
                            st.success(f"Extracted Scheme: **{scheme.scheme_name}** (`{scheme.scheme_ref}`)")
                            st.info("Navigate to 'Extraction Results' to inspect fields and evidence quotations.")
                    except Exception as e:
                        st.error(f"Processing failed: {e}")
                    finally:
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)

    with tab2:
        st.subheader("Ingest Pre-Generated Synthetic Evaluation Cases")
        st.markdown(
            "Quickly ingest the benchmark cases designed for this technical assignment:\n"
            "- **Document A:** English digital PDF (multi-page, ₹50,000 benefit)\n"
            "- **Document B:** Hindi Devanagari PDF (multi-page, ₹25,000 benefit)\n"
            "- **Document C:** Scanned/image-based PDF (pure image, requires OCR, ₹12,000 benefit)"
        )

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("📄 Load Doc A (English)"):
                p = SAMPLE_DOCS_DIR / "doc_a_english_scheme.pdf"
                if p.exists():
                    with st.spinner("Processing Doc A..."):
                        m = loader.load_pdf(str(p), source_id="DOC-001", source_type="government_pdf", captured_at="2026-10-30")
                        s = engine.extract_scheme(m, scheme_ref="SCHEME-001")
                        st.success(f"Loaded: {s.scheme_name}")
                else:
                    st.error("Synthetic doc_a not found. Please run generator.")

        with col_b:
            if st.button("📜 Load Doc B (Hindi)"):
                p = SAMPLE_DOCS_DIR / "doc_b_hindi_scheme.pdf"
                if p.exists():
                    with st.spinner("Processing Doc B (Devanagari)..."):
                        m = loader.load_pdf(str(p), source_id="DOC-002", source_type="government_pdf", captured_at="2026-10-30")
                        s = engine.extract_scheme(m, scheme_ref="SCHEME-002")
                        st.success(f"Loaded: {s.scheme_name}")
                else:
                    st.error("Synthetic doc_b not found. Please run generator.")

        with col_c:
            if st.button("🖼️ Load Doc C (Scanned OCR)"):
                p = SAMPLE_DOCS_DIR / "doc_c_scanned_scheme.pdf"
                if p.exists():
                    with st.spinner("Processing Doc C (OCR Pipeline)..."):
                        m = loader.load_pdf(str(p), source_id="DOC-003", source_type="government_pdf", captured_at="2026-10-30")
                        s = engine.extract_scheme(m, scheme_ref="SCHEME-003")
                        st.success(f"Loaded: {s.scheme_name}")
                else:
                    st.error("Synthetic doc_c not found. Please run generator.")
