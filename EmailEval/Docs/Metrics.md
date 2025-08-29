## Metrics & Math

This document describes the scoring math and key rules for each metric. All scores are on a 0–10 scale unless noted.

### Class Inference (for Length bands)
Heuristic from subject+body keywords maps to one of:
- `transactional`, `promo`, `follow_up`, `support`, `outreach`, `internal_request`

### Length (subject + body)
Formula components:
- Subject length score (0–3): peak at 30–60 chars; soft band 20–80 yields 2; else 1 if non‑empty, else 0
- Body length score (0–7):
  - Ideal band → 7.0
  - Good band → linearly decays toward 4.0 at good edges
  - Outside good → quadratic penalty: `bscore = max(0, 4 - (d/50)^2)` where `d` is distance to nearest good bound
- Total = clamp(subject_score + body_score, 0..10)

Class‑aware bands (words):
- internal_request: ideal 40–100, good 20–150
- follow_up:        ideal 60–110, good 40–160
- outreach:         ideal 90–150, good 60–210
- promo:            ideal 100–180, good 80–220
- transactional:    ideal 60–100, good 40–150
- support:          ideal 80–140, good 50–200

Rationale: Aligns with findings that concise emails increase response rates, with context‑sensitive ranges for different email types (see Research).

### Clarity (LLM‑assisted)
Components (LLM extracts sub‑scores, summed to 0–10):
- Explicit ask (0–5)
- Subject usefulness (0–3)
- Intro clarity (0–2)

LLM returns booleans and a JSON `score_components`. We take the bounded sum as clarity.

### Spam Score (deterministic + LLM lexicon)
Start at 10.0 and subtract penalties:
- Subject ALL CAPS: −2
- Exclamations: subject>1 → −1; total>2 → −1
- Triggers (regex): urgency −1.25, reward −1.5, clickbait −1.0, marketing −0.75 (capped total −6 via this group)
- LLM lexicon counts: weighted penalty = A×0.6 + B×0.35 + C×0.2, capped at −3.0
- Optional HTML text‑image ratio: −2 (if enabled)
- URLs: more than 3 → −1
- Consistency cap: if (urgency or reward or clickbait) and (ALL CAPS or ≥2 exclamations), cap score ≤ 6.0
Clamp to [0,10].

### Personalization (LLM cues + deterministic curve)
Inputs: `cues` list with `{text,type,relevant}` and `too_intrusive` flag.
- Count cues and sum relevance.
- Degree curve (medium best):
  - 0 cues → 3
  - 1 cue → 6 if relevant else 5
  - 2 cues → 9 if ≥1 relevant else 7
  - 3+ cues → 6 (or 5 if intrusive)
- Subject bonus: +1 if a relevant cue text appears in the subject
Clamp to [0,10].

### Tone (LLM flags + deterministic math)
- Base 8.0
- Greeting +0.5 (e.g., Hi/Hello/Good morning)
- Sign‑off +0.5 (e.g., Regards/Best/Thanks)
- ALL CAPS in subject −2
- Exclamations: subject>1 −1; total>2 −1
- Emojis: >1 subtract (count−1)
- LLM flags: `too_aggressive` −1.5; `overly_casual_for_b2b` −0.75; `passive_aggressive_markers` −0.5
- Regex markers: hostile −3.0; passive‑aggressive −1.0 (additional −0.5 each if content is not family‑like)
- Polite markers (please/thanks/appreciate): +min(0.25×count, 0.75)
- Upper cap: if any negative flags present, cap ≤ 9.0
Clamp to [0,10].

### Grammatical Hygiene (LLM‑assisted)
LLM returns JSON: `typos_count`, `grammar_errors[]`, and `score_0_10`. We pass through the numeric score and emit reasons like `typos=N` and joined error hints.

### Weights and Normalization
User inputs are 0–10 per metric. We normalize so the sum of weights equals 6. The weighted total is:

`weighted_total = clamp( sum(weight_i × score_i) / sum(weights), 0..10 )`


