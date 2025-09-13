import re, json
from typing import List

# Heuristic normalization & role extraction. If roles unknown, we keep all text.

SPEAKER_RE = re.compile(r"^(user|client|customer|advisor|agent|assistant|model)\s*[:\-]", re.I)


def normalize_conversation(text: str) -> List[str]:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return lines


def extract_model_utterances(lines: List[str], prefer_llm_provider: str = None) -> str:
    model_lines = []
    user_aliases = ("user", "client", "customer")
    model_aliases = ("advisor", "agent", "assistant", "model")

    for l in lines:
        m = SPEAKER_RE.match(l)
        if m:
            who = m.group(1).lower()
            if who in model_aliases:
                model_lines.append(SPEAKER_RE.sub("", l).strip())
            # if user line, skip
        else:
            # Untagged; keep it (we prefer to include content to avoid missing eval)
            model_lines.append(l)

    return "\n".join(model_lines).strip()
