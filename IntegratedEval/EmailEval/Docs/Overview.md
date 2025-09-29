## Email‑Eval — System Overview

### Purpose
Guide new users to understand how Email‑Eval scores emails across six metrics (clarity, length, spam risk, personalization, tone, grammatical hygiene) and how to interpret results. Outputs include per‑metric scores (0–10), explanations, improvement comments, and exportable CSV/JSON.

### High‑Level Flow
- Input: Subject and Body (plain text)
- Engine: Choose OpenAI or Claude for LLM‑assisted checks
- Weights: Six sliders (0–10). Internally normalized so total effective weight equals 6
- Processing:
  - Preprocess: whitespace normalization, word count, sentence split
  - Infer class (transactional, promo, follow_up, support, outreach, internal_request)
  - Metric scorers run (deterministic + LLM‑assisted)
  - Weighted total computed from normalized weights
- Output:
  - Scores and explanations per metric
  - Short comments per metric
  - Token usage (by engine)
  - CSV and ZIP (CSV + JSON)

### Who Is This For?
- New users evaluating email quality and understanding trade‑offs across metrics
- Researchers benchmarking prompts/models using the exported CSV/JSON
- Developers integrating `evaluate()` into scripts or apps

### What This Is Not
- A text generator. It evaluates existing text.
- A deliverability guarantee. Spam score reflects content/format triggers, not end‑to‑end sender reputation.

### The Six Core Metrics — What and Why
- Clarity: Detects explicit asks, subject usefulness, and intro clarity → clearer purpose improves prioritization and comprehension.
- Length: Scores subject length and body word count against class‑aware bands → concise ranges increase response/CTR depending on type.
- Spam Risk: Penalizes caps/exclamations/trigger phrases/too many URLs and uses safe lexicon counts → reduces content‑based deliverability risks.
- Personalization: Rewards relevant, moderate cues (name/company/role/context) and penalizes intrusive ones → medium level maximizes opens.
- Tone: Encourages greeting/sign‑off and polite markers; discourages caps, excessive exclamations, emojis, passive‑aggressive/hostile language → professional tone alignment.
- Grammatical Hygiene: Surfaces typos and grammar errors with a hygiene score → cleaner copy improves perceived intelligence and trust.

### Weighting — Defaults and Normalization
- Default weights (from `email_eval/config.py`):
  - clarity 9.0, length 7.5, spam_score 8.5, personalization 7.5, tone 7.5, grammatical_hygiene 7.0
- Normalization: inputs are rescaled so their sum equals 6.0
  - scale = 6.0 / sum(raw_weights)
  - normalized_weight[k] = raw_weight[k] × scale (min 0)
- Weighted total:
  - weighted_total = clamp( sum(normalized_weight[k] × score[k]) / sum(normalized_weight), 0..10 )

### Framework — Step by Step (module map)
1) Input capture (Gradio UI in `app.py`): subject, body, engine, raw weights
2) Normalize weights (`api._normalize_weights`) and infer class (`api._infer_class`)
3) Clarity (`clarity_llm.clarity_score`): LLM JSON with ask/subject/intro sub‑scores → 0–10
4) Length (`api._score_length`): subject char length + body word count against class bands (`config.CLASS_BANDS`)
5) Spam (`spam_llm.spam_counts` + `api._score_spam`): tiered lexicon counts + regex triggers + caps/exclam/URLs; optional HTML ratio flag
6) Personalization (`personalization_llm.personalization_flags` + `api._score_personalization`): cues and intrusiveness → medium‑best curve
7) Tone (`tone_llm.tone_flags` + `api._score_tone`): greeting/sign‑off bonuses; caps/exclam/emoji penalties; passive‑aggressive/hostile detection
8) Grammar (`grammar_llm.grammar_score`): LLM returns typos/errors and a hygiene score
9) Aggregate: build `scores`, compute `weighted_total`, compile `explanations`, `comments` (`comments_llm.subjective_comments`), and `usage`
10) Export: CSV and JSON; ZIP bundles both (`app.py`)

### Fallbacks and Safety
- If any LLM step fails, that metric either falls back to heuristics (where available) or returns a conservative default with reason `llm_failed`.
- Spam lexicon avoids profanity lists; only marketing‑style phrases are counted.


### Core Return Shape
- `class`: inferred class string
- `scores`: dict of six metrics on 0–10
- `weighted_total`: overall 0–10
- `explanations`: reasons list per metric (strings)
- `comments`: brief improvement suggestions per metric
- `usage`: token counts per engine and total
- `meta`: engine, normalized weights, version

See `Results.md` for the JSON and CSV field details.

### Engines and Keys
- OpenAI: `OPENAI_API_KEY`
- Claude: `ANTHROPIC_API_KEY`
- Local runs may use `.env` (if `python-dotenv` is present)

### Research‑Grounded Defaults
Design choices follow sources in `Research.md`. Length bands are class‑aware; personalization uses a medium‑is‑best curve; spam risk combines common industry triggers with safe LLM lexicon counts; tone considers greetings/sign‑offs, caps/exclamations/emoji discipline, and passive‑aggressive/hostile markers; grammar scoring is LLM‑assisted hygiene.

Hugging Face Space (Try No Code): [Email‑Eval](https://huggingface.co/spaces/BrainDrive/Email-Eval)


