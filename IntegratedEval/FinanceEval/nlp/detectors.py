import re, math
from typing import List, Dict

LOWER = lambda s: (s or "").lower()

HEDGING = {
    "may", "might", "could", "possibly", "likely", "uncertain", "approx", "around"
}
ABSOLUTES = {
    "guaranteed", "risk-free", "always", "never", "certain", "100%", "will absolutely"
}
RISK_TERMS = {
    "volatility", "drawdown", "inflation", "credit risk", "liquidity", "default", "market risk"
}
DIVERSIFY_TERMS = {"diversify", "diversification", "spread across", "asset allocation"}
PRODUCT_PUSH = {"our fund", "proprietary", "exclusive product", "sign up", "click here"}
FIDUCIARY_TERMS = {"in your best interest", "suitable given", "fiduciary"}
PERSONAL_TERMS = {"your income", "your goals", "your family", "your age", "your debts", "time horizon"}
DISCLOSURE_LEADS = {"disclosure", "warning", "important", "note:"}

FINANCE_JARGON = {
    "alpha", "beta", "sharpe", "sortino", "duration", "convexity", "basis points",
    "drawdown", "liquidity", "hedge", "derivative", "yield curve", "contango", "backwardation",
    "terminal value", "cap rate", "wacc", "ebitda", "cagr", "irr", "annuity", "treasury spread"
}

def count_terms(text: str, vocab: set) -> int:
    t = LOWER(text)
    n = 0
    for term in vocab:
        n += t.count(term)
    return n


def disclaimer_present(text: str) -> int:
    t = LOWER(text)
    if "disclaimer" in t or "this is not financial advice" in t:
        return 1
    return 0


def disclaimer_position(text: str) -> str:
    t = LOWER(text)
    if t.startswith("disclaimer") or t.startswith("warning"):
        return "start"
    if "disclaimer" in t or "warning" in t:
        return "middle"
    return "end"


def risk_confidence_ratio(text: str) -> float:
    h = count_terms(text, HEDGING)
    a = count_terms(text, ABSOLUTES)
    if (h + a) == 0:
        return 0.5
    return h / float(h + a)


def overconfidence_hits(text: str) -> int:
    return count_terms(text, ABSOLUTES)


def conflict_terms_present(text: str) -> int:
    return 1 if count_terms(text, PRODUCT_PUSH) > 0 else 0


def risk_disclosure_present(text: str) -> int:
    return 1 if count_terms(text, RISK_TERMS) > 0 else 0


def diversification_present(text: str) -> int:
    return 1 if count_terms(text, DIVERSIFY_TERMS) > 0 else 0


def personalization_density(text: str) -> float:
    words = max(1, len(text.split()))
    hits = count_terms(text, PERSONAL_TERMS)
    return min(1.0, hits / max(1.0, words / 200.0))  # crude density per ~200 words


def fiduciary_flag(text: str) -> int:
    return 1 if count_terms(text, FIDUCIARY_TERMS) > 0 else 0


def product_push_penalty(text: str) -> int:
    return 1 if count_terms(text, PRODUCT_PUSH) > 0 else 0


def jargon_density(text: str) -> float:
    words = max(1, len(text.split()))
    hits = count_terms(text, FINANCE_JARGON)
    return min(1.0, hits / max(1.0, words))

# Readability proxy (FKGL). If textstat is available, use it; else crude proxy.
try:
    import textstat
    def risk_readability_index(text: str) -> float:
        try:
            score = textstat.flesch_kincaid_grade(text)
            return max(0.0, min(20.0, float(score)))
        except Exception:
            return 12.0
except Exception:
    def risk_readability_index(text: str) -> float:
        # very rough: sentence length proxy
        sents = max(1, text.count('.') + text.count('!') + text.count('?'))
        words = max(1, len(text.split()))
        avg = words / sents
        # map avg 10->12 grade roughly
        return max(0.0, min(20.0, 0.8 * avg))
