## Results Format

### JSON (from `evaluate`)
Top‑level keys:
- `class`: inferred email class string
- `scores`: dict
  - `clarity`, `length`, `spam_score`, `personalization`, `tone`, `grammatical_hygiene` → floats (0–10)
- `weighted_total`: float (0–10)
- `explanations`: dict of metric → list[str] explaining rule/flag hits
- `comments`: dict of metric → 1–2 sentence suggestions
- `usage`: dict
  - `openai_total`, `claude_total`, `total`: integer token counts (approx)
- `meta`: dict
  - `engine`: `openai` or `claude`
  - `weights`: normalized weights (sum≈6)
  - `version`: tool version string

### CSV Export
Columns:
- `metric`, `score_0_10`
- Includes a `weighted_total` row at the end

### ZIP Export
Bundled files:
- JSON (identical to `evaluate` output)
- CSV as above

### Notes on Explanations
- Clarity: may include `ask_signals`, `subject_useful`, `intro_clear`, or `llm_failed`
- Length: `subject_len`, `body_wc`, `class`
- Spam: `ALL_CAPS_subject`, `exclam>1_subject`, `exclam_total>2`, `urgency_markers`, `reward_claims`, `clickbait_calls`, `marketing_phrases`, `lexicon_penalty=X`, `too_many_urls=N`
- Personalization: `cues=N`, `relevant=K`, `too_intrusive`
- Tone: `greeting`, `signoff`, `ALL_CAPS_subject`, `exclam>1_subject`, `exclam_total>2`, `emoji_extra=N`, `too_aggressive`, `overly_casual_for_b2b`, `passive_aggressive_phrasing`, `hostile_language`, `polite_markers=N`
- Grammar: `typos=N`, `errors=...` (joined list)


### Top 3 Model Stats (optional aggregation)
If you evaluate multiple generation models (or prompts) on the same email set and aggregate their exported CSV/JSON, report the top 3 by weighted_total.

Recommended fields per model:
- `model_name`
- `mean_weighted_total` (0–10)
- `std_weighted_total`
- `n_samples`
- `mean_scores` per metric (clarity, length, spam_score, personalization, tone, grammatical_hygiene)
- `engine_token_usage` (sum of OpenAI/Claude tokens if applicable)

Example table schema:
- model_name | mean_total | std_total | n | clarity | length | spam | personalization | tone | grammar | tokens

Computation guidance:
- For each model, average `weighted_total` across the evaluation set.
- Also average each metric score to diagnose strengths/weaknesses.
- Break ties by higher mean clarity and lower spam risk.
- Keep the evaluation set fixed across models for fairness.

#### Example (provided run)

Rank | Model Name | Overall Score | Clarity | Length | Spam Risk | Personalization | Tone | Grammar
--- | --- | --- | --- | --- | --- | --- | --- | ---
🥇 1 | Tulu-2-7B (AI2) | 8.89 | 8.33 | 10.00 | 9.80 | 7.00 | 8.25 | 10.00
🥈 2 | StarChat-Beta (Hugging Face H4) | 8.54 | 8.00 | 6.98 | 10.00 | 9.00 | 7.25 | 10.00
🥉 3 | LFM2-1.2B (Lightning AI) | 8.44 | 10.00 | 8.44 | 9.39 | 4.50 | 8.00 | —

Notes:
- Scores are on 0–10. “Overall Score” is `weighted_total` averaged over the shared evaluation set.
- The example reflects one batch evaluation; your results will vary based on emails and weights.


