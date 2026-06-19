"""Show calibrated values from baseline evaluation."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.evaluation.startup_scoring_calibration import run_startup_scoring_baseline_calibration

result = run_startup_scoring_baseline_calibration()

best_ai_idx = result.best_ai_candidate_index
if best_ai_idx is not None:
    bc = result.ai_candidates[best_ai_idx]
    print("AI Native best weights (candidate {}):".format(best_ai_idx))
    for k, v in bc.weights.items():
        print("  {}: {}".format(k, v))
    print("  (sum: {:.4f})".format(sum(bc.weights.values())))

best_nv_idx = result.best_nv_candidate_index
if best_nv_idx is not None:
    bc = result.nv_candidates[best_nv_idx]
    print("\nNVIDIA Fit best weights (candidate {}):".format(best_nv_idx))
    for k, v in bc.weights.items():
        print("  {}: {}".format(k, v))
    print("  (sum: {:.4f})".format(sum(bc.weights.values())))

if result.ai_threshold:
    print("\nAI threshold: {}".format(result.ai_threshold.get("threshold")))
if result.nv_threshold:
    print("NV threshold: {}".format(result.nv_threshold.get("threshold")))
if result.ai_uncertainty:
    print("AI uncertainty penalty: {}".format(result.ai_uncertainty.get("best_penalty")))
if result.nv_uncertainty:
    print("NV uncertainty penalty: {}".format(result.nv_uncertainty.get("best_penalty")))
