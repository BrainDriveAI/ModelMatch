# FinanceEval 🛠 — Metric & Evaluation Overview

Below is how FinanceEval measures up: what metrics are used, how top models compare, and what research underpins the framework.

---

## 🔢 Metrics Design (What is Measured & How)

FinanceEval scores advice / model outputs along six core metrics. Each metric has explicit design choices inspired by empirical findings:

| Metric | Key Components / Checks |
|---|--------------------------|
| **Trust & Transparency** | Checks for early risk and conflict disclosures; penalizes overconfident or absolute claims (e.g. “guaranteed”, “risk-free”); uses hedge language (“may”, “could”) to improve trust. |
| **Competence & Accuracy** | Numeric correctness (calculations etc.), semantic similarity to known good advice, penalties for omissions (fees, taxes, realistic assumptions). |
| **Explainability** | Judging whether advice provides causal reasoning (“because”, “due to”), structured steps, readability, clarity in logic flow. |
| **Client-Centeredness / Fiduciary Alignment** | Personalization depth, mention of client’s circumstances (goals, income), avoidance of bias & conflict of interest, framing advice in best interest. |
| **Risk Safety / Bias Sensitivity** | Flags for cognitive biases (herding, overconfidence), requirement for risk disclosures, mention of diversification, balanced pros/cons. |
| **Financial Literacy / Communication Clarity** | Measures jargon density, readability, structure (bullets, numbered steps), making advice understandable to non-experts. |

Each metric typically scored on a 1–5 or 0-10 normalized scale. The framework includes both deterministic / rule-based checks and LLM-assisted judgments.


## ⚙️ How to Use This README to Navigate the Full Docs

- For exact formulas,math and thresholds , refer to **Metrics.md**.  
- To understand metric wise scores for top 5 models from our recent evaluation, check **Results.md**.  
- If you want to dig into *why* FinanceEval uses certain thresholds/rules or how they were derived from literature, see **Research.md**.

---

