from .detectors import risk_readability_index

CAUSAL_MARKERS = {"because", "therefore", "due to", "hence", "so that", "as a result"}


def _causal_count(text: str) -> int:
    t = text.lower()
    return sum(t.count(w) for w in CAUSAL_MARKERS)


def _has_structure(text: str) -> int:
    t = text.strip().lower()
    # simple heuristic: numbered or bulleted lines
    lines = [l for l in t.splitlines() if l]
    has_num = any(l.lstrip().startswith(tuple(str(i)+"." for i in range(1,6))) for l in lines)
    has_dash = any(l.lstrip().startswith(('-', '*', '•')) for l in lines)
    return 1 if (has_num or has_dash) else 0


def score(text: str):
    c = _causal_count(text)
    structured = _has_structure(text)
    rr = risk_readability_index(text)
    # normalize causal markers roughly assuming 0..10 scale
    norm_causal = min(1.0, c / 10.0)
    # risk complexity: map grade 0..20 to 0..1
    risk_complexity = min(1.0, rr / 20.0)

    sub = 0.4*norm_causal + 0.3*structured + 0.3*(1.0 - risk_complexity)
    sub = max(0.0, min(1.0, sub))
    return {
        'subscore': sub,
        'causal_markers': c,
        'has_structure': structured,
        'risk_readability_grade': rr,
    }
