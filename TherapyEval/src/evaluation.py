import re
import json
import datetime
import pandas as pd
import os
from src.api_clients import BACKENDS

def split_json_objects(s):
    objs, depth, start = [], 0, None
    for i, ch in enumerate(s):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                objs.append(s[start:i+1])
    return objs

def evaluate_with_judges(conversation, selected_models, variant, *weights_and_temp, prompt_template):
    weights, temperature = list(weights_and_temp[:-1]), weights_and_temp[-1]
    if not conversation.strip():
        raise ValueError("Conversation input is empty.")
    from src.conversation import structure_conversation
    structured = structure_conversation(conversation)
    system_msg = (
        "You are Judge-Care-Lock, a rigorous evaluator of AI-therapist dialogues.\n"
        "1. Use ONLY the transcript—quote it for every decision.\n"
        "2. Apply the multi-layer rubric exactly; do NOT invent scales.\n"
        "3. Return valid JSON matching the schema; no extra text."
    )
    user_prompt = prompt_template.replace("{CONVERSATION}", structured)

    metrics_rows = []
    comments_map = {}
    tokens_map = {}
    pros_map = {}
    cons_map = {}
    summary_map = {}

    for model_name in selected_models:
        fn = BACKENDS[model_name]
        raw, toks = fn(system_msg, user_prompt, temperature)
        tokens_map[model_name] = toks

        clean = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()
        objs = split_json_objects(clean)
        if not objs:
            raise ValueError(f"No valid JSON from {model_name}:\n{clean}")
        try:
            parsed = json.loads(objs[0])
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON from {model_name}: {str(e)}")

        row = {"Model": model_name}
        total_score = 0.0
        for idx, (m, data) in enumerate(parsed["metrics"].items()):
            score = data.get("score", 0.0)
            row[m] = score
            total_score += score * weights[idx]
        row["Total"] = round(total_score, 2)
        metrics_rows.append(row)
        comments_map[model_name] = parsed
        pros_map[model_name] = parsed.get("positive", [])
        cons_map[model_name] = parsed.get("negative", [])
        summary_map[model_name] = parsed.get("summary", "")

    # Generate JSON file in outputs/
    os.makedirs("outputs", exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"outputs/carelock_eval_{ts}.json"
    combined = {
        "metrics_table": metrics_rows,
        "parsed_per_model": comments_map,
        "tokens_per_model": tokens_map,
        "pros_per_model": pros_map,
        "cons_per_model": cons_map,
        "summary_per_model": summary_map
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2)

    # Return 6 outputs
    return (pd.DataFrame(metrics_rows), comments_map, tokens_map,
            pros_map, cons_map, summary_map)
