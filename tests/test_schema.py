"""
Tests for Pydantic data schemas, structured benefits, and validation constraints.
"""

import pytest
from pydantic import ValidationError
from models.field_record import Evidence, BenefitDetail, FieldRecord
from models.scheme import REQUIRED_SCHEME_FIELDS

def test_evidence_model_validation():
    ev = Evidence(
        text="Eligible applicants will receive Rs 50,000",
        page=2,
        section="Benefits",
        source="doc_a.pdf",
        source_id="DOC-001",
        captured_at="2026-10-30"
    )
    assert ev.page == 2
    assert ev.verified is False

def test_field_record_valid():
    record = FieldRecord(
        scheme_ref="SCHEME-001",
        field="benefits",
        value="50000",
        confidence=0.95,
        status="found",
        structured_benefit=BenefitDetail(
            benefit_type="financial",
            amount="50000",
            currency="INR",
            frequency="one-time"
        )
    )
    assert record.field == "benefits"
    assert record.confidence == 0.95
    assert record.structured_benefit.amount == "50000"

def test_confidence_boundary_enforcement():
    with pytest.raises(ValidationError):
        FieldRecord(
            scheme_ref="SCHEME-001",
            field="department",
            value="Dept",
            confidence=1.5,  # Exceeds 1.0
            status="found"
        )

    with pytest.raises(ValidationError):
        FieldRecord(
            scheme_ref="SCHEME-001",
            field="department",
            value="Dept",
            confidence=-0.1,  # Below 0.0
            status="found"
        )

def test_invalid_status_rejected():
    with pytest.raises(ValidationError):
        FieldRecord(
            scheme_ref="SCHEME-001",
            field="department",
            value="Dept",
            confidence=0.9,
            status="hallucinated"  # Invalid status
        )

def test_all_eight_required_categories():
    assert len(REQUIRED_SCHEME_FIELDS) == 8
    expected = [
        "scheme_name", "department", "benefits", "eligibility_conditions",
        "required_documents", "application_procedure", "deadline", "official_link"
    ]
    for exp in expected:
        assert exp in REQUIRED_SCHEME_FIELDS
