"""
Cross-source conflict detection engine.
Detects disagreements across multiple ingested sources (e.g. official government PDF vs catalogue listing),
creates ConflictGroup records preserving all source evidence, and flags records for human review.
"""

import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone
from models.scheme import ConflictGroup, ConflictItem, SchemeRecord
from models.field_record import FieldRecord

def normalize_value_for_comparison(field_name: str, value: Optional[str]) -> str:
    """
    Normalizes numeric, currency, and date strings to enable semantic comparison.
    """
    if not value:
        return ""
    val = value.strip().lower()

    if field_name == "benefits":
        # Extract pure digits if monetary
        numbers = re.findall(r'\d+', val.replace(",", ""))
        if numbers:
            return numbers[0]  # e.g. "50000" or "40000"

    if field_name == "deadline":
        # Standardize date separators
        val = val.replace("/", "-").replace(".", "-")
        # Extract YYYY-MM-DD if present
        match = re.search(r'\d{4}-\d{2}-\d{2}', val)
        if match:
            return match.group(0)

    # General text normalization
    return re.sub(r'\s+', ' ', val)

class ConflictDetector:
    def __init__(self):
        pass

    def compare_schemes(
        self,
        primary_scheme: SchemeRecord,
        secondary_scheme: SchemeRecord
    ) -> List[ConflictGroup]:
        """
        Compares two scheme extractions covering the same scheme_ref.
        Returns any detected ConflictGroups.
        """
        if primary_scheme.scheme_ref != secondary_scheme.scheme_ref:
            return []

        conflicts = []
        fields_to_check = set(primary_scheme.fields.keys()).union(secondary_scheme.fields.keys())

        for field_name in fields_to_check:
            f1 = primary_scheme.fields.get(field_name)
            f2 = secondary_scheme.fields.get(field_name)

            if not f1 or not f2:
                continue

            # Only compare if both found a value or one found and one didn't
            val1_raw = f1.value or ""
            val2_raw = f2.value or ""

            norm1 = normalize_value_for_comparison(field_name, val1_raw)
            norm2 = normalize_value_for_comparison(field_name, val2_raw)

            # Check if values conflict
            if norm1 and norm2 and norm1 != norm2:
                conflict_id = f"CONF-{primary_scheme.scheme_ref}-{field_name}"

                item1 = ConflictItem(
                    source_id=primary_scheme.source.source_id,
                    source_name=primary_scheme.source.filename,
                    source_type=primary_scheme.source.source_type,
                    captured_at=primary_scheme.source.captured_at,
                    value=val1_raw,
                    evidence_text=f1.evidence.text if f1.evidence else None,
                    page=f1.evidence.page if f1.evidence else None,
                    section=f1.evidence.section if f1.evidence else None
                )

                item2 = ConflictItem(
                    source_id=secondary_scheme.source.source_id,
                    source_name=secondary_scheme.source.filename,
                    source_type=secondary_scheme.source.source_type,
                    captured_at=secondary_scheme.source.captured_at,
                    value=val2_raw,
                    evidence_text=f2.evidence.text if f2.evidence else None,
                    page=f2.evidence.page if f2.evidence else None,
                    section=f2.evidence.section if f2.evidence else None
                )

                conflicts.append(
                    ConflictGroup(
                        conflict_id=conflict_id,
                        scheme_ref=primary_scheme.scheme_ref,
                        field=field_name,
                        records=[item1, item2],
                        detected_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                        resolved=False
                    )
                )

                # Update status of both field records to 'conflict'
                f1.status = "conflict"
                f2.status = "conflict"
                primary_scheme.approval_status = "conflicted"

        return conflicts
