"""
Independent Evidence Validation Engine.
Deterministically verifies whether quoted evidence text genuinely exists on the referenced source page.
Uses conservative Unicode normalization (NFKC) and whitespace collapsing while preserving original text.
"""

import unicodedata
import re
from typing import Optional, Tuple, List, Dict, Any
from models.field_record import Evidence, FieldRecord

def normalize_text_for_search(text: str) -> str:
    """
    Applies conservative Unicode NFKC normalization, removes soft hyphens/zero-width characters,
    and collapses consecutive whitespace characters into a single space.
    """
    if not text:
        return ""
    # Unicode NFKC normalization
    normalized = unicodedata.normalize('NFKC', text)
    # Remove zero-width spaces, soft hyphens, and BOM
    normalized = re.sub(r'[\u200b\u200c\u200d\u00ad\ufeff]', '', normalized)
    # Collapse multiple whitespaces/newlines to single space
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized

class EvidenceValidator:
    def __init__(self):
        pass

    def validate_evidence(
        self,
        evidence: Optional[Evidence],
        page_texts: List[Dict[str, Any]],
        document_source_id: str
    ) -> Tuple[bool, float, str]:
        """
        Validates an Evidence record against source document pages.
        Returns:
            (is_verified: bool, match_score: float, diagnostic_note: str)
        """
        if not evidence or not evidence.text or not evidence.text.strip():
            return False, 0.0, "Missing evidence quotation."

        # 1. Validate Source ID
        if evidence.source_id and evidence.source_id != document_source_id:
            return False, 0.0, f"Source ID mismatch: evidence claims '{evidence.source_id}', expected '{document_source_id}'."

        # 2. Validate Page Reference
        total_pages = len(page_texts)
        if evidence.page is None:
            return False, 0.0, "Evidence is missing page number reference."

        if evidence.page < 1 or evidence.page > total_pages:
            return False, 0.0, f"Invalid page reference: page {evidence.page} does not exist in {total_pages}-page document."

        # Find target page text
        target_page_obj = next((p for p in page_texts if p["page_number"] == evidence.page), None)
        if not target_page_obj:
            return False, 0.0, f"Page {evidence.page} text could not be retrieved from source document."

        raw_page_text = target_page_obj["text"]

        # 3. Direct Substring Check (Raw text)
        if evidence.text in raw_page_text:
            return True, 1.0, f"Exact verbatim quotation confirmed on Page {evidence.page}."

        # 4. Normalized Substring Check
        norm_page = normalize_text_for_search(raw_page_text)
        norm_evidence = normalize_text_for_search(evidence.text)

        if norm_evidence in norm_page:
            return True, 1.0, f"Quotation confirmed on Page {evidence.page} (verified via Unicode/whitespace normalization)."

        # Check case-insensitive
        if norm_evidence.lower() in norm_page.lower():
            return True, 0.95, f"Quotation confirmed on Page {evidence.page} (case-folded match)."

        # 5. Token Overlap Check for Long Quotations
        evidence_words = norm_evidence.split()
        if len(evidence_words) >= 5:
            # Check if at least 80% contiguous words exist
            window_size = len(evidence_words)
            page_words = norm_page.split()
            best_overlap = 0
            for i in range(len(page_words) - window_size + 1):
                window = page_words[i:i + window_size]
                common = sum(1 for w1, w2 in zip(evidence_words, window) if w1.lower() == w2.lower())
                if common > best_overlap:
                    best_overlap = common

            ratio = best_overlap / len(evidence_words)
            if ratio >= 0.85:
                return True, round(ratio, 2), f"Substantial quotation overlap ({int(ratio * 100)}%) found on Page {evidence.page}."

        # Check other pages to see if LLM cited the wrong page
        for other_p in page_texts:
            if other_p["page_number"] == evidence.page:
                continue
            if norm_evidence in normalize_text_for_search(other_p["text"]):
                return False, 0.5, f"Quotation found on Page {other_p['page_number']}, but LLM erroneously cited Page {evidence.page}."

        return False, 0.0, f"Evidence quotation not found on Page {evidence.page} in source document."

    def validate_field_records(
        self,
        fields: Dict[str, FieldRecord],
        page_texts: List[Dict[str, Any]],
        document_source_id: str
    ) -> Dict[str, FieldRecord]:
        """
        Validates all fields in a scheme, updating evidence verification status and notes.
        """
        for field_name, record in fields.items():
            if record.status == "found" and record.evidence:
                verified, score, note = self.validate_evidence(
                    record.evidence,
                    page_texts,
                    document_source_id
                )
                record.evidence.verified = verified
                record.evidence.verification_score = score
                record.evidence.verification_note = note
            elif record.status == "not_found":
                # Missing field legitimately has no evidence
                if record.evidence:
                    record.evidence.verified = False
                    record.evidence.verification_note = "Field marked not_found but contains evidence."
        return fields
