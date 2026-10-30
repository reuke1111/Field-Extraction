"""
Evaluation metrics calculator for field extraction, evidence verification, and conflict detection.
Handles null values, missing fields, and empty datasets cleanly.
"""

import re
from typing import Dict, Any, List, Optional
from models.field_record import FieldRecord

def normalize_text_for_eval(text: Optional[str]) -> str:
    if not text:
        return ""
    # Strip commas from numbers, then strip whitespace, lower, remove punctuation
    t = str(text).replace(",", "").replace("₹", "").replace("Rs", "").replace("rs", "")
    t = re.sub(r'[$:;/()\-•\n]', ' ', t).strip().lower()
    return re.sub(r'\s+', ' ', t)

def is_field_match(field_name: str, extracted_val: Optional[str], expected_val: Optional[str]) -> bool:
    """
    Evaluates whether an extracted field matches ground truth value.
    Supports semantic matching for amounts, dates, names, and descriptive criteria.
    """
    if extracted_val is None and expected_val is None:
        return True
    if extracted_val is None or expected_val is None:
        return False

    norm_ext = normalize_text_for_eval(extracted_val)
    norm_exp = normalize_text_for_eval(expected_val)

    # 1. Exact normalized match
    if norm_ext == norm_exp:
        return True

    # 2. Benefits: check if extracted digits match expected amount digits
    if field_name == "benefits":
        ext_digits = re.findall(r'\d+', norm_ext)
        exp_digits = re.findall(r'\d+', norm_exp)
        if ext_digits and exp_digits and ext_digits[0] == exp_digits[0]:
            return True

    # 3. Substring containment
    if norm_exp in norm_ext or norm_ext in norm_exp:
        return True

    # 4. Token Overlap for multi-word descriptions (eligibility, documents, procedure)
    tokens_ext = set(norm_ext.split())
    tokens_exp = set(norm_exp.split())
    if tokens_ext and tokens_exp:
        intersection = tokens_ext.intersection(tokens_exp)
        union = tokens_ext.union(tokens_exp)
        jaccard = len(intersection) / len(union) if union else 0.0
        overlap_exp = len(intersection) / len(tokens_exp) if tokens_exp else 0.0
        if jaccard >= 0.40 or overlap_exp >= 0.60:
            return True

    return False

class EvaluationMetrics:
    @staticmethod
    def evaluate_scheme_extraction(
        extracted_fields: Dict[str, FieldRecord],
        expected_fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculates field-level accuracy, precision, recall, and evidence validity for a single scheme.
        """
        total_expected = len(expected_fields)
        if total_expected == 0:
            return {
                "accuracy": 0.0,
                "precision": 0.0,
                "recall": 0.0,
                "f1_score": 0.0,
                "evidence_validity_rate": 0.0,
                "field_evaluations": {}
            }

        true_positives = 0
        false_positives = 0
        false_negatives = 0
        true_negatives = 0
        evidence_verified_count = 0
        populated_count = 0

        field_evaluations = {}

        for field_name, exp_data in expected_fields.items():
            exp_val = exp_data.get("value")
            exp_status = exp_data.get("status", "found")
            ext_record = extracted_fields.get(field_name)

            ext_val = ext_record.value if ext_record else None
            ext_status = ext_record.status if ext_record else "not_found"
            ev_verified = (ext_record.evidence.verified if (ext_record and ext_record.evidence) else False)

            is_match = is_field_match(field_name, ext_val, exp_val)

            if exp_status == "found":
                if ext_status in ["found", "conflict"] and is_match:
                    true_positives += 1
                elif ext_status in ["found", "conflict"] and not is_match:
                    false_positives += 1
                else:
                    false_negatives += 1
            else:
                # Expected not_found
                if ext_status == "not_found":
                    true_negatives += 1
                else:
                    false_positives += 1

            if ext_status in ["found", "conflict"]:
                populated_count += 1
                if ev_verified:
                    evidence_verified_count += 1

            field_evaluations[field_name] = {
                "extracted_value": ext_val,
                "expected_value": exp_val,
                "match": is_match,
                "status": ext_status,
                "evidence_verified": ev_verified,
                "confidence": ext_record.confidence if ext_record else 0.0
            }

        # Calculations
        correct_predictions = true_positives + true_negatives
        accuracy = correct_predictions / total_expected if total_expected > 0 else 0.0

        denom_p = (true_positives + false_positives)
        precision = true_positives / denom_p if denom_p > 0 else 1.0

        denom_r = (true_positives + false_negatives)
        recall = true_positives / denom_r if denom_r > 0 else 0.0

        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        ev_rate = evidence_verified_count / populated_count if populated_count > 0 else 1.0

        return {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "evidence_validity_rate": round(ev_rate, 4),
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "field_evaluations": field_evaluations
        }
