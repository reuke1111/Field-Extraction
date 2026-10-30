"""
Page 1: System Dashboard
Summary metrics, system status, and visual overview.
"""

import streamlit as st
from database.repository import Repository
from evaluation.evaluation_runner import EvaluationRunner
from ui import render_md_table

def render_dashboard():
    st.title("🏛️ Haqdarshak Scheme Knowledge Extraction System")
    st.markdown(
        "**AI-Powered First-Pass Extraction with Traceable Evidence & Human-in-the-Loop Governance**"
    )

    repo = Repository()
    stats = repo.get_dashboard_stats()

    # Top metric cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Documents", stats["total_documents"], help="Total source documents ingested")
    with col2:
        st.metric("Total Schemes", stats["total_schemes"], help="Total scheme entities indexed")
    with col3:
        st.metric("Fields Extracted", stats["total_fields"], help="Scheme attributes tracked")
    with col4:
        st.metric("Approved Records", stats["approved_records"], help="Schemes fully verified and published")

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("⚠️ Governance & Attention Needed")
        st.metric(
            "Fields Needing Review",
            stats["fields_needing_review"],
            delta="-Action Required" if stats["fields_needing_review"] > 0 else "All Clear",
            delta_color="inverse"
        )
        st.metric(
            "Unresolved Conflicts",
            stats["unresolved_conflicts"],
            delta="-Discrepancy Flagged" if stats["unresolved_conflicts"] > 0 else "Resolved",
            delta_color="inverse"
        )

    with col_b:
        st.subheader("📊 Extraction Quality Summary")
        eval_runs = repo.list_evaluation_runs()
        if eval_runs:
            latest = eval_runs[0]
            st.write(f"**Latest Benchmark Run:** `{latest['eval_id']}` ({latest['run_timestamp']})")
            c1, c2, c3 = st.columns(3)
            c1.metric("Field Accuracy", f"{latest['accuracy'] * 100:.1f}%")
            c2.metric("Evidence Validity", f"{latest['evidence_validity_rate'] * 100:.1f}%")
            c3.metric("Conflict Recall", f"{latest['conflict_detection_recall'] * 100:.1f}%")
        else:
            st.info("No benchmark evaluation has been run yet. Navigate to 'Evaluation' to run benchmarks.")

    st.markdown("---")
    st.subheader("📁 Ingested Documents Overview")
    docs = repo.list_documents()
    if docs:
        doc_rows = []
        for d in docs:
            doc_rows.append({
                "Source ID": d.source_id,
                "Filename": d.filename,
                "Source Type": d.source_type,
                "Language": d.detected_language.upper(),
                "Pages": d.total_pages,
                "Scanned": "Yes (OCR)" if d.has_scanned_pages else "Digital",
                "Captured At": d.captured_at
            })
        render_md_table(doc_rows)
    else:
        st.info("No documents uploaded yet. Go to 'Document Upload' to ingest your first PDF.")
