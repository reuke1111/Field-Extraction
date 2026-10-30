"""
Page 5: Human Review & Publication Approval Workflow
Enforces strict quality gates: blocks approval if unresolved conflicts or unverified evidence exist.
Preserves original AI extraction alongside reviewer corrections.
"""

import streamlit as st
from datetime import datetime
from database.repository import Repository
from models.scheme import REQUIRED_SCHEME_FIELDS

def render_human_review():
    st.title("✍️ Human Review & Scheme Approval")
    st.markdown("Review extracted attributes, apply researcher corrections, and approve records for final publication.")

    repo = Repository()
    schemes = repo.list_schemes()

    if not schemes:
        st.info("No schemes available for review.")
        return

    # Scheme selector
    scheme_options = {f"{s.scheme_ref} - {s.scheme_name} ({s.approval_status})": s.scheme_ref for s in schemes}
    selected_label = st.selectbox("Select Scheme for Review", list(scheme_options.keys()))
    scheme_ref = scheme_options[selected_label]
    scheme = repo.get_scheme(scheme_ref)

    if not scheme:
        st.error("Scheme record not found.")
        return

    # Check for active unresolved conflicts on this scheme
    active_conflicts = [c for c in repo.list_conflicts(scheme_ref) if not c.resolved]
    invalid_evidence_fields = [
        f for f in scheme.fields.values()
        if f.status == "found" and (not f.evidence or not f.evidence.verified)
    ]

    # Status Alert Banners
    if active_conflicts:
        st.error(f"🚨 **APPROVAL BLOCKED:** Scheme has {len(active_conflicts)} unresolved cross-source conflict(s). Resolve in 'Conflict Review' first.")

    if invalid_evidence_fields:
        field_list = ", ".join([f"`{f.field}`" for f in invalid_evidence_fields])
        st.warning(f"⚠️ **EVIDENCE WARNING:** {len(invalid_evidence_fields)} populated field(s) have unverified evidence ({field_list}).")

    st.subheader(f"Auditing Scheme: **{scheme.scheme_name}** (`{scheme.scheme_ref}`)")
    st.caption(f"Current State: `{scheme.approval_status.upper()}` | Source: `{scheme.source.filename}`")

    st.markdown("---")
    st.markdown("### Field-by-Field Review & Override")

    # Display form for each field
    for f_name in REQUIRED_SCHEME_FIELDS:
        f = scheme.fields.get(f_name)
        if not f:
            continue

        with st.expander(f"Field: **{f_name}** — Extracted: `{f.value or 'null'}`", expanded=False):
            col_ai, col_rev = st.columns(2)
            with col_ai:
                st.markdown("**🤖 AI Extraction Output:**")
                st.markdown(f"- **Original Value:** `{f.value}`")
                st.markdown(f"- **Status:** `{f.status}`")
                st.markdown(f"- **Confidence:** `{f.confidence * 100:.1f}%`")
                if f.evidence:
                    st.markdown(f"- **Evidence (Page {f.evidence.page}):**")
                    st.info(f"\"{f.evidence.text}\"")
                    st.caption(f"Verification: {'✅ Verified' if f.evidence.verified else '❌ Unverified'} ({f.evidence.verification_note})")

            with col_rev:
                st.markdown("**🧑‍💻 Researcher Correction & Audit:**")
                with st.form(key=f"field_form_{scheme_ref}_{f_name}"):
                    curr_val = f.reviewer_value if f.reviewer_value is not None else (f.value or "")
                    new_val = st.text_input("Corrected Value (leave as is if accurate)", value=curr_val)
                    
                    action = st.radio(
                        "Decision",
                        ["Accept Value", "Reject Field", "Needs Additional Research"],
                        index=0 if f.reviewer_accepted is True else (1 if f.reviewer_accepted is False else 0)
                    )
                    notes = st.text_area("Audit Notes", value=f.reviewer_notes or "", placeholder="e.g. Verified against state circular clause 4(b).")
                    
                    save_field = st.form_submit_button("Save Field Audit")
                    if save_field:
                        accepted_flag = True if action == "Accept Value" else False
                        repo.update_field_review(
                            scheme_ref=scheme_ref,
                            field=f_name,
                            reviewer_value=new_val if new_val != f.value else None,
                            accepted=accepted_flag,
                            reviewer_notes=notes
                        )
                        st.success(f"Audit saved for `{f_name}`!")
                        st.rerun()

    st.markdown("---")
    st.subheader("🏁 Final Scheme Approval Decision")

    can_approve = (len(active_conflicts) == 0) and (len(invalid_evidence_fields) == 0)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Quality Gate Pre-Requisites:")
        st.write(f"- Active Conflicts: **{len(active_conflicts)}** {'✅' if len(active_conflicts) == 0 else '❌'}")
        st.write(f"- Unverified Evidence on Populated Fields: **{len(invalid_evidence_fields)}** {'✅' if len(invalid_evidence_fields) == 0 else '❌'}")

    with col2:
        reviewer_name = st.text_input("Approving Researcher Name", value="Senior ML Research Auditor")
        approval_memo = st.text_area("Approval Memo / Audit Record", placeholder="Scheme verified in full against primary circular.")

        b1, b2 = st.columns(2)
        with b1:
            approve_btn = st.button("✅ Approve Scheme", type="primary", disabled=not can_approve)
            if approve_btn:
                repo.update_scheme_approval(
                    scheme_ref=scheme_ref,
                    approval_status="approved",
                    reviewer=reviewer_name,
                    notes=approval_memo
                )
                st.success(f"Scheme `{scheme_ref}` is now APPROVED for publication!")
                st.rerun()

        with b2:
            reject_btn = st.button("❌ Reject Scheme")
            if reject_btn:
                repo.update_scheme_approval(
                    scheme_ref=scheme_ref,
                    approval_status="rejected",
                    reviewer=reviewer_name,
                    notes=approval_memo
                )
                st.warning(f"Scheme `{scheme_ref}` has been REJECTED.")
                st.rerun()
