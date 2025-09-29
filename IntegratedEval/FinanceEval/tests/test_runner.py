# tests/test_runner.py
"""
FinanceEval – Safe Test Runner
No runtime writes. Uses only in-memory comparisons.
"""

import os, json
import pandas as pd
from core.providers import get_provider, ProviderKind
from core.preprocess import normalize_conversation, extract_model_utterances
from core.evaluators import evaluate_all_metrics
from core.fusion import weighted_total
from core.schema import METRIC_ORDER

# Load static test inputs (read-only)
TEST_INPUTS_PATH = os.path.join(os.path.dirname(__file__), "redteam_inputs.jsonl")
GOLDEN_OUTPUTS_PATH = os.path.join(os.path.dirname(__file__), "golden_outputs.json")

def load_redteam_inputs():
    with open(TEST_INPUTS_PATH, "r") as f:
        return [json.loads(line) for line in f]

def load_golden_outputs():
    if os.path.exists(GOLDEN_OUTPUTS_PATH):
        with open(GOLDEN_OUTPUTS_PATH, "r") as f:
            return json.load(f)
    return {}

def run_one(provider, conversation_text, alpha_map):
    norm = normalize_conversation(conversation_text)
    model_only = extract_model_utterances(norm)
    metrics_out, usage, raw_json = evaluate_all_metrics(
        provider=provider,
        conversation_text=model_only,
        alpha_map=alpha_map
    )
    # Return dict only, no file writes
    return {
        "metrics": {m: v["fused_0_10"] for m, v in metrics_out.items()},
        "usage": usage,
        "raw": raw_json
    }

if __name__ == "__main__":
    alpha_map = {
        "trust": 0.70, "accuracy": 0.65, "explain": 0.50,
        "client_first": 0.70, "risk_safety": 0.60, "clarity": 0.70
    }

    inputs = load_redteam_inputs()
    goldens = load_golden_outputs()

    # Example: run against OpenAI GPT-4o if key is available
    if os.environ.get("OPENAI_API_KEY"):
        provider = get_provider(ProviderKind.OPENAI, "gpt-4o")
        for case in inputs:
            convo = case["conversation"]
            notes = case.get("notes", "")
            result = run_one(provider, convo, alpha_map)
            print("=== CASE ===")
            print(notes)
            print(pd.DataFrame([result["metrics"]]))
            print("Token usage:", result["usage"])
            # Golden comparison (if available)
            # No saving, just console diff
            case_key = notes or convo[:30]
            if case_key in goldens:
                print("Golden vs Result:", goldens[case_key], result["metrics"])
