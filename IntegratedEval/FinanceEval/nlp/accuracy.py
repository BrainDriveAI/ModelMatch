import re
from .detectors import \
    risk_confidence_ratio

# Minimal deterministic math checks: sum/avg/% and 4% rule flag

PCT_RE = re.compile(r"(\d{1,3}(?:\.\d+)?)\s*%")
NUM_RE = re.compile(r"\b\d+(?:,\d{3})*(?:\.\d+)?\b")


def _calc_error_rate(text: str) -> float:
    # Placeholder: no actual recalculation; we penalize suspicious patterns lightly
    # (You can extend to detect inconsistent sums if you pass structured numbers.)
    return 0.0


def _implausible_return_flag(text: str) -> int:
    t = text.lower()
    if "guaranteed" in t and PCT_RE.search(t):
        val = float(PCT_RE.search(t).group(1))
        return 1 if val >= 12.0 else 0
    return 0


def _unqualified_4pct_flag(text: str) -> int:
    t = text.lower()
    if "4%" in t and ("always" in t or "guaranteed" in t):
        return 1
    return 0


def _omission_penalty(text: str) -> float:
    # If performance touted but no mention of fees/taxes/sequence risk
    t = text.lower()
    perf = ("return" in t or "%" in t)
    hygiene = any(w in t for w in ["fee", "tax", "sequence of returns"])
    return 0.2 if (perf and not hygiene) else 0.0


def score(text: str):
    calc_err = _calc_error_rate(text)
    impl_flag = _implausible_return_flag(text)
    w4_flag = _unqualified_4pct_flag(text)
    omission = _omission_penalty(text)

    sub = 1.0 - calc_err - 0.2*impl_flag - 0.2*w4_flag - 0.1*omission
    sub = max(0.0, min(1.0, sub))
    return {
        'subscore': sub,
        'calc_error_rate': calc_err,
        'implausible_return_flag': impl_flag,
        'unqualified_4pct_flag': w4_flag,
        'omission_penalty': omission,
    }
