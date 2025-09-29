import os, json, re
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple

# OpenAI
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

# Anthropic
try:
    import anthropic
except Exception:
    anthropic = None

class ProviderKind:
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

@dataclass
class Provider:
    kind: str
    model: str
    label: str

    def judge(self, system_prompt: str, user_prompt: str) -> Tuple[Dict[str, Any], Dict[str, int]]:
        raise NotImplementedError

class OpenAIProvider(Provider):
    def __init__(self, model: str):
        super().__init__(ProviderKind.OPENAI, model, f"OpenAI/{model}")
        if OpenAI is None:
            raise RuntimeError("openai package not available. Add to requirements.txt")
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def judge(self, system_prompt: str, user_prompt: str):
        # Use chat.completions for broader compatibility
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0
        )
        content = resp.choices[0].message.content
        usage = resp.usage
        usage_dict = {
            "prompt": getattr(usage, "prompt_tokens", 0) or getattr(usage, "input_tokens", 0) or 0,
            "completion": getattr(usage, "completion_tokens", 0) or getattr(usage, "output_tokens", 0) or 0,
            "total": getattr(usage, "total_tokens", 0) or 0,
        }
        return _safe_json(content), usage_dict

class AnthropicProvider(Provider):
    def __init__(self, model: str):
        super().__init__(ProviderKind.ANTHROPIC, model, f"Anthropic/{model}")
        if anthropic is None:
            raise RuntimeError("anthropic package not available. Add to requirements.txt")
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    def judge(self, system_prompt: str, user_prompt: str):
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            temperature=0,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        # Anthropic returns a list of content blocks
        content = "".join([b.text for b in resp.content if hasattr(b, "text")])
        usage = getattr(resp, "usage", None)
        usage_dict = {
            "prompt": getattr(usage, "input_tokens", 0) if usage else 0,
            "completion": getattr(usage, "output_tokens", 0) if usage else 0,
            "total": (getattr(usage, "input_tokens", 0) + getattr(usage, "output_tokens", 0)) if usage else 0,
        }
        return _safe_json(content), usage_dict


def get_provider(kind: str, model: str) -> Provider:
    if kind == ProviderKind.OPENAI:
        return OpenAIProvider(model)
    elif kind == ProviderKind.ANTHROPIC:
        return AnthropicProvider(model)
    else:
        raise ValueError(f"Unknown provider kind: {kind}")

# ----------------------
# Helpers
# ----------------------
JSON_RE = re.compile(r"\{[\s\S]*\}")

def _safe_json(s: str) -> dict:
    try:
        return json.loads(s)
    except Exception:
        m = JSON_RE.search(s or "")
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
    return {}
