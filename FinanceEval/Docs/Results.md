# Top 5 Model Stats (FinanceEval)

Computation guidance:
* Overall Score = average weighted scores (refer Readme page for weight/metrics) across evaluation set.
* Each metric is averaged across runs for fairness.

| Rank | Model Name | Overall Score | Trust | Accuracy | Explainability | Client-First | Risk Safety | Clarity | Link |
|------|------------|---------------|-------|----------|----------------|--------------|-------------|---------|------|
| 🥇 1 | meta-llama/llama-3-70b-instruct | 6.26 | 5.25 | 7.39 | 7.81 | 4.91 | 4.22 | 8.25 | [HF Link](https://huggingface.co/meta-llama/Meta-Llama-3-70B-Instruct) |
| 🥈 2 | meta-llama/llama-3.3-70b-instruct | 5.87 | 4.81 | 6.58 | 7.50 | 4.83 | 4.53 | 7.36 | [HF Link](https://huggingface.co/meta-llama/llama-3.3-70b-instruct) |
| 🥉 3 | nvidia/llama-3.1-nemotron-70b-instruct | 5.78 | 4.81 | 6.23 | 7.48 | 5.53 | 3.85 | 7.38 | [HF Link](https://huggingface.co/nvidia/llama-3.1-nemotron-70b-instruct) |
| 4️⃣ 4 | meta-llama/llama-3-8b-instruct | 5.68 | 4.81 | 4.95 | 7.57 | 5.64 | 4.50 | 8.25 | [HF Link](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct) |
| 5️⃣ 5 | microsoft/phi-3-mini-128k-instruct | 5.13 | 4.38 | 5.99 | 6.29 | 3.69 | 4.35 | 6.11 | [HF Link](https://huggingface.co/microsoft/phi-3-mini-128k-instruct) |

Notes:
* Scores are on 0–10 (normalized scale).
* Reflects 4 batch evaluation (4 domains per model) with FinanceEval; results vary by dataset and weights.
