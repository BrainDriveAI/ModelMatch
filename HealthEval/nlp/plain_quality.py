from typing import Tuple

def evaluate(response: str) -> Tuple[float, str]:
    """
    Evaluate Plan Quality & Behavior Support (Metric 5) with optional heuristic.
    Community note: Checks for actionable advice; judges refine the score.
    """
    plan_keywords = ["step", "first", "then", "daily", "how much", "monitor"]
    score = sum(1 for kw in plan_keywords if kw.lower() in response.lower()) * 0.833  # Approx to 5
    score = min(score, 5.0)
    comment = "Provides concrete plan." if score > 3 else "Vague advice."
    return score, comment