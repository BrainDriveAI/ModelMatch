# FinanceEval 💰 

## What is FinanceEval?

FinanceEval assesses the quality of financial advice given by a model to a human across six metrics: Trust & Transparency, Competence & Accuracy, Explainability, Client-Centeredness/Fiduciary Alignment, Bias-Sensitivity & Risk Safety, and Financial Literacy Support/Communication Clarity. It combines deterministic rules, math, and LLM/NLP hybrid evaluation to produce per-metric scores (1–5), explanations, and a JSON output.

## Hugging Face Space

FinanceEval Space

## What Does It Do?

- Evaluates financial advice across six research-backed metrics.
- Provides detailed scores (1–10) with evidence and reasoning.
- Generates a structured JSON output for each evaluation run.
- Supports analysis across sub-domains like Budgeting, Investments, and Retirement Planning.

## How It Works

- **Input:** Plain text financial advice transcript.
- **Process:** Select evaluation sub-domain, run with default or custom weights.
- **Output:** JSON with metric scores, flags, evidence, and reasoning.

👉 Try it live: [FinanceEval on Hugging Face Spaces](https://huggingface.co/spaces/BrainDrive/FinanceEval)

## Scoring Criteria (High-Level)

- **Trust & Transparency:** Assesses honesty, risk disclosures, and balanced tone.
- **Competence & Accuracy:** Checks numeric accuracy and semantic plausibility.
- **Explainability:** Evaluates clarity and causal reasoning in advice.
- **Client-Centeredness/Fiduciary Alignment:** Measures personalization and conflict handling.
- **Bias-Sensitivity & Risk Safety:** Detects biases and ensures risk disclosures.
- **Financial Literacy Support/Communication Clarity:** Gauges jargon use and teaching clarity.

## Features ✨

- Research-grounded metric design.
- Hybrid LLM/NLP evaluation framework.
- Supports multiple finance sub-domains.
- JSON output for detailed analysis.

## Installation 🔧

```bash
cd FinanceEval
pip install -r requirements.txt
```

---

## Environment Variables (API Keys)

FinanceEval can use LLM assistance from **OpenAI** or **Anthropic**.  
Set your keys before running the app:

### macOS / Linux (bash/zsh)

```bash
export OPENAI_API_KEY="your_openai_key_here"
export ANTHROPIC_API_KEY="your_anthropic_key_here"
```

### Windows (PowerShell)

```powershell
setx OPENAI_API_KEY "your_openai_key_here"
setx ANTHROPIC_API_KEY "your_anthropic_key_here"
```


## Run Locally

```bash
python3 app.py
```

The app starts on [http://localhost:7860](http://localhost:7860) by default.

---

## Project Structure

```
financeeval/
├── app.py            # Gradio app entrypoint
├── core/             # Core evaluation logic
│   ├── providers.py
│   ├── preprocess.py
│   ├── evaluators.py
│   ├── fusion.py
│   └── schema.py
├── nlp/              # NLP modules
│   ├── detectors.py
│   ├── trust.py
│   ├── accuracy.py
│   ├── explain.py
│   ├── client_first.py
│   ├── risk_safety.py
│   └── clarity.py
├── prompts/          # LLM prompts
│   ├── trust.txt
│   ├── accuracy.txt
│   ├── explain.txt
│   ├── client_first.txt
│   ├── risk_safety.txt
│   └── clarity.txt
├── schema/           # Output schema
│   └── output_schema.json
├── tests/            # Test data
│   ├── redteam_inputs.jsonl
│   └── golden_outputs.json
├── requirements.txt
└── README.md
```

## Privacy & Keys

Inputs are processed in-memory. LLM usage requires API keys set via environment variables or .env file. Remove keys before sharing.

## Troubleshooting

- Missing output: Check LLM API connectivity.
- Low scores: Review metric definitions in the document.

## Outputs

- JSON with metric scores and reasoning.
- Detailed evaluation per metric.

## Research and Documentation

For detailed knowledge about the FinanceEval evaluation framework, metric design, research grounding, and reporting outputs, please refer to the Docs folder:

👉 [FinanceEval Docs on GitHub](https://github.com/BrainDriveAI/ModelMatch/tree/main/FinanceEval/Docs)

The Docs include:
- **Metrics.md** — exact scoring math, rules, and guardrails for each metric.  
- **Research.md** — synthesis of academic and industry sources applied metric-wise.  
- **Results.md** — output schema, JSON/CSV formats, and leaderboard reporting examples.  



