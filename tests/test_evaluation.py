"""
Tests for evaluation metrics, ground truth benchmarking, and quality gates.
"""

from evaluation.metrics import EvaluationMetrics, is_field_match
from evaluation.ground_truth import GroundTruthManager
from models.field_record import FieldRecord, Evidence

def test_semantic_field_matching():
    # Benefits digits matching
    assert is_field_match("benefits", "₹50,000", "50000")
    assert is_field_match("benefits", "50000", "50000")
    assert not is_field_match("benefits", "40000", "50000")

    # Deadline format matching
    assert is_field_match("deadline", "2026-12-31", "2026-12-31")

    # Name matching
    assert is_field_match("scheme_name", "State Women Entrepreneurship Assistance Scheme (SWEAS)", "State Women Entrepreneurship Assistance Scheme")

def test_evaluation_metrics_calculation():
    extracted = {
        "scheme_name": FieldRecord(scheme_ref="S1", field="scheme_name", value="Scheme A", confidence=0.9, status="found", evidence=Evidence(text="Scheme A", page=1, source="doc.pdf", source_id="D1", captured_at="2026-10-30", verified=True)),
        "benefits": FieldRecord(scheme_ref="S1", field="benefits", value="50000", confidence=0.95, status="found", evidence=Evidence(text="benefit 50000", page=1, source="doc.pdf", source_id="D1", captured_at="2026-10-30", verified=True)),
        "deadline": FieldRecord(scheme_ref="S1", field="deadline", value=None, confidence=0.8, status="not_found")
    }

    expected = {
        "scheme_name": {"value": "Scheme A", "status": "found"},
        "benefits": {"value": "50000", "status": "found"},
        "deadline": {"value": None, "status": "not_found"}
    }

    res = EvaluationMetrics.evaluate_scheme_extraction(extracted, expected)
    assert res["accuracy"] == 1.0
    assert res["precision"] == 1.0
    assert res["recall"] == 1.0
    assert res["f1_score"] == 1.0
    assert res["evidence_validity_rate"] == 1.0

def test_ground_truth_dataset_loading():
    gt = GroundTruthManager()
    schemes = gt.get_all_schemes()
    assert "SCHEME-001" in schemes
    assert "SCHEME-002" in schemes
    assert "SCHEME-003" in schemes
    assert len(gt.get_expected_conflicts()) >= 1
