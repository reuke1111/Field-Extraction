"""
Tests for cross-source conflict detection, preservation, and resolution.
"""

from core.conflict_detector import ConflictDetector
from models.scheme import SchemeRecord, ExtractionRunMetadata
from models.source import SourceMetadata
from models.field_record import FieldRecord, Evidence

def test_detect_and_preserve_benefit_amount_conflict():
    detector = ConflictDetector()

    meta1 = SourceMetadata(
        source_id="DOC-001",
        filename="govt_circular.pdf",
        sha256_hash="hash1",
        source_type="government_pdf",
        captured_at="2026-10-30",
        total_pages=2
    )
    meta2 = SourceMetadata(
        source_id="CAT-001",
        filename="catalogue_listing.json",
        sha256_hash="hash2",
        source_type="catalogue_listing",
        captured_at="2026-10-15",
        total_pages=1
    )

    run = ExtractionRunMetadata(
        run_id="RUN-1", model_name="m", model_version="1", provider="mock", prompt_version="p", cost_status="calculated"
    )

    scheme1 = SchemeRecord(
        scheme_ref="SCHEME-001",
        scheme_name="Women Scheme",
        source=meta1,
        run_metadata=run,
        fields={
            "benefits": FieldRecord(
                scheme_ref="SCHEME-001",
                field="benefits",
                value="50000",
                confidence=0.95,
                status="found",
                evidence=Evidence(text="one-time financial benefit of Rs 50,000", page=1, source="govt_circular.pdf", source_id="DOC-001", captured_at="2026-10-30", verified=True)
            )
        }
    )

    scheme2 = SchemeRecord(
        scheme_ref="SCHEME-001",
        scheme_name="Women Scheme",
        source=meta2,
        run_metadata=run,
        fields={
            "benefits": FieldRecord(
                scheme_ref="SCHEME-001",
                field="benefits",
                value="40000",
                confidence=0.92,
                status="found",
                evidence=Evidence(text="grant assistance of Rs 40,000", page=1, source="catalogue_listing.json", source_id="CAT-001", captured_at="2026-10-15", verified=True)
            )
        }
    )

    conflicts = detector.compare_schemes(scheme1, scheme2)
    assert len(conflicts) == 1
    c = conflicts[0]
    assert c.field == "benefits"
    assert c.scheme_ref == "SCHEME-001"
    assert len(c.records) == 2
    assert c.records[0].value == "50000"
    assert c.records[1].value == "40000"
    assert c.resolved is False

    # Verify both records are marked as conflict status
    assert scheme1.fields["benefits"].status == "conflict"
    assert scheme2.fields["benefits"].status == "conflict"
    assert scheme1.approval_status == "conflicted"
