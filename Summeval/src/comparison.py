import json
from src.api_clients import openai_client

last_eval_result = {}  # Shared state

def get_last_eval_data():
    return last_eval_result if last_eval_result else None

def run_comparison(human_scores, human_comments, model_scores, model_comments):
    prompt = f"""Compare human and model summary evaluations.

Human Scores: {human_scores}
Model Scores: {model_scores}

Human Comments: {human_comments}
Model Comments: {model_comments}

Output key differences, strengths, and any mismatches."""
    res = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )
    return res.choices[0].message.content

def import_model_metrics():
    data = get_last_eval_data()
    if not data or "scores" not in data:
        return ["" ] * 6
    s = data["scores"]
    return (
        str(s.get("coverage", "")),
        str(s.get("alignment", "")),
        str(s.get("hallucination", "")),
        str(s.get("relevance", "")),
        str(s.get("bias_toxicity", "")),
        json.dumps(data.get("comments", ""), indent=2)
    )