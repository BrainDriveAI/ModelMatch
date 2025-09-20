# NLP modules for individual HealthEval metrics (optional for heuristics)
# Community note: Main evaluation via judges in evaluators.py; these for fallback or hybrid if needed.
from .evidence_transparency import evaluate
from .clinical_safety import evaluate
from .empathy_quality import evaluate
from .clarity_comprehension import evaluate
from .plan_quality import evaluate
from .trust_agency import evaluate