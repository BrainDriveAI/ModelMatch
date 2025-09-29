# core/evaluators.py

import logging
import json
from typing import List
from .schema import HealthEvalInput, HealthEvalOutput
from .providers import JudgeProvider
from .constants import AVAILABLE_JUDGES, DEFAULT_WEIGHTS, METRIC_NAMES


class HealthEvalEvaluator:
    """
    Evaluates conversations against health-related metrics using judge models.
    """

    def __init__(self, judge_provider: JudgeProvider):
        self.judge_provider = judge_provider
        logging.debug("HealthEvalEvaluator initialized with JudgeProvider")

    def evaluate(
        self,
        input_data: HealthEvalInput,
        weights: List[float] = None,
        selected_judges: List[str] = None
    ) -> HealthEvalOutput:
        """
        Run evaluation across selected judges and return aggregated scores.
        """

        if weights is None:
            weights = DEFAULT_WEIGHTS

        if selected_judges is None or len(selected_judges) == 0:
            selected_judges = list(AVAILABLE_JUDGES.keys())

        logging.debug(f"Running evaluation with judges={selected_judges} weights={weights}")

        # Collect results
        model_scores = {}
        for judge in selected_judges:
            judge_model = AVAILABLE_JUDGES[judge]
            raw_response, tokens = self.judge_provider.ask_model(
                model=judge_model,
                query=input_data.query,
                response=input_data.response
            )

            scores, comment = self._parse_model_output(raw_response)

            total_score = (
                sum([s * w for s, w in zip(scores, weights)]) / sum(weights)
                if any(scores) else 0.0
            )

            model_scores[judge] = {
                "response": raw_response,
                "tokens": tokens,
                "scores": scores,
                "total_score": total_score,
                "comment": comment,
            }

        # Build HealthEvalOutput
        output = HealthEvalOutput(
          query=input_data.query,
          weights=weights,
          selected_judges=selected_judges,
          models=model_scores
        )

        logging.debug(f"Evaluation completed: {output}")
        return output

    def _parse_model_output(self, raw_response: str) -> (List[float], str):
        """
        Parse JSON response from model into scores and comment.
        Falls back gracefully if parsing fails.
        """
        try:
            parsed = json.loads(raw_response)

            scores = [
                float(parsed.get("Evidence & Transparency Fit", 0.0)),
                float(parsed.get("Clinical Safety & Escalation", 0.0)),
                float(parsed.get("Empathy & Relationship Quality", 0.0)),
                float(parsed.get("Clarity & Comprehension", 0.0)),
                float(parsed.get("Plan Quality & Behavior Support", 0.0)),
                float(parsed.get("Trust, Explainability & User Agency", 0.0)),
            ]

            comment = parsed.get("Comment", "")
            return scores, comment

        except Exception as e:
            logging.error(f"Failed to parse model output: {e}\nRaw response: {raw_response}")
            return [0.0] * len(METRIC_NAMES), f"Parsing error: {e}. Raw: {raw_response[:200]}..."
