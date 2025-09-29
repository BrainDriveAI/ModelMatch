# IntegratedEval

IntegratedEval is a unified evaluation suite built to benchmark general-purpose language models across five critical domains: email, finance, health, summarization, and therapy. It stitches together the domain-specific evaluators already used in production workflows and surfaces their results through a single Gradio interface, making cross-domain quality checks faster and more consistent.

## Domains at a Glance

- **EmailEval**: Scores outbound messages for clarity, tone, personalization, grammar, and spam risk using the domain’s proven rubric and weight presets.
- **FinanceEval**: Audits financial advisor conversations for trust, accuracy, clarity, risk disclosure, and client-first behavior by running both judge LLMs and rule-based detectors.
- **HealthEval**: Evaluates clinical guidance against safety, transparency, empathy, and best-practice alignment using the Care-Lock-ready judge ensemble.
- **Summeval**: Grades news or document summaries on coverage, alignment, hallucination, relevance, and bias toxicity via Twin-Lock and Judge-Lock evaluators.
- **TherapyEval**: Assesses supportive conversations on empathy, ethical safety, boundary awareness, and therapeutic rapport using the Care-Lock variant of the therapy rubric.

## How It Works

1. **Unified UI**: `app.py` launches a Gradio dashboard that collects the required inputs for each domain in one place.
2. **Domain Orchestration**: The app dispatches inputs to existing evaluators without rewriting their logic, preserving established metrics and scoring rules.
3. **Judge Constraints**: Each domain runs against the GPT-4o and Claude 3.5 Sonnet pathways to keep comparisons consistent.
4. **Aggregation**: Scores, comments, rationales, and token usage by judge are normalized into a single scoreboard plus a detailed JSON payload for downstream analytics.

## Use Cases

- Benchmark new general-purpose models before deployment across compliance-heavy workflows.
- Perform regression testing on multi-domain assistants after fine-tuning or prompt updates.
- Generate standardized evaluation reports for stakeholders who need comparable metrics across domains.
- Rapidly identify strengths and weaknesses of external models during vendor assessments.

## Current Winners (Top 3)

| Model                        | Summary | Email | Therapy | Finance | Health | Total Avg |
|------------------------------|---------|-------|---------|---------|--------|-----------|
| **Phi-3 Mini 4K Instruct**   | 9.87    | 8.35  | 9.05    | 8.88    | 9.27   | **9.08**  |
| **Mistral 7B Instruct v0.3** | 9.94    | 7.94  | 8.57    | 8.58    | 9.33   | **8.87**  |
| **OpenHermes 2.5 Mistral 7B**| 9.73    | 8.02  | 8.10    | 8.70    | 9.40   | **8.79**  |

## How to Use

```bash
# 1. Clone the repository
git clone https://github.com/<your-org>/IntegratedEval.git
cd IntegratedEval

# 2. Install dependencies (optionally inside a virtual environment)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Provide API credentials
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"

# 4. Launch the app
python3 app.py
```

The Gradio interface starts on the default configuration; paste your email, conversation, and summary inputs, adjust weights if needed, and click **Evaluate**. The UI displays per-domain scores, judge-level details, and a consolidated JSON view you can download or integrate elsewhere.

## Features

- Single-pane evaluation across five specialized domains.
- Consistent judge model set for apples-to-apples comparisons.
- Configurable weights and prompts that honor each domain’s native presets.
- Token usage tracking and community-friendly evaluation summaries for reports.

## Conclusion

IntegratedEval brings domain rigor and operational simplicity together, enabling teams to verify model quality against real-world expectations in minutes.


