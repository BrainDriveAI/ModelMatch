from typing import Tuple
import re

def evaluate(response: str) -> Tuple[float, str]:
    """
    Evaluate Trust, Explainability & User Agency (Metric 6) with optional heuristic.
    Community note: Detects reasoning/choices; judges provide detailed evaluation.
    """
    trust_cues = [
        r"(?i)because|since|evidence suggests",
        r"(?i)you can choose|options|prefer|decide"
    ]
    matches = sum(1 for cue in trust_cues if re.search(cue, response))
    score = (matches / len(trust_cues)) * 5
    comment = "Explains and empowers user." if matches > 1 else "Lacks explainability."
    return float(score), comment