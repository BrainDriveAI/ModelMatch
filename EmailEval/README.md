## Email-Eval 📧 — Research-Grounded Email Quality Evaluator

### What is Email-Eval?
Email-Eval evaluates the quality of emails (Subject + Body) across six metrics: clarity, length, spam risk, personalization, tone, and grammatical hygiene. It uses deterministic rules and math, with optional lightweight LLM assistance (OpenAI or Claude), to produce per‑metric scores (0–10), explanations, comments, a weighted total, and downloadable CSV/JSON.

Hugging Face Space: [BrainDrive / Email-Eval](https://huggingface.co/spaces/BrainDrive/Email-Eval)

### What Does It Do?
- Scores six metrics individually (0–10) and returns a weighted total
- Provides explanations and succinct improvement comments per metric
- Class-aware length scoring using research-backed bands
- Spam risk via deterministic triggers plus safe LLM lexicon counts
- CSV and ZIP (CSV + JSON) export for analysis and benchmarking

### How It Works
1) Input: Subject and Body (plain text).
2) Choose Engine: OpenAI or Claude (LLM assistance is optional but recommended).
3) Adjust Weights: Sliders 0–10 for each metric (internally normalized).
4) Run: The app computes metric scores, explanations, and comments.
5) Output: View table, comments, token usage, and download CSV/ZIP.

### Scoring Criteria (High‑Level)
- Clarity: LLM-based ask detection, subject usefulness, and intro clarity (0–10).
- Length: Subject length + body word-count relative to class bands (0–10).
- Spam Score: Starts at 10, minus penalties for ALL CAPS, exclamations, urgency/reward/clickbait/marketing markers, excessive URLs, and optional lexicon counts.
- Personalization: LLM-detected cues scored on a "medium is best" curve; overly intrusive cues reduce score.
- Tone: Greeting/sign-off bonuses; penalties for ALL CAPS, exclamation overuse, emojis, passive-aggressive/hostile phrasing; polite markers grant small bonuses.
- Grammatical Hygiene: LLM returns typos/error list and a hygiene score (0–10).

For detailed math, bands, and rule lists, see `Docs/Metrics.md` and `Docs/Research.md`.

### Features ✨
- Deterministic math with optional LLM assistance
- Research‑grounded defaults and class‑aware length bands
- Export to CSV/JSON for analysis and ranking
- Lightweight, runs locally or on Spaces

### Installation 🔧
```bash
cd EmailEval
pip install -r requirements.txt
```

### Environment Variables (LLM engines)
Set the keys for the engine you plan to use:
```bash
export OPENAI_API_KEY="..."
export ANTHROPIC_API_KEY="..."
```
Optionally place them in a `.env` file (loaded if `python-dotenv` is available).

### Run Locally
```bash
python3 app.py
```
The app starts on `http://localhost:7860` by default. Override with `PORT` if needed:
```bash
PORT=7860 python3 app.py
```

### Project Structure
```
email-eval/
  app.py                 # Gradio app entrypoint (HF Space compatible)
  email_eval/            # Evaluator modules
    api.py               # Main evaluate() and metric aggregation
    config.py            # Default weights, length bands, spam tier weights
    preprocess.py        # Normalization, tokenization helpers
    rules.py             # Regex patterns for asks, tone, spam triggers
    clarity_llm.py       # LLM-assisted clarity scoring
    grammar_llm.py       # LLM-assisted grammar hygiene
    personalization_llm.py # LLM cue extraction
    tone_llm.py          # LLM tone flags
    spam_llm.py          # LLM tiered spam lexicon counts
    comments_llm.py      # Subjective comments (LLM with heuristic fallback)
  Docs/                  # Documentation (see Docs/README.md)
  requirements.txt
  README.md
  .gitignore
```

### Privacy & Keys
- Inputs are processed in‑memory by the app.
- If you enable LLM assistance, text is sent to the selected provider (OpenAI/Anthropic) for scoring prompts.
- Provide API keys via env vars or `.env`. Remove keys before sharing.

### Troubleshooting
- Missing keys: set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`.
- No output/blank comments: try switching engine or check network access.
- Scores look capped: see `Docs/Metrics.md` for caps and penalty rules.

### Contributing
- Open issues for bugs or documentation gaps.
- When changing scoring, update `Docs/Metrics.md` and cite sources in `Docs/Research.md`.
- Keep outputs backward‑compatible (`Docs/Results.md`).
- Join [BrainDrive Community](https://community.braindrive.ai) to share results.

### Outputs
- Scores tab: metric-wise scores (0–10) and weighted total
- Comments tab: improvement suggestions per metric
- Usage tab: approximate token usage (OpenAI/Claude)
- Downloads: CSV and ZIP (CSV + JSON)

See `Docs/Results.md` for JSON fields and CSV layout.

### Research References
This tool’s metric design and defaults are grounded in published findings on clarity, concise length ranges, spam triggers, personalization efficacy, tone, and grammar perception. A curated synthesis is provided in `Docs/Research.md`.



