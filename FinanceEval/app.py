# app.py 

import os, glob, json, zipfile, traceback
import gradio as gr
import pandas as pd
from datetime import datetime, timezone

from core.providers import get_provider, ProviderKind
from core.preprocess import normalize_conversation, extract_model_utterances
from core.evaluators import evaluate_all_metrics
from core.fusion import weighted_total

# -----------------------------
# Defaults
# -----------------------------
DEFAULT_METRIC_WEIGHTS = {
    "trust": 0.20,
    "accuracy": 0.25,
    "explain": 0.15,
    "client_first": 0.15,
    "risk_safety": 0.15,
    "clarity": 0.10,
}

# -----------------------------
# Core runner
# -----------------------------
def run_eval(conversation: str,
             use_openai: bool,
             use_anthropic: bool,
             w_trust: float, w_accuracy: float, w_explain: float,
             w_client: float, w_risk: float, w_clarity: float):

    try:
        if not conversation or conversation.strip() == "":
            return None, None, None, None, "❌ Please paste a conversation to evaluate."

        # cleanup old ZIPs
        for f in glob.glob("/tmp/financeeval_*.zip"):
            try:
                os.remove(f)
            except Exception:
                pass

        # normalize weights from sliders
        user_weights = {
            "trust": w_trust, "accuracy": w_accuracy, "explain": w_explain,
            "client_first": w_client, "risk_safety": w_risk, "clarity": w_clarity
        }
        s = sum(user_weights.values()) or 1.0
        for k in user_weights:
            user_weights[k] = user_weights[k] / s

        # preprocess
        norm = normalize_conversation(conversation)
        model_only = extract_model_utterances(norm)

        providers = []
        if use_openai:
            providers.append(get_provider(ProviderKind.OPENAI, "gpt-4o"))
        if use_anthropic:
            providers.append(get_provider(ProviderKind.ANTHROPIC, "claude-3-5-sonnet-20240620"))
        if not providers:
            return None, None, None, None, "❌ Select at least one model provider."

        all_tables, compare_rows, token_usage_blocks, json_blobs = [], [], [], {}

        for p in providers:
            metrics_out, usage, raw_json = evaluate_all_metrics(
                provider=p, conversation_text=model_only, alpha_map={}
            )
            rows = []
            for m, payload in metrics_out.items():
                rows.append({
                    "Metric": m,
                    "LLM Score (1-5)": payload.get("judge_score", None),
                    "Final Score (0-10)": round(payload.get("score_0_10", 0.0), 2),
                    "Comment": payload.get("comment", ""),
                    "NLP Flags": json.dumps(payload.get("nlp_details", {}))[:200]
                })
            df = pd.DataFrame(rows)

            # total score with weight sliders
            total = weighted_total({k: v.get("score_0_10", 0.0) for k, v in metrics_out.items()},
                                   user_weights)

            compare_rows.append({
                "Model": p.label,
                **{r["Metric"]: r["Final Score (0-10)"] for _, r in df.iterrows()},
                "Total (0-10)": round(total, 2)
            })
            token_usage_blocks.append(
                f"{p.label}: prompt={usage.get('prompt',0)}, completion={usage.get('completion',0)}, total={usage.get('total',0)}"
            )
            json_blobs[p.label] = raw_json
            all_tables.append((p.label, df, round(total, 2)))

        compare_df = pd.DataFrame(compare_rows)
        avg_df = None
        if len(providers) > 1:
            num_cols = [c for c in compare_df.columns if c != "Model"]
            avg_row = {"Model": "Average"}
            for c in num_cols:
                avg_row[c] = round(compare_df[c].mean(), 2)
            avg_df = pd.DataFrame([avg_row])

        # ---- Write ZIP into /tmp ----
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        zip_path = f"/tmp/financeeval_{ts}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for label, df, total in all_tables:
                df2 = df.copy()
                df2.loc[len(df2)] = {
                    "Metric": "TOTAL",
                    "LLM Score (1-5)": "-",
                    "Final Score (0-10)": total,
                    "Comment": "",
                    "NLP Flags": ""
                }
                zf.writestr(f"results_{label}_{ts}.csv", df2.to_csv(index=False).encode("utf-8"))
            zf.writestr(f"comparison_{ts}.csv", compare_df.to_csv(index=False).encode("utf-8"))
            zf.writestr(f"judgments_{ts}.json", json.dumps(json_blobs, indent=2).encode("utf-8"))

        # merge tables for UI
        merged_tables = []
        for label, df, total in all_tables:
            merged_tables.append(pd.DataFrame({
                "Metric": [f"— {label} —"],
                "LLM Score (1-5)": [""],
                "Final Score (0-10)": [""],
                "Comment": [""],
                "NLP Flags": [""]
            }))
            merged_tables.append(df)
        merged_df = pd.concat(merged_tables, ignore_index=True)
        usage_text_all = "\n".join(token_usage_blocks)

        return merged_df, compare_df, (avg_df if avg_df is not None else pd.DataFrame()), zip_path, usage_text_all

    except Exception as e:
        tb = traceback.format_exc()
        error_text = f"❌ Error: {str(e)}\n\nTraceback:\n{tb}"
        return None, None, None, None, error_text


# -----------------------------
# Gradio UI
# -----------------------------
def create_demo():
    with gr.Blocks(title="FinanceEval – Localhost") as demo:
        gr.Markdown("# 🔎 FinanceEval – Localhost Evaluation")

        conversation = gr.Textbox(label="Conversation", lines=16, placeholder="Paste transcript here...")
        with gr.Accordion("Model Selection", open=True):
            use_openai = gr.Checkbox(value=True, label="Use OpenAI GPT-4o")
            use_anthropic = gr.Checkbox(value=False, label="Use Claude 3.5 Sonnet")

        with gr.Accordion("Metric Weights", open=True):
            w_trust = gr.Slider(0,1,value=DEFAULT_METRIC_WEIGHTS["trust"],step=0.01,label="Trust")
            w_accuracy = gr.Slider(0,1,value=DEFAULT_METRIC_WEIGHTS["accuracy"],step=0.01,label="Accuracy")
            w_explain = gr.Slider(0,1,value=DEFAULT_METRIC_WEIGHTS["explain"],step=0.01,label="Explainability")
            w_client = gr.Slider(0,1,value=DEFAULT_METRIC_WEIGHTS["client_first"],step=0.01,label="Client-First")
            w_risk = gr.Slider(0,1,value=DEFAULT_METRIC_WEIGHTS["risk_safety"],step=0.01,label="Risk Safety")
            w_clarity = gr.Slider(0,1,value=DEFAULT_METRIC_WEIGHTS["clarity"],step=0.01,label="Clarity")

        run_btn = gr.Button("Evaluate")
        with gr.Tab("Per-Model Results"):
            table_out = gr.Dataframe()
        with gr.Tab("Comparison"):
            compare_out = gr.Dataframe()
            avg_out = gr.Dataframe()
        with gr.Tab("Downloads & Usage"):
            zip_file = gr.File(label="Download ZIP (CSVs + JSON)", type="filepath")
            usage_text = gr.Textbox(label="Token Usage / Errors", lines=8)

        run_btn.click(
            fn=run_eval,
            inputs=[conversation, use_openai, use_anthropic,
                    w_trust, w_accuracy, w_explain, w_client, w_risk, w_clarity],
            outputs=[table_out, compare_out, avg_out, zip_file, usage_text]
        )
    return demo


if __name__ == "__main__":
    demo = create_demo()
    demo.launch(server_name="127.0.0.1", server_port=int(os.environ.get("PORT", 7860)))
