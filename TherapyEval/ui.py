import gradio as gr
from src.evaluation import evaluate_with_judges
from src.api_clients import BACKENDS

def create_app():
    # Load prompt template
    try:
        with open("prompts/carelock.txt", "r", encoding="utf-8") as f:
            PROMPT_TEMPLATE = f.read()
    except FileNotFoundError:
        raise FileNotFoundError("carelock.txt not found in repository root. Please upload it.")

    with gr.Blocks(title="Therapist LLM Evaluator – Care-Lock") as app:
        gr.Markdown("## 🧠 Therapist LLM Evaluator – Care-Lock Variant")
        convo = gr.Textbox(lines=12, label="Paste Full Conversation")
        models = gr.CheckboxGroup(
            list(BACKENDS.keys()),
            value=list(BACKENDS.keys()),
            label="Evaluator Models"
        )
        variant = gr.Radio(["Care-Lock"], value="Care-Lock", label="Variant")
        temp = gr.Slider(0.0, 1.5, step=0.1, value=0.0, label="Temperature")
        weight_labels = [
            "Empathy", "Emotional Relevance", "Tone", "Boundary Awareness",
            "Supportiveness", "Ethical Safety", "Clarity", "Consistency",
            "Self-Awareness", "Adaptability"
        ]
        sliders = [
            gr.Slider(0, 1, step=0.01, value=d, label=l)
            for l, d in zip(weight_labels,
                            [0.2, 0.15, 0.10, 0.10, 0.10, 0.10, 0.05, 0.05, 0.05, 0.10])
        ]
        generate = gr.Button("🔍 Generate Evaluation")
        metrics_table = gr.DataFrame(label="Metrics by Model (with Total)")
        comments_json = gr.JSON(label="Parsed JSON per Model")
        tokens_json = gr.JSON(label="Tokens Used per Model")
        pros_json = gr.JSON(label="Pros per Model")
        cons_json = gr.JSON(label="Cons per Model")
        summary_json = gr.JSON(label="Summary per Model")

        generate.click(
            fn=lambda *args: evaluate_with_judges(*args, prompt_template=PROMPT_TEMPLATE),
            inputs=[convo, models, variant, *sliders, temp],
            outputs=[
                metrics_table, comments_json, tokens_json,
                pros_json, cons_json, summary_json
            ]
        )
    return app
