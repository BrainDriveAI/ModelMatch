import os, orjson as json
import regex as re

# Try optional .env so local runs can pick up keys without exporting
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

PROMPT_PERSONALIZATION = """Return JSON only describing personalization cues in the email.

<EMAIL>
Subject: {subject}

{body}
</EMAIL>

Definition:
- Personalization cues: explicit references to the recipient (name, role, company, location, prior context), dynamic fields, or tailored details that indicate the message is written for a specific person/situation.
- Relevance: whether the cue logically relates to the email’s topic/ask.
- Intrusive: cues that feel privacy-invasive (e.g., excessive personal history) or out of place for the context.

Output JSON strictly in this schema (no prose):
{{
  "cues": [
    {{"text": <string>, "type": <"name"|"company"|"role"|"location"|"context">, "relevant": <true|false>}} ,
    ...
  ],
  "too_intrusive": <true|false>
}}
"""


def _extract_json(text: str):
    t = (text or "").strip().strip("```").strip()
    try:
        return json.loads(t)
    except Exception:
        pass
    start = t.find("{"); end = t.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(t[start:end+1])
        except Exception:
            pass
    return {"cues": [], "too_intrusive": False}


def _openai_call(prompt):
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    r = client.chat.completions.create(model="gpt-4o-mini", temperature=0, messages=[{"role":"user","content":prompt}])
    usage = r.usage
    return r.choices[0].message.content, {"prompt_tokens": getattr(usage, "prompt_tokens", 0), "completion_tokens": getattr(usage, "completion_tokens", 0)}


def _claude_call(prompt):
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    m = client.messages.create(model="claude-3-5-sonnet-20240620", max_tokens=600, temperature=0, messages=[{"role":"user","content":prompt}])
    return m.content[0].text, {"prompt_tokens": getattr(m.usage, "input_tokens", 0), "completion_tokens": getattr(m.usage, "output_tokens", 0)}


def _heuristic_personalization(subject: str, body: str):
    text = f"{subject or ''}\n{body or ''}"
    cues = []

    # Name/greeting detection (simple heuristic)
    m = re.search(r"(?i)^(hi|hello|dear)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b", (body or "").strip())
    if m:
        cues.append({"text": m.group(2), "type": "name", "relevant": True})

    # Role/company keywords
    if re.search(r"(?i)\b(ceo|cto|founder|manager|director|engineer|designer)\b", text):
        cues.append({"text": "role_reference", "type": "role", "relevant": True})
    if re.search(r"(?i)\b(inc\.|llc|limited|ltd|corp\.|company|startup)\b", text):
        cues.append({"text": "company_reference", "type": "company", "relevant": True})

    # Contextual references
    if re.search(r"(?i)\b(follow\s*up|as discussed|regarding|re:|meeting|last week|yesterday)\b", text):
        cues.append({"text": "context_reference", "type": "context", "relevant": True})

    too_intrusive = bool(re.search(r"(?i)\b(ssn|social security|salary|home address|private|confidential)\b", text))
    return {"cues": cues, "too_intrusive": too_intrusive}


def personalization_flags(subject: str, body: str, engine: str = "openai"):
    prompt = PROMPT_PERSONALIZATION.format(subject=subject or "", body=body or "")
    try:
        raw, usage = (_openai_call if engine == "openai" else _claude_call)(prompt)
        data = _extract_json(raw)
        # Validate structure
        cues = data.get("cues", []) if isinstance(data, dict) else []
        if not isinstance(cues, list): cues = []
        too_intrusive = bool(data.get("too_intrusive", False)) if isinstance(data, dict) else False
        return {"cues": cues, "too_intrusive": too_intrusive}, usage
    except Exception:
        # Fallback to heuristics with zero usage
        return _heuristic_personalization(subject, body), {"prompt_tokens": 0, "completion_tokens": 0}


