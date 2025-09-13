from .detectors import personalization_density, fiduciary_flag, product_push_penalty

def score(text: str):
    pd = personalization_density(text)
    fid = fiduciary_flag(text)
    ppush = product_push_penalty(text)

    sub = 0.35*pd + 0.25*fid + 0.25*(1 if fid else 0) - 0.25*ppush
    sub = max(0.0, min(1.0, sub))
    return {
        'subscore': sub,
        'personalization_density': pd,
        'fiduciary_flag': fid,
        'product_push_penalty': ppush,
    }
