import os
import json
import tempfile
import zipfile
import concurrent.futures
import pandas as pd
from src.utils import _inject, openai_call, deepseek_call, claude_call, split_json_objects, parse, wavg
from src.config import MAX_TOKENS, PRESET

BACKENDS_ALL = {"OpenAI": openai_call, "DeepSeek": deepseek_call, "Claude": claude_call}

last_summary = {}
last_eval_result = {}

def evaluate(article, summary, variant, active_back, temp,
             w_cov, w_align, w_hall, w_rel, w_bias, show_ev):

    weights = dict(coverage=w_cov, alignment=w_align, hallucination=w_hall,
                   relevance=w_rel, bias_toxicity=w_bias)

    run_variants = ["Twin-Lock","Judge-Lock"] if variant=="ParallelX-TJ" else [variant]

    rows, feedback, tokens, raw_blobs = [], {}, {b:0 for b in active_back}, {}

    PROMPTS = {
        "Twin-Lock":  open("prompts/twinlock.txt",  encoding="utf-8").read(),
        "Judge-Lock": open("prompts/judgelock.txt", encoding="utf-8").read(),
    }

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as exe:
        futures = []
        for v in run_variants:
            prompt = PROMPTS[v]
            for b in active_back:
                futures.append(
                    exe.submit(lambda args: (args[0],args[1],*args[2]),
                               (v,b,BACKENDS_ALL[b](prompt, article, summary, temp)))
                )

        for fut in concurrent.futures.as_completed(futures):
            vtag, backend, raw, tok = fut.result()
            tokens[backend] += tok
            raw_blobs[f"{vtag}_{backend}"] = raw
            parsed = parse(raw)
            if not show_ev and "hallucination" in parsed:
                for c in parsed["hallucination"].get("claims_checked", []):
                    c.pop("evidence", None)
            rows.append({
                "Variant":       vtag,
                "Model":         backend,
                "coverage":      parsed.get("coverage", {}).get("overall_score", 0),
                "alignment":     parsed.get("alignment", {}).get("overall_score", 0),
                "hallucination": parsed.get("hallucination", {}).get("overall_score", 0),
                "relevance":     parsed.get("relevance", {}).get("overall_score", 0),
                "bias_toxicity": parsed.get("bias_toxicity", {}).get("overall_score", 0),
                "Total":         round(wavg(parsed, weights), 2),
            })
            feedback[f"{vtag} • {backend}"] = parsed

    df = pd.DataFrame(rows)
    avg = df.groupby("Variant")["Total"].mean().round(2).to_dict()
    if variant != "ParallelX-TJ":
        avg = {variant: avg.get(variant)}

    tmp = tempfile.mkdtemp()
    csv_path = os.path.join(tmp,"metrics.csv"); df.to_csv(csv_path,index=False)
    zip_path = os.path.join(tmp,"raw_json.zip")
    with zipfile.ZipFile(zip_path,"w") as z:
        for tag, blob in raw_blobs.items():
            p = os.path.join(tmp, f"{tag}.json")
            with open(p,"w",encoding="utf-8") as f: f.write(blob)
            z.write(p, arcname=os.path.basename(p))

    last_eval_result.update({"scores": avg, "comments": feedback})
    return df, feedback, avg, tokens, csv_path, zip_path