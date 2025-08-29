import os, orjson as json
import regex as re
from .preprocess import sentences

PROMPT_CLARITY = """You are an email clarity scorer. Evaluate based on these criteria:

Input:
Subject: {subject}
Body: {body}

Criteria:
- Explicit ask (0-5): Detect if there's a clear call to action (e.g., please review, schedule, confirm). Score higher for direct, polite asks with timelines.
- Subject usefulness (0-3): Does the subject convey topic, outcome, or time? E.g., includes review, update, by date.
- Intro clarity (0-2): First 1-2 sentences (≤35 words) state purpose clearly.

Compute total clarity = ask + subject + intro (0-10).

Return ONLY JSON (no prose):
{{
 "has_explicit_ask": <bool>,
 "ask_signals": [<verbatim spans or phrases>],
 "subject_useful": <bool>,
 "intro_clear": <bool>,
 "score_components": {{"ask": <0-5>, "subject": <0-3>, "intro": <0-2>}},
 "clarity_score_0_10": <0-10>
}}
"""

def _extract_json(text: str):
    """Tolerant JSON extractor: strips codefences and grabs the first {...} block."""
    t = (text or "").strip().strip("```").strip()
    # fast path
    try:
        return json.loads(t)
    except Exception:
        pass
    # fallback: find first balanced braces
    start = t.find("{")
    end = t.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(t[start:end+1])
        except Exception:
            pass
    return {
        "has_explicit_ask": False,
        "ask_signals": [],
        "subject_useful": False,
        "intro_clear": False,
        "score_components": {"ask": 0, "subject": 0, "intro": 0},
        "clarity_score_0_10": 0
    }  # fallback

def _openai_call(prompt):
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[{"role":"user","content":prompt}]
    )
    content = resp.choices[0].message.content
    usage = resp.usage
    return content, {"prompt_tokens": getattr(usage,"prompt_tokens",0),
                     "completion_tokens": getattr(usage,"completion_tokens",0)}

def _claude_call(prompt):
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    msg = client.messages.create(model="claude-3-5-sonnet-20240620",
                                 max_tokens=800, temperature=0,
                                 messages=[{"role":"user","content":prompt}])
    content = msg.content[0].text
    usage = {"prompt_tokens": getattr(msg.usage, "input_tokens", 0),
             "completion_tokens": getattr(msg.usage, "output_tokens", 0)}
    return content, usage

def clarity_score(subject, body, engine="openai"):
    prompt = PROMPT_CLARITY.format(subject=subject or "", body=body or "")
    try:
        raw, usage = (_openai_call if engine=="openai" else _claude_call)(prompt)
        llm_json = _extract_json(raw)
    except Exception:
        llm_json = {}
        usage = {"prompt_tokens":0, "completion_tokens":0}

    # Extract and validate scores
    sc = llm_json.get("score_components", {}) if isinstance(llm_json, dict) else {}
    ask = min(max(int(sc.get("ask", 0)), 0), 5)
    subj = min(max(int(sc.get("subject", 0)), 0), 3)
    intro = min(max(int(sc.get("intro", 0)), 0), 2)
    clarity = max(0, min(10, ask + subj + intro))

    return clarity, {"llm": llm_json, "usage": usage, "fallback": False}