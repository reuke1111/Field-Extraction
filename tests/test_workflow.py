"""
Tests for full human review workflow, database persistence, approval quality gates, and export.
"""

import tempfile
import os
import json
import csv
from database.db import init_db
from database.repository import Repository
from models.source import SourceMetadata
from models.scheme import SchemeRecord, ExtractionRunMetadata, ConflictGroup, ConflictItem
from models.field_record import FieldRecord, Evidence

def test_workflow_and_approval_gates():
    # Use isolated temporary database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    try:
        init_db(db_path)
        repo = Repository(db_path=db_path)

        # 1. Setup Source & Scheme
        meta = SourceMetadata(
            source_id="DOC-TEST",
            filename="test_scheme.pdf",
            sha256_hash="testhash123",
            source_type="government_pdf",
            captured_at="2026-10-30",
            total_pages=1
        )
        repo.save_document(meta, [{"page_number": 1, "text": "Test Scheme text with benefit Rs 10000", "is_scanned": False, "ocr_applied": False}])

        run_meta = ExtractionRunMetadata(
            run_id="RUN-TEST",
            model_name="mock-model",
            model_version="1.0",
            provider="mock",
            prompt_version="v1.0",
            cost_status="unavailable_for_mock"
        )

        ev = Evidence(
            text="benefit Rs 10000",
            page=1,
            source="test_scheme.pdf",
            source_id="DOC-TEST",
            captured_at="2026-10-30",
            verified=True,
            verification_score=1.0
        )

        scheme = SchemeRecord(
            scheme_ref="SCHEME-TEST",
            scheme_name="Test Scheme",
            source=meta,
            run_metadata=run_meta,
            fields={
                "benefits": FieldRecord(
                    scheme_ref="SCHEME-TEST",
                    field="benefits",
                    value="10000",
                    confidence=0.95,
                    status="found",
                    evidence=ev
                )
            },
            approval_status="pending_review"
        )
        repo.save_scheme_and_fields(scheme, run_meta)

        # Verify initial state
        loaded = repo.get_scheme("SCHEME-TEST")
        assert loaded is not None
        assert loaded.fields["benefits"].value == "10000"
        assert loaded.approval_status == "pending_review"

        # 2. Test Human Review Correction
        repo.update_field_review(
            scheme_ref="SCHEME-TEST",
            field="benefits",
            reviewer_value="12000",
            accepted=True,
            reviewer_notes="Correction based on gazette amendment"
        )

        loaded_after_review = repo.get_scheme("SCHEME-TEST")
        # AI original value preserved, reviewer value updated
        assert loaded_after_review.fields["benefits"].value == "10000"
        assert loaded_after_review.fields["benefits"].reviewer_value == "12000"
        assert loaded_after_review.fields["benefits"].reviewer_accepted is True

        # 3. Add Unresolved Conflict
        conflict = ConflictGroup(
            conflict_id="CONF-TEST-1",
            scheme_ref="SCHEME-TEST",
            field="benefits",
            records=[
                ConflictItem(source_id="DOC-TEST", source_name="test.pdf", source_type="government_pdf", captured_at="2026-10-30", value="10000"),
                ConflictItem(source_id="CAT-TEST", source_name="cat.json", source_type="catalogue_listing", captured_at="2026-10-15", value="8000")
            ],
            resolved=False
        )
        repo.save_conflict_group(conflict)

        active_conflicts = [c for c in repo.list_conflicts("SCHEME-TEST") if not c.resolved]
        assert len(active_conflicts) == 1

        # 4. Resolve Conflict
        repo.resolve_conflict(
            conflict_id="CONF-TEST-1",
            choice="Accept Source A: 10000",
            reason="Primary government circular supersedes unverified catalogue draft.",
            resolver="Lead Auditor"
        )

        active_conflicts_post = [c for c in repo.list_conflicts("SCHEME-TEST") if not c.resolved]
        assert len(active_conflicts_post) == 0

        # 5. Approve Scheme
        repo.update_scheme_approval(
            scheme_ref="SCHEME-TEST",
            approval_status="approved",
            reviewer="Lead Auditor",
            notes="Fully verified and approved."
        )

        final_scheme = repo.get_scheme("SCHEME-TEST")
        assert final_scheme.approval_status == "approved"
        assert final_scheme.approved_by == "Lead Auditor"

    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
