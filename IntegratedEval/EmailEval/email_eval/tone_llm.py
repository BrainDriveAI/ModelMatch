import os, orjson as json

PROMPT_TONE = """Return JSON only with tone flags for professional email.

<EMAIL>
Subject: {subject}

{body}
</EMAIL>

Output JSON:
{{
 "too_aggressive": true|false,
 "overly_casual_for_b2b": true|false,
 "passive_aggressive_markers": [string]
}}
No prose.
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
    return {"too_aggressive": False, "overly_casual_for_b2b": False, "passive_aggressive_markers": []}  # fallback

def _openai(prompt):
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    r = client.chat.completions.create(model="gpt-4o", temperature=0,
        messages=[{"role":"user","content":prompt}])
    usage = r.usage
    return r.choices[0].message.content, {"prompt_tokens": getattr(usage,"prompt_tokens",0), "completion_tokens": getattr(usage,"completion_tokens",0)}

def _claude(prompt):
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    m = client.messages.create(model="claude-3-5-sonnet-20240620", max_tokens=512, temperature=0,
        messages=[{"role":"user","content":prompt}])
    return m.content[0].text, {"prompt_tokens": getattr(m.usage, "input_tokens", 0), "completion_tokens": getattr(m.usage, "output_tokens", 0)}

def tone_flags(subject, body, engine="openai"):
    raw, u = (_openai if engine=="openai" else _claude)(PROMPT_TONE.format(subject=subject or "", body=body or ""))
    raw = raw.strip().strip("```").strip()
    return _extract_json(raw), u  # Use tolerant extractor