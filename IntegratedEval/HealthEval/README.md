# HealthEval: Open-Source Health AI Evaluation Framework

HealthEval is an open-source framework for evaluating health-focused AI models on their ability to provide safe, clear, and trustworthy advice—using human-centered standards and research-backed metrics. Built for reproducibility, transparency, and community contribution, HealthEval helps researchers, developers, and clinicians benchmark models with a human-in-the-loop approach.

---

## 🚀 Quickstart
1. **Clone the repository:**
   ```bash
   git clone https://github.com/BrainDriveAI/HealthEval.git
   cd HealthEval
   ```
2. **Set your API keys:**
   - **Mac/Linux:**
     ```bash
     export OPENAI_API_KEY="your-openai-key"
     export ANTHROPIC_API_KEY="your-anthropic-key"
     ```
   - **Windows (Command Prompt):**
     ```cmd
     set OPENAI_API_KEY=your-openai-key
     set ANTHROPIC_API_KEY=your-anthropic-key
     ```
   - **Windows (PowerShell):**
     ```powershell
     $env:OPENAI_API_KEY="your-openai-key"
     $env:ANTHROPIC_API_KEY="your-anthropic-key"
     ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the app:**
   ```bash
   python3 app.py
   ```

> **No-code version:** Try HealthEval instantly on HuggingFace Spaces: [BrainDrive/HealthEval](https://huggingface.co/spaces/BrainDrive/HealthEval)

---

## 📁 Folder Structure (Detailed)
- `app.py` — Main Gradio app entrypoint. Handles UI, model selection, evaluation, and result display.
- `core/` — Core logic:
  - `constants.py`: Metric names, scoring anchors, and constants.
  - `evaluators.py`: Main evaluation logic, judge model integration, metric scoring.
  - `fusion.py`: Combines scores from different evaluators/models.
  - `preprocess.py`: Preprocesses user input and model responses.
  - `providers.py`: Model loading and inference (e.g., HuggingFace models).
  - `schema.py`: Data schema for evaluation results.
- `nlp/` — Metric-specific evaluation modules:
  - `clarity_comprehension.py`, `clinical_safety.py`, `empathy_quality.py`, `evidence_transparency.py`, `plain_quality.py`, `trust_agency.py`: Logic and prompt templates for each metric.
- `prompts/` — Prompt templates for each metric, used by NLP modules.
- `schema/` — JSON schema for validating evaluation results.
- `requirements.txt` — Python dependencies.
- `DOCS/` — Extended documentation: metrics, research, results, and folder overview.

---

## 🏆 Top 3 Model Scores (All 6 Metrics)
| Model Name      | Evidence | Clinical | Empathy | Clarity | Plan | Trust | Total |
|-----------------|----------|----------|---------|---------|------|-------|-------|
| Qwen-UMLS       | 6        | 7.5      | 8       | 8       | 7    | 8.25  | 7.445 |
| Phi-3 Mini      | 7.5      | 7.5      | 8       | 8       | 5    | 8.25  | 7.435 |
| Llama3-Med      | 7.5      | 7.5      | 8       | 8       | 3.5  | 8     | 7.18  |

*See [DOCS/results.md](DOCS/results.md) for more details and official model links.*

---

## 📝 Scoring Criteria (Summary)
- **Evidence & Transparency:** Does the model state its purpose, limitations, and evidence?
- **Clinical Safety & Escalation:** Does it spot red-flags and escalate to human care when needed?
- **Empathy & Relationship Quality:** Does it use validating, non-judgmental, and collaborative language?
- **Clarity & Comprehension:** Is the advice clear, structured, and easy to follow?
- **Plan Quality & Behavior Support:** Are the steps concrete, feasible, and supported?
- **Trust, Explainability & User Agency:** Does it explain reasoning, acknowledge uncertainty, and offer user choices?

Scores are on a 0–10 scale per metric, using detailed rubrics (see [DOCS/metrics.md](DOCS/metrics.md)).

---

## 🤖 Judge Models Used
- **GPT-4o** (OpenAI, 2024)
- **Claude Sonnet 3.5** (Anthropic, 2024)

> **Note:** You must provide your own API keys for OpenAI and Anthropic to use these judge models.

---

## 📚 References
- See [DOCS/research.md](DOCS/research.md) for the full list of research papers and frameworks that underpin HealthEval’s metrics and logic.
- Inspired by [ModelMatch/EmailEval](https://github.com/BrainDriveAI/ModelMatch/tree/main/EmailEval)

---

## ⚖️ License
This project is licensed under the MIT License.
