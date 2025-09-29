# Class-aware length bands grounded in your research synthesis (response: 50–125; CTR: 100–200; balanced ~100). :contentReference[oaicite:1]{index=1}
CLASS_BANDS = {
  "internal_request": {"ideal": (40,100), "good": (20,150), "subj": (30,60)},  # Lowered for concise emails
  "follow_up":        {"ideal": (60,110), "good": (40,160), "subj": (28,55)},
  "outreach":         {"ideal": (90,150), "good": (60,210), "subj": (30,60)},
  "promo":            {"ideal": (100,180),"good": (80,220), "subj": (30,60)},
  "transactional":    {"ideal": (60,100), "good": (40,150), "subj": (25,55)},
  "support":          {"ideal": (80,140), "good": (50,200), "subj": (28,55)},
}

# Weights (0–10 scale). Higher for clarity & spam per findings; strong but secondary for length, tone, grammar, personalization. :contentReference[oaicite:2]{index=2}
DEFAULT_WEIGHT_PRESETS = {
  "research_defaults": {
    "clarity": 9.0,               # clarity/actionability shows largest lift in comprehension & perceived quality
    "length": 7.5,                # concise bands improve response; class-aware bands applied
    "spam_score": 8.5,            # content triggers accumulate, hurting deliverability
    "personalization": 7.5,       # medium level best; avoid heavy
    "tone": 7.5,                  # greeting/sign-off, caps/exclaim/emoji discipline, polite markers
    "grammatical_hygiene": 7.0    # typos/grammos reduce perceived writer quality
  }
}

# Spam tier weights (marketing-y phrases only; no profanity)
SPAM_TIER_WEIGHTS = {"A": 0.6, "B": 0.35, "C": 0.2}