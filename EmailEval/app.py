# app.py  —  Hugging Face Space entrypoint (fixed imports)

import os
import io
import csv
import json
import zipfile
import datetime
import gradio as gr

# --- robust imports: absolute first, safe fallback for local runs ---
try:
    from email_eval.api import evaluate, DEFAULT_WEIGHT_PRESETS, metric_keys
except Exception:
    # allow running `python app.py` locally without installing a package
    import sys, pathlib
    sys.path.append(str(pathlib.Path(__file__).parent.resolve()))
    from email_eval.api import evaluate, DEFAULT_WEIGHT_PRESETS, metric_keys

ENGINES = ["openai", "claude"]
PRESET = "research_defaults"

def run_eval(subject, body, engine,
             w_clarity, w_length, w_spam, w_perso, w_tone, w_grammar):
    # normalize/collect weights
    weights = {
        "clarity": float(w_clarity),
        "length": float(w_length),
        "spam_score": float(w_spam),
        "personalization": float(w_perso),
        "tone": float(w_tone),
        "grammatical_hygiene": float(w_grammar),
    }

    # evaluate
    out = evaluate(subject or "", body or "", engine=engine, weights=weights)

    # JSON for exports
    out_json_str = json.dumps(out, indent=2, ensure_ascii=False)

    # comments pane - use LLM comments + explanations
    comments_lines = []
    for k in metric_keys():
        comm = out.get("comments", {}).get(k, 'No comment.')
        expl = "; ".join(out.get("explanations", {}).get(k, []))
        comments_lines.append(f"{k}: {comm}" + (f" (explanations: {expl})" if expl else ""))
    comments_str = "\n".join(comments_lines) if comments_lines else "No comments."

    # tokens used pane
    usage = out.get("usage", {}) or {}
    tokens_line = (
        f"OpenAI tokens: {usage.get('openai_total', 0)} | "
        f"Claude tokens: {usage.get('claude_total', 0)} | "
        f"Total: {usage.get('total', 0)}"
    )

    # CSV export
    ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    csv_path = f"/tmp/email_eval_{ts}.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "score_0_10"])
        for k in metric_keys():
            writer.writerow([k, out["scores"][k]])
        writer.writerow(["weighted_total", out["weighted_total"]])

    # ZIP export (CSV + JSON)
    zip_path = f"/tmp/email_eval_{ts}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"email_eval_{ts}.json", out_json_str)
        with open(csv_path, "rb") as f:
            zf.writestr(f"email_eval_{ts}.csv", f.read())

    # Scores table data (metric, score_0_10) + weighted total
    table_rows = [[k, out["scores"][k]] for k in metric_keys()]
    table_rows.append(["weighted_total", out["weighted_total"]])

    return table_rows, comments_str, tokens_line, csv_path, zip_path


with gr.Blocks(title="Email Evaluator (Subject + Body)") as demo:
    gr.HTML("""
    <style>
    button.primary, .gr-button-primary, button[aria-label="Evaluate"].primary {
        background-color: #000 !important; color: #fff !important; border-color: #000 !important;
    }
    </style>
    """)
    gr.Markdown(
        "# Email Evaluator — Subject + Body\n"
        "Six metrics · Rules + math-based LLM (OpenAI / Claude) · Research-grounded defaults."
    )

    subject = gr.Textbox(
        label="Subject",
        placeholder="e.g., Q3 draft — please review by Thu 5 PM"
    )
    body = gr.Textbox(
        label="Body (plain text)",
        lines=16,
        placeholder="Paste the email body here..."
    )
    engine = gr.Dropdown(
        ENGINES, value="openai",
        label="Engine (LLM assistance for clarity, tone flags, personalization cues, spam-lexicon matching)"
    )

    gr.Markdown("### Weights (0–10 each; normalized internally)")
    w1 = gr.Slider(0, 10, value=DEFAULT_WEIGHT_PRESETS["research_defaults"]["clarity"],
                   step=0.5, label="Clarity")
    w2 = gr.Slider(0, 10, value=DEFAULT_WEIGHT_PRESETS["research_defaults"]["length"],
                   step=0.5, label="Length")
    w3 = gr.Slider(0, 10, value=DEFAULT_WEIGHT_PRESETS["research_defaults"]["spam_score"],
                   step=0.5, label="Spam")
    w4 = gr.Slider(0, 10, value=DEFAULT_WEIGHT_PRESETS["research_defaults"]["personalization"],
                   step=0.5, label="Personalization")
    w5 = gr.Slider(0, 10, value=DEFAULT_WEIGHT_PRESETS["research_defaults"]["tone"],
                   step=0.5, label="Tone")
    w6 = gr.Slider(0, 10, value=DEFAULT_WEIGHT_PRESETS["research_defaults"]["grammatical_hygiene"],
                   step=0.5, label="Grammar")

    btn = gr.Button("Evaluate", variant="primary")

    with gr.Tab("Scores"):
        out_table = gr.Dataframe(headers=["metric","score_0_10"], row_count=(7,"fixed"), col_count=(2,"fixed"), wrap=True, interactive=False, label="Metric-wise scores and total")
    with gr.Tab("Comments"):
        comments = gr.Textbox(label="Comments & triggered rules", lines=10)
    with gr.Tab("Usage"):
        tokens = gr.Textbox(label="Tokens used")

    with gr.Row():
        dl_csv = gr.File(label="Download CSV")
        dl_zip = gr.File(label="Download ZIP (CSV + JSON)")

    btn.click(
        run_eval,
        inputs=[subject, body, engine, w1, w2, w3, w4, w5, w6],
        outputs=[out_table, comments, tokens, dl_csv, dl_zip]
    )

if __name__ == "__main__":
    # Hugging Face Spaces will run this automatically, but local runs benefit from this.
    demo.launch(server_name="0.0.0.0", server_port=int(os.getenv("PORT", "7860")), show_error=True)