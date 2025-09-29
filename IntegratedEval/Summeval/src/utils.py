import json

def _inject(prompt: str, art: str, summ: str) -> str:
    return prompt.replace("{insert_article_here}", art).replace("{insert_summary_here}", summ)

def openai_call(p, a, s, temp):
    from src.api_clients import get_openai_client
    from src.config import MAX_TOKENS
    safe_prompt = "SYSTEM INSTRUCTION: Respond ONLY with the five JSON objects, no markdown, no extra text.\n\n" + _inject(p, a, s)
    client = get_openai_client()
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": safe_prompt}],
        max_tokens=MAX_TOKENS["OpenAI"],
        temperature=temp
    )
    return r.choices[0].message.content, r.usage.total_tokens

def deepseek_call(p, a, s, temp):
    from src.api_clients import deepseek_client
    from src.config import MAX_TOKENS
    safe_prompt = "SYSTEM INSTRUCTION: Respond ONLY with the five JSON objects, no markdown, no extra text.\n\n" + _inject(p, a, s)
    r = deepseek_client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": safe_prompt}],
        max_tokens=MAX_TOKENS["DeepSeek"],
        temperature=temp
    )
    return r.choices[0].message.content, r.usage.total_tokens


def claude_call(p, a, s, temp):
    from src.api_clients import get_claude_client
    from src.config import MAX_TOKENS
    safe_prompt = "SYSTEM INSTRUCTION: Respond ONLY with the five JSON objects, no markdown, no extra text.\n\n" + _inject(p, a, s)
    client = get_claude_client()
    try:
        r = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            messages=[{"role": "user", "content": safe_prompt}],
            max_tokens=MAX_TOKENS["Claude"],
            temperature=temp
        )
        txt = r.content[0].text.strip()
        tot = r.usage.input_tokens + r.usage.output_tokens
        return txt, tot
    except Exception as e:
        print(f"Claude API call failed: {e}")
        raise

def split_json_objects(s: str):
    objs, depth, start = [], 0, None
    for i, ch in enumerate(s):
        if ch == "{":
            if depth == 0: start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                objs.append(s[start:i + 1])
    return objs

def parse(raw: str):
    out = {}
    for js in split_json_objects(raw):
        try:
            d = json.loads(js)
        except json.JSONDecodeError:
            continue
        m = str(d.get("metric", "")).lower().replace("-", "_")
        canonical = {
            "coverage": "coverage",
            "alignment": "alignment",
            "hallucination": "hallucination",
            "relevance": "relevance",
            "bias_toxicity": "bias_toxicity"
        }.get(m)
        if canonical:
            out[canonical] = d
            continue
        dl = {k.lower(): k for k in d}
        if "key_points" in dl: out["coverage"] = d
        elif "aspects" in dl: out["alignment"] = d
        elif "claims_checked" in dl: out["hallucination"] = d
        elif "article_theme" in dl: out["relevance"] = d
        elif ("bias_score" in dl) or ("biasscore" in dl): out["bias_toxicity"] = d
    return out

def wavg(m, w):
    if all(v == 0 for v in w.values()): return 0.0
    total = sum(w.values())
    return sum(m.get(k, {}).get("overall_score", 0) * w[k] for k in w) / total

def preset_vals(name):
    from src.config import PRESET
    return [PRESET[name][k] for k in ("coverage","alignment","hallucination","relevance","bias_toxicity")]
