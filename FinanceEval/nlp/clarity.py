from .detectors import jargon_density


def _structure_presence(text: str) -> int:
    lines = [l for l in text.splitlines() if l.strip()]
    if not lines:
        return 0
    # Headings or steps indicate structure
    has_head = any(l.strip().endswith(":") for l in lines)
    has_steps = any(l.strip().lower().startswith(tuple(str(i)+"." for i in range(1,6))) for l in lines)
    return 1 if (has_head or has_steps) else 0


def _glossary_coverage(text: str) -> float:
    # heuristic: if parentheses appear after a term, assume explained once
    # This is a placeholder; can be replaced by dictionary lookups and pattern checks
    opens = text.count('(')
    closes = text.count(')')
    pairs = min(opens, closes)
    return min(1.0, pairs / 5.0)


def score(text: str):
    jd = jargon_density(text)
    gc = _glossary_coverage(text)
    sp = _structure_presence(text)

    sub = 0.4*(1 - min(1.0, jd)) + 0.4*gc + 0.2*sp
    sub = max(0.0, min(1.0, sub))
    return {
        'subscore': sub,
        'jargon_density': jd,
        'glossary_coverage': gc,
        'structure_presence': sp,
    }
