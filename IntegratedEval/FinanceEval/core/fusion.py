# core/fusion.py (simplified: no fusion, just pass-through)

from typing import Dict

def normalize_llm_score(judge_score) -> float:
    """
    Convert LLM score (1–5) into 0–10 scale.
    If None, return 0.
    """
    if judge_score is None:
        return 0.0
    try:
        return round(max(0.0, min(5.0, float(judge_score))) * 2.0, 2)
    except Exception:
        return 0.0

def weighted_total(metric_scores_0_10: Dict[str, float], weights: Dict[str, float]) -> float:
    tot = 0.0
    for k, v in metric_scores_0_10.items():
        w = weights.get(k, 0.0)
        tot += (v or 0.0) * w
    return round(tot, 2)
