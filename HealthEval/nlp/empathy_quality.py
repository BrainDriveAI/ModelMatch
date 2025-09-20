from typing import Tuple

def evaluate(response: str) -> Tuple[float, str]:
    """
    Evaluate Empathy & Relationship Quality (Metric 3) with optional heuristic.
    Community note: Keyword-based empathy check; judges handle detailed scoring.
    """
    empathy_keywords = ["I understand", "I'm sorry", "That sounds", "Let's work", "Your feelings"]
    score = sum(1 for kw in empathy_keywords if kw.lower() in response.lower()) * 1.0
    score = min(score, 5.0)
    comment = "Shows empathy." if score > 2.5 else "Limited empathy."
    return score, comment