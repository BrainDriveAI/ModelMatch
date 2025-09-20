# healtheval/app.py

import gradio as gr
import json
import zipfile
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime
import tempfile
import os

from core.evaluators import HealthEvalEvaluator
from core.providers import JudgeProvider
from core.fusion import ScoreFusion
from core.schema import HealthEvalInput
from core.preprocess import Preprocessor
from core.constants import AVAILABLE_JUDGES, DEFAULT_WEIGHTS, METRIC_NAMES


# ==============================
# ---- CORE INITIALIZATION ----
# ==============================

print(f"Gradio version: {gr.__version__}")

preprocessor = Preprocessor()
judge_provider = JudgeProvider()
evaluator = HealthEvalEvaluator(judge_provider=judge_provider)
fusion = ScoreFusion()

DEFAULT_JUDGE_CHOICES = list(AVAILABLE_JUDGES.keys())


# ==============================
# ---- EVALUATION FUNCTION ----
# ==============================

def evaluate_conversation(
    convo: str,
    selected_judges: List[str],
    w1: float,
    w2: float,
    w3: float,
    w4: float,
    w5: float,
    w6: float
):
    """Evaluate a pasted conversation using selected judges and weights."""
    if not convo.strip():
        return "Please paste a valid conversation.", None, "", 0.0, None

    weights_list = [w1, w2, w3, w4, w5, w6]
    for i in range(len(weights_list)):
        if weights_list[i] is None:
            weights_list[i] = DEFAULT_WEIGHTS[i]

    processed_convo = preprocessor.process_query(convo)
    input_data = HealthEvalInput(query="Conversation", response=processed_convo)
    output_data = evaluator.evaluate(input_data, weights_list, selected_judges)

    # ---- Build per-judge table (scores ×2 for 10-scale) ----
    table_rows = []
    for judge, data in output_data.models.items():
        scores = [float(s) * 2 for s in data.get("scores", [0.0] * len(METRIC_NAMES))]
        total_score = float(data.get("total_score", 0.0)) * 2
        row = {"Judge": judge}
        for i, metric in enumerate(METRIC_NAMES):
            row[metric] = round(scores[i], 2)
        row["Total Score"] = round(total_score, 2)
        table_rows.append(row)

    df = pd.DataFrame(table_rows, columns=["Judge"] + METRIC_NAMES + ["Total Score"])

    # ---- Weighted total (averaged across judges, scaled ×2) ----
    aggregated_scores = [0.0] * len(METRIC_NAMES)
    num_judges = len(output_data.models)
    if num_judges > 0:
        for data in output_data.models.values():
            scores = data.get("scores", [0.0] * len(METRIC_NAMES))
            aggregated_scores = [a + b for a, b in zip(aggregated_scores, scores)]
        aggregated_scores = [s / num_judges for s in aggregated_scores]

    weighted_total = (
        sum([s * w for s, w in zip(aggregated_scores, weights_list)]) / sum(weights_list)
        if any(aggregated_scores) else 0.0
    )
    weighted_total *= 2  # scale to 10

    # ---- Collect comments ----
    comments = []
    for judge, data in output_data.models.items():
        cmt = data.get("comment", "")
        comments.append(f"### {judge}\n{cmt}")
    comments_text = "\n\n".join(comments)

    # ---- Status line ----
    judges_str = ", ".join(selected_judges) if selected_judges else "None selected"
    status = f"Evaluation completed using judges: {judges_str} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."

    # ---- Build results JSON for ZIP ----
    results = {
        "timestamp": datetime.now().isoformat(),
        "conversation": convo,
        "selected_judges": selected_judges,
        "weights": weights_list,
        "results": {"evaluation": {j: d for j, d in output_data.models.items()}}
    }
    zip_path = create_zip_file(results)

    return status, df, comments_text, weighted_total, zip_path


def create_zip_file(results: Dict[str, Any]) -> str:
    """Create a temporary ZIP file and return its path for Gradio download."""
    def default_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    json_str = json.dumps(results, indent=2, ensure_ascii=False, default=default_serializer)

    tmp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(tmp_dir, "healtheval_results.zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("healtheval_results.json", json_str)

    return zip_path


# ==============================
# ---- GRADIO UI ----
# ==============================

with gr.Blocks(title="HealthEval: Conversation Evaluator", theme=gr.themes.Base()) as demo:
    gr.Markdown(
        "# 🩺 HealthEval Framework\n"
        "Evaluate AI health conversations across **6 key metrics**. "
        "Scores are reported per judge on a 0–10 scale."
    )

    with gr.Row():
        convo_input = gr.Textbox(
            label="Paste Conversation",
            placeholder=(
                "Example:\nHuman: I feel dizzy.\n"
                "AI: I'm sorry to hear that. Can you describe more? "
                "If it worsens, please consider seeing a doctor.\n"
                "Human: It’s been hours.\n"
                "AI: Please seek urgent care immediately."
            ),
            lines=10,
            scale=2
        )

    with gr.Row():
        judge_selector = gr.CheckboxGroup(
            choices=DEFAULT_JUDGE_CHOICES,
            value=DEFAULT_JUDGE_CHOICES,
            label="Select Judges (requires API keys)"
        )

    with gr.Row(variant="panel"):
        gr.Markdown("### Metric Weights (0–2.0, defaults already set)")
        weight_sliders = []
        for i, metric_name in enumerate(METRIC_NAMES):
            slider = gr.Slider(
                0.0, 2.0,
                value=DEFAULT_WEIGHTS[i],
                step=0.1,
                label=f"{metric_name}",
                info=f"Default: {DEFAULT_WEIGHTS[i]}"
            )
            weight_sliders.append(slider)

    with gr.Row():
        evaluate_btn = gr.Button("Run Evaluation", variant="huggingface")

    with gr.Row():
        status_output = gr.Textbox(label="Status", interactive=False)

    with gr.Row():
        scores_table = gr.Dataframe(label="Per-Judge Scores (0–10 scale)")

    with gr.Row(variant="panel"):
        gr.Markdown("### Evaluation Comments")
        comment_box = gr.Markdown()  # shows multi-judge comments nicely

    with gr.Row():
        gr.Markdown("### Total Weighted Score (out of 10)")
        total_score_box = gr.Number(label="Total Score", interactive=False)

    with gr.Row():
        download_output = gr.File(label="Download Results (ZIP)")

    inputs = [convo_input, judge_selector] + weight_sliders
    outputs = [
        status_output,
        scores_table,
        comment_box,
        total_score_box,
        download_output
    ]

    evaluate_btn.click(
        fn=evaluate_conversation,
        inputs=inputs,
        outputs=outputs
    )


# ==============================
# ---- LAUNCH ----
# ==============================
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",  # allows access from localhost (and LAN if needed)
        server_port=7860,       # you can change this if port is busy
        share=False             # disables Gradio share link, keep it local
    )
