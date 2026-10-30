"""
Transparent heuristic confidence calculation engine.
Separates model confidence from deterministic evidence validity.
Incorporates evidence verification, OCR source type, and extraction completeness.
"""

from typing import Optional
from models.field_record import FieldRecord

class ConfidenceCalculator:
    """
    Computes transparent, explainable confidence scores for extracted fields.
    Note: Confidence scores are heuristic until calibrated against a large empirical dataset.
    """

    @staticmethod
    def calculate_field_confidence(
        record: FieldRecord,
        is_scanned_page: bool = False,
        base_model_confidence: Optional[float] = None
    ) -> float:
        """
        Calculates a composite confidence score [0.0 - 1.0].
        """
        # If field is legitimately not found, model confidence reflects certainty of absence
        if record.status == "not_found":
            return round(base_model_confidence or 0.85, 2)

        # Base confidence from model
        score = base_model_confidence if base_model_confidence is not None else 0.90

        # OCR penalty: scanned text introduces character noise
        if is_scanned_page:
            score *= 0.88

        # Evidence verification penalty (HEAVIEST FACTOR)
        if record.evidence:
            if not record.evidence.verified:
                # If quotation cannot be verified on the page, drastically lower confidence
                score = min(score * 0.40, 0.45)
            else:
                # Boost slightly by verification score
                score = min(1.0, score * (0.85 + 0.15 * record.evidence.verification_score))
        else:
            # Populated field with no evidence quotation at all
            score = 0.20

        # Completeness check: empty value for 'found' status
        if not record.value or not record.value.strip():
            score = 0.10

        return max(0.0, min(1.0, round(score, 2)))

    @staticmethod
    def needs_human_review(record: FieldRecord, threshold: float = 0.85) -> bool:
        """
        Determines whether a field requires mandatory researcher inspection.
        """
        if record.status == "conflict":
            return True
        if record.status == "found":
            if not record.evidence or not record.evidence.verified:
                return True
            if record.confidence < threshold:
                return True
        return False
