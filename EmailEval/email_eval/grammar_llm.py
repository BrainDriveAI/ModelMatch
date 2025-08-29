import os, orjson as json

PROMPT_GRAMMAR = """Analyze the email for grammatical hygiene, typos, and errors.

Subject: {subject}
Body: {body}

Tasks:
- Count typos or spelling errors.
- List grammar errors (e.g., subject-verb agreement, punctuation).
- Score 0-10: 10 for perfect, deduct for errors (e.g., -1 per minor, -2 per major, scaled by length).

Output JSON:
{{
 "typos_count": <int>,
 "grammar_errors": [<string>],
 "score_0_10": <float>
}}
No prose.
"""

def _extract_json(text: str):
    t = (text or "").strip().strip("```").strip()
    try:
        return json.loads(t)
    except:
        pass
    start = t.find("{")
    end = t.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(t[start:end+1])
        except:
            pass
    return {"typos_count": 0, "grammar_errors": [], "score_0_10": 10.0}

def _openai(p):
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    r = client.chat.completions.create(model="gpt-4o-mini", temperature=0,
        messages=[{"role":"user","content":p}])
    return r.choices[0].message.content, r.usage

def _claude(p):
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    m = client.messages.create(model="claude-3-5-sonnet-20240620", max_tokens=512, temperature=0,
        messages=[{"role":"user","content":p}])
    return m.content[0].text, m.usage

def grammar_score(subject, body, engine="openai"):
    raw, usage = (_openai if engine=="openai" else _claude)(PROMPT_GRAMMAR.format(subject=subject or "", body=body or ""))
    raw = raw.strip().strip("```").strip()
    data = _extract_json(raw)
    u = {"prompt_tokens": getattr(usage, "prompt_tokens", getattr(usage, "input_tokens", 0)),
         "completion_tokens": getattr(usage, "completion_tokens", getattr(usage, "output_tokens", 0))}
    score = float(data.get("score_0_10", 10.0))
    reasons = []
    if data.get("typos_count", 0) > 0: reasons.append(f"typos={data['typos_count']}")
    if data.get("grammar_errors"): reasons.append(f"errors={'; '.join(data['grammar_errors'])}")
    return score, reasons, u