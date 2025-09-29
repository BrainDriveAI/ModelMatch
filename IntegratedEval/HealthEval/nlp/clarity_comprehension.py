from typing import Tuple
import re

def evaluate(response: str) -> Tuple[float, str]:
    """
    Evaluate Clarity & Comprehension (Metric 4) with optional heuristic.
    Community note: Assesses structure and jargon; judges provide final scores.
    """
    structure_score = 0
    if re.search(r'[\d+\.\-]\s', response): structure_score += 2.5  # Numbered lists
    if re.search(r'[-*•]\s', response): structure_score += 2.5  # Bullets
    jargon_score = 5.0 if not re.search(r'(?i)hypertension|myocardial|pathophysiology', response) else 2.5
    score = (structure_score + jargon_score) / 2
    comment = "Clear and structured." if score > 3 else "Needs better structure."
    return score, comment