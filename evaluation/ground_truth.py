"""
Ground truth loader and manager.
Reads manually verified reference datasets from synthetic_data/ground_truth.json.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from config import SYNTHETIC_DATA_DIR

class GroundTruthManager:
    def __init__(self, gt_path: Optional[str] = None):
        self.gt_path = Path(gt_path) if gt_path else (SYNTHETIC_DATA_DIR / "ground_truth.json")
        self._data = self._load()

    def _load(self) -> Dict[str, Any]:
        if not self.gt_path.exists():
            raise FileNotFoundError(f"Ground truth dataset not found at: {self.gt_path}")
        with open(self.gt_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_scheme_ground_truth(self, scheme_ref: str) -> Optional[Dict[str, Any]]:
        return self._data.get("schemes", {}).get(scheme_ref)

    def get_all_schemes(self) -> Dict[str, Any]:
        return self._data.get("schemes", {})

    def get_expected_conflicts(self) -> list:
        return self._data.get("conflicts", [])
