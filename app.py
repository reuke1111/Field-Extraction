"""
Haqdarshak AI-Powered Scheme Knowledge Extraction System.
Option A1: Field Extraction with Evidence.
Main Streamlit Application.
"""

import streamlit as st
from database.db import init_db

# Initialize database schema upon startup
init_db()

# Page configuration
st.set_page_config(
    page_title="Haqdarshak AI Scheme Extraction",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Navigation
from ui.dashboard import render_dashboard
from ui.upload import render_upload
from ui.extraction_review import render_extraction_review
from ui.conflict_review import render_conflict_review
from ui.human_review import render_human_review
from ui.evaluation_dashboard import render_evaluation
from ui.approved_records import render_approved_records

PAGES = {
    "1. Dashboard": render_dashboard,
    "2. Document Upload": render_upload,
    "3. Extraction Results": render_extraction_review,
    "4. Conflict Review": render_conflict_review,
    "5. Human Review": render_human_review,
    "6. Evaluation & Benchmarks": render_evaluation,
    "7. Approved Records": render_approved_records
}

def main():
    st.sidebar.title("🏛️ Haqdarshak AI")
    st.sidebar.caption("Scheme Knowledge Extraction Prototype")
    
    choice = st.sidebar.radio("Navigation", list(PAGES.keys()))
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "**System Architecture:**\n"
        "- 📑 **Source Grounding:** 100% Traceable Evidence\n"
        "- ⚖️ **Conflict Detection:** Preserves Disagreements\n"
        "- 🧑‍💻 **Quality Gate:** Human Verification Enforced\n"
        "- 🤖 **LLM Engine:** Provider-Agnostic with Mock/Gemini"
    )
    st.sidebar.caption("Prototype Version 1.0.0 | A1 Option")

    render_fn = PAGES[choice]
    render_fn()

if __name__ == "__main__":
    main()
