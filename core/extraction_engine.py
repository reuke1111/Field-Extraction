"""
Extraction Engine coordinator.
Orchestrates page formatting, LLM extraction, Pydantic validation, evidence verification,
confidence computation, and database storage.
"""

import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from models.source import SourceMetadata
from models.field_record import FieldRecord, Evidence, BenefitDetail
from models.scheme import (
    SchemeRecord,
    ExtractionRunMetadata,
    REQUIRED_SCHEME_FIELDS
)
from llm.base import BaseLLMProvider
from llm.provider import get_llm_provider
from core.evidence_validator import EvidenceValidator
from core.confidence import ConfidenceCalculator
from config import PROMPT_VERSION
from database.repository import Repository

class ExtractionEngine:
    def __init__(
        self,
        llm_provider: Optional[BaseLLMProvider] = None,
        repository: Optional[Repository] = None,
        evidence_validator: Optional[EvidenceValidator] = None
    ):
        self.llm_provider = llm_provider or get_llm_provider()
        self.repository = repository or Repository()
        self.evidence_validator = evidence_validator or EvidenceValidator()
        self.confidence_calculator = ConfidenceCalculator()

    def format_pages_for_prompt(self, pages: List[Dict[str, Any]]) -> str:
        """
        Formats per-page text with explicit boundary markers for LLM consumption.
        """
        formatted = []
        for p in pages:
            num = p["page_number"]
            text = p["text"].strip()
            formatted.append(f"--- [PAGE {num}] ---\n{text}\n")
        return "\n".join(formatted)

    def extract_scheme(
        self,
        source: SourceMetadata,
        scheme_ref: Optional[str] = None
    ) -> SchemeRecord:
        """
        Executes full extraction pipeline on an ingested document.
        """
        # 1. Fetch document pages
        pages = self.repository.get_document_pages(source.source_id)
        if not pages:
            raise ValueError(f"No pages found in repository for document '{source.source_id}'.")

        # Derive scheme_ref if not provided
        if not scheme_ref:
            # Map known documents or generate ID
            if "doc_a" in source.filename.lower() or "cat_001" in source.source_id.lower():
                scheme_ref = "SCHEME-001"
            elif "doc_b" in source.filename.lower():
                scheme_ref = "SCHEME-002"
            elif "doc_c" in source.filename.lower():
                scheme_ref = "SCHEME-003"
            else:
                scheme_ref = f"SCHEME-{uuid.uuid4().hex[:6].upper()}"

        # 2. Format text for LLM
        document_text = self.format_pages_for_prompt(pages)

        # 3. Call LLM provider
        raw_fields, run_info = self.llm_provider.extract_scheme_fields(
            document_text=document_text,
            document_metadata=source.model_dump(),
            prompt_version=PROMPT_VERSION
        )

        run_id = f"RUN-{uuid.uuid4().hex[:8].upper()}"
        run_meta = ExtractionRunMetadata(
            run_id=run_id,
            model_name=run_info.get("model_name", self.llm_provider.model_name),
            model_version=run_info.get("model_version", self.llm_provider.model_version),
            provider=run_info.get("provider", self.llm_provider.provider_name),
            prompt_version=PROMPT_VERSION,
            input_tokens=run_info.get("input_tokens", 0),
            output_tokens=run_info.get("output_tokens", 0),
            total_tokens=run_info.get("total_tokens", 0),
            estimated_cost_usd=run_info.get("estimated_cost_usd"),
            cost_status=run_info.get("cost_status", "calculated"),
            latency_seconds=run_info.get("latency_seconds", 0.0),
            created_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        )

        # 4. Parse & validate fields into FieldRecords
        field_records = {}
        scheme_name_val = "Unnamed Welfare Scheme"

        for field_name in REQUIRED_SCHEME_FIELDS:
            raw_field = raw_fields.get(field_name, {})
            val = raw_field.get("value")
            status = raw_field.get("status", "found" if val else "not_found")
            raw_confidence = raw_field.get("confidence", 0.85 if val else 0.0)
            note = raw_field.get("note")

            if field_name == "scheme_name" and val:
                scheme_name_val = str(val)

            # Build Evidence
            evidence_obj = None
            ev_text = raw_field.get("evidence_text")
            if ev_text:
                evidence_obj = Evidence(
                    text=str(ev_text),
                    page=raw_field.get("page"),
                    section=raw_field.get("section"),
                    source=source.filename,
                    source_id=source.source_id,
                    captured_at=source.captured_at,
                    source_url=source.source_url
                )

            # Build Structured Benefit if applicable
            structured_benefit = None
            if field_name == "benefits":
                structured_benefit = BenefitDetail(
                    benefit_type=raw_field.get("benefit_type", "financial"),
                    amount=raw_field.get("amount") or (str(val) if val and str(val).isdigit() else None),
                    currency=raw_field.get("currency", "INR"),
                    frequency=raw_field.get("frequency"),
                    conditions=raw_field.get("conditions")
                )

            record = FieldRecord(
                scheme_ref=scheme_ref,
                field=field_name,
                value=str(val) if val is not None else None,
                evidence=evidence_obj,
                confidence=float(raw_confidence),
                status=status,
                note=note,
                structured_benefit=structured_benefit
            )
            field_records[field_name] = record

        # 5. Validate Evidence against source pages
        field_records = self.evidence_validator.validate_field_records(
            fields=field_records,
            page_texts=pages,
            document_source_id=source.source_id
        )

        # 6. Compute composite confidence scores
        for fname, record in field_records.items():
            is_scanned = source.has_scanned_pages
            record.confidence = self.confidence_calculator.calculate_field_confidence(
                record=record,
                is_scanned_page=is_scanned,
                base_model_confidence=record.confidence
            )

        # 7. Assemble SchemeRecord
        scheme_record = SchemeRecord(
            scheme_ref=scheme_ref,
            scheme_name=scheme_name_val,
            source=source,
            run_metadata=run_meta,
            fields=field_records,
            approval_status="pending_review"
        )

        # 8. Persist scheme and fields
        self.repository.save_scheme_and_fields(scheme_record, run_meta)

        return scheme_record
