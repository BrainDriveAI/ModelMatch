from .detectors import (
    disclaimer_present, disclaimer_position, risk_confidence_ratio,
    overconfidence_hits, conflict_terms_present
)

def score(text: str):
    dp = disclaimer_present(text)
    pos = disclaimer_position(text)
    early = 1 if pos == 'start' else 0
    rcr = risk_confidence_ratio(text)
    over = overconfidence_hits(text)
    conflict = conflict_terms_present(text)

    sub = 0.4*dp + 0.2*early + 0.2*min(1.0, rcr) - 0.2*(1 if over>0 else 0) - 0.1*conflict
    sub = max(0.0, min(1.0, sub))
    return {
        'subscore': sub,
        'disclaimer_present': dp,
        'disclaimer_early': early,
        'risk_confidence_ratio': rcr,
        'overconfidence_hits': over,
        'conflict_terms_present': conflict,
    }
