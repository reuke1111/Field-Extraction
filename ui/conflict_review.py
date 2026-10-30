"""
Page 4: Cross-Source Conflict Review
Displays disagreeing values side-by-side and allows reviewers to record reasoned resolutions.
"""

import streamlit as st
from database.repository import Repository

def render_conflict_review():
    st.title("⚖️ Cross-Source Conflict Review")
    st.markdown(
        "When multiple sources (e.g. government circulars vs portal catalogue listings) disagree, "
        "the system **preserves both records** rather than silently overwriting. Reviewers must resolve discrepancies with documented reasons."
    )

    repo = Repository()
    conflicts = repo.list_conflicts()

    if not conflicts:
        st.success("✅ No cross-source conflicts detected across ingested documents.")
        return

    st.subheader(f"Flagged Conflict Groups ({len(conflicts)})")

    for idx, conf in enumerate(conflicts):
        status_badge = "✅ RESOLVED" if conf.resolved else "🚨 UNRESOLVED CONFLICT"
        st.markdown(f"### {status_badge} — Field: `{conf.field}` (Scheme: `{conf.scheme_ref}`)")
        st.caption(f"Conflict ID: `{conf.conflict_id}` | Detected At: {conf.detected_at}")

        rec_a = conf.records[0] if len(conf.records) > 0 else None
        rec_b = conf.records[1] if len(conf.records) > 1 else None

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"#### 🏛️ Source A: {rec_a.source_type.replace('_', ' ').title() if rec_a else 'Source A'}")
            if rec_a:
                st.markdown(f"**Document:** `{rec_a.source_name}` (`{rec_a.source_id}`)")
                st.markdown(f"**Captured Date:** `{rec_a.captured_at}`")
                st.markdown(f"**Extracted Value:** `{rec_a.value}`")
                st.markdown(f"**Quotation Evidence (Page {rec_a.page}):**")
                st.info(f"\"{rec_a.evidence_text}\"")

        with col_b:
            st.markdown(f"#### 🌐 Source B: {rec_b.source_type.replace('_', ' ').title() if rec_b else 'Source B'}")
            if rec_b:
                st.markdown(f"**Document:** `{rec_b.source_name}` (`{rec_b.source_id}`)")
                st.markdown(f"**Captured Date:** `{rec_b.captured_at}`")
                st.markdown(f"**Extracted Value:** `{rec_b.value}`")
                st.markdown(f"**Quotation Evidence (Page {rec_b.page}):**")
                st.info(f"\"{rec_b.evidence_text}\"")

        # Resolution interface
        st.markdown("##### 📝 Reviewer Resolution Decision")
        if conf.resolved:
            st.success(
                f"**Resolved Choice:** `{conf.resolution_choice}`\n\n"
                f"**Documented Reason:** {conf.resolution_reason}\n\n"
                f"**Resolved By:** `{conf.resolved_by}` on `{conf.resolved_at}`"
            )
        else:
            with st.form(key=f"resolve_form_{conf.conflict_id}_{idx}"):
                options = [
                    f"Accept Source A Value: {rec_a.value if rec_a else ''}",
                    f"Accept Source B Value: {rec_b.value if rec_b else ''}",
                    "Mark as Unresolved / Escalated",
                    "Custom Overwrite Value"
                ]
                choice = st.selectbox("Resolution Action", options)
                reason = st.text_area(
                    "Documented Reason / Audit Note",
                    placeholder="e.g. Official Government PDF supersedes preliminary catalogue draft as verified by notification date."
                )
                reviewer_name = st.text_input("Reviewer Name / Staff ID", value="Senior Researcher")

                submit = st.form_submit_button("Submit Conflict Resolution", type="primary")
                if submit:
                    if not reason.strip():
                        st.error("Please provide a documented reason for this resolution.")
                    else:
                        repo.resolve_conflict(
                            conflict_id=conf.conflict_id,
                            choice=choice,
                            reason=reason,
                            resolver=reviewer_name
                        )
                        st.success("Conflict resolution recorded! Refreshing...")
                        st.rerun()

        st.markdown("---")
