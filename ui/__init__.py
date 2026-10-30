import streamlit as st
from typing import Any


def render_md_table(rows: list[dict[str, Any]]) -> None:
    """
    Renders a list of dictionaries as a clean Markdown table without triggering
    pandas import (avoids Windows Application Control DLL blocks on pandas._libs.sparse).
    """
    if not rows:
        st.info("No records to display.")
        return

    headers = list(rows[0].keys())
    header_line = "| " + " | ".join(headers) + " |"
    sep_line = "| " + " | ".join(["---"] * len(headers)) + " |"

    body_lines = []
    for row in rows:
        vals = [str(row.get(h, "")).replace("|", "\\|").replace("\n", " ") for h in headers]
        body_lines.append("| " + " | ".join(vals) + " |")

    md_table = "\n".join([header_line, sep_line] + body_lines)
    st.markdown(md_table)


from ui.dashboard import render_dashboard
from ui.upload import render_upload
from ui.extraction_review import render_extraction_review
from ui.conflict_review import render_conflict_review
from ui.human_review import render_human_review
from ui.evaluation_dashboard import render_evaluation
from ui.approved_records import render_approved_records

__all__ = [
    "render_md_table",
    "render_dashboard",
    "render_upload",
    "render_extraction_review",
    "render_conflict_review",
    "render_human_review",
    "render_evaluation",
    "render_approved_records"
]
