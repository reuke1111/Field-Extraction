"""
Page 3: Extraction Results & Evidence Inspection
"""

import streamlit as st
from database.repository import Repository
from models.scheme import REQUIRED_SCHEME_FIELDS
from ui import render_md_table

def render_extraction_review():
    st.title("🔍 Extraction Results & Evidence Inspection")
    st.markdown("Inspect extracted scheme fields, traceable source quotations, page citations, and verification status.")

    repo = Repository()
    schemes = repo.list_schemes()

    if not schemes:
        st.info("No schemes available yet. Upload a document from 'Document Upload' first.")
        return

    # Scheme selector
    scheme_options = {f"{s.scheme_ref} - {s.scheme_name}": s.scheme_ref for s in schemes}
    selected_label = st.selectbox("Select Scheme Record", list(scheme_options.keys()))
    scheme_ref = scheme_options[selected_label]
    scheme = repo.get_scheme(scheme_ref)

    if not scheme:
        st.error("Scheme not found.")
        return

    # Header metadata card
    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f"**Source File:** `{scheme.source.filename}`")
    col2.markdown(f"**Language:** `{scheme.source.detected_language.upper()}`")
    col3.markdown(f"**Pages:** `{scheme.source.total_pages}`")
    status_color = "green" if scheme.approval_status == "approved" else ("red" if scheme.approval_status == "conflicted" else "orange")
    col4.markdown(f"**Approval Status:** :{status_color}[{scheme.approval_status.upper()}]")

    st.markdown("---")

    # Table of fields
    st.subheader("Extracted Scheme Attributes")
    table_data = []
    for f_name in REQUIRED_SCHEME_FIELDS:
        f = scheme.fields.get(f_name)
        if f:
            ev_status = "✅ Verified" if (f.evidence and f.evidence.verified) else ("⚠️ Invalid/Unverified" if f.status == "found" else "N/A (Missing)")
            review_state = "Accepted" if f.reviewer_accepted is True else ("Rejected" if f.reviewer_accepted is False else "Pending Review")
            table_data.append({
                "Field": f.field,
                "Extracted Value": (f.value[:60] + "...") if f.value and len(f.value) > 60 else (f.value or "—"),
                "Confidence": f"{f.confidence * 100:.1f}%",
                "Evidence Validity": ev_status,
                "Status": f.status.upper(),
                "Review State": review_state
            })
    render_md_table(table_data)

    st.markdown("---")
    st.subheader("🔬 Deep Evidence & Citation Inspector")
    inspected_field_name = st.selectbox("Choose a field to inspect evidence quotation and source page", REQUIRED_SCHEME_FIELDS)
    field_record = scheme.fields.get(inspected_field_name)

    if field_record:
        col_left, col_right = st.columns([1, 1])
        with col_left:
            st.markdown(f"### Field: `{field_record.field}`")
            st.markdown(f"**Extracted Value:** `{field_record.value}`")
            st.markdown(f"**Extraction Status:** `{field_record.status}`")
            st.markdown(f"**Confidence Score:** `{field_record.confidence * 100:.1f}%` (Heuristic)")

            if field_record.structured_benefit:
                sb = field_record.structured_benefit
                st.info(f"**Structured Benefit Breakdown:**\n- Type: `{sb.benefit_type}`\n- Amount: `{sb.amount}` {sb.currency}\n- Frequency: `{sb.frequency}`\n- Conditions: `{sb.conditions}`")

            if field_record.evidence:
                ev = field_record.evidence
                st.markdown("#### 📜 Traceable Source Evidence")
                ev_box = f"> \"{ev.text}\""
                st.markdown(ev_box)
                st.markdown(f"- **Cited Page:** Page {ev.page}")
                st.markdown(f"- **Section:** {ev.section or 'General'}")
                st.markdown(f"- **Source ID:** `{ev.source_id}` ({ev.source})")
                st.markdown(f"- **Capture Date:** {ev.captured_at}")
                if ev.source_url:
                    st.markdown(f"- **Official Link:** [{ev.source_url}]({ev.source_url})")

                if ev.verified:
                    st.success(f"✅ Evidence Verification Passed (Match score: {ev.verification_score:.2f})\n{ev.verification_note}")
                else:
                    st.error(f"❌ Evidence Verification Failed:\n{ev.verification_note}")
            else:
                st.warning("No evidence quotation associated with this field.")

        with col_right:
            st.markdown("### 📄 Original Document Page Text")
            pages = repo.get_document_pages(scheme.source.source_id)
            target_page_num = (field_record.evidence.page if field_record.evidence and field_record.evidence.page else 1)
            selected_page_num = st.selectbox(
                "View Document Page",
                options=[p["page_number"] for p in pages],
                index=min(max(0, target_page_num - 1), len(pages) - 1)
            )

            page_obj = next((p for p in pages if p["page_number"] == selected_page_num), None)
            if page_obj:
                badge = "🖼️ Scanned Page (OCR Processed)" if page_obj["is_scanned"] else "📄 Digital Selectable Text"
                st.caption(f"{badge} | Page {page_obj['page_number']} | Character count: {len(page_obj['text'])}")
                st.text_area("Source Page Text", value=page_obj["text"], height=320, disabled=True)
            else:
                st.warning("Page text unavailable.")
