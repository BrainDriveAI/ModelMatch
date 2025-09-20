from typing import List
import numpy as np
from .schema import HealthEvalOutput

class ScoreFusion:
    @staticmethod
    def compute_total_score(scores: List[float], weights: List[float]) -> float:
        if sum(weights) == 0:
            return 0.0
        return np.average(scores, weights=weights)

    @staticmethod
    def aggregate_evaluations(outputs: List[HealthEvalOutput], method: str = "average") -> HealthEvalOutput:
        if method == "average":
            avg_scores = np.mean([o.scores for o in outputs], axis=0).tolist()
            avg_total = np.mean([o.total_score for o in outputs])
            return HealthEvalOutput(scores=avg_scores, total_score=avg_total, comment="Aggregated")
        return outputs[0] if outputs else HealthEvalOutput()