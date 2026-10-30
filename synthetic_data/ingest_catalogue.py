import json
from pathlib import Path
from database import Repository
from models.source import SourceMetadata
from models.field_record import FieldRecord, Evidence, BenefitDetail
from models.scheme import SchemeRecord, ExtractionRunMetadata
from core.conflict_detector import ConflictDetector

def ingest_catalogue_source():
    repo = Repository()
    cat_file = Path("sample_documents/doc_a_catalogue_listing.json")
    with open(cat_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta_raw = data["source_metadata"]
    meta = SourceMetadata(
        source_id=meta_raw["source_id"],
        filename="doc_a_catalogue_listing.json",
        file_type="json",
        file_size_bytes=cat_file.stat().st_size,
        sha256_hash="catalogue_sha256_synthetic_001",
        source_type=meta_raw["source_type"],
        source_url=meta_raw.get("source_url"),
        captured_at=meta_raw["captured_at"],
        detected_language="en",
        total_pages=1,
        has_scanned_pages=False,
        ocr_method="catalogue_metadata_json"
    )

    # Save page text
    repo.save_document(meta, [{"page_number": 1, "text": json.dumps(data), "is_scanned": False, "ocr_applied": False}])

    run_meta = ExtractionRunMetadata(
        run_id="RUN-CAT-001",
        model_name="catalogue_parser_v1",
        model_version="1.0",
        provider="mock",
        prompt_version="v1.0-catalogue",
        cost_status="unavailable_for_mock"
    )

    # Build fields for catalogue scheme
    fields = {
        "scheme_name": FieldRecord(scheme_ref="SCHEME-001", field="scheme_name", value=data["scheme_name"], confidence=1.0, status="found"),
        "department": FieldRecord(scheme_ref="SCHEME-001", field="department", value=data["department"], confidence=1.0, status="found"),
        "benefits": FieldRecord(
            scheme_ref="SCHEME-001",
            field="benefits",
            value=data["benefit_amount"],
            confidence=0.95,
            status="found",
            evidence=Evidence(
                text=data["evidence_quote"],
                page=1,
                section=data["section"],
                source="doc_a_catalogue_listing.json",
                source_id="CAT-001",
                captured_at=meta_raw["captured_at"],
                source_url=meta_raw.get("source_url"),
                verified=True,
                verification_score=1.0
            ),
            structured_benefit=BenefitDetail(
                benefit_type=data["benefit_type"],
                amount=data["benefit_amount"],
                currency=data["benefit_currency"],
                frequency=data["benefit_frequency"]
            )
        )
    }

    cat_scheme = SchemeRecord(
        scheme_ref="SCHEME-001",
        scheme_name=data["scheme_name"],
        source=meta,
        run_metadata=run_meta,
        fields=fields,
        approval_status="pending_review"
    )

    # Retrieve existing Doc A scheme
    primary_scheme = repo.get_scheme("SCHEME-001")
    if primary_scheme:
        detector = ConflictDetector()
        conflicts = detector.compare_schemes(primary_scheme, cat_scheme)
        print(f"Conflicts detected: {len(conflicts)}")
        for c in conflicts:
            print(f"  Conflict ID: {c.conflict_id} | Field: {c.field}")
            print(f"    Source 1: {c.records[0].source_name} -> {c.records[0].value}")
            print(f"    Source 2: {c.records[1].source_name} -> {c.records[1].value}")
            repo.save_conflict_group(c)

        # Update primary scheme in repo to reflect conflicted status
        repo.save_scheme_and_fields(primary_scheme, primary_scheme.run_metadata)

if __name__ == "__main__":
    ingest_catalogue_source()
