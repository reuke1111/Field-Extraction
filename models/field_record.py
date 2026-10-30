"""
Pydantic data models for extracted scheme fields, evidence, and structured benefits.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field

class Evidence(BaseModel):
    """
    Traceable quotation evidence pointing to a specific page and source document.
    """
    text: str = Field(description="The exact quotation from the source text.")
    page: Optional[int] = Field(default=None, description="1-based page number where evidence was located.")
    section: Optional[str] = Field(default=None, description="Section heading under which the fact appears.")
    source: str = Field(description="Filename or human-readable source label.")
    source_id: str = Field(description="Unique system ID of the source document, e.g. DOC-001.")
    captured_at: str = Field(description="Date source was captured or indexed, format YYYY-MM-DD.")
    source_url: Optional[str] = Field(default=None, description="Verified official source URL if one genuinely exists.")
    verified: bool = Field(default=False, description="Whether evidence text was deterministically found on source page.")
    verification_score: float = Field(default=0.0, description="Exact or normalized matching score [0.0 to 1.0].")
    verification_note: Optional[str] = Field(default=None, description="Validation diagnostic message.")

class BenefitDetail(BaseModel):
    """
    Structured breakdown of scheme benefits.
    """
    benefit_type: str = Field(default="financial", description="financial, subsidy, loan, training, in-kind")
    amount: Optional[str] = Field(default=None, description="Numeric or amount string, e.g. '50000'")
    currency: Optional[str] = Field(default="INR", description="Currency identifier, e.g. INR")
    frequency: Optional[str] = Field(default=None, description="one-time, monthly, annual, recurring")
    conditions: Optional[str] = Field(default=None, description="Conditions or stipulations attached to benefit.")

class FieldRecord(BaseModel):
    """
    Individual extracted scheme attribute record.
    """
    scheme_ref: str = Field(description="Unique scheme reference code, e.g. SCHEME-001.")
    field: str = Field(description="One of the standard extraction categories.")
    value: Optional[str] = Field(default=None, description="Extracted value or null if not found.")
    evidence: Optional[Evidence] = Field(default=None, description="Traceable quotation evidence.")
    confidence: float = Field(ge=0.0, le=1.0, description="Heuristic confidence score [0.0 to 1.0].")
    status: Literal["found", "not_found", "conflict"] = Field(description="Extraction status.")
    note: Optional[str] = Field(default=None, description="Extraction or missing fact explanation.")
    structured_benefit: Optional[BenefitDetail] = Field(default=None, description="Structured benefit details if applicable.")
    
    # Reviewer governance fields
    reviewer_value: Optional[str] = Field(default=None, description="Human reviewer corrected value.")
    reviewer_accepted: Optional[bool] = Field(default=None, description="True if reviewer accepted/approved field.")
    reviewer_notes: Optional[str] = Field(default=None, description="Auditor review notes.")
