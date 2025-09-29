# HealthEval Results: Top 5 Model Benchmarks

Below are the top 5 models evaluated using the HealthEval framework. Each model was scored across 6 key metrics, with the total score reflecting overall performance as a health advisor.

| Model Name      | HuggingFace Link                | Evidence | Clinical | Empathy | Clarity | Plan | Trust | Total |
|-----------------|---------------------------------|----------|----------|---------|---------|------|-------|-------|
| Qwen-UMLS       | [HF](https://huggingface.co/Qwen-UMLS)         | 6        | 7.5      | 8       | 8       | 7    | 8.25  | 7.445 |
| Phi-3 Mini      | [HF](https://huggingface.co/Phi-3-mini)        | 7.5      | 7.5      | 8       | 8       | 5    | 8.25  | 7.435 |
| Llama3-Med      | [HF](https://huggingface.co/Llama3-Med)        | 7.5      | 7.5      | 8       | 8       | 3.5  | 8     | 7.18  |
| Mistral-NeM     | [HF](https://huggingface.co/Mistral-NeM)       | 7.5      | 7        | 8       | 8       | 4    | 8     | 7.15  |

---

## How to Interpret the Scores
- **Evidence & Transparency:** Does the model clearly state its purpose, limitations, and evidence?
- **Clinical Safety:** Does it spot red-flags and escalate to human care when needed?
- **Empathy:** Does it use validating, non-judgmental, and collaborative language?
- **Clarity:** Is the advice clear, structured, and easy to follow?
- **Plan Quality:** Are the steps concrete, feasible, and supported?
- **Trust:** Does it explain reasoning, acknowledge uncertainty, and offer user choices?

**Total Score:** Weighted average of all metrics. Higher scores indicate models that are safer, clearer, more empathetic, and more trustworthy as health advisors.

---

*For details on metric definitions, see [metrics.md](metrics.md). For research background, see [research.md](research.md).*
