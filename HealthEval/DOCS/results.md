# HealthEval Results: Top 5 Model Benchmarks

Below are the top 5 models evaluated using the HealthEval framework. Each model was scored across 6 key metrics, with the total score reflecting overall performance as a health advisor.

| Model Name                     | HuggingFace Link                                                                 | Evidence | Clinical | Empathy | Clarity | Plan | Trust | Total |
|--------------------------------|----------------------------------------------------------------------------------|----------|----------|---------|---------|------|-------|-------|
| Qwen-UMLS-7B-Instruct          | [HF](https://huggingface.co/prithivMLmods/Qwen-UMLS-7B-Instruct)                 | 6.0      | 7.5      | 8.0     | 8.0     | 7.0  | 8.25  | 7.445 |
| Phi-3 Mini                     | [HF](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct)                    | 7.5      | 7.5      | 8.0     | 8.0     | 5.0  | 8.25  | 7.435 |
| Llama3-Med42-8B                | [HF](https://huggingface.co/m42-health/Llama3-Med42-8B)                          | 7.5      | 7.5      | 8.0     | 8.0     | 3.5  | 8.0   | 7.180 |
| Mistral-NeMo-Minitron-8B-Instruct | [HF](https://huggingface.co/nvidia/Mistral-NeMo-Minitron-8B-Instruct)            | 7.5      | 7.0      | 8.0     | 8.0     | 4.0  | 8.0   | 7.150 |
| DeepSeek V2 Lite Chat          | [HF](https://huggingface.co/deepseek-ai/DeepSeek-V2-Lite-Chat)                   | 6.5      | 6.5      | 8.0     | 8.0     | 5.5  | 8.25  | 7.125 |

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

