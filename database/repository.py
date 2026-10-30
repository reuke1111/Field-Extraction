"""
Database repository handling queries, persistence, transactions, and state updates.
"""

import json
from typing import Optional, Any
from database.db import get_db_connection
from models.source import SourceMetadata
from models.field_record import FieldRecord, Evidence, BenefitDetail
from models.scheme import (
    SchemeRecord,
    ExtractionRunMetadata,
    ConflictGroup,
    ConflictItem
)

class Repository:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    def _conn(self):
        return get_db_connection(self.db_path) if self.db_path else get_db_connection()

    # ----------------- Document Operations ----------------- #
    def save_document(self, metadata: SourceMetadata, pages_text: list[dict[str, Any]]) -> None:
        """
        Saves document metadata and per-page text content within an atomic transaction.
        """
        conn = self._conn()
        cur = conn.cursor()
        try:
            cur.execute("""
            INSERT OR REPLACE INTO documents (
                source_id, filename, file_type, file_size_bytes, sha256_hash,
                source_type, source_url, captured_at, detected_language,
                total_pages, has_scanned_pages, ocr_method, warnings
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metadata.source_id,
                metadata.filename,
                metadata.file_type,
                metadata.file_size_bytes,
                metadata.sha256_hash,
                metadata.source_type,
                metadata.source_url,
                metadata.captured_at,
                metadata.detected_language,
                metadata.total_pages,
                1 if metadata.has_scanned_pages else 0,
                metadata.ocr_method,
                json.dumps(metadata.warnings)
            ))

            for page in pages_text:
                cur.execute("""
                INSERT OR REPLACE INTO document_pages (
                    source_id, page_number, text_content, is_scanned, ocr_applied, character_count
                ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    metadata.source_id,
                    page["page_number"],
                    page["text"],
                    1 if page.get("is_scanned") else 0,
                    1 if page.get("ocr_applied") else 0,
                    len(page["text"])
                ))
            conn.commit()
        finally:
            conn.close()

    def get_document_by_id(self, source_id: str) -> Optional[SourceMetadata]:
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM documents WHERE source_id = ?", (source_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        return SourceMetadata(
            source_id=row["source_id"],
            filename=row["filename"],
            file_type=row["file_type"],
            file_size_bytes=row["file_size_bytes"],
            sha256_hash=row["sha256_hash"],
            source_type=row["source_type"],
            source_url=row["source_url"],
            captured_at=row["captured_at"],
            detected_language=row["detected_language"],
            total_pages=row["total_pages"],
            has_scanned_pages=bool(row["has_scanned_pages"]),
            ocr_method=row["ocr_method"],
            warnings=json.loads(row["warnings"]) if row["warnings"] else []
        )

    def get_document_by_hash(self, sha256_hash: str) -> Optional[SourceMetadata]:
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM documents WHERE sha256_hash = ?", (sha256_hash,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        return SourceMetadata(
            source_id=row["source_id"],
            filename=row["filename"],
            file_type=row["file_type"],
            file_size_bytes=row["file_size_bytes"],
            sha256_hash=row["sha256_hash"],
            source_type=row["source_type"],
            source_url=row["source_url"],
            captured_at=row["captured_at"],
            detected_language=row["detected_language"],
            total_pages=row["total_pages"],
            has_scanned_pages=bool(row["has_scanned_pages"]),
            ocr_method=row["ocr_method"],
            warnings=json.loads(row["warnings"]) if row["warnings"] else []
        )

    def get_document_pages(self, source_id: str) -> list[dict[str, Any]]:
        conn = self._conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT page_number, text_content, is_scanned, ocr_applied FROM document_pages WHERE source_id = ? ORDER BY page_number ASC",
            (source_id,)
        )
        rows = cur.fetchall()
        conn.close()
        return [
            {
                "page_number": r["page_number"],
                "text": r["text_content"],
                "is_scanned": bool(r["is_scanned"]),
                "ocr_applied": bool(r["ocr_applied"])
            }
            for r in rows
        ]

    def list_documents(self) -> list[SourceMetadata]:
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM documents ORDER BY created_at DESC")
        rows = cur.fetchall()
        conn.close()
        return [
            SourceMetadata(
                source_id=r["source_id"],
                filename=r["filename"],
                file_type=r["file_type"],
                file_size_bytes=r["file_size_bytes"],
                sha256_hash=r["sha256_hash"],
                source_type=r["source_type"],
                source_url=r["source_url"],
                captured_at=r["captured_at"],
                detected_language=r["detected_language"],
                total_pages=r["total_pages"],
                has_scanned_pages=bool(r["has_scanned_pages"]),
                ocr_method=r["ocr_method"],
                warnings=json.loads(r["warnings"]) if r["warnings"] else []
            )
            for r in rows
        ]

    # ----------------- Scheme & Run Operations ----------------- #
    def save_scheme_and_fields(
        self,
        scheme: SchemeRecord,
        run_meta: ExtractionRunMetadata
    ) -> None:
        conn = self._conn()
        cur = conn.cursor()
        try:
            # 1. Save extraction run
            cur.execute("""
            INSERT OR REPLACE INTO extraction_runs (
                run_id, source_id, scheme_ref, model_name, model_version,
                provider, prompt_version, input_tokens, output_tokens,
                total_tokens, estimated_cost_usd, cost_status, latency_seconds
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run_meta.run_id,
                scheme.source.source_id,
                scheme.scheme_ref,
                run_meta.model_name,
                run_meta.model_version,
                run_meta.provider,
                run_meta.prompt_version,
                run_meta.input_tokens,
                run_meta.output_tokens,
                run_meta.total_tokens,
                run_meta.estimated_cost_usd,
                run_meta.cost_status,
                run_meta.latency_seconds
            ))

            # 2. Save scheme header
            cur.execute("""
            INSERT OR REPLACE INTO schemes (
                scheme_ref, scheme_name, source_id, run_id,
                approval_status, approval_notes, approved_by, approved_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scheme.scheme_ref,
                scheme.scheme_name,
                scheme.source.source_id,
                run_meta.run_id,
                scheme.approval_status,
                scheme.approval_notes,
                scheme.approved_by,
                scheme.approved_at
            ))

            # 3. Save each field record
            for field_name, f in scheme.fields.items():
                ev = f.evidence
                cur.execute("""
                INSERT OR REPLACE INTO field_records (
                    scheme_ref, field, value, confidence, status, note,
                    evidence_text, evidence_page, evidence_section,
                    evidence_source, evidence_source_id, evidence_captured_at,
                    evidence_source_url, evidence_verified, evidence_verification_score,
                    evidence_verification_note, structured_benefit,
                    reviewer_value, reviewer_accepted, reviewer_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    scheme.scheme_ref,
                    field_name,
                    f.value,
                    f.confidence,
                    f.status,
                    f.note,
                    ev.text if ev else None,
                    ev.page if ev else None,
                    ev.section if ev else None,
                    ev.source if ev else None,
                    ev.source_id if ev else None,
                    ev.captured_at if ev else None,
                    ev.source_url if ev else None,
                    1 if (ev and ev.verified) else 0,
                    ev.verification_score if ev else 0.0,
                    ev.verification_note if ev else None,
                    f.structured_benefit.model_dump_json() if f.structured_benefit else None,
                    f.reviewer_value,
                    1 if f.reviewer_accepted is True else (0 if f.reviewer_accepted is False else None),
                    f.reviewer_notes
                ))
            conn.commit()
        finally:
            conn.close()

    def get_scheme(self, scheme_ref: str) -> Optional[SchemeRecord]:
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM schemes WHERE scheme_ref = ?", (scheme_ref,))
        s_row = cur.fetchone()
        if not s_row:
            conn.close()
            return None

        # Source
        cur.execute("SELECT * FROM documents WHERE source_id = ?", (s_row["source_id"],))
        doc_row = cur.fetchone()
        source = SourceMetadata(
            source_id=doc_row["source_id"],
            filename=doc_row["filename"],
            file_type=doc_row["file_type"],
            file_size_bytes=doc_row["file_size_bytes"],
            sha256_hash=doc_row["sha256_hash"],
            source_type=doc_row["source_type"],
            source_url=doc_row["source_url"],
            captured_at=doc_row["captured_at"],
            detected_language=doc_row["detected_language"],
            total_pages=doc_row["total_pages"],
            has_scanned_pages=bool(doc_row["has_scanned_pages"]),
            ocr_method=doc_row["ocr_method"],
            warnings=json.loads(doc_row["warnings"]) if doc_row["warnings"] else []
        )

        # Run
        cur.execute("SELECT * FROM extraction_runs WHERE run_id = ?", (s_row["run_id"],))
        r_row = cur.fetchone()
        run_meta = ExtractionRunMetadata(
            run_id=r_row["run_id"],
            model_name=r_row["model_name"],
            model_version=r_row["model_version"],
            provider=r_row["provider"],
            prompt_version=r_row["prompt_version"],
            input_tokens=r_row["input_tokens"],
            output_tokens=r_row["output_tokens"],
            total_tokens=r_row["total_tokens"],
            estimated_cost_usd=r_row["estimated_cost_usd"],
            cost_status=r_row["cost_status"],
            latency_seconds=r_row["latency_seconds"],
            created_at=r_row["created_at"]
        )

        # Fields
        cur.execute("SELECT * FROM field_records WHERE scheme_ref = ?", (scheme_ref,))
        field_rows = cur.fetchall()
        fields = {}
        for fr in field_rows:
            ev = None
            if fr["evidence_text"]:
                ev = Evidence(
                    text=fr["evidence_text"],
                    page=fr["evidence_page"],
                    section=fr["evidence_section"],
                    source=fr["evidence_source"] or source.filename,
                    source_id=fr["evidence_source_id"] or source.source_id,
                    captured_at=fr["evidence_captured_at"] or source.captured_at,
                    source_url=fr["evidence_source_url"],
                    verified=bool(fr["evidence_verified"]),
                    verification_score=fr["evidence_verification_score"] or 0.0,
                    verification_note=fr["evidence_verification_note"]
                )
            
            sb = None
            if fr["structured_benefit"]:
                sb = BenefitDetail.model_validate_json(fr["structured_benefit"])

            accepted = None
            if fr["reviewer_accepted"] == 1:
                accepted = True
            elif fr["reviewer_accepted"] == 0:
                accepted = False

            fields[fr["field"]] = FieldRecord(
                scheme_ref=scheme_ref,
                field=fr["field"],
                value=fr["value"],
                evidence=ev,
                confidence=fr["confidence"],
                status=fr["status"],
                note=fr["note"],
                structured_benefit=sb,
                reviewer_value=fr["reviewer_value"],
                reviewer_accepted=accepted,
                reviewer_notes=fr["reviewer_notes"]
            )

        conn.close()
        return SchemeRecord(
            scheme_ref=s_row["scheme_ref"],
            scheme_name=s_row["scheme_name"],
            source=source,
            run_metadata=run_meta,
            fields=fields,
            approval_status=s_row["approval_status"],
            approval_notes=s_row["approval_notes"],
            approved_by=s_row["approved_by"],
            approved_at=s_row["approved_at"]
        )

    def list_schemes(self) -> list[SchemeRecord]:
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT scheme_ref FROM schemes ORDER BY created_at DESC")
        refs = [r["scheme_ref"] for r in cur.fetchall()]
        conn.close()
        schemes = []
        for ref in refs:
            s = self.get_scheme(ref)
            if s:
                schemes.append(s)
        return schemes

    def update_field_review(
        self,
        scheme_ref: str,
        field: str,
        reviewer_value: Optional[str],
        accepted: bool,
        reviewer_notes: Optional[str]
    ) -> None:
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("""
        UPDATE field_records
        SET reviewer_value = ?, reviewer_accepted = ?, reviewer_notes = ?, updated_at = CURRENT_TIMESTAMP
        WHERE scheme_ref = ? AND field = ?
        """, (
            reviewer_value,
            1 if accepted else 0,
            reviewer_notes,
            scheme_ref,
            field
        ))
        conn.commit()
        conn.close()

    def update_scheme_approval(
        self,
        scheme_ref: str,
        approval_status: str,
        reviewer: str,
        notes: Optional[str] = None
    ) -> None:
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("""
        UPDATE schemes
        SET approval_status = ?, approved_by = ?, approval_notes = ?, approved_at = CURRENT_TIMESTAMP
        WHERE scheme_ref = ?
        """, (approval_status, reviewer, notes, scheme_ref))
        conn.commit()
        conn.close()

    # ----------------- Conflicts Operations ----------------- #
    def save_conflict_group(self, conflict: ConflictGroup) -> None:
        conn = self._conn()
        cur = conn.cursor()
        records_json = json.dumps([r.model_dump() for r in conflict.records])
        cur.execute("""
        INSERT OR REPLACE INTO conflict_groups (
            conflict_id, scheme_ref, field, records_json, detected_at,
            resolved, resolution_choice, resolution_reason, resolved_by, resolved_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            conflict.conflict_id,
            conflict.scheme_ref,
            conflict.field,
            records_json,
            conflict.detected_at,
            1 if conflict.resolved else 0,
            conflict.resolution_choice,
            conflict.resolution_reason,
            conflict.resolved_by,
            conflict.resolved_at
        ))
        conn.commit()
        conn.close()

    def list_conflicts(self, scheme_ref: Optional[str] = None) -> list[ConflictGroup]:
        conn = self._conn()
        cur = conn.cursor()
        if scheme_ref:
            cur.execute("SELECT * FROM conflict_groups WHERE scheme_ref = ? ORDER BY detected_at DESC", (scheme_ref,))
        else:
            cur.execute("SELECT * FROM conflict_groups ORDER BY detected_at DESC")
        rows = cur.fetchall()
        conn.close()

        results = []
        for r in rows:
            raw_records = json.loads(r["records_json"])
            records = [ConflictItem.model_validate(item) for item in raw_records]
            results.append(
                ConflictGroup(
                    conflict_id=r["conflict_id"],
                    scheme_ref=r["scheme_ref"],
                    field=r["field"],
                    records=records,
                    detected_at=r["detected_at"],
                    resolved=bool(r["resolved"]),
                    resolution_choice=r["resolution_choice"],
                    resolution_reason=r["resolution_reason"],
                    resolved_by=r["resolved_by"],
                    resolved_at=r["resolved_at"]
                )
            )
        return results

    def resolve_conflict(
        self,
        conflict_id: str,
        choice: str,
        reason: str,
        resolver: str
    ) -> None:
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("""
        UPDATE conflict_groups
        SET resolved = 1, resolution_choice = ?, resolution_reason = ?, resolved_by = ?, resolved_at = CURRENT_TIMESTAMP
        WHERE conflict_id = ?
        """, (choice, reason, resolver, conflict_id))
        conn.commit()
        conn.close()

    # ----------------- Evaluation Runs Operations ----------------- #
    def save_evaluation_run(self, eval_id: str, summary: dict[str, Any], results: dict[str, Any]) -> None:
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("""
        INSERT OR REPLACE INTO evaluation_runs (
            eval_id, overall_accuracy, overall_precision, overall_recall,
            overall_f1, evidence_validity_rate, conflict_detection_recall, results_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            eval_id,
            summary.get("accuracy", 0.0),
            summary.get("precision", 0.0),
            summary.get("recall", 0.0),
            summary.get("f1_score", 0.0),
            summary.get("evidence_validity_rate", 0.0),
            summary.get("conflict_detection_recall", 0.0),
            json.dumps(results)
        ))
        conn.commit()
        conn.close()

    def list_evaluation_runs(self) -> list[dict[str, Any]]:
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM evaluation_runs ORDER BY run_timestamp DESC")
        rows = cur.fetchall()
        conn.close()
        return [
            {
                "eval_id": r["eval_id"],
                "run_timestamp": r["run_timestamp"],
                "accuracy": r["overall_accuracy"],
                "precision": r["overall_precision"],
                "recall": r["overall_recall"],
                "f1_score": r["overall_f1"],
                "evidence_validity_rate": r["evidence_validity_rate"],
                "conflict_detection_recall": r["conflict_detection_recall"],
                "results": json.loads(r["results_json"])
            }
            for r in rows
        ]

    # ----------------- System Stats ----------------- #
    def get_dashboard_stats(self) -> dict[str, int]:
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM documents")
        total_docs = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM schemes")
        total_schemes = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM field_records")
        total_fields = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM field_records WHERE status = 'found' AND (evidence_verified = 0 OR confidence < 0.85 OR reviewer_accepted IS NULL)")
        fields_needing_review = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM conflict_groups WHERE resolved = 0")
        unresolved_conflicts = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM schemes WHERE approval_status = 'approved'")
        approved_records = cur.fetchone()[0]

        conn.close()
        return {
            "total_documents": total_docs,
            "total_schemes": total_schemes,
            "total_fields": total_fields,
            "fields_needing_review": fields_needing_review,
            "unresolved_conflicts": unresolved_conflicts,
            "approved_records": approved_records
        }
