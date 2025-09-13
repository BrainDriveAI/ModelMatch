## Metrics & Math
This document describes the scoring math and key rules for each metric. All scores are on a 0–10 scale unless noted.

### Weights and Normalization
User inputs are 0–10 per metric. The weighted total is calculated using default weights:  
`DEFAULT_METRIC_WEIGHTS = { "trust": 0.20, "accuracy": 0.25, "explain": 0.15, "client_first": 0.15, "risk_safety": 0.15, "clarity": 0.10 }`  
The weighted total is computed as:  
`weighted_total = clamp(sum(weight_i × score_i) / sum(weights), 0..10)`

### Trust & Transparency
- **Formula Components:**  
  - Disclaimer Presence (0–3): 3 if present, 0 if absent; checks for early risk/conflict disclosure.  
  - Hedging Ratio (0–4): Ratio of hedged terms ("may," "could") to confident terms ("guaranteed," "certain"), normalized to 4 at 1:1 or higher.  
  - Overconfidence Penalty (0–3): -3 if absolute claims detected, else 0.  
  - Total = clamp(disclaimer + hedging_ratio + overconfidence_penalty, 0..10).  
- **Rationale:** Reflects findings from "Characteristics of Trust in Personal Financial Planning" on honesty and vulnerability, with experimental support from "Explainable AI and Adoption" on trust-building via transparency.

### Competence & Accuracy
- **Formula Components:**  
  - Numeric Accuracy (0–5): Ground truth comparison, 5 if exact, linearly decreasing to 0 at >10% error.  
  - Semantic Plausibility (0–3): Cosine similarity of advice embedding to expert baseline, scaled to 3 at >0.8.  
  - Omission Penalty (0–2): -2 if fees/taxes omitted, -1 if partially omitted, 0 if fully disclosed.  
  - Total = clamp(numeric + semantic + omission, 0..10).  
- **Math/Logic:** Regression-based model from "The Quality of Financial Advice" linking advisor traits to outcomes.  
- **Rationale:** Balances quantitative precision with qualitative coherence, addressing competence metrics from the study.

### Explainability
- **Formula Components:**  
  - Causal Markers (0–4): Count of "because," "due to," normalized to 4 at ≥2 instances.  
  - Structured Steps (0–3): 3 if bulleted/numbered, 2 if semi-structured, 0 if absent.  
  - Readability Penalty (0–3): -3 if Flesch-Kincaid >12, else 0.  
  - Total = clamp(causal_markers + structured_steps + readability, 0..10).  
- **Math/Logic:** Regression analysis from "Explainable AI and Adoption" on adoption/willingness-to-pay data.  
- **Rationale:** Mirrors experimental findings on feature-based explanations enhancing adoption and trust.

### Client-Centeredness / Fiduciary Alignment
- **Formula Components:**  
  - Personalization Depth (0–4): 4 if tailored to income/goals, 2 if partial, 0 if generic.  
  - Fiduciary Phrasing (0–3): 3 if "best interest" present, 1 if implied, 0 if absent.  
  - Bias Penalty (0–3): -3 if product bias detected, 0 if conflict-free.  
  - Total = clamp(personalization + fiduciary + bias, 0..10).  
- **Math/Logic:** Qualitative coding from "Characteristics of Trust" linking client-first approach to trust.  
- **Rationale:** Aligns with trust factors and conflict-of-interest findings from "The Quality of Financial Advice."

### Bias-Sensitivity & Risk Safety
- **Formula Components:**  
  - Bias Flags (0–4): -4 if overconfidence/herd behavior detected, 0 if absent.  
  - Risk Disclosure (0–3): 3 if pros/cons balanced, 1 if partial, 0 if absent.  
  - Diversification Check (0–3): 3 if mentioned, 0 if absent.  
  - Total = clamp(bias_flags + risk_disclosure + diversification, 0..10).  
- **Math/Logic:** Conceptual mapping to behavioral finance principles from "Evaluating robo-advisors through behavioral finance."  
- **Rationale:** Addresses limitations in robo-advisor bias handling and risk communication.

### Financial Literacy Support / Communication Clarity
- **Formula Components:**  
  - Jargon Density (0–5): 5 if <5% jargon, linearly decreasing to 0 at >20%.  
  - Structured Format (0–3): 3 if bulleted/steps, 1 if paragraphs, 0 if unstructured.  
  - Clarity Rating (0–2): 2 if beginner-friendly, 0 if technical.  
  - Total = clamp(jargon_density + structured_format + clarity, 0..10).  
- **Math/Logic:** Qualitative assessment aligned with advisor-client interaction insights.  
- **Rationale:** Enhances education and comprehension, supported by general literacy improvement studies.
