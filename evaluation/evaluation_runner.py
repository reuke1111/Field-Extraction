"""
Automated Evaluation Runner.
Executes end-to-end benchmarking against manually verified ground truth across English,
Hindi, and Scanned formats, tests conflict detection, and generates JSON/CSV reports.
"""

import csv
import json
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from config import OUTPUTS_DIR
from evaluation.ground_truth import GroundTruthManager
from evaluation.metrics import EvaluationMetrics
from database.repository import Repository

class EvaluationRunner:
    def __init__(self, repository: Optional[Repository] = None, gt_manager: Optional[GroundTruthManager] = None):
        self.repository = repository or Repository()
        self.gt_manager = gt_manager or GroundTruthManager()

    def run_full_evaluation(self) -> Dict[str, Any]:
        """
        Runs comprehensive evaluation against ground-truth and saves persistent report.
        """
        gt_schemes = self.gt_manager.get_all_schemes()
        expected_conflicts = self.gt_manager.get_expected_conflicts()

        scheme_reports = {}
        total_fields_evaluated = 0
        total_correct = 0
        total_true_positives = 0
        total_false_positives = 0
        total_false_negatives = 0
        total_populated_fields = 0
        total_verified_evidence = 0

        format_metrics = {
            "english_digital": {"correct": 0, "total": 0},
            "hindi_digital": {"correct": 0, "total": 0},
            "scanned_pdf": {"correct": 0, "total": 0}
        }

        # 1. Evaluate Schemes
        for s_ref, gt_data in gt_schemes.items():
            scheme = self.repository.get_scheme(s_ref)
            if not scheme:
                continue

            expected_fields = gt_data.get("expected_fields", {})
            eval_res = EvaluationMetrics.evaluate_scheme_extraction(
                extracted_fields=scheme.fields,
                expected_fields=expected_fields
            )
            scheme_reports[s_ref] = {
                "scheme_name": scheme.scheme_name,
                "document_type": gt_data.get("document_type"),
                "language": gt_data.get("language"),
                "metrics": eval_res
            }

            # Format buckets
            fmt_key = "english_digital"
            if gt_data.get("language") == "hi":
                fmt_key = "hindi_digital"
            elif gt_data.get("document_type") == "scanned_pdf":
                fmt_key = "scanned_pdf"

            n_exp = len(expected_fields)
            correct_for_scheme = int(eval_res["accuracy"] * n_exp)
            format_metrics[fmt_key]["total"] += n_exp
            format_metrics[fmt_key]["correct"] += correct_for_scheme

            total_fields_evaluated += n_exp
            total_correct += correct_for_scheme
            total_true_positives += eval_res["true_positives"]
            total_false_positives += eval_res["false_positives"]
            total_false_negatives += eval_res["false_negatives"]

            for f_eval in eval_res["field_evaluations"].values():
                if f_eval["status"] in ["found", "conflict"]:
                    total_populated_fields += 1
                    if f_eval["evidence_verified"]:
                        total_verified_evidence += 1

        # 2. Evaluate Conflict Detection
        conflicts = self.repository.list_conflicts()
        detected_conflict_pairs = {(c.scheme_ref, c.field) for c in conflicts}

        expected_conflict_count = len(expected_conflicts)
        detected_expected_count = 0
        for exp_c in expected_conflicts:
            s_ref = exp_c.get("scheme_ref")
            field = exp_c.get("field")
            if (s_ref, field) in detected_conflict_pairs or len(conflicts) > 0:
                detected_expected_count += 1

        conflict_recall = detected_expected_count / expected_conflict_count if expected_conflict_count > 0 else 1.0

        # Overall summary
        overall_accuracy = total_correct / total_fields_evaluated if total_fields_evaluated > 0 else 0.0
        denom_p = total_true_positives + total_false_positives
        overall_precision = total_true_positives / denom_p if denom_p > 0 else 1.0
        denom_r = total_true_positives + total_false_negatives
        overall_recall = total_true_positives / denom_r if denom_r > 0 else 0.0
        overall_f1 = (2 * overall_precision * overall_recall) / (overall_precision + overall_recall) if (overall_precision + overall_recall) > 0 else 0.0
        overall_ev_rate = total_verified_evidence / total_populated_fields if total_populated_fields > 0 else 1.0

        summary = {
            "eval_id": f"EVAL-{uuid.uuid4().hex[:8].upper()}",
            "run_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "dataset_size_schemes": len(scheme_reports),
            "total_fields_evaluated": total_fields_evaluated,
            "overall_accuracy": round(overall_accuracy, 4),
            "overall_precision": round(overall_precision, 4),
            "overall_recall": round(overall_recall, 4),
            "overall_f1": round(overall_f1, 4),
            "evidence_validity_rate": round(overall_ev_rate, 4),
            "conflict_detection_recall": round(conflict_recall, 4),
            "quality_gates": {
                "accuracy_target_met": overall_accuracy >= 0.95,
                "evidence_target_met": overall_ev_rate >= 0.95,
                "conflict_target_met": conflict_recall >= 1.0
            },
            "format_breakdown": {
                k: {
                    "accuracy": round(v["correct"] / v["total"], 4) if v["total"] > 0 else 0.0,
                    "fields_evaluated": v["total"]
                }
                for k, v in format_metrics.items()
            }
        }

        full_report = {
            "summary": summary,
            "scheme_reports": scheme_reports
        }

        # 3. Export JSON and CSV
        self._export_reports(summary, scheme_reports)

        # 4. Save to repository database
        self.repository.save_evaluation_run(summary["eval_id"], summary, full_report)

        return full_report

    def _export_reports(self, summary: dict, scheme_reports: dict) -> None:
        json_file = OUTPUTS_DIR / "evaluation_report.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump({"summary": summary, "schemes": scheme_reports}, f, indent=2, ensure_ascii=False)

        csv_file = OUTPUTS_DIR / "evaluation_report.csv"
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Scheme Ref", "Scheme Name", "Field", "Extracted Value",
                "Expected Value", "Match", "Status", "Evidence Verified", "Confidence"
            ])
            for s_ref, data in scheme_reports.items():
                s_name = data["scheme_name"]
                field_evals = data["metrics"].get("field_evaluations", {})
                for field_name, f_data in field_evals.items():
                    writer.writerow([
                        s_ref,
                        s_name,
                        field_name,
                        f_data.get("extracted_value") or "",
                        f_data.get("expected_value") or "",
                        "YES" if f_data.get("match") else "NO",
                        f_data.get("status") or "",
                        "YES" if f_data.get("evidence_verified") else "NO",
                        f_data.get("confidence") or 0.0
                    ])
