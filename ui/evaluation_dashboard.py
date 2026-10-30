"""
Page 6: Evaluation & Cost Estimation Dashboard
Displays automated benchmark performance against ground truth and transparent token cost modeling.
"""

import json
import streamlit as st
from config import INPUT_TOKEN_PRICE_PER_M, OUTPUT_TOKEN_PRICE_PER_M
from evaluation.evaluation_runner import EvaluationRunner
from database.repository import Repository
from ui import render_md_table

def render_evaluation():
    st.title("📈 Ground-Truth Evaluation & Cost Estimation")
    st.markdown("Automated quality auditing across English, Hindi, and Scanned schemes against verified ground truth.")

    repo = Repository()
    runner = EvaluationRunner(repository=repo)

    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        if st.button("⚡ Run Full Automated Benchmark", type="primary"):
            with st.spinner("Executing evaluation against ground truth dataset..."):
                report = runner.run_full_evaluation()
                st.success("Benchmark completed and recorded!")
                st.rerun()

    with col_info:
        st.caption("Benchmark compares all active schemes in repository against `synthetic_data/ground_truth.json` field-by-field.")

    st.markdown("---")

    eval_runs = repo.list_evaluation_runs()
    if not eval_runs:
        st.warning("No benchmark evaluation runs found yet. Click 'Run Full Automated Benchmark' above.")
        return

    latest = eval_runs[0]
    results = latest["results"]
    summary = results.get("summary", {})

    st.subheader(f"📊 Benchmark Summary (Run ID: `{latest['eval_id']}`)")
    st.caption(f"Executed on: {latest['run_timestamp']} | Dataset Size: {summary.get('dataset_size_schemes', 0)} Schemes ({summary.get('total_fields_evaluated', 0)} Fields)")

    # Key Metrics Cards
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Field Accuracy", f"{summary.get('overall_accuracy', 0.0) * 100:.1f}%")
    c2.metric("Precision", f"{summary.get('overall_precision', 0.0) * 100:.1f}%")
    c3.metric("Recall", f"{summary.get('overall_recall', 0.0) * 100:.1f}%")
    c4.metric("F1 Score", f"{summary.get('overall_f1', 0.0) * 100:.1f}%")

    c5, c6 = st.columns(2)
    c5.metric(
        "Traceable Evidence Rate",
        f"{summary.get('evidence_validity_rate', 0.0) * 100:.1f}%",
        help="Percentage of populated extracted fields whose quotations were confirmed on source pages"
    )
    c6.metric(
        "Conflict Detection Recall",
        f"{summary.get('conflict_detection_recall', 0.0) * 100:.1f}%",
        help="Percentage of expected cross-source conflicts successfully detected and flagged"
    )

    st.markdown("---")
    st.subheader("📑 Performance Breakdown by Document Format")

    format_data = summary.get("format_breakdown", {})
    f_rows = []
    for fmt_name, data in format_data.items():
        f_rows.append({
            "Document Format": fmt_name.replace("_", " ").title(),
            "Fields Evaluated": data.get("fields_evaluated", 0),
            "Accuracy": f"{data.get('accuracy', 0.0) * 100:.1f}%"
        })
    render_md_table(f_rows)

    st.markdown("---")
    st.subheader("🔬 Scheme-by-Scheme Field Comparisons")
    scheme_reports = results.get("scheme_reports", {})

    for s_ref, s_info in scheme_reports.items():
        with st.expander(f"Scheme: {s_info.get('scheme_name')} (`{s_ref}`) — Accuracy: {s_info['metrics']['accuracy'] * 100:.1f}%"):
            field_evals = s_info["metrics"].get("field_evaluations", {})
            rows = []
            for fname, fe in field_evals.items():
                rows.append({
                    "Field": fname,
                    "Extracted Value": (str(fe.get("extracted_value"))[:50] + "...") if fe.get("extracted_value") and len(str(fe.get("extracted_value"))) > 50 else str(fe.get("extracted_value") or "—"),
                    "Expected Value": (str(fe.get("expected_value"))[:50] + "...") if fe.get("expected_value") and len(str(fe.get("expected_value"))) > 50 else str(fe.get("expected_value") or "—"),
                    "Match": "✅ YES" if fe.get("match") else "❌ NO",
                    "Evidence Verified": "✅" if fe.get("evidence_verified") else "❌",
                    "Confidence": f"{fe.get('confidence', 0.0) * 100:.1f}%"
                })
            render_md_table(rows)

    st.markdown("---")
    # Cost Estimation Section
    st.subheader("💰 Model Metadata & Scheme Extraction Cost Estimation")
    st.markdown(
        "Accurate per-scheme operational cost projection based on Google Cloud Gemini Flash pricing as of October 2026."
    )

    col_cost_a, col_cost_b = st.columns(2)
    with col_cost_a:
        st.markdown("#### Model & Token Pricing Architecture")
        schemes = repo.list_schemes()
        latest_run = schemes[0].run_metadata if schemes else None
        
        model_name = latest_run.model_name if latest_run else "gemini-2.5-flash / mock"
        model_version = latest_run.model_version if latest_run else "2026-v2.5"
        provider = latest_run.provider if latest_run else "mock"

        st.write(f"- **Active Model Name:** `{model_name}`")
        st.write(f"- **Model Version:** `{model_version}`")
        st.write(f"- **Provider:** `{provider.upper()}`")
        st.write(f"- **Configured Input Token Price:** `${INPUT_TOKEN_PRICE_PER_M:.4f} per 1M tokens`")
        st.write(f"- **Configured Output Token Price:** `${OUTPUT_TOKEN_PRICE_PER_M:.4f} per 1M tokens`")

        if provider == "mock":
            st.info("ℹ️ **Mock Provider Notice:** Extraction cost is marked **UNAVAILABLE** for mock runs rather than artificially claiming $0.00.")

    with col_cost_b:
        st.markdown("#### 5,000 Scheme Enterprise Volume Projection")
        avg_input_tokens = 2500
        avg_output_tokens = 450
        cost_per_scheme = (avg_input_tokens / 1_000_000 * INPUT_TOKEN_PRICE_PER_M) + (avg_output_tokens / 1_000_000 * OUTPUT_TOKEN_PRICE_PER_M)
        total_monthly_cost = cost_per_scheme * 5000

        st.metric("Estimated LLM Cost Per Scheme", f"${cost_per_scheme:.5f} USD")
        st.metric("Estimated Cost for 5,000 Schemes", f"${total_monthly_cost:.2f} USD")
        st.caption(
            "Assumptions: Average government PDF = 3 pages (~2,500 input tokens, ~450 output tokens structured JSON). "
            "Excludes fixed compute / server hosting costs and local CPU OCR processing costs."
        )
