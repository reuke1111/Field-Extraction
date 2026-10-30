"""
Scheme records, conflict groups, and review approval decisions.
"""

from typing import Optional, Literal
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from models.field_record import FieldRecord
from models.source import SourceMetadata

# Standard 8 required scheme extraction fields
REQUIRED_SCHEME_FIELDS = [
    "scheme_name",
    "department",
    "benefits",
    "eligibility_conditions",
    "required_documents",
    "application_procedure",
    "deadline",
    "official_link"
]

def utc_now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

class ExtractionRunMetadata(BaseModel):
    """
    Audit metadata for a model extraction pass.
    """
    run_id: str
    model_name: str
    model_version: str
    provider: str
    prompt_version: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: Optional[float] = None
    cost_status: str = "calculated"  # calculated, unavailable_for_mock, estimate_unavailable
    latency_seconds: float = 0.0
    created_at: str = Field(default_factory=utc_now_str)

class ConflictItem(BaseModel):
    source_id: str
    source_name: str
    source_type: str
    captured_at: str
    value: Optional[str] = None
    evidence_text: Optional[str] = None
    page: Optional[int] = None
    section: Optional[str] = None

class ConflictGroup(BaseModel):
    conflict_id: str
    scheme_ref: str
    field: str
    records: list[ConflictItem]
    detected_at: str = Field(default_factory=utc_now_str)
    resolved: bool = False
    resolution_choice: Optional[str] = None  # selected value or manual override
    resolution_reason: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[str] = None

class SchemeRecord(BaseModel):
    """
    Full extracted scheme entity aggregating all field records and audit trail.
    """
    scheme_ref: str
    scheme_name: str
    source: SourceMetadata
    run_metadata: ExtractionRunMetadata
    fields: dict[str, FieldRecord] = Field(default_factory=dict)
    approval_status: Literal["pending_review", "approved", "rejected", "conflicted"] = "pending_review"
    approval_notes: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
