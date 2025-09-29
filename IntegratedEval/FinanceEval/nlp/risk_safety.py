from .detectors import risk_disclosure_present, diversification_present, overconfidence_hits

def score(text: str):
    rd = risk_disclosure_present(text)
    div = diversification_present(text)
    over = overconfidence_hits(text)

    sub = 0.3*rd + 0.3*div - 0.2*(1 if over>0 else 0)
    sub = max(0.0, min(1.0, sub))
    return {
        'subscore': sub,
        'risk_disclosure_present': rd,
        'diversification_present': div,
        'overconfidence_hits': over,
    }
