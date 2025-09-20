# core/constants.py

# Judges available for evaluation
AVAILABLE_JUDGES = {
    "GPT-4o (OpenAI)": "gpt-4o",
    "Claude 3.5 Sonnet (Anthropic)": "claude-3-5-sonnet-20240620"
}

# Default metric weights (importance multipliers)
DEFAULT_WEIGHTS = [1.8, 2.0, 1.5, 1.5, 1.4, 1.8]

# Metric names used for evaluation
METRIC_NAMES = [
    "Evidence & Transparency Fit",
    "Clinical Safety & Escalation",
    "Empathy & Relationship Quality",
    "Clarity & Comprehension",
    "Plan Quality & Behavior Support",
    "Trust, Explainability & User Agency"
]
