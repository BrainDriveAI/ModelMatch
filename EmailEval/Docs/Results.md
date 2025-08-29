### Top 3 Model Stats (Winners for Email Gen)

Computation guidance:
- For each model, average `weighted_total` across the evaluation set.
- Also average each metric score to diagnose strengths/weaknesses.
- Break ties by higher mean clarity and lower spam risk.
- Keep the evaluation set fixed across models for fairness.

Rank | Model Name | Overall Score | Clarity | Length | Spam Score | Personalization | Tone | Grammatical Hygiene
--- | --- | --- | --- | --- | --- | --- | --- | ---
🥇 1 | Tulu-2-7B (AI2) | 8.89 | 8.33 | 10.00 | 9.80 | 7.00 | 8.25 | 10.00
🥈 2 | StarChat-Beta (Hugging Face H4) | 8.54 | 8.00 | 6.98 | 10.00 | 9.00 | 7.25 | 10.00
🥉 3 | LFM2-1.2B (Lightning AI) | 8.44 | 10.00 | 8.44 | 9.39 | 4.50 | 8.00 | 10.00

Notes:
- Scores are on 0–10. “Overall Score” is `weighted_total` averaged over the shared evaluation set.
- The example reflects one batch evaluation; your results will vary based on emails and weights.


