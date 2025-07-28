import gradio as gr
from src.api_clients import openai_client, claude_client, deepseek_client
from src.api_clients import get_openrouter_models
from src.summary_generator import generate_summary_from_openrouter, is_prompt_valid_for_summary
from src.summary_generator import generate_summary_from_openrouter, is_prompt_valid_for_summary
from src.evaluation import evaluate
from src.comparison import get_last_eval_data, run_comparison, import_model_metrics
from src.utils import preset_vals

from config.css import CSS

with gr.Blocks(css=CSS) as demo:
    with gr.Tabs():

        # ▸ Tab 1: Unified Summary + Evaluation
        with gr.Tab("🧠 Generate + Evaluate"):
            gr.Markdown("## Unified Summary Generator and Evaluator")
            article = gr.Textbox(label="Paste article", lines=10)
            auto_gen_toggle = gr.Checkbox(label="Enable Auto-Generation if Summary is Empty", value=True)
            summary = gr.Textbox(label="Paste summary", lines=6, visible=False, interactive=True)
            prompt = gr.Textbox(label="Prompt for summary (only if generating)", lines=2, visible=True, interactive=True)
            model = gr.Dropdown(choices=get_openrouter_models(), label="Model (for generation)", visible=True, interactive=True)

            variant = gr.Radio(["Twin-Lock","Judge-Lock","ParallelX-TJ"], value="Twin-Lock", label="Variant", elem_id="variant-group")
            back = gr.CheckboxGroup(["OpenAI","DeepSeek","Claude"], value=["OpenAI","DeepSeek","Claude"], label="Back-ends", elem_id="backend-group")
            p0 = preset_vals("Twin-Lock")
            w_cov  = gr.Slider(0,1,p0[0],step=0.01,label="Coverage",      elem_classes=["metric-slider"])
            w_align= gr.Slider(0,1,p0[1],step=0.01,label="Alignment",     elem_classes=["metric-slider"])
            w_hall = gr.Slider(0,1,p0[2],step=0.01,label="Hallucination", elem_classes=["metric-slider"])
            w_rel  = gr.Slider(0,1,p0[3],step=0.01,label="Relevance",     elem_classes=["metric-slider"])
            w_bias = gr.Slider(0,1,p0[4],step=0.01,label="Bias/Toxicity", elem_classes=["metric-slider"])
            temp = gr.Slider(0,1,0,step=0.01,label="temperature")
            show_ev = gr.Checkbox(True,label="Show evidence spans")

            run = gr.Button("🔁 Generate & Evaluate")
            gen_sum = gr.Textbox(label="Generated Summary", lines=6, visible=True)
            table  = gr.DataFrame(label="Metrics")
            comm   = gr.JSON(label="Comments JSON")
            score  = gr.JSON(label="Average score")
            tokbox = gr.JSON(label="Token usage")
            csv_dl = gr.File(label="CSV download")
            zip_dl = gr.File(label="Raw JSON zip")

            def toggle_ui(auto):
                return (
                    gr.update(visible=not auto, interactive=not auto),
                    gr.update(visible=auto, interactive=auto),
                    gr.update(visible=auto, interactive=auto),
                    gr.update(value=("🔁 Generate & Evaluate" if auto else "✅ Only Evaluate")),
                    gr.update(visible=auto)  # toggle gen_sum
                )

            auto_gen_toggle.change(
                toggle_ui, 
                auto_gen_toggle, 
                [summary, prompt, model, run, gen_sum]
            )

            def unified_run(article, prompt, model, summary, auto_flag, variant, active_back, temp,
                            w_cov, w_align, w_hall, w_rel, w_bias, show_ev):
                if auto_flag and not summary:
                    if not is_prompt_valid_for_summary(prompt):
                        return "⛔ Prompt rejected: not summarization-related.", None, None, None, None, None, None
                    summary = generate_summary_from_openrouter(article, prompt, model)
                elif not auto_flag and not summary:
                    return "⚠️ Please provide a summary or enable auto-generation.", None, None, None, None, None, None

                
                return summary, *evaluate(article, summary, variant, active_back, temp, w_cov, w_align, w_hall, w_rel, w_bias, show_ev)

            run.click(
                unified_run, 
                [article, prompt, model, summary, auto_gen_toggle, variant, back, temp,
                 w_cov,w_align,w_hall,w_rel,w_bias,show_ev],
                [gen_sum, table, comm, score, tokbox, csv_dl, zip_dl]
            )

        # ▸ Tab 3: Comparison
                # ▸ Tab 3: Comparison (manual inputs for both human and model, no import button)
        with gr.Tab("📊 Comparison"):
            with gr.Column():
                gr.Markdown("## Compare Human vs Model Evaluations")
                gr.Markdown("### 🧍 Human Evaluation")
                with gr.Row():
                    hc = gr.Slider(1, 10, 1, step=1, label="Coverage")
                    ha = gr.Slider(1, 10, 1, step=1, label="Alignment")
                    hh = gr.Slider(1, 10, 1, step=1, label="Hallucination")
                    hr = gr.Slider(1, 10, 1, step=1, label="Relevance")
                    hb = gr.Slider(1, 10, 1, step=1, label="Bias/Toxicity")
                human_comments = gr.Textbox(label="Human Comments")

                gr.Markdown("### 🤖 Model Evaluation")
                with gr.Row():
                    mc = gr.Slider(1, 10, 1, step=1, label="Coverage")
                    ma = gr.Slider(1, 10, 1, step=1, label="Alignment")
                    mh = gr.Slider(1, 10, 1, step=1, label="Hallucination")
                    mr = gr.Slider(1, 10, 1, step=1, label="Relevance")
                    mb = gr.Slider(1, 10, 1, step=1, label="Bias/Toxicity")
                model_comments = gr.Textbox(label="Model Comments")

                def compare_structured(hc, ha, hh, hr, hb, human_comments, mc, ma, mh, mr, mb, model_comments):
                    human_scores = {
                        "coverage": hc,
                        "alignment": ha,
                        "hallucination": hh,
                        "relevance": hr,
                        "bias_toxicity": hb
                    }
                    model_scores = {
                        "coverage": mc,
                        "alignment": ma,
                        "hallucination": mh,
                        "relevance": mr,
                        "bias_toxicity": mb
                    }
                    return run_comparison(human_scores, human_comments, model_scores, model_comments)

                compare_btn = gr.Button("🔍 Compare")
                output_analysis = gr.Textbox(label="Analysis", lines=10)
                compare_btn.click(
                    compare_structured,
                    [hc, ha, hh, hr, hb, human_comments, mc, ma, mh, mr, mb, model_comments],
                    output_analysis
                ) 

demo.launch(share=True, show_error=True)
