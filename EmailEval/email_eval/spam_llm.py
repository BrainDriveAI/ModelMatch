import os, orjson as json

PROMPT_SPAM = """Analyze the email for spam-like marketing phrases (case-insensitive). Focus only on common sales-y terms like guarantees, urgency, exclusives, etc. Do not include profanity or unrelated flags.

Subject: {subject}
Body: {body}

Return counts per tier in JSON only:
- Tier A: High-spam (e.g., strong calls like "act now", "risk-free")
- Tier B: Medium-spam (e.g., "limited time", "exclusive deal")
- Tier C: Low-spam (e.g., "great offer", "bonus")

Output JSON:
{{"A": <int count>, "B": <int count>, "C": <int count>}}
No prose or lists of phrases.
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
    return {"A": 0, "B": 0, "C": 0}  # fallback

def _openai(prompt):
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    r = client.chat.completions.create(model="gpt-4o-mini", temperature=0,
        messages=[{"role":"user","content":prompt}])
    return r.choices[0].message.content, r.usage

def _claude(prompt):
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    m = client.messages.create(model="claude-3-5-sonnet-20240620", max_tokens=300, temperature=0,
        messages=[{"role":"user","content":prompt}])
    return m.content[0].text, m.usage

def spam_counts(subject, body, engine="openai"):
    p = PROMPT_SPAM.format(subject=subject or "", body=(body or "")[:8000])
    raw, usage = (_openai if engine=="openai" else _claude)(p)
    raw = raw.strip().strip("```").strip()
    data = _extract_json(raw)
    u = {"prompt_tokens": getattr(usage, "prompt_tokens", getattr(usage, "input_tokens", 0)),
         "completion_tokens": getattr(usage, "completion_tokens", getattr(usage, "output_tokens", 0))}
    return {"A": int(data.get("A",0)), "B": int(data.get("B",0)), "C": int(data.get("C",0))}, u