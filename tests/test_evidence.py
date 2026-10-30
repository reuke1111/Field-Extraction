"""
Tests for independent evidence validation engine.
"""

from core.evidence_validator import EvidenceValidator
from models.field_record import Evidence

def test_evidence_exact_match():
    validator = EvidenceValidator()
    pages = [
        {"page_number": 1, "text": "GOVERNMENT OF STATE. The financial benefit is Rs 50,000 for approved entrepreneurs."},
        {"page_number": 2, "text": "Deadline is 2026-12-31."}
    ]

    ev = Evidence(
        text="The financial benefit is Rs 50,000 for approved entrepreneurs.",
        page=1,
        source="doc.pdf",
        source_id="DOC-001",
        captured_at="2026-10-30"
    )

    verified, score, note = validator.validate_evidence(ev, pages, "DOC-001")
    assert verified is True
    assert score == 1.0

def test_evidence_unicode_and_whitespace_normalization():
    validator = EvidenceValidator()
    pages = [
        {"page_number": 1, "text": "The   applicant \n must be a   female individual aged 21-55."}
    ]

    ev = Evidence(
        text="The applicant must be a female individual aged 21-55.",
        page=1,
        source="doc.pdf",
        source_id="DOC-001",
        captured_at="2026-10-30"
    )

    verified, score, note = validator.validate_evidence(ev, pages, "DOC-001")
    assert verified is True
    assert score == 1.0

def test_fabricated_evidence_fails():
    validator = EvidenceValidator()
    pages = [
        {"page_number": 1, "text": "Scheme provides financial assistance."},
        {"page_number": 2, "text": "Apply online at portal."}
    ]

    ev = Evidence(
        text="All applicants receive a free electric vehicle and smartphone.",  # Fabricated
        page=1,
        source="doc.pdf",
        source_id="DOC-001",
        captured_at="2026-10-30"
    )

    verified, score, note = validator.validate_evidence(ev, pages, "DOC-001")
    assert verified is False
    assert score == 0.0
    assert "not found" in note.lower()

def test_wrong_page_citation_fails():
    validator = EvidenceValidator()
    pages = [
        {"page_number": 1, "text": "Introduction and title of the scheme."},
        {"page_number": 2, "text": "The deadline for submission is 2026-12-31."}
    ]

    # Quotation exists on Page 2, but evidence erroneously claims Page 1
    ev = Evidence(
        text="The deadline for submission is 2026-12-31.",
        page=1,
        source="doc.pdf",
        source_id="DOC-001",
        captured_at="2026-10-30"
    )

    verified, score, note = validator.validate_evidence(ev, pages, "DOC-001")
    assert verified is False
    assert "found on page 2, but llm erroneously cited page 1" in note.lower()

def test_out_of_bounds_page():
    validator = EvidenceValidator()
    pages = [{"page_number": 1, "text": "Only one page exists."}]

    ev = Evidence(
        text="Some text",
        page=5,
        source="doc.pdf",
        source_id="DOC-001",
        captured_at="2026-10-30"
    )

    verified, score, note = validator.validate_evidence(ev, pages, "DOC-001")
    assert verified is False
    assert "invalid page reference" in note.lower()

def test_source_id_mismatch():
    validator = EvidenceValidator()
    pages = [{"page_number": 1, "text": "Valid text"}]

    ev = Evidence(
        text="Valid text",
        page=1,
        source="doc.pdf",
        source_id="DOC-999",  # Mismatch
        captured_at="2026-10-30"
    )

    verified, score, note = validator.validate_evidence(ev, pages, "DOC-001")
    assert verified is False
    assert "mismatch" in note.lower()
