import os, json, orjson

# Optional .env loading so local runs can pick up keys without exporting
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

PROMPT_COMMENTS = """You are an email quality reviewer. Provide subjective comments (1-2 sentences) with reasoning for each metric, based on the email and scores. Suggest improvements if score <8.

Email:
Subject: {subject}
Body: {body}

Scores and explanations: {scores_json}

Metrics: clarity, length, spam_score, personalization, tone, grammatical_hygiene

Output JSON only:
{{
 "clarity": "comment text",
 "length": "comment text",
 ...
}}
No prose."""

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
    return {}  # fallback to empty dict on failure

def _openai(p):
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    r = client.chat.completions.create(model="gpt-4o-mini", temperature=0.2,  # Slight temp for subjectivity
        messages=[{"role":"user","content":p}])
    return r.choices[0].message.content, r.usage

def _claude(p):
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    m = client.messages.create(model="claude-3-5-sonnet-20240620", max_tokens=800, temperature=0.2,
        messages=[{"role":"user","content":p}])
    return m.content[0].text, m.usage

def _heuristic_comment_for_metric(metric: str, score: float, reasons: list, subject: str, body: str) -> str:
    s = float(score or 0.0)
    rs = reasons or []
    def has(tag):
        return any(tag in r for r in rs)
    if metric == "clarity":
        if s >= 8:
            return "Clear ask and concise intro; subject is informative."
        if has("ask_signals="):
            return "Some ask signals detected; tighten the intro and subject for more clarity."
        return "Clarify the ask, make the subject more specific, and tighten the opening."
    if metric == "length":
        if s >= 8:
            return "Length is within the ideal band for this email class."
        return "Adjust length toward the ideal range; aim for concise, informative copy."
    if metric == "spam_score":
        if s >= 9.5 and not rs:
            return "No spammy phrasing detected; formatting looks safe."
        notes = []
        if has("ALL_CAPS_subject"): notes.append("avoid all‑caps subjects")
        if any("exclam" in r for r in rs): notes.append("limit exclamation marks")
        if any("lexicon_penalty" in r for r in rs): notes.append("reduce salesy phrases")
        return ("Reduce potential spam triggers: " + ", ".join(notes)) if notes else "Avoid spammy phrasing and excessive punctuation."
    if metric == "personalization":
        if s >= 8:
            return "Personalization is relevant and well‑balanced."
        return "Add one or two relevant personal details (name, role, context) without being intrusive."
    if metric == "tone":
        if s >= 8:
            return "Tone is professional with appropriate greeting/sign‑off."
        notes = []
        if has("greeting"): pass
        else: notes.append("add a brief greeting")
        if has("signoff"): pass
        else: notes.append("add a polite sign‑off")
        if has("ALL_CAPS_subject"): notes.append("avoid all‑caps in subject")
        if any("exclam" in r for r in rs): notes.append("limit exclamation marks")
        return ("Improve tone: " + ", ".join(notes)) if notes else "Aim for polite, professional tone with clear, direct phrasing."
    if metric == "grammatical_hygiene":
        if s >= 9:
            return "Grammar looks clean; no obvious issues."
        notes = []
        for r in rs:
            if r.startswith("typos="): notes.append("fix typos")
            if r.startswith("errors="): notes.append("resolve grammar/punctuation issues")
        return ("Improve grammatical hygiene: " + ", ".join(notes)) if notes else "Proofread for typos and punctuation consistency."
    return "No comment."


def _compose_heuristic_comments(subject, body, scores, explanations):
    out = {}
    for metric, score in (scores or {}).items():
        reasons = (explanations or {}).get(metric, [])
        out[metric] = _heuristic_comment_for_metric(metric, score, reasons, subject, body)
    return out


def subjective_comments(subject, body, scores, explanations, engine="openai"):
    scores_json = json.dumps({"scores": scores, "explanations": explanations}, ensure_ascii=False)
    prompt = PROMPT_COMMENTS.format(subject=subject or "", body=body or "", scores_json=scores_json)
    try:
        raw, usage = (_openai if engine=="openai" else _claude)(prompt)
        raw = raw.strip().strip("```").strip()
        data = _extract_json(raw)  # Use tolerant extractor
        # Validate and backfill missing keys using heuristics
        heur = _compose_heuristic_comments(subject, body, scores, explanations)
        if not isinstance(data, dict):
            data = heur
        else:
            for k, v in heur.items():
                if not data.get(k):
                    data[k] = v
        u = {"prompt_tokens": getattr(usage, "prompt_tokens", getattr(usage, "input_tokens", 0)),
             "completion_tokens": getattr(usage, "completion_tokens", getattr(usage, "output_tokens", 0))}
        return data, u
    except Exception:
        # Full fallback: deterministic comments only, zero usage
        return _compose_heuristic_comments(subject, body, scores, explanations), {"prompt_tokens": 0, "completion_tokens": 0}