import os, json
from typing import Dict, Any, Tuple

from core.providers import Provider
from core.fusion import normalize_llm_score
from core.schema import METRIC_ORDER

# NLP modules
from nlp import trust as nlp_trust
from nlp import accuracy as nlp_accuracy
from nlp import explain as nlp_explain
from nlp import client_first as nlp_client
from nlp import risk_safety as nlp_risk
from nlp import clarity as nlp_clarity

PROMPT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts')

PROMPTS = {
    'trust': os.path.join(PROMPT_DIR, 'trust.txt'),
    'accuracy': os.path.join(PROMPT_DIR, 'accuracy.txt'),
    'explain': os.path.join(PROMPT_DIR, 'explain.txt'),
    'client_first': os.path.join(PROMPT_DIR, 'client_first.txt'),
    'risk_safety': os.path.join(PROMPT_DIR, 'risk_safety.txt'),
    'clarity': os.path.join(PROMPT_DIR, 'clarity.txt'),
}

SYSTEM_PREAMBLE = "You are a meticulous, concise finance evaluator. Always return strict JSON only."

def _load_prompt(name: str) -> str:
    with open(PROMPTS[name], 'r') as f:
        return f.read()

def _judge_one(provider: Provider, metric: str, conversation_text: str) -> Tuple[Dict[str, Any], Dict[str, int]]:
    prompt = _load_prompt(metric)
    user_prompt = f"Conversation to evaluate:\n\n{conversation_text}\n\nReturn only JSON."
    result, usage = provider.judge(SYSTEM_PREAMBLE, f"{prompt}\n\n{user_prompt}")
    return (result or {}), (usage or {"prompt":0,"completion":0,"total":0})

def evaluate_all_metrics(provider: Provider, conversation_text: str, alpha_map: Dict[str, float]):
    out: Dict[str, Dict[str, Any]] = {}
    total_usage = {"prompt": 0, "completion": 0, "total": 0}
    raw_json = {}

    nlp_funcs = {
        'trust': nlp_trust.score,
        'accuracy': nlp_accuracy.score,
        'explain': nlp_explain.score,
        'client_first': nlp_client.score,
        'risk_safety': nlp_risk.score,
        'clarity': nlp_clarity.score,
    }

    for metric in METRIC_ORDER:
        judge_json, usage = _judge_one(provider, metric, conversation_text)
        raw_json[metric] = judge_json

        # Extract LLM judge score and comment
        if metric in judge_json:
            judge_score = judge_json.get(metric)
        else:
            judge_score = None
        comment = judge_json.get("reason", "")

        # Normalize LLM score 1–5 → 0–10
        fused = normalize_llm_score(judge_score)

        # Run NLP detectors (flags only)
        nlp_payload = nlp_funcs[metric](conversation_text)

        out[metric] = {
            'judge_score': judge_score,
            'score_0_10': fused,
            'comment': comment,
            'nlp_details': nlp_payload
        }

        for k in total_usage:
            total_usage[k] += usage.get(k, 0)

    return out, total_usage, raw_json
