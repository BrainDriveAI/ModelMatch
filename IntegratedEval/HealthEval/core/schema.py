# core/schema.py

from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime


class HealthEvalInput(BaseModel):
    """
    Input schema for health conversation evaluation.
    """
    query: str = Field(..., description="The human query or conversation context.")
    response: str = Field(..., description="The AI model's response to evaluate.")


class HealthEvalOutput(BaseModel):
    """
    Output schema for health evaluation.
    Stores per-judge results with scores, total score, and comments.
    """
    query: str = Field(..., description="The query text that was evaluated.")
    weights: List[float] = Field(..., min_items=6, max_items=6)
    selected_judges: List[str] = Field(..., description="Judges used for evaluation")
    models: Dict[str, Dict[str, Any]] = Field(
        ..., description="Per-judge evaluation results including scores, total_score, comment, tokens, response"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Example structure of models field:
# {
#   "GPT-4o (OpenAI)": {
#       "response": "... raw model output ...",
#       "tokens": 345,
#       "scores": [4.5, 5.0, 3.8, 4.2, 4.0, 4.1],
#       "total_score": 4.43,
#       "comment": "AI was safe, empathetic, and clear."
#   },
#   "Claude 3.5 Sonnet (Anthropic)": {
#       "response": "... raw model output ...",
#       "tokens": 287,
#       "scores": [...],
#       "total_score": ...,
#       "comment": "..."
#   }
# }
